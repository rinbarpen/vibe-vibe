#!/usr/bin/env python3
"""Offline, per-file Tutor installer and reversible legacy-project upgrade.

The shell entrypoint delegates here. Backup restore.py is a copy of this file;
its only inputs are the adjacent manifest.json and files/, not the source repo.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import sys
import tempfile


SCENARIOS = ("self-study", "exam-prep", "course-learning", "research-reading")
BASE_RULES = ("core", "material-processing", "note-organization", "progress",
              "qa", "review-discipline")
ROOT_FILES = ("CLAUDE.md", "AGENTS.md", "README.md", ".cursorrules")
PROJECT_DIRS = [f"materials/{kind}" for kind in
                ("slides", "pdf", "video", "web", "audio", "images", "exercises", "epub")]
PROJECT_DIRS += ["notes/atoms", "notes/summaries", "flashcards/decks", "flashcards/reviews",
                 "projects", ".cursor/rules", ".cursor/commands", ".cursor/templates",
                 "skills", "references", "agents", "scripts"]
INDEX = """# Knowledge Index

Import/indexing counts do not measure learning or mastery.
Material maps, optional learning paths and personal records belong in
projects/<教材或主题>/: MATERIAL_INDEX.md, LEARNING_PATH.md, LEARNING_RECORD.md.
Topic-only tutoring does not require a material map.

| Project | Material Map (if any) | Learning Path (if any) | Learning Record |
|---------|-----------------------|------------------------|-----------------|
"""


def exists(path):
    return path.exists() or path.is_symlink()


def bounded(root, relative, directory=False):
    """Validate all parents; a file leaf link may be atomically replaced."""
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"Invalid project path: {relative}")
    path = root / rel
    (path if directory else path.parent).resolve().relative_to(root)
    if directory and exists(path) and not path.is_dir():
        raise ValueError(f"Destination directory conflicts with a file: {path}")
    if not directory and path.is_dir() and not path.is_symlink():
        raise ValueError(f"Destination file conflicts with a directory: {path}")
    return path


def atomic_copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".vibe-install-", dir=destination.parent)
    os.close(fd)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def atomic_json(destination, data):
    fd, temporary = tempfile.mkstemp(prefix=".vibe-state-", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, destination)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def signature(path):
    if path.is_symlink():
        return {"kind": "symlink", "target": os.readlink(path)}
    if not path.exists():
        return {"kind": "absent"}
    return {"kind": "file", "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "mode": stat.S_IMODE(path.stat().st_mode), "mtime_ns": path.stat().st_mtime_ns}


def legacy_paths():
    return [f".cursor/rules/knowledge-learning-{name}.mdc" for name in (*BASE_RULES, *SCENARIOS)] + [
        "agents/knowledge-agents.md"]


def is_legacy(root):
    if any(exists(root / path) for path in legacy_paths()):
        return True
    for name in ("AGENTS.md", "CLAUDE.md", "skills/SKILL.md"):
        path = root / name
        if path.is_file() and not path.is_symlink():
            text = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"(?im)^(?:name:\s*knowledge-learning\s*$|#\s+(?:Agent Instructions for )?Knowledge-Learning\b)", text):
                return True
    return False


def choose_scenario(root, explicit, force=False):
    found = {name for name in SCENARIOS if any(
        exists(root / f".cursor/rules/{prefix}-{name}.mdc")
        for prefix in ("knowledge-learning", "tutor"))}
    path = root / ".cursor/scenario.md"
    if path.is_file() and not path.is_symlink():
        heading = path.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
        heading = heading[0] if heading else ""
        for name, titles in {
            "self-study": ("Self-Study Scenario", "自主学习场景"),
            "course-learning": ("Course Learning Scenario", "课程学习场景"),
            "exam-prep": ("Exam Preparation Scenario", "备考场景"),
            "research-reading": ("Research Reading Scenario", "研究阅读场景"),
        }.items():
            if any(title in heading for title in titles):
                found.add(name)
    if explicit:
        if found - {explicit} and not force:
            raise ValueError("Changing an installed scenario requires --force; project preserved")
        return explicit
    if len(found) > 1:
        raise ValueError("Conflicting installed scenarios; specify --scenario explicitly: "
                         + ", ".join(sorted(found)))
    return next(iter(found), None)


def restore(backup, force=False, check=True):
    data = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    root = Path(data["root"]).resolve()
    # Preflight the entire restore before writing anything.
    for rel, entry in data["files"].items():
        path = bounded(root, rel)
        if check and not force:
            if "after" not in entry:
                raise ValueError("Interrupted upgrade: inspect backup, then restore with --force")
            if signature(path) not in (entry["after"], entry["before"]):
                raise ValueError(f"Changed since upgrade, preserved: {path}; use --force to restore")
        if entry["before"]["kind"] == "file":
            saved = bounded(backup, "files/" + rel)
            if saved.is_symlink() or signature(saved) != entry["before"]:
                raise ValueError(f"Backup checksum mismatch: {rel}")
    for rel, entry in data["files"].items():
        path = bounded(root, rel)
        before = entry["before"]
        if signature(path) == before:
            continue
        if before["kind"] == "absent":
            if exists(path):
                path.unlink()
        elif before["kind"] == "symlink":
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix=".vibe-link-", dir=path.parent)
            os.close(fd)
            os.unlink(temporary)
            try:
                os.symlink(before["target"], temporary)
                os.replace(temporary, path)
            finally:
                if os.path.lexists(temporary):
                    os.unlink(temporary)
        else:
            atomic_copy(backup / "files" / rel, path)
    for rel in sorted(data["created_dirs"], key=lambda name: len(Path(name).parts), reverse=True):
        path = bounded(root, rel, directory=True)
        if path.is_dir() and not path.is_symlink():
            try:
                path.rmdir()  # Never delete content added since installation.
            except OSError:
                pass
    print(f"Restored project: {root}")


def install(target, scenario, force):
    root = target.expanduser().resolve()
    source = Path(__file__).resolve().parent.parent
    legacy = is_legacy(root)
    if legacy and not force:
        raise ValueError("Legacy knowledge-learning project preserved. Upgrade with: "
                         f"vibe add manifest tutor {shlex.quote(str(root))} --force")
    scenario = choose_scenario(root, scenario, force)
    copies = {name: source / name for name in ROOT_FILES}
    for src, dst in (("rules", ".cursor/rules"), ("commands", ".cursor/commands"),
                     ("templates", ".cursor/templates"), ("skills", "skills"),
                     ("references", "references"), ("agents", "agents")):
        for path in sorted((source / src).rglob("*")):
            if path.is_file():
                copies[str(Path(dst) / path.relative_to(source / src))] = path
    copies["scripts/export-notes.py"] = source / "scripts/export-notes.py"
    if scenario:
        folder = source / "scenarios" / scenario
        copies[".cursor/scenario.md"] = folder / "CLAUDE.md"
        for path in (folder / "rules").glob("*.mdc"):
            copies[".cursor/rules/" + path.name] = path
    removals = [rel for rel in legacy_paths() if legacy and exists(root / rel)]
    if force and scenario:
        removals += [f".cursor/rules/tutor-{name}.mdc" for name in SCENARIOS
                     if name != scenario and exists(root / f".cursor/rules/tutor-{name}.mdc")]
    writes = {rel: src for rel, src in copies.items() if force or not exists(root / rel)}
    # Generated data is initialized only once, including on --force.
    generated = {"notes/_index.md": INDEX.encode("utf-8")}
    generated.update({rel + "/.gitkeep": b"" for rel in PROJECT_DIRS
                      if rel.startswith(("materials/", "flashcards/"))})
    generated = {rel: content for rel, content in generated.items() if not exists(root / rel)}
    touched = sorted(set(writes) | set(generated) | set(removals))
    directories = set(PROJECT_DIRS)
    for rel in [*copies, *generated]:
        directories.update(str(p) for p in Path(rel).parents if str(p) != ".")
    for rel in directories:
        bounded(root, rel, directory=True)
    for rel in [*copies, *removals, *generated]:
        bounded(root, rel)
    # Validate backup parents before even creating project folders.
    backup_parent = bounded(root, ".vibe-tool/backups/tutor", directory=True)
    before = {rel: {"before": signature(root / rel)} for rel in touched}
    created_dirs = sorted(rel for rel in directories if not exists(root / rel))
    backup = None
    if legacy or (force and any(e["before"]["kind"] != "absent" for e in before.values())):
        backup_parent.mkdir(parents=True, exist_ok=True)
        backup = Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-"),
                                      dir=backup_parent))
        for rel, entry in before.items():
            if entry["before"]["kind"] == "file":
                atomic_copy(root / rel, backup / "files" / rel)
        data = {"root": str(root), "files": before, "created_dirs": created_dirs}
        atomic_json(backup / "manifest.json", data)
        atomic_copy(Path(__file__), backup / "restore.py")
        print("Backup: " + str(backup))
    try:
        root.mkdir(parents=True, exist_ok=True)
        for rel in sorted(directories):
            (root / rel).mkdir(parents=True, exist_ok=True)
        for rel, src in writes.items():
            atomic_copy(src, bounded(root, rel))
        for rel, content in generated.items():
            path = bounded(root, rel)
            # No pre-existing path is opened or truncated here.
            with path.open("xb") as stream:
                stream.write(content)
        # Retire old instructions only after every new template was installed.
        for rel in removals:
            bounded(root, rel).unlink()
        if backup:
            for rel, entry in before.items():
                entry["after"] = signature(root / rel)
            atomic_json(backup / "manifest.json", data)
    except Exception:
        if backup:
            restore(backup, force=True, check=False)
        raise
    print(f"Tutor initialized: {root}" + (f" (scenario: {scenario})" if scenario else ""))
    if backup:
        print("Restore: " + shlex.join([sys.executable, "-B", str(backup / "restore.py")]))
    print('Start naturally: “我想学……” / “解释这道题” / 上传教材并说出你的需求。')
    print("Optional: /learn --plan · /study --next · /review · /exam · /track")
    print("Built-in skills: skills/ (see skills/SKILL.md)")
    print("Settings: STRICT_SOURCE_MODE=true; NOTEBOOKLM_ENGINE=false (environment only)")


def main():
    parser = argparse.ArgumentParser(description="Initialize Tutor; preserve existing files unless --force.")
    if Path(__file__).name == "restore.py":
        parser.add_argument("--force", action="store_true", help="Restore even modified template paths")
        args = parser.parse_args()
        restore(Path(__file__).resolve().parent, args.force)
    else:
        parser.add_argument("target", nargs="?", default=".")
        parser.add_argument("--scenario", choices=SCENARIOS)
        parser.add_argument("--force", "-f", action="store_true")
        args = parser.parse_args()
        if not args.target:
            parser.error("Target directory must not be empty")
        install(Path(args.target), args.scenario, args.force)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
