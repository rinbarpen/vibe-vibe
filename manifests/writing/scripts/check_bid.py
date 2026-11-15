#!/usr/bin/env python3
"""Read-only bid matrix readiness checks; not substantive or release approval."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys

ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")
SHA = re.compile(r"[0-9a-fA-F]{64}\Z")
CATEGORIES = {"qualification", "mandatory", "scored", "general", "submission"}
SOURCE_KINDS = {"tender", "clarification", "bidder", "reference"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def fields(value, expected, where):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{where}: expected exactly {', '.join(expected)}")


def string(value, where):
    if not isinstance(value, str):
        raise ValueError(f"{where}: expected string")
    return value


def identifier(value, where):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError(f"{where}: expected letter-led ASCII ID")
    return value


def array(value, where):
    if not isinstance(value, list):
        raise ValueError(f"{where}: expected array")


def choice(value, allowed, where):
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{where}: expected one of {', '.join(sorted(allowed))}")


def local_path(root, value):
    string(value, "path")
    if not value.strip():
        return None
    relative = PurePosixPath(value)
    if ("\\" in value or ":" in value or relative.is_absolute()
            or PureWindowsPath(value).drive or not relative.parts
            or ".." in relative.parts or "\x00" in value):
        raise ValueError(f"invalid project-relative path: {value!r}")
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"symlink in project path: {value}")
    return path


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def validate_schema(data, root):
    fields(data, ("schema_version", "project", "sources", "requirements"), "root")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("schema_version: expected integer 1")
    project = data["project"]
    fields(project, ("name", "lot", "tender_revision", "deadline"), "project")
    for key, value in project.items():
        string(value, "project." + key)
    if project["deadline"].strip():
        deadline = datetime.fromisoformat(project["deadline"].replace("Z", "+00:00"))
        if deadline.utcoffset() is None:
            raise ValueError("project.deadline: timezone is required")
    array(data["sources"], "sources")
    array(data["requirements"], "requirements")
    sources, req_ids = {}, set()
    for source in data["sources"]:
        fields(source, ("id", "kind", "path", "sha256"), "source")
        sid = identifier(source["id"], "source.id")
        if sid in sources:
            raise ValueError("duplicate source ID: " + sid)
        choice(source["kind"], SOURCE_KINDS, sid + ".kind")
        local_path(root, source["path"])
        sha = string(source["sha256"], sid + ".sha256")
        if sha and not SHA.fullmatch(sha):
            raise ValueError(sid + ".sha256: expected empty or 64 hex characters")
        sources[sid] = source
    for req in data["requirements"]:
        fields(req, ("id", "source_id", "locator", "text", "category", "status",
                     "response_path", "requires_evidence", "evidence", "note"), "requirement")
        rid = identifier(req["id"], "requirement.id")
        if rid in req_ids:
            raise ValueError("duplicate requirement ID: " + rid)
        req_ids.add(rid)
        for key in ("source_id", "locator", "text", "note"):
            string(req[key], rid + "." + key)
        sid = req["source_id"]
        if sid not in sources:
            raise ValueError(f"{rid}: unknown source {sid!r}")
        if sources[sid]["kind"] not in {"tender", "clarification"}:
            raise ValueError(rid + ": requirement basis must be tender or clarification")
        choice(req["category"], CATEGORIES, rid + ".category")
        choice(req["status"], {"pending", "gap", "covered"}, rid + ".status")
        local_path(root, req["response_path"])
        if type(req["requires_evidence"]) is not bool:
            raise ValueError(rid + ".requires_evidence: expected boolean")
        array(req["evidence"], rid + ".evidence")
        for evidence in req["evidence"]:
            fields(evidence, ("source_id", "locator"), rid + ".evidence[]")
            string(evidence["source_id"], rid + ".evidence.source_id")
            string(evidence["locator"], rid + ".evidence.locator")
            if evidence["source_id"] not in sources:
                raise ValueError(rid + ": unknown evidence source " + evidence["source_id"])
    return sources


def check(data, root, mode):
    sources = validate_schema(data, root)
    problems = []

    def pending(message):
        problems.append(("ERROR" if mode == "release" else "WARN", message))

    for field, value in data["project"].items():
        if not value.strip():
            pending("missing project." + field)
    if not any(source["kind"] == "tender" for source in sources.values()):
        pending("at least one tender source is required")
    if not data["requirements"]:
        pending("requirements matrix is empty")
    for sid, source in sources.items():
        path = local_path(root, source["path"])
        if path is None or not path.is_file():
            pending(sid + ": source file missing")
        if not source["sha256"]:
            pending(sid + ": source SHA-256 missing")
        elif path is not None and path.is_file() and digest(path) != source["sha256"].lower():
            problems.append(("ERROR", sid + ": source SHA-256 mismatch"))
    for req in data["requirements"]:
        rid = req["id"]
        for key in ("locator", "text"):
            if not req[key].strip():
                pending(f"{rid}: {key} missing")
        if req["status"] != "covered":
            pending(f"{rid}: status={req['status']}")
        response = local_path(root, req["response_path"])
        if response is None or not response.is_file():
            pending(rid + ": response file missing")
        elif f"<!-- REQ:{rid} -->" not in response.read_text(encoding="utf-8"):
            pending(rid + ": response marker missing")
        if req["requires_evidence"] and not req["evidence"]:
            pending(rid + ": supporting evidence missing")
        for evidence in req["evidence"]:
            if not evidence["locator"].strip():
                pending(rid + ": evidence locator missing")
            if sources[evidence["source_id"]]["kind"] == "reference":
                pending(rid + ": style/reference material is not supporting evidence")
    for level, message in problems:
        print(f"{level} {message}")
    errors = sum(level == "ERROR" for level, _ in problems)
    warnings = sum(level == "WARN" for level, _ in problems)
    covered = sum(req["status"] == "covered" for req in data["requirements"])
    print(f"MATRIX mode={mode} sources={len(sources)} requirements={len(data['requirements'])} "
          f"covered={covered} errors={errors} warnings={warnings}")
    print("Readiness only: content review, rendered QA and genuine release decisions remain separate.")
    return 1 if errors else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--mode", choices=("draft", "release"), default="draft")
    args = parser.parse_args(argv)
    try:
        if args.matrix.is_symlink():
            raise ValueError("matrix file must not be a symlink")
        root = args.matrix.resolve().parent
        data = json.loads(args.matrix.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        return check(data, root, args.mode)
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print("INPUT ERROR " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
