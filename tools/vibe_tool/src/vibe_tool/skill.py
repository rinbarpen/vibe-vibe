"""Skill addition/installation logic."""

import shutil
import sys
from pathlib import Path

from .discovery import discover_skills, resolve_skill

EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def _is_excluded(path: Path) -> bool:
    name = path.name
    if name in EXCLUDE_DIRS:
        return True
    # AI Vibe Writing stores referenced authoring prompts under .ai_context.
    # Keep this narrowly scoped; other hidden metadata stays excluded.
    if name.startswith(".") and name not in (".cursor", ".claude", ".ai_context"):
        return True
    return False


def add_skill(
    skills_root,
    name: str,
    target: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> int:
    """Install a single skill into target/.agents/skills/<name>/ ."""
    skill_info = resolve_skill(skills_root, name)
    dest = target / ".agents" / "skills" / skill_info.name

    return _install_one(skill_info.source_path, dest, skill_info.name, force, dry_run)


def add_all_skills(
    skills_root,
    target: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> int:
    """Install all skills from skills_root into target/.agents/skills/."""
    skills = discover_skills(*skills_root)
    installed = 0
    skipped = 0
    errors = 0

    for skill_info in skills:
        dest = target / ".agents" / "skills" / skill_info.name
        result = _install_one(
            skill_info.source_path, dest, skill_info.name, force, dry_run
        )
        if result == 0:
            installed += 1
        elif result == 2:  # skipped
            skipped += 1
        else:
            errors += 1

    print(f"\n{len(skills)} skills: {installed} installed, {skipped} skipped, {errors} errors")
    return 1 if errors > 0 else 0


def _install_one(
    source: Path,
    dest: Path,
    name: str,
    force: bool,
    dry_run: bool,
) -> int:
    """Copy a single skill directory. Returns 0=ok, 2=skipped, 1=error."""
    if dest.exists():
        if not force:
            print(f"  SKIP  {name} (exists, use --force to overwrite)")
            return 2
        if not dry_run:
            shutil.rmtree(dest)

    if dry_run:
        print(f"  WILL  {name}")
        return 0

    def _ignore(d: str, names: list[str]) -> list[str]:
        return [n for n in names if _is_excluded(Path(d) / n)]

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest, ignore=_ignore, dirs_exist_ok=False)
        print(f"  COPY  {name}")
        return 0
    except OSError as e:
        print(f"  ERROR {name}: {e}", file=sys.stderr)
        return 1
