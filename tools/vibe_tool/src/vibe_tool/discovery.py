"""Dynamic discovery of manifests and skills."""

from collections import defaultdict
from pathlib import Path, PureWindowsPath

from .types import ManifestInfo, SkillInfo

INIT_BLACKLIST = {"agent-browser"}


def discover_manifests(manifests_dir: Path) -> list[ManifestInfo]:
    """Scan manifests_dir for valid manifests (must have CLAUDE.md)."""
    manifests: list[ManifestInfo] = []
    for entry in sorted(manifests_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if entry.name in INIT_BLACKLIST:
            continue

        claude_md = entry / "CLAUDE.md"
        if not claude_md.exists():
            continue

        description = _read_description(claude_md)

        init_scripts = sorted(entry.glob("scripts/*init*.sh"))
        has_init = len(init_scripts) > 0
        init_path = init_scripts[0] if has_init else None

        scenarios_dir = entry / "scenarios"
        scenarios: list[str] = []
        if scenarios_dir.is_dir():
            scenarios = sorted(
                d.name for d in scenarios_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            )

        manifests.append(ManifestInfo(
            name=entry.name,
            path=entry,
            description=description,
            has_init_script=has_init,
            init_script_path=init_path,
            scenarios=scenarios,
            required_skills=_read_required_skills(entry),
        ))

    return manifests


def _read_required_skills(manifest_path: Path) -> list[str]:
    """Read optional skills.txt listing required skill names (one per line)."""
    skills_file = manifest_path / "skills.txt"
    if not skills_file.is_file():
        return []

    names: list[str] = []
    try:
        for line in skills_file.read_text(encoding="utf-8").splitlines():
            name = line.split("#", 1)[0].strip()
            if name:
                names.append(name)
    except OSError:
        return []
    return names


def discover_skills(*roots: Path) -> list[SkillInfo]:
    """Recursively find all directories containing SKILL.md under given roots.

    Name collisions (same directory name in different sub-paths) are resolved
    by encoding the relative path with hyphens.
    """
    by_name: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for root in roots:
        for skill_md in sorted(root.rglob("SKILL.md")):
            skill_dir = skill_md.parent
            try:
                rel = skill_dir.relative_to(root)
            except ValueError:
                continue
            by_name[skill_dir.name].append((skill_dir, str(rel)))

    skills: list[SkillInfo] = []
    for entries in by_name.values():
        for skill_dir, rel_path in entries:
            if len(entries) == 1:
                name = skill_dir.name
            else:
                name = rel_path.replace("/", "-").replace("\\", "-")
            skills.append(SkillInfo(
                name=name,
                source_path=skill_dir,
                id_path=rel_path,
            ))

    return skills


def resolve_manifest(manifests_dir: Path, name: str) -> ManifestInfo:
    """Look up a single manifest by name. Raises ValueError with candidates."""
    if name.lower() == "knowledge-learning":
        raise ValueError(
            "Manifest 'knowledge-learning' has been renamed to 'tutor'.\n"
            "Use: vibe init tutor [target]\n"
            "Upgrade an existing project: vibe add manifest tutor <target> --force"
        )
    manifests = discover_manifests(manifests_dir)
    by_name = {m.name: m for m in manifests}

    if name in by_name:
        return by_name[name]

    # Try case-insensitive match
    lower = name.lower()
    for m in manifests:
        if m.name.lower() == lower:
            return m

    # Try substring match
    candidates = [m.name for m in manifests if lower in m.name.lower()]
    if len(candidates) == 1:
        return by_name[candidates[0]]

    all_names = [m.name for m in manifests]
    raise ValueError(
        f"Manifest '{name}' not found.\n"
        f"Available: {', '.join(all_names)}"
    )


def resolve_skill(skills_root, name: str) -> SkillInfo:
    """Look up a skill by its legacy name or an exact relative ``id_path``.

    Path queries deliberately do not use fuzzy matching. Their installation
    name is stable even when another submodule adds a same-named skill later.
    """
    normalized = name.replace("\\", "/")
    if (
        not name
        or Path(normalized).is_absolute()
        or PureWindowsPath(name).drive
        or any(part in ("", ".", "..") for part in normalized.split("/"))
    ):
        raise ValueError(f"Invalid skill identifier: {name!r}; use a relative skill name or id_path.")

    roots = _as_roots(skills_root)
    skills = discover_skills(*roots)

    if "/" in normalized:
        matches = [s for s in skills if s.id_path.replace("\\", "/") == normalized]
        if len(matches) == 1:
            return SkillInfo(
                name=normalized.replace("/", "-"),
                source_path=matches[0].source_path,
                id_path=normalized,
            )
        if len(matches) > 1:
            sources = ", ".join(str(s.source_path) for s in matches)
            raise ValueError(f"Skill id_path '{name}' is ambiguous across roots: {sources}")
        raise ValueError(f"Skill id_path '{name}' not found among {len(skills)} skills.")

    by_name = {s.name: s for s in skills}
    by_lower = {s.name.lower(): s for s in skills}

    if name in by_name:
        return by_name[name]
    if name.lower() in by_lower:
        return by_lower[name.lower()]

    # Substring match
    lower = name.lower()
    candidates = [s.name for s in skills if lower in s.name.lower()]
    if len(candidates) == 1:
        return by_name[candidates[0]]
    if len(candidates) > 1:
        raise ValueError(
            f"Skill '{name}' is ambiguous. Candidates: {', '.join(candidates[:10])}"
        )

    raise ValueError(f"Skill '{name}' not found among {len(skills)} skills.")


def _as_roots(skills_root) -> tuple[Path, ...]:
    """Normalize a single Path or a sequence of Paths into a tuple of roots."""
    if isinstance(skills_root, (tuple, list)):
        return tuple(Path(r) for r in skills_root)
    return (Path(skills_root),)


def _read_description(claude_md: Path) -> str:
    """Extract the first meaningful line from CLAUDE.md as description."""
    try:
        content = claude_md.read_text(encoding="utf-8")
        for line in content.split("\n"):
            stripped = line.strip().lstrip("#").strip()
            if stripped and not stripped.startswith("---"):
                return stripped
    except OSError:
        pass
    return ""
