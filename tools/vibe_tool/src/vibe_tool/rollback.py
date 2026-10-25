"""Self-contained backup verification and restoration (also shipped as restore.py)."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import sys
from pathlib import Path


def fingerprint(path: Path) -> dict:
    """Describe content, permissions and links without following links."""
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return {"kind": "missing"}
    permissions = stat.S_IMODE(mode)
    if stat.S_ISLNK(mode):
        return {"kind": "symlink", "target": os.readlink(path)}
    if stat.S_ISREG(mode):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return {"kind": "file", "mode": permissions, "sha256": digest.hexdigest()}
    if stat.S_ISDIR(mode):
        entries = {p.name: fingerprint(p) for p in sorted(path.iterdir())}
        payload = json.dumps(entries, sort_keys=True, ensure_ascii=True).encode()
        return {"kind": "directory", "mode": permissions,
                "sha256": hashlib.sha256(payload).hexdigest()}
    raise ValueError(f"Unsupported filesystem object: {path}")


def checked_path(target: Path, relative: str | Path) -> Path:
    """Validate a lexical project path and reject symlink ancestors."""
    relative = Path(relative)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError(f"Invalid project-relative path: {relative}")
    dest = target / relative
    for part in relative.parts[:-1]:
        target = target / part
        if target.is_symlink():
            raise ValueError(f"Symlink ancestor in update path: {target}")
        if target.exists() and not target.is_dir():
            raise ValueError(f"Expected directory in update path: {target}")
    return dest


def copy_path(source: Path, dest: Path) -> None:
    """Copy one node without dereferencing symbolic links."""
    if source.is_symlink():
        dest.symlink_to(os.readlink(source))
    elif source.is_dir():
        shutil.copytree(source, dest, symlinks=True)
    else:
        shutil.copy2(source, dest)


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def restore_backup(backup: Path, *, paths: set[str] | None = None) -> None:
    """Verify every selected backup before restoring any project content."""
    backup = backup.resolve()
    record = json.loads((backup / "changes.json").read_text(encoding="utf-8"))
    if record.get("schema_version") != 1:
        raise ValueError("Unsupported backup schema")
    target = Path(record["target"])
    if (not target.is_absolute() or not target.is_dir() or target.is_symlink()
            or target.resolve() != target):
        raise ValueError(f"Original target directory is missing or moved: {target}")
    entries = [e for e in record["changes"] if paths is None or e["path"] in paths]
    for relative in record.get("created_directories", []):
        checked_path(target, relative)
    for entry in entries:
        checked_path(target, entry["path"])
        saved = checked_path(backup / "before", entry["path"])
        if fingerprint(saved) != entry["before"]:
            raise ValueError(f"Backup checksum mismatch: {entry['path']}")
    for entry in reversed(entries):
        dest = checked_path(target, entry["path"])
        saved = backup / "before" / entry["path"]
        remove_path(dest)
        if entry["before"]["kind"] != "missing":
            dest.parent.mkdir(parents=True, exist_ok=True)
            copy_path(saved, dest)
        if fingerprint(dest) != entry["before"]:
            raise OSError(f"Restoration verification failed: {entry['path']}")
    # Only remove directories created by the update, never existing project dirs.
    for relative in sorted(record.get("created_directories", []),
                           key=lambda p: len(Path(p).parts), reverse=True):
        directory = checked_path(target, relative)
        try:
            directory.rmdir()
        except (FileNotFoundError, OSError):
            pass


def main() -> int:
    try:
        restore_backup(Path(__file__).resolve().parent)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Restore failed: {exc}", file=sys.stderr)
        return 1
    print("Restored original project content and installation records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
