"""Prepared local updates with verified backups and independent rollback."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .rollback import checked_path, copy_path, fingerprint, remove_path, restore_backup


@dataclass(frozen=True)
class Change:
    path: Path
    source: Path


def ensure_separate(source: Path, dest: Path, *, preserve_links: bool = False) -> None:
    """Reject updates that would replace their own source."""
    def location(path: Path) -> Path:
        if preserve_links and path.is_symlink():
            return path.parent.resolve() / path.name
        return path.resolve()
    source, dest = location(source), location(dest)
    if source == dest or source in dest.parents or dest in source.parents:
        raise ValueError(f"Source and destination overlap: {source} / {dest}")


def _replace(source: Path, dest: Path) -> None:
    """Prepare a sibling copy before replacing the old leaf or directory."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.parent / f".vibe-update-{uuid.uuid4().hex}"
    try:
        copy_path(source, temp)
        # Files and links can be atomically replaced without unlinking the old
        # node first. Directory replacements are protected by the full backup.
        if ((temp.is_dir() and not temp.is_symlink())
                or (dest.is_dir() and not dest.is_symlink())):
            remove_path(dest)
        os.replace(temp, dest)
    finally:
        remove_path(temp)


def _prepare(target: Path, changes: list[Change]) -> list[dict]:
    prepared = []
    selected: list[Path] = []
    for change in changes:
        rel = Path(change.path)
        dest = checked_path(target, rel)
        if rel.parts[0] == ".git" or (
            rel.parts[0] == ".vibe-tool" and rel != Path(".vibe-tool/installations.json")
        ):
            raise ValueError(f"Reserved update path: {rel}")
        if any(rel == p or rel in p.parents or p in rel.parents for p in selected):
            raise ValueError(f"Overlapping update paths: {rel}")
        selected.append(rel)
        # Leaf links are copied/replaced as nodes, never written through. Two
        # links to the same external resource do not overlap each other's node.
        ensure_separate(change.source, dest, preserve_links=True)
        before, after = fingerprint(dest), fingerprint(change.source)
        if after["kind"] == "missing":
            raise ValueError(f"Prepared source is missing: {change.source}")
        if (before["kind"] == "directory" and after["kind"] != "directory") or (
            after["kind"] == "directory" and before["kind"] not in ("missing", "symlink", "directory")
        ):
            raise ValueError(f"File/directory type conflict: {rel}")
        if before == after:
            print(f"  SKIP  {rel} (unchanged)")
            continue
        prepared.append({"path": rel.as_posix(), "before": before,
                         "after": after, "source": str(change.source)})
    return prepared


def _create_backup(target: Path, entries: list[dict], label: str) -> Path:
    # Validate even the backup infrastructure before creating any directory.
    checked_path(target, ".vibe-tool/backups/placeholder")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = target / ".vibe-tool" / "backups" / f"{stamp}-{uuid.uuid4().hex[:8]}"
    created = set()
    for entry in entries:
        parent = (target / entry["path"]).parent
        while parent != target:
            if not parent.exists():
                created.add(parent.relative_to(target).as_posix())
            parent = parent.parent
    backup.mkdir(parents=True)
    try:
        for entry in entries:
            source = target / entry["path"]
            dest = backup / "before" / entry["path"]
            if entry["before"]["kind"] != "missing":
                dest.parent.mkdir(parents=True, exist_ok=True)
                copy_path(source, dest)
            if fingerprint(dest) != entry["before"]:
                raise OSError(f"Backup verification failed: {entry['path']}")
        record = {"schema_version": 1, "target": str(target), "label": label,
                  "created_directories": sorted(created), "changes": entries}
        (backup / "changes.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        shutil.copy2(Path(__file__).with_name("rollback.py"), backup / "restore.py")
        # Reopen both roles before any application is attempted.
        json.loads((backup / "changes.json").read_text(encoding="utf-8"))
        compile((backup / "restore.py").read_text(encoding="utf-8"), "restore.py", "exec")
        return backup
    except BaseException:
        shutil.rmtree(backup, ignore_errors=True)
        raise


def apply_update(target: Path, changes: list[Change], *, label: str,
                 dry_run: bool = False) -> int:
    """Apply prepared nodes; return 0 on success and 1 on validation/I/O failure."""
    backup = None
    touched: set[str] = set()
    try:
        target = target.resolve()
        if not target.is_dir():
            raise ValueError(f"Target directory does not exist: {target}")
        entries = _prepare(target, changes)
        if not entries:
            print("Already up to date; no backup or project changes.")
            return 0
        for entry in entries:
            action = "ADD" if entry["before"]["kind"] == "missing" else "UPDATE"
            print(f"  {'WILL ' if dry_run else ''}{action}  {entry['path']}")
        if dry_run:
            print("Dry run; project content, installation records and backups unchanged.")
            return 0
        backup = _create_backup(target, entries, label)
        for entry in entries:
            dest = checked_path(target, entry["path"])
            source = Path(entry["source"])
            if fingerprint(dest) != entry["before"] or fingerprint(source) != entry["after"]:
                raise OSError(f"Content changed during update: {entry['path']}")
            touched.add(entry["path"])
            _replace(source, dest)
            if fingerprint(dest) != entry["after"]:
                raise OSError(f"Update verification failed: {entry['path']}")
        print(f"Updated {label}: {len(entries)} changed paths.")
        print(f"Backup: {backup}")
        print(f"Restore: {shlex.join([sys.executable, str(backup / 'restore.py')])}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        if backup is not None:
            try:
                restore_backup(backup, paths=touched)
                print("Rolled back all applied paths.", file=sys.stderr)
            except (OSError, ValueError) as restore_exc:
                print(f"Automatic restore failed: {restore_exc}", file=sys.stderr)
            print(f"Restore: {shlex.join([sys.executable, str(backup / 'restore.py')])}",
                  file=sys.stderr)
        return 1
