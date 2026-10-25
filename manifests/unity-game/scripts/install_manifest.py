#!/usr/bin/env python3
"""Install the Unity workflow without modifying Unity assets or project settings.

No third-party dependencies. A ledger limits --force to this scaffold's own files;
state and deliverables are never force-overwritten. The vibe CLI installs skills
separately after this installer succeeds.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid


SOURCE = Path(__file__).resolve().parents[1]
LEDGER = Path(".unity-game/install.json")
JOURNAL = Path(".unity-game/install-transaction.json")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def checked_destination(target: Path, relative: Path) -> Path:
    """Reject symlinked files/parents instead of following them during install."""
    current = target
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink destination: {relative}")
        if current != target / relative and current.exists() and not current.is_dir():
            raise ValueError(f"parent is not a directory: {relative}")
    return target / relative


def validated_files(value: object, label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError(f"invalid {label} files")
    for key, sha in value.items():
        if (not isinstance(key, str) or not key or not Path(key).parts or Path(key).is_absolute()
                or ".." in Path(key).parts or Path(key).as_posix() != key
                or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha)):
            raise ValueError(f"invalid {label} path or hash: {key!r}")
    return dict(value)


def ledger_bytes(files: dict[str, str]) -> bytes:
    return (json.dumps({"manifest": "unity-game", "schema_version": 1, "files": files},
                       ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def recover_transaction(target: Path, ledger: dict[str, str],
                        sources: dict[str, bool]) -> tuple[dict[str, str], set[str], bool]:
    """Inspect an interrupted transaction without writing or claiming changed files.

    Journal hashes describe intended writes, not proof they happened. Ownership is
    recovered only when the destination still has the intended bytes. Existing
    ownership survives other changes, but force refresh skips those conflicts on
    this recovery invocation; newly created/edited files remain unowned.
    """
    path = checked_destination(target, JOURNAL)
    if not path.exists():
        return dict(ledger), set(), False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(data, dict) or data.get("manifest") != "unity-game"
                or type(data.get("schema_version")) is not int
                or data.get("schema_version") != 1 or not isinstance(data.get("writes"), dict)):
            raise ValueError("invalid transaction format")
        base = validated_files(data.get("base_files"), "transaction")
        writes = data["writes"]
        for key, item in writes.items():
            if key not in sources:
                raise ValueError(f"transaction path {key!r} is absent from this scaffold version; "
                                 "rerun recovery with the original manifest sources, then upgrade; "
                                 "preserve the journal for inspection")
            if (not isinstance(item, dict)
                    or type(item.get("protected")) is not bool
                    or item["protected"] != sources[key]
                    or not isinstance(item.get("sha256"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])
                    or (item.get("previous_sha256") is not None
                        and (not isinstance(item["previous_sha256"], str)
                             or not re.fullmatch(r"[0-9a-f]{64}", item["previous_sha256"])))):
                raise ValueError(f"invalid transaction write: {key!r}")
            dest = checked_destination(target, Path(key))
            if dest.exists() and not dest.is_file():
                raise ValueError(f"transaction destination is not a file: {key}")
        # A previous recovery may have committed some/all proven writes before
        # interruption while removing the journal. Reject unrelated ledger drift.
        if any(key not in ledger for key in base):
            raise ValueError("transaction and ledger diverged")
        for key, sha in ledger.items():
            item = writes.get(key)
            if sha != base.get(key) and not (item and not item["protected"] and sha == item["sha256"]):
                raise ValueError("transaction and ledger diverged")
    except (OSError, ValueError, TypeError) as exc:
        raise ValueError(f"invalid installation transaction: {exc}") from exc
    recovered = dict(ledger)
    conflicts: set[str] = set()
    for key, item in writes.items():
        if item["protected"]:
            continue
        dest = target / key
        actual = digest(dest.read_bytes()) if dest.is_file() else None
        if actual == item["sha256"]:
            recovered[key] = actual
            print(f"  RECOVER  {key} (verified written bytes)")
        elif actual != item.get("previous_sha256"):
            # The old ledger hash is evidence of historical ownership only; do
            # not attach the journal's intended hash to subsequently edited data.
            conflicts.add(key)
            print(f"  KEEP  {key} (changed after interrupted install; integrate manually)")
    return recovered, conflicts, True


def source_files() -> list[tuple[Path, Path, bool]]:
    """(source, destination relative to project, protected seed)."""
    files = [(SOURCE / name, Path(name), False) for name in ("CLAUDE.md", "AGENTS.md")]
    files.append((SOURCE / "README.md", Path(".unity-game/README.md"), False))
    files.append((SOURCE / "agents/subagent-roles.md", Path(".unity-game/agents/subagent-roles.md"), False))
    for directory in (".claude/agents", ".codex/agents", "references", "templates", "scripts"):
        folder = SOURCE / directory
        if not folder.is_dir():
            raise ValueError(f"missing scaffold directory: {folder}")
        for src in sorted(folder.rglob("*")):
            if not src.is_file() or "__pycache__" in src.parts or src.suffix == ".pyc":
                continue
            if directory == "scripts" and src.name in {"init-unity-game.sh", "install_manifest.py"}:
                continue
            if src.is_symlink():
                raise ValueError(f"symlink source: {src}")
            relative = src.relative_to(SOURCE)
            dest = relative if directory.startswith(".") else Path(".unity-game") / relative
            files.append((src, dest, False))
    for name in ("status", "tasks", "decisions", "artifacts"):
        files.append((SOURCE / f"templates/state/{name}.md", Path(f".unity-game/state/{name}.md"), True))
    for src, _, _ in files:
        if not src.is_file():
            raise ValueError(f"missing scaffold file: {src}")
    return files


def install(target: Path, force: bool, dry_run: bool) -> int:
    # Resolve the target itself, but never follow links within the project.
    target = target.expanduser().resolve()
    if target.exists() and not target.is_dir():
        raise ValueError(f"target is not a directory: {target}")
    if target == SOURCE or SOURCE.is_relative_to(target) or target.is_relative_to(SOURCE):
        raise ValueError("target must be separate from the manifest source")

    ledger_path = checked_destination(target, LEDGER)
    previous: dict = {"manifest": "unity-game", "schema_version": 1, "files": {}}
    if ledger_path.exists():
        try:
            previous = json.loads(ledger_path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise ValueError(f"invalid installation ledger: {exc}") from exc
        if (not isinstance(previous, dict) or previous.get("manifest") != "unity-game"
                or type(previous.get("schema_version")) is not int
                or previous.get("schema_version") != 1
                or not isinstance(previous.get("files"), dict)):
            raise ValueError("invalid installation ledger format")
    previous_files = validated_files(previous["files"], "installation ledger")
    sources = source_files()
    owned, recovery_conflicts, recovering = recover_transaction(
        target, previous_files, {relative.as_posix(): protected for _, relative, protected in sources})
    recovered_files = dict(owned)
    actions: list[tuple[Path, Path, bytes, int, bool]] = []
    # Validate the entire plan before any write, including output directory paths.
    # The public CLI installs required skills after this script succeeds; include
    # those destinations in preflight even though this script never writes them.
    skills_file = SOURCE / "skills.txt"
    if skills_file.is_file():
        for line in skills_file.read_text(encoding="utf-8").splitlines():
            name = line.split("#", 1)[0].strip()
            if not name:
                continue
            if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
                raise ValueError(f"invalid required skill name: {name}")
            dest = checked_destination(target, Path(".agents/skills") / name)
            if dest.exists() and not dest.is_dir():
                raise ValueError(f"expected skill directory: {name}")
    for relative in (LEDGER, JOURNAL, Path(".unity-game/deliverables"), Path(".unity-game/runs")):
        destination = checked_destination(target, relative)
        if relative not in (LEDGER, JOURNAL) and destination.exists() and not destination.is_dir():
            raise ValueError(f"expected directory: {relative}")
    backup_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    backup_root = Path(".unity-game/backups") / backup_id
    checked_destination(target, backup_root)
    for src, relative, protected in sources:
        dest = checked_destination(target, relative)
        key = relative.as_posix()
        if dest.exists() and not dest.is_file():
            raise ValueError(f"expected file: {relative}")
        data = src.read_bytes()
        if key in recovery_conflicts:
            continue
        if dest.exists():
            if protected:
                print(f"  KEEP  {key} (project state)")
                continue
            if key not in owned:
                print(f"  KEEP  {key} (pre-existing; integrate manually)")
                continue
            if not force:
                print(f"  SKIP  {key} (managed; use --force to refresh)")
                continue
            if dest.read_bytes() == data:
                print(f"  SAME  {key}")
                continue
        replacing = dest.exists()
        if replacing:
            checked_destination(target, backup_root / relative)
        actions.append((dest, relative, data, src.stat().st_mode & 0o777, replacing))
        if not protected:
            owned[key] = digest(data)
        print(f"  {'SEED' if protected else 'COPY'}  {key}" + (" (backup before refresh)" if replacing else ""))

    label = "[dry-run]" if dry_run else "[unity-game]"
    print(f"{label} {len(actions)} file operations for {target}")
    if dry_run:
        return 1 if recovery_conflicts else 0
    journal_path = target / JOURNAL
    if recovering:
        # Commit only evidence-backed recovery before replacing the old journal.
        # If either write/unlink fails, the original journal is still recoverable.
        recovered_data = ledger_bytes(recovered_files)
        if not ledger_path.exists() or ledger_path.read_bytes() != recovered_data:
            atomic_write(ledger_path, recovered_data)
        journal_path.unlink()
        previous_files = recovered_files
    if actions:
        writes = {}
        source_protection = {relative.as_posix(): protected for _, relative, protected in sources}
        for dest, relative, data, _, _ in actions:
            writes[relative.as_posix()] = {
                "sha256": digest(data), "protected": source_protection[relative.as_posix()],
                "previous_sha256": digest(dest.read_bytes()) if dest.is_file() else None,
            }
        transaction = {"manifest": "unity-game", "schema_version": 1,
                       "base_files": previous_files, "writes": writes}
        atomic_write(journal_path, (json.dumps(transaction, indent=2, sort_keys=True) + "\n").encode())
        for dest, relative, data, mode, replacing in actions:
            if replacing:
                backup = checked_destination(target, backup_root / relative)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, backup)
            atomic_write(dest, data, mode)
    (target / ".unity-game/deliverables").mkdir(parents=True, exist_ok=True)
    (target / ".unity-game/runs").mkdir(parents=True, exist_ok=True)
    data = ledger_bytes(owned)
    if not ledger_path.exists() or ledger_path.read_bytes() != data:
        atomic_write(ledger_path, data)
    if journal_path.exists():
        journal_path.unlink()
    if recovery_conflicts:
        print("Recovery preserved post-interruption edits; review KEEP files before retrying.", file=sys.stderr)
        return 1
    print("Next: read .unity-game/README.md; confirm the project brief before Unity project setup.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("-f", "--force", action="store_true", help="Refresh only ledger-owned scaffold files; back up replacements")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Preview without creating files or directories")
    args = parser.parse_args()
    try:
        return install(Path(args.target), args.force, args.dry_run)
    except (OSError, ValueError) as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
