#!/usr/bin/env python3
"""Content-addressed project snapshots, revision impact and recoverable restoration."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
from check_bid import digest, identifier, local_path, SHA
from reference_tools import atomic, commit, json_bytes, load, project


def managed_files(root, bid, plan, refs):
    paths = {"bid.json", "long-task.json", "references.json", "brief.md", "MANIFEST.md"}
    originals = {s["path"] for s in bid["sources"] if s["path"]}
    paths.update(originals)
    paths.update(plan.get("context_paths", []))
    for chapter in plan["chapters"]:
        paths.add(chapter["path"])
        if chapter.get("checkpoint"):
            paths.add(chapter["checkpoint"]["review_path"])
    for asset in plan.get("assets", []):
        paths.update(asset[k] for k in ("path", "editable_path", "preview_path"))
    for note in refs["source_notes"]:
        paths.update(note[k] for k in ("extract_path", "review_path"))
    for gap in plan.get("supplements", []):
        paths.update(e["path"] for e in gap["evidence"])
    if plan.get("rendered"):
        paths.update(plan["rendered"][k] for k in ("path", "qa_path"))
    for folder in ("work/chapters", "review"):
        base = local_path(root, folder)
        if base.exists() and not base.is_dir():
            raise ValueError("expected project data directory: " + folder)
        if base.is_dir():
            for file in base.rglob("*"):
                if file.is_file() or file.is_symlink():
                    paths.add(file.relative_to(root).as_posix())
    files, missing = {}, []
    for relative in sorted(paths - {""}):
        p = local_path(root, relative)
        if Path(relative).parts[0] in {"scripts", "templates", "references", "rules", ".agents", ".claude", ".git", ".vibe-tool", "archives"}:
            raise ValueError("snapshot data path overlaps configuration/archive: " + relative)
        if p and p.is_file():
            files[relative] = {"sha256": digest(p), "role": "original" if relative in originals else "working"}
        elif p and p.exists():
            raise ValueError("expected file in project data: " + relative)
        else:
            missing.append(relative)
    return files, missing


def object_path(root, sha):
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ValueError("invalid snapshot object hash")
    return local_path(root, "archives/revisions/objects/" + sha.lower())


def record_path(root, rid):
    identifier(rid, "revision ID")
    return local_path(root, "archives/revisions/" + rid + ".json")


def data_path(root, relative):
    path = local_path(root, relative)
    if path is None or Path(relative).parts[0] in {"scripts", "templates", "references", "rules", ".agents", ".claude", ".git", ".vibe-tool", "archives"}:
        raise ValueError("revision path overlaps configuration/archive: " + relative)
    return path


def read_record(root, rid):
    data = load(record_path(root, rid))
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data.get("schema_version") != 1 or data.get("id") != rid or not isinstance(data.get("files"), dict):
        raise ValueError("invalid revision record")
    for relative, entry in data["files"].items():
        data_path(root, relative)
        if not isinstance(entry, dict) or set(entry) != {"sha256", "role"} or entry["role"] not in {"original", "working"}:
            raise ValueError("invalid revision entry")
        obj = object_path(root, entry["sha256"])
        if not obj.is_file() or digest(obj) != entry["sha256"]:
            raise ValueError("snapshot object missing or corrupted: " + relative)
    return data


def snapshot(root, rid, reason, parent=""):
    if not reason.strip():
        raise ValueError("snapshot requires a concrete --reason")
    if parent:
        read_record(root, parent)
    bid, plan, refs = project(root)
    files, missing = managed_files(root, bid, plan, refs)
    result = dict(schema_version=1, id=rid, reason=reason, parent=parent, files=files, missing=missing)
    path = record_path(root, rid)
    if path.exists():
        if read_record(root, rid) == result:
            return result, False
        raise ValueError("revision ID already records different content; use a new ID")
    for relative, entry in files.items():
        payload = local_path(root, relative).read_bytes()
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise ValueError("project changed during snapshot")
        obj = object_path(root, entry["sha256"])
        if obj.exists():
            if digest(obj) != entry["sha256"]:
                raise ValueError("existing snapshot object hash mismatch")
        else:
            atomic(obj, payload)
    # Detect a late working-file edit before publishing the revision record.
    if managed_files(root, *project(root))[0] != files:
        raise ValueError("project changed before snapshot publication")
    atomic(path, json_bytes(result))
    return result, True


def record_json(root, record, relative, fallback):
    entry = record["files"].get(relative)
    if not entry:
        return fallback
    path = local_path(root, relative) if record.get("live") else object_path(root, entry["sha256"])
    return load(path)


def difference(before, after):
    changes = []
    for path in sorted(set(before["files"]) | set(after["files"])):
        old = before["files"].get(path, {}).get("sha256")
        new = after["files"].get(path, {}).get("sha256")
        if old != new:
            changes.append(dict(path=path, before_sha256=old, after_sha256=new,
                                status="added" if old is None else "removed" if new is None else "modified"))
    return changes


def text_differences(root, before, after, changes):
    output = []
    for change in changes:
        path = change["path"]
        versions = []
        for record in (before, after):
            entry = record["files"].get(path)
            if not entry:
                versions.append("")
                continue
            source = local_path(root, path) if record.get("live") else object_path(root, entry["sha256"])
            payload = source.read_bytes()
            if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
                raise ValueError("file changed during difference review: " + path)
            try:
                versions.append(payload.decode("utf-8"))
            except UnicodeDecodeError:
                versions.append(None)
        if None in versions:
            output.append(dict(path=path, binary=True, diff="", truncated=False))
            continue
        lines = list(difflib.unified_diff(versions[0].splitlines(keepends=True), versions[1].splitlines(keepends=True),
                                         fromfile="before/" + path, tofile="after/" + path))
        output.append(dict(path=path, binary=False, diff="".join(lines[:200]), truncated=len(lines) > 200))
    return output


def impact(root, before, after, changes):
    old_bid = record_json(root, before, "bid.json", {"sources": [], "requirements": []})
    new_bid = record_json(root, after, "bid.json", {"sources": [], "requirements": []})
    old_plan = record_json(root, before, "long-task.json", {"chapters": []})
    new_plan = record_json(root, after, "long-task.json", {"chapters": []})
    old_refs = record_json(root, before, "references.json", {"source_notes": [], "citations": []})
    new_refs = record_json(root, after, "references.json", {"source_notes": [], "citations": []})
    changed_paths = {e["path"] for e in changes}
    source_ids = {s["id"] for b in (old_bid, new_bid) for s in b["sources"] if s["path"] in changed_paths}
    for key, idkey in (("sources", "id"), ("requirements", "id")):
        old = {e[idkey]: e for e in old_bid[key]}
        new = {e[idkey]: e for e in new_bid[key]}
        changed = {iid for iid in old.keys() | new.keys() if old.get(iid) != new.get(iid)}
        if key == "sources":
            source_ids.update(changed)
        else:
            changed_requirements = changed
    old_notes = {n["source_id"]: n for n in old_refs["source_notes"]}
    new_notes = {n["source_id"]: n for n in new_refs["source_notes"]}
    for sid in old_notes.keys() | new_notes.keys():
        if old_notes.get(sid) != new_notes.get(sid):
            source_ids.add(sid)
            for note in (old_notes.get(sid), new_notes.get(sid)):
                if note and note["supersedes"]:
                    source_ids.add(note["supersedes"])
        for note in (old_notes.get(sid), new_notes.get(sid)):
            if note and {note["extract_path"], note["review_path"]} & changed_paths:
                source_ids.add(sid)
    old_cites = {c["id"]: c for c in old_refs["citations"]}
    new_cites = {c["id"]: c for c in new_refs["citations"]}
    changed_cites = {cid for cid in old_cites.keys() | new_cites.keys() if old_cites.get(cid) != new_cites.get(cid)}
    affected, chapters = set(), {}
    for p in (old_plan, new_plan):
        for c in p["chapters"]:
            chapters[c["id"]] = c
            source_req_ids = {r["id"] for b in (old_bid, new_bid) for r in b["requirements"]
                              if r["source_id"] in source_ids or any(e["source_id"] in source_ids for e in r["evidence"])}
            if c["path"] in changed_paths or set(c["requirement_ids"]) & (changed_requirements | source_req_ids):
                affected.add(c["id"])
            if c.get("checkpoint") and c["checkpoint"]["review_path"] in changed_paths:
                affected.add(c["id"])
        if set(p.get("context_paths", [])) & changed_paths:
            affected.update(c["id"] for c in p["chapters"])
        for a in p.get("assets", []):
            if {a[k] for k in ("path", "editable_path", "preview_path")} & changed_paths or set(a["source_ids"]) & source_ids:
                affected.update(a["chapter_ids"])
    for c in list(old_cites.values()) + list(new_cites.values()):
        if c["id"] in changed_cites or c["source_id"] in source_ids:
            affected.update(c["chapter_ids"])
            changed_cites.add(c["id"])
    old_assets = {a["id"]: a for a in old_plan.get("assets", [])}
    new_assets = {a["id"]: a for a in new_plan.get("assets", [])}
    for aid in old_assets.keys() | new_assets.keys():
        if old_assets.get(aid) != new_assets.get(aid):
            for asset in (old_assets.get(aid), new_assets.get(aid)):
                if asset:
                    affected.update(asset["chapter_ids"])
    old_chapters = {c["id"]: c for c in old_plan["chapters"]}
    new_chapters = {c["id"]: c for c in new_plan["chapters"]}
    for cid in old_chapters.keys() | new_chapters.keys():
        old = {k: v for k, v in old_chapters.get(cid, {}).items() if k not in {"checkpoint", "status"}}
        new = {k: v for k, v in new_chapters.get(cid, {}).items() if k not in {"checkpoint", "status"}}
        if old != new:
            affected.add(cid)
    direct = set(affected)
    while True:
        more = {cid for cid, c in chapters.items() if set(c["depends_on"]) & affected}
        if more <= affected:
            break
        affected.update(more)
    return dict(source_ids=sorted(source_ids), citation_ids=sorted(changed_cites),
                direct_chapters=sorted(direct), dependent_chapters=sorted(affected - direct))


def current_record(root, fallback=None):
    try:
        bid, plan, refs = project(root)
        files, missing = managed_files(root, bid, plan, refs)
        return dict(files=files, missing=missing, live=True)
    except (OSError, ValueError, TypeError, KeyError):
        if fallback is None:
            raise
        # Recovery still works when a user is halfway through editing JSON.
        files, missing = {}, []
        scope = dict(fallback["files"])
        for relative in ("bid.json", "long-task.json", "references.json", "brief.md", "MANIFEST.md"):
            scope.setdefault(relative, {"role": "working"})
        for relative, entry in scope.items():
            p = local_path(root, relative)
            if p and p.is_file():
                files[relative] = dict(sha256=digest(p), role=entry["role"])
            else:
                missing.append(relative)
        return dict(files=files, missing=missing, live=True, recovery_scope=True)


def safety_record(root, rid, current, reason):
    for relative, entry in current["files"].items():
        payload = local_path(root, relative).read_bytes()
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise ValueError("current state changed before restore")
        obj = object_path(root, entry["sha256"])
        if obj.exists() and digest(obj) != entry["sha256"]:
            raise ValueError("safety object corrupted")
        if not obj.exists():
            atomic(obj, payload)
    record = dict(schema_version=1, id=rid, reason=reason, parent="",
                  files=current["files"], missing=current["missing"])
    atomic(record_path(root, rid), json_bytes(record))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("snapshot", "diff", "restore"))
    parser.add_argument("root", type=Path)
    parser.add_argument("--id")
    parser.add_argument("--reason", default="")
    parser.add_argument("--parent", default="")
    parser.add_argument("--from", dest="from_id")
    parser.add_argument("--to", dest="to_id")
    parser.add_argument("--apply", action="store_true", help="Actually restore; default is a preview")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if args.command == "snapshot":
            record, created = snapshot(root, args.id, args.reason, args.parent)
            print(f"SNAPSHOT {record['id']} files={len(record['files'])} new={created}; originals retained")
        elif args.command == "diff":
            before = read_record(root, args.from_id)
            after = read_record(root, args.to_id) if args.to_id else current_record(root, before)
            changes = difference(before, after)
            scope = {"warning": "Current metadata is mid-edit; structural impact requires repair."} if after.get("recovery_scope") else impact(root, before, after, changes)
            print(json.dumps(dict(changes=changes, impact=scope,
                                  text_diffs=text_differences(root, before, after, changes),
                                  note="Impact is for review; user edits are not overwritten."), ensure_ascii=False, indent=2))
        else:
            target = read_record(root, args.id)  # Verify all objects before any mutation.
            current = current_record(root, target)
            changes = difference(current, target)
            updates, preserved = {}, []
            for relative, entry in target["files"].items():
                path = local_path(root, relative)
                if entry["role"] == "original" and path.exists():
                    if digest(path) != entry["sha256"]:
                        raise ValueError("original has changed; preserve and investigate: " + relative)
                    continue
                if not path.is_file() or digest(path) != entry["sha256"]:
                    updates[relative] = object_path(root, entry["sha256"]).read_bytes()
            preserved = sorted(set(current["files"]) - set(target["files"]))
            if not args.apply:
                print(json.dumps(dict(restore_files=sorted(updates), preserve_new_files=preserved, action="preview only"), ensure_ascii=False, indent=2))
                return 0
            safety_id = "RESTORE-" + uuid.uuid4().hex[:12]
            safety_record(root, safety_id, current, "Before restoring " + args.id)
            commit(root, updates)
            for relative, entry in target["files"].items():
                if digest(local_path(root, relative)) != entry["sha256"]:
                    raise OSError("restored file hash mismatch: " + relative)
            print(f"RESTORED {args.id}; prior current state={safety_id}; preserved_new_files={len(preserved)}")
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print("REVISION ERROR " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
