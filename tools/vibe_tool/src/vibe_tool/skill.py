"""Skill addition/installation logic."""

import os
import shutil
import sys
from pathlib import Path

from .discovery import _as_roots, discover_skills, resolve_skill
from .installations import load_installations, record_skill, source_ref

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

    root = _repository_root(skills_root)
    if not dry_run:
        # Preflight provenance before changing the installed directory.
        load_installations(target)
        source_ref(root, skill_info.source_path)
    result = _install_one(skill_info.source_path, dest, skill_info.name, force, dry_run)
    if result == 0 and not dry_run:
        record_skill(root, target, skill_info.name, skill_info.source_path, force=True)
    return result


def add_all_skills(
    skills_root,
    target: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> int:
    """Install all skills from skills_root into target/.agents/skills/."""
    skills = discover_skills(*_as_roots(skills_root))
    root = _repository_root(skills_root)
    if not dry_run:
        load_installations(target)
        for info in skills:
            source_ref(root, info.source_path)
    installed = 0
    skipped = 0
    errors = 0

    for skill_info in skills:
        dest = target / ".agents" / "skills" / skill_info.name
        result = _install_one(
            skill_info.source_path, dest, skill_info.name, force, dry_run
        )
        if result == 0:
            if not dry_run:
                record_skill(root, target, skill_info.name, skill_info.source_path, force=True)
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


def _repository_root(skills_root) -> Path:
    """Find the aggregate root, including manifest-local dependency roots."""
    roots = _as_roots(skills_root)
    for root in roots:
        absolute = Path(os.path.abspath(root))
        for parent in (absolute, *absolute.parents):
            if (parent / "manifests").is_dir() and (parent / "skills").is_dir():
                return parent
    # Also support minimal API fixtures and standalone skill collections.
    if len(roots) == 1:
        return roots[0].absolute().parent
    return Path(os.path.commonpath([str(root.absolute()) for root in roots]))
