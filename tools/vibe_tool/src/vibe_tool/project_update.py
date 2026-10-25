"""Synchronize named project installations from the current local source tree."""

from __future__ import annotations

import copy
import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path

from .discovery import resolve_manifest, resolve_skill
from .installations import (
    INSTALLATIONS_RELATIVE_PATH,
    load_installations,
    manifest_option_keys,
    normalized_options,
    skill_entry,
    source_ref,
    write_installations,
)
from .manifest_update import render_manifest
from .rollback import checked_path
from .skill import _is_excluded
from .transaction import Change, apply_update, ensure_separate
from .types import SkillInfo


def _target(target: Path) -> Path:
    target = Path(target).resolve()
    if not target.is_dir():
        raise ValueError(f"Target directory does not exist: {target}")
    checked_path(target, INSTALLATIONS_RELATIVE_PATH)
    return target


def _recorded_skill(root: Path, name: str, data: dict) -> SkillInfo | None:
    entries = data["skills"]
    if name in entries:
        canonical = name
    else:
        candidates = [key for key in entries if key.lower() == name.lower()]
        if len(candidates) != 1:
            return None
        canonical = candidates[0]
    relative = entries[canonical]["source"]
    source = root / relative
    if not source.is_dir() or not (source / "SKILL.md").is_file():
        raise ValueError(f"Recorded skill source is missing: {source}")
    return SkillInfo(name=canonical, source_path=source, id_path=relative)


def _copy_skill(source: Path, destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> list[str]:
        return [name for name in names if _is_excluded(Path(directory) / name)]
    shutil.copytree(source, destination, symlinks=True, ignore=ignore)


def _stage_skill(root: Path, info: SkillInfo, target: Path, staging: Path,
                 data: dict) -> Change:
    relative = Path(".agents/skills") / info.name
    dest = checked_path(target, relative)
    if not dest.is_dir() or not (dest / "SKILL.md").is_file():
        raise ValueError(
            f"Skill '{info.name}' is not installed in {target}. "
            f"Use: vibe add skill {info.name} {target}"
        )
    ensure_separate(info.source_path, dest)
    source = staging / info.name
    _copy_skill(info.source_path, source)
    data["skills"][info.name] = skill_entry(root, info.source_path)
    return Change(relative, source)


def _stage_records(target: Path, staging: Path, previous: dict,
                   updated: dict) -> list[Change]:
    if previous == updated:
        return []
    write_installations(staging, updated)
    source = staging / INSTALLATIONS_RELATIVE_PATH
    existing = target / INSTALLATIONS_RELATIVE_PATH
    if existing.exists() and not existing.is_symlink():
        source.chmod(stat.S_IMODE(existing.stat().st_mode))
    return [Change(INSTALLATIONS_RELATIVE_PATH, source)]


def update_skill(root: Path, name: str, target: Path, *, dry_run: bool = False) -> int:
    """Replace one installed skill, with a complete pre-update backup."""
    try:
        root, target = Path(root).resolve(), _target(target)
        original = load_installations(target)
        updated = copy.deepcopy(original)
        info = _recorded_skill(root, name, original)
        if info is None:
            info = resolve_skill((root / "skills", root / "mine"), name)
            info = _recorded_skill(root, info.name, original) or info
        with tempfile.TemporaryDirectory(prefix="vibe-update-") as temporary:
            staging = Path(temporary).resolve()
            changes = [_stage_skill(root, info, target, staging / "skills", updated)]
            changes.extend(_stage_records(target, staging / "records", original, updated))
            return apply_update(target, changes, label=f"skill {info.name}", dry_run=dry_run)
    except (OSError, ValueError) as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1


def _options(manifest, stored: dict | None, provided: dict) -> dict[str, str]:
    keys = manifest_option_keys(manifest.name)
    explicit = {key: value for key, value in provided.items() if value is not None}
    unsupported = set(explicit) - set(keys)
    if unsupported:
        raise ValueError(
            f"Manifest '{manifest.name}' does not support: "
            + ", ".join(f"--{key}" for key in sorted(unsupported))
        )
    options = dict(stored["options"]) if stored else {}
    options.update(explicit)
    missing = [key for key in keys if key not in options]
    if missing:
        raise ValueError(
            f"Legacy manifest '{manifest.name}' has no recorded generation options. "
            "Specify " + ", ".join(f"--{key}" for key in missing)
            + "; use an empty value for no scenario or template defaults."
        )
    options = normalized_options(manifest.name, options)
    if "provider" in options and not options["provider"]:
        options["provider"] = "github"
    if "provider" in options and options["provider"] not in ("git", "github", "gitlab", "gitee"):
        raise ValueError(f"Unsupported provider: {options['provider']}")
    scenario = options.get("scenario", "")
    if scenario:
        scenarios = scenario.split(",") if manifest.name == "vibe-coding" else [scenario]
        if any(value not in manifest.scenarios for value in scenarios):
            raise ValueError(
                f"Unknown scenario for {manifest.name}: {scenario}. "
                f"Available: {', '.join(manifest.scenarios)}"
            )
    return options


def _dependencies(root: Path, manifest, target: Path, staging: Path,
                  data: dict) -> list[Change]:
    changes = []
    seen = set()
    roots = (root / "skills", root / "mine", manifest.path / "skills")
    for name in manifest.required_skills:
        # Recorded sources disambiguate manifest-local installations and survive
        # unrelated additions to the catalog that change collision suffixes.
        recorded = [key for key in data["skills"] if key.lower() == name.lower()]
        if len(recorded) == 1:
            dest = checked_path(target, Path(".agents/skills") / recorded[0])
            if not os.path.lexists(dest):
                print(f"  SKIP  {recorded[0]} (required skill is not installed)")
                continue
        info = _recorded_skill(root, name, data)
        if info is None:
            try:
                info = resolve_skill(roots, name)
            except ValueError:
                dest = checked_path(target, Path(".agents/skills") / name)
                if os.path.lexists(dest):
                    raise
                print(f"  SKIP  {name} (required skill is not installed)")
                continue
            info = _recorded_skill(root, info.name, data) or info
        dest = checked_path(target, Path(".agents/skills") / info.name)
        if not os.path.lexists(dest):
            print(f"  SKIP  {info.name} (required skill is not installed)")
            continue
        if info.name not in seen:
            changes.append(_stage_skill(root, info, target, staging, data))
            seen.add(info.name)
    return changes


def update_manifest(root: Path, name: str, target: Path, *, dry_run: bool = False,
                    **options: str) -> int:
    """Update generated resources and installed dependencies in one transaction."""
    try:
        root, target = Path(root).resolve(), _target(target)
        original = load_installations(target)
        updated = copy.deepcopy(original)
        manifest = resolve_manifest(root / "manifests", name)
        ensure_separate(manifest.path, target)
        stored = original["manifests"].get(manifest.name)
        if stored and stored["source"] != source_ref(root, manifest.path):
            raise ValueError(f"Manifest source differs from its installation record: {manifest.name}")
        effective = _options(manifest, stored, options)
        with tempfile.TemporaryDirectory(prefix="vibe-update-") as temporary:
            staging = Path(temporary).resolve()
            rendered = staging / "manifest"
            paths = render_manifest(manifest, rendered, target, effective)
            if not stored and not any(os.path.lexists(checked_path(target, path)) for path in paths):
                raise ValueError(
                    f"Manifest '{manifest.name}' has no installed resources in {target}. "
                    f"Use: vibe add manifest {manifest.name} {target}"
                )
            changes = [Change(path, rendered / path) for path in paths]
            changes.extend(_dependencies(root, manifest, target, staging / "skills", updated))
            updated["manifests"][manifest.name] = {
                "source": source_ref(root, manifest.path), "options": effective,
            }
            changes.extend(_stage_records(target, staging / "records", original, updated))
            return apply_update(target, changes, label=f"manifest {manifest.name}", dry_run=dry_run)
    except (OSError, ValueError) as exc:
        print(f"Update failed: {exc}", file=sys.stderr)
        return 1
