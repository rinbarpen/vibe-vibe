#!/usr/bin/env python3
"""Receive original materials and audit stable source citations; no source rewriting."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import sys
import tempfile

sys.dont_write_bytecode = True
from check_bid import (array, choice, digest, fields, identifier, local_path,
                       SHA, SOURCE_KINDS, string, unique_object, validate_schema)

NOTE_FIELDS = ("source_id", "title", "origin", "original_name", "version", "source_date", "url", "use", "supersedes", "extract_path", "extract_sha256", "review_path", "review_sha256", "status")
CITE_FIELDS = ("id", "source_id", "locator", "usage", "summary", "chapter_ids", "historical", "note")


def load(path):
    if path.is_symlink():
        raise ValueError("symlink state file")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def empty():
    return {"schema_version": 1, "source_notes": [], "citations": []}


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()


def actual(root, path):
    p = local_path(root, path)
    return digest(p) if p and p.is_file() else "MISSING"


def valid_file(root, path, sha):
    return bool(sha and actual(root, path) == sha.lower())


def atomic(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".writing-ref-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def commit(root, updates):
    """Preserve previous bytes and roll back this small multi-file update on failure."""
    before = {}
    for relative, payload in updates.items():
        path = local_path(root, relative)
        if path is None or path.exists() and not path.is_file():
            raise ValueError("invalid update path: " + relative)
        before[relative] = path.read_bytes() if path.exists() else None
    for relative, payload in before.items():
        if payload is not None and payload != updates[relative]:
            sha = hashlib.sha256(payload).hexdigest()
            backup = local_path(root, f"archives/reference-state/{sha}/{Path(relative).name}")
            if backup.exists() and backup.read_bytes() != payload:
                raise ValueError("reference backup hash mismatch")
            if not backup.exists():
                atomic(backup, payload)
    written = []
    try:
        for relative, payload in updates.items():
            path = local_path(root, relative)
            current = path.read_bytes() if path.exists() else None
            if current != before[relative]:
                raise ValueError("project changed during update: " + relative)
            if current != payload:
                written.append(relative)
                atomic(path, payload)
                if path.read_bytes() != payload:
                    raise OSError("reference update verification failed: " + relative)
    except Exception:
        for relative in reversed(written):
            if before[relative] is None:
                local_path(root, relative).unlink()
            else:
                atomic(local_path(root, relative), before[relative])
        raise
    return written


def validate(refs, bid, plan, root):
    sources = validate_schema(bid, root)
    fields(refs, ("schema_version", "source_notes", "citations"), "references")
    if type(refs["schema_version"]) is not int or refs["schema_version"] != 1:
        raise ValueError("references.schema_version: expected integer 1")
    chapter_ids = {c["id"] for c in plan["chapters"]}
    notes, cites = {}, {}
    for key, target, required in (("source_notes", notes, NOTE_FIELDS), ("citations", cites, CITE_FIELDS)):
        array(refs[key], key)
        for item in refs[key]:
            fields(item, required, key + "[]")
            iid = identifier(item["source_id"] if key == "source_notes" else item["id"], key)
            if iid in target:
                raise ValueError("duplicate reference ID: " + iid)
            if item["source_id"] not in sources:
                raise ValueError("unknown source: " + str(item["source_id"]))
            target[iid] = item
    for sid, note in notes.items():
        for key in NOTE_FIELDS:
            string(note[key], sid + "." + key)
        choice(note["use"], {"fact", "style", "mixed"}, sid + ".use")
        choice(note["status"], {"pending", "reviewed"}, sid + ".status")
        for key in ("extract_path", "review_path"):
            local_path(root, note[key])
        if note["review_path"] and local_path(root, note["review_path"]) in {local_path(root, p) for p in ("bid.json", "long-task.json", "references.json", sources[sid]["path"], note["extract_path"])}:
            raise ValueError(sid + ": review record must be distinct from metadata and source files")
        for key in ("extract_sha256", "review_sha256"):
            if note[key] and not SHA.fullmatch(note[key]):
                raise ValueError(sid + ": invalid " + key)
        if note["supersedes"] and note["supersedes"] not in sources:
            raise ValueError(sid + ": unknown superseded source")
        seen, cursor = set(), sid
        while cursor in notes and notes[cursor]["supersedes"]:
            if cursor in seen:
                raise ValueError("superseded-source cycle")
            seen.add(cursor)
            cursor = notes[cursor]["supersedes"]
    for cid, cite in cites.items():
        if not cid.startswith("C-"):
            raise ValueError("citation ID must start with C-")
        for key in ("source_id", "locator", "summary", "note"):
            string(cite[key], cid + "." + key)
        choice(cite["usage"], {"fact", "quote", "style"}, cid + ".usage")
        if type(cite["historical"]) is not bool:
            raise ValueError(cid + ".historical: expected boolean")
        array(cite["chapter_ids"], cid + ".chapter_ids")
        if any(not isinstance(c, str) or c not in chapter_ids for c in cite["chapter_ids"]) or len(cite["chapter_ids"]) != len(set(cite["chapter_ids"])):
            raise ValueError(cid + ": unknown or duplicate chapter IDs")
    return sources, notes, cites


def body_citations(text):
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(\x60{3,}|~{3,})", line)
        if marker:
            char = marker.group(1)[0]
            fence = None if fence == char else char if fence is None else fence
            continue
        if fence is None:
            lines.append(line)
    text = re.sub(r"\x60[^\x60\n]*\x60", "", "\n".join(lines))
    return set(re.findall(r"\[\^(C-[A-Za-z0-9_-]+)\](?!:)", text))


def audit(refs, bid, plan, root):
    sources, notes, cites = validate(refs, bid, plan, root)
    chapters = {c["id"]: c for c in plan["chapters"]}
    issues = {cid: [] for cid in chapters}
    note_issues, global_issues = {}, []
    superseded = {n["supersedes"]: sid for sid, n in notes.items() if n["supersedes"]}
    for sid, n in notes.items():
        problems = []
        if not valid_file(root, sources[sid]["path"], sources[sid]["sha256"]):
            problems.append("原件缺失或哈希变化")
        if n["extract_path"] and not valid_file(root, n["extract_path"], n["extract_sha256"]):
            problems.append("提取/OCR副本缺失或变化")
        review = local_path(root, n["review_path"])
        if n["status"] != "reviewed" or not valid_file(root, n["review_path"], n["review_sha256"]):
            problems.append("接收后尚未完成当前版本核对")
        elif sources[sid]["sha256"] not in review.read_text(encoding="utf-8") or n["extract_sha256"] and n["extract_sha256"] not in review.read_text(encoding="utf-8"):
            problems.append("核对记录未绑定原件/提取副本版本")
        note_issues[sid] = problems
    actual_refs = {}
    for cid, chapter in chapters.items():
        path = local_path(root, chapter["path"])
        actual_refs[cid] = body_citations(path.read_text(encoding="utf-8")) if path and path.is_file() else set()
        for label in sorted(actual_refs[cid]):
            if label not in cites:
                issues[cid].append("未登记的引用: " + label)
            elif cid not in cites[label]["chapter_ids"]:
                issues[cid].append("引用未关联当前章节: " + label)
    by_chapter = {cid: [] for cid in chapters}
    for label, cite in cites.items():
        sid, problems = cite["source_id"], []
        if not cite["chapter_ids"]:
            global_issues.append(label + ": 未关联章节")
        if not cite["locator"].strip() or not cite["summary"].strip():
            problems.append("缺原页/段落/表格定位或引用用途")
        if sid not in notes:
            problems.append("缺来源题名、用途及核对记录")
        else:
            problems += note_issues[sid]
            if cite["usage"] in {"fact", "quote"} and notes[sid]["use"] == "style":
                problems.append("文风参考不作为事实或原文引证")
        if cite["usage"] != "style" and sid in superseded and not cite["historical"]:
            problems.append("来源已被新版本替代，需比较后修订而非自动换引")
        if cite["historical"] and not cite["note"].strip():
            problems.append("历史版本引用缺适用范围说明")
        for cid in cite["chapter_ids"]:
            if label not in actual_refs[cid]:
                issues[cid].append("已登记引用未出现在正文: " + label)
            issues[cid].extend(label + ": " + problem for problem in problems)
            by_chapter[cid].append(label)
    for chapter in chapters.values():
        for req in bid["requirements"]:
            if req["id"] in chapter["requirement_ids"] and req["source_id"] in superseded:
                issues[chapter["id"]].append(req["id"] + ": 条款依据已被新版本替代，请核对补遗影响")
    asset_sources = {cid: set() for cid in chapters}
    for asset in plan.get("assets", []):
        for cid in asset["chapter_ids"]:
            asset_sources[cid].update(asset["source_ids"])
            for sid in asset["source_ids"]:
                if sid in superseded:
                    issues[cid].append(asset["id"] + ": 素材来源已被新版本替代，请核对图文影响")
                if sid in note_issues:
                    issues[cid].extend(asset["id"] + ": " + problem for problem in note_issues[sid])
    pins = {}
    for cid, labels in by_chapter.items():
        used = sorted({cites[label]["source_id"] for label in labels} | asset_sources[cid])
        pins[cid] = {"citations": [cites[label] for label in labels],
                     "notes": {sid: {**notes[sid], "extract_actual": actual(root, notes[sid]["extract_path"]), "review_actual": actual(root, notes[sid]["review_path"])} for sid in used if sid in notes},
                     "source_ids": used}
    return dict(issues=issues, pins=pins, note_issues=note_issues, global_issues=global_issues,
                sources=sources, notes=notes, citations=cites)


def project(root):
    bid = load(local_path(root, "bid.json"))
    plan_path = local_path(root, "long-task.json")
    plan = load(plan_path) if plan_path.is_file() else {"chapters": []}
    if plan_path.is_file():
        from long_task import validate as validate_plan
        validate_plan(plan, bid, root)
    refs_path = local_path(root, "references.json")
    refs = load(refs_path) if refs_path.is_file() else empty()
    validate(refs, bid, plan, root)
    return bid, plan, refs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("ingest", "attach-extract", "verify", "check", "bibliography"))
    parser.add_argument("root", type=Path)
    parser.add_argument("--file", type=Path)
    parser.add_argument("--id")
    parser.add_argument("--kind", choices=sorted(SOURCE_KINDS), default="reference")
    parser.add_argument("--title", default="")
    parser.add_argument("--use", choices=("fact", "style", "mixed"), default="mixed")
    parser.add_argument("--version", default="received-v1")
    parser.add_argument("--origin", default="user_upload")
    parser.add_argument("--source-date", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--supersedes", default="")
    parser.add_argument("--review")
    parser.add_argument("--chapter")
    parser.add_argument("--mode", choices=("draft", "release"), default="draft")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if not root.is_dir():
            raise ValueError("project directory missing")
        bid, plan, refs = project(root)
        sources, notes, _ = validate(refs, bid, plan, root)
        if args.command == "ingest":
            sid = identifier(args.id, "source ID")
            if not args.file or not args.file.is_file():
                raise ValueError("ingest requires an existing uploaded --file")
            payload = args.file.read_bytes()
            sha = hashlib.sha256(payload).hexdigest()
            if sid in sources:
                n = notes.get(sid)
                if sources[sid]["sha256"] == sha and valid_file(root, sources[sid]["path"], sha) and n and (sources[sid]["kind"], n["use"], n["version"], n["supersedes"], n["title"], n["origin"], n["source_date"], n["url"]) == (args.kind, args.use, args.version, args.supersedes, args.title or args.file.name, args.origin, args.source_date, args.url):
                    print("UNCHANGED " + sid)
                    return 0
                raise ValueError("source ID exists; receive revised bytes with a new ID and --supersedes")
            suffix = args.file.suffix if re.fullmatch(r"\.[A-Za-z0-9]{1,12}", args.file.suffix) else ".bin"
            path = f"sources/originals/{sid}/original{suffix}"
            if local_path(root, path).exists():
                raise ValueError("original destination already exists")
            bid["sources"].append(dict(id=sid, kind=args.kind, path=path, sha256=sha))
            text_input = suffix.lower() in {".txt", ".md", ".csv", ".json"}
            if text_input:
                try:
                    payload.decode("utf-8")
                except UnicodeDecodeError:
                    text_input = False
            refs["source_notes"].append(dict(source_id=sid, title=args.title or args.file.name, origin=args.origin, original_name=args.file.name,
                version=args.version, source_date=args.source_date, url=args.url, use=args.use, supersedes=args.supersedes,
                extract_path=path if text_input else "", extract_sha256=sha if text_input else "",
                review_path="", review_sha256="", status="pending"))
            validate(refs, bid, plan, root)
            commit(root, {path: payload, "bid.json": json_bytes(bid), "references.json": json_bytes(refs)})
            if digest(local_path(root, path)) != sha:
                raise OSError("received original checksum mismatch")
            print(f"RECEIVED {sid} {path} SHA256={sha}; verification pending; original upload unchanged")
        elif args.command in {"attach-extract", "verify"}:
            if args.id not in notes:
                raise ValueError("unknown registered source ID")
            note = notes[args.id]
            source = sources[args.id]
            if not valid_file(root, source["path"], source["sha256"]):
                raise ValueError("original source changed; investigate before updating references")
            updates = {}
            if args.command == "attach-extract":
                if not args.file or not args.file.is_file():
                    raise ValueError("attach-extract requires the actual extraction/OCR --file")
                payload = args.file.read_bytes()
                payload.decode("utf-8")
                sha = hashlib.sha256(payload).hexdigest()
                path = f"sources/extracted/{args.id}/{sha}.txt"
                if local_path(root, path).exists() and digest(local_path(root, path)) != sha:
                    raise ValueError("existing extraction checksum mismatch")
                updates[path] = payload
                note.update(extract_path=path, extract_sha256=sha, review_path="", review_sha256="", status="pending")
            else:
                review = local_path(root, args.review or "")
                if review is None or not review.is_file() or review == local_path(root, source["path"]) or review == local_path(root, note["extract_path"]):
                    raise ValueError("verify requires a distinct actual --review record")
                text = review.read_text(encoding="utf-8")
                if source["sha256"] not in text or note["extract_sha256"] and note["extract_sha256"] not in text:
                    raise ValueError("review must bind current original and extraction hashes")
                if note["extract_path"] and not valid_file(root, note["extract_path"], note["extract_sha256"]):
                    raise ValueError("extraction changed since registration")
                note.update(review_path=args.review, review_sha256=digest(review), status="reviewed")
            updates["references.json"] = json_bytes(refs)
            validate(refs, bid, plan, root)
            commit(root, updates)
            print(args.command.upper() + " " + args.id + "; original preserved")
        else:
            state = audit(refs, bid, plan, root)
            if args.command == "bibliography":
                chapters = {c["id"]: c for c in plan["chapters"]}
                if args.chapter not in chapters:
                    raise ValueError("bibliography requires a valid --chapter")
                for label, cite in state["citations"].items():
                    if args.chapter in cite["chapter_ids"]:
                        n = notes.get(cite["source_id"], {})
                        s = sources[cite["source_id"]]
                        path = posixpath.relpath(s["path"], posixpath.dirname(chapters[args.chapter]["path"]) or ".")
                        print(f"[^{label}]: {n.get('title', cite['source_id'])}；版本 {n.get('version', '待补')}；{cite['locator']}；[原件](<{path}>)；SHA-256 {s['sha256']}。")
            else:
                problems = list(state["global_issues"])
                problems += [f"{cid}: {issue}" for cid, issues in state["issues"].items() for issue in issues]
                for issue in problems:
                    print(("ERROR " if args.mode == "release" else "WARN ") + issue)
                for sid, issues in state["note_issues"].items():
                    if issues:
                        print("SOURCE " + sid + ": " + "; ".join(issues))
                print(f"REFERENCES sources={len(notes)} citations={len(state['citations'])} issues={len(problems)}; locator and claim support still require actual review")
                return 1 if problems and args.mode == "release" else 0
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print("REFERENCE ERROR " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
