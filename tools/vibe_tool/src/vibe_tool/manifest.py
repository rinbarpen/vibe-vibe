"""Manifest init and add operations.

Delegates to existing init scripts when present, falls back to generic file-copy
for manifests without scripts.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from .discovery import resolve_manifest
from .types import ManifestInfo

# ── Flag mapping per manifest init script ──

_SCRIPT_FLAG_MAP: dict[str, dict[str, str]] = {
    "vibe-coding": {
        "scenario": "--scenario={value}",
        "owner": "-o {value}",
        "org": "--org {value}",
        "repo": "--repo {value}",
        "email": "--email {value}",
        "cloud": "--cloud={value}",
        "force": "-f",
        "dry_run": "-n",
    },
    "github-enterprise": {
        "owner": "-o {value}",
        "org": "--org {value}",
        "repo": "--repo {value}",
        "email": "--email {value}",
        "force": "-f",
        "dry_run": "-n",
    },
    "auto-research": {
        "owner": "-o {value}",
        "org": "--org {value}",
        "repo": "--repo {value}",
        "force": "-f",
        "dry_run": "-n",
    },
    "auto-research-ars": {
        "force": "-f",
        "dry_run": "-n",
    },
    "knowledge-learning": {
        "scenario": "--scenario {value}",
        "force": "--force",
        "dry_run": "-n",
    },
    "ui-testing": {
        "scenario": "--scenario={value}",
        "force": "-f",
        "dry_run": "-n",
    },
    "fund-proposal": {
        "force": "-f",
        "dry_run": "-n",
    },
}


def init_manifest(
    manifests_dir: Path,
    name: str,
    target: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    **kwargs: str,
) -> int:
    """Initialize a NEW project from a manifest.

    Creates target directory, then delegates to the manifest's init script
    or performs a generic file-copy init.
    """
    manifest = resolve_manifest(manifests_dir, name)

    target = target.resolve()
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    rc = 0
    if manifest.init_script_path is not None:
        rc = _run_init_script(manifest, target, force, dry_run, **kwargs)
    else:
        rc = _generic_init(manifest, target, force, dry_run)

    if rc == 0:
        return _install_required_skills(manifests_dir, manifest, target, force, dry_run)
    return rc


def add_manifest(
    manifests_dir: Path,
    name: str,
    target: Path,
    *,
    force: bool = False,
    dry_run: bool = False,
    **kwargs: str,
) -> int:
    """Add manifest files to an EXISTING project.

    Same as init but expects target to already exist.
    """
    manifest = resolve_manifest(manifests_dir, name)

    target = target.resolve()
    if not target.is_dir():
        print(f"Error: target directory does not exist: {target}", file=sys.stderr)
        return 1

    rc = 0
    if manifest.init_script_path is not None:
        rc = _run_init_script(manifest, target, force, dry_run, **kwargs)
    else:
        rc = _generic_init(manifest, target, force, dry_run)

    if rc == 0:
        return _install_required_skills(manifests_dir, manifest, target, force, dry_run)
    return rc


# ── Script delegation ──

def _run_init_script(
    manifest: ManifestInfo,
    target: Path,
    force: bool,
    dry_run: bool,
    **kwargs: str,
) -> int:
    """Call the manifest's init shell script as a subprocess."""
    script_path = manifest.init_script_path
    assert script_path is not None

    flag_map = _SCRIPT_FLAG_MAP.get(manifest.name, {})

    # Build script arguments; target dir is passed as first positional arg
    script_args: list[str] = [str(target)]

    for key, value in kwargs.items():
        if not value:
            continue
        if key in ("force", "dry_run"):
            bool_val = key == "force" and force or key == "dry_run" and dry_run
            if bool_val and key in flag_map:
                script_args.append(flag_map[key])
            continue

        if key in flag_map:
            script_args.append(flag_map[key].format(value=value))

    # force/dry_run for manifests where they aren't in flag_map
    if force and "force" not in flag_map:
        script_args.append("-f")
    if dry_run and "dry_run" not in flag_map:
        script_args.append("-n")

    # Build environment (VIBE_MANIFEST needed by vibe-coding init)
    env = dict(subprocess.os.environ)
    env["VIBE_MANIFEST"] = str(manifest.path)

    cmd = [str(script_path)] + script_args

    if dry_run:
        print(f"[dry-run] Would run: {' '.join(cmd)}")
        print(f"[dry-run]   in: {target}")
        return 0

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=str(target),
        env=env,
    )
    return result.returncode


# ── Generic init (no script) ──

def _generic_init(
    manifest: ManifestInfo,
    target: Path,
    force: bool,
    dry_run: bool,
) -> int:
    """Copy manifest files into target using a standard layout."""
    src = manifest.path
    actions: list[tuple[str, Path]] = []

    # Directory structure
    dirs = [
        ".cursor/rules",
        ".cursor/plans",
        ".cursor/commands",
    ]
    for d in dirs:
        dest = target / d
        if dry_run:
            actions.append(("mkdir", dest))
        else:
            dest.mkdir(parents=True, exist_ok=True)

    # Root-level files (non-overwriting unless --force)
    root_files = ["CLAUDE.md", "AGENTS.md", ".cursorrules", "README.md", "CONTRIBUTING.md"]
    for filename in root_files:
        src_file = src / filename
        if not src_file.is_file():
            continue
        dst_file = target / filename
        if dst_file.exists() and not force:
            actions.append(("skip", dst_file))
            continue
        rel_src = _relpath(src_file, manifest.path)
        if dry_run:
            actions.append(("copy", dst_file))
        else:
            shutil.copy2(src_file, dst_file)
            actions.append(("copy", dst_file))

    # Rules (*.mdc → .cursor/rules/)
    rules_dir = src / "rules"
    if rules_dir.is_dir():
        for rule_file in sorted(rules_dir.glob("*.mdc")):
            dst_file = target / ".cursor" / "rules" / rule_file.name
            if dst_file.exists() and not force:
                actions.append(("skip", dst_file))
                continue
            if dry_run:
                actions.append(("copy", dst_file))
            else:
                _copy_with_subst(rule_file, dst_file, manifest.path, target)
                actions.append(("copy", dst_file))

    # Commands (*/ → .cursor/commands/)
    commands_dir = src / "commands"
    if commands_dir.is_dir():
        for cmd_dir in sorted(commands_dir.iterdir()):
            if not cmd_dir.is_dir():
                continue
            dst_dir = target / ".cursor" / "commands" / cmd_dir.name
            dst_dir.mkdir(parents=True, exist_ok=True)
            for cmd_file in cmd_dir.iterdir():
                if not cmd_file.is_file():
                    continue
                dst_file = dst_dir / cmd_file.name
                if dst_file.exists() and not force:
                    actions.append(("skip", dst_file))
                    continue
                if dry_run:
                    actions.append(("copy", dst_file))
                else:
                    shutil.copy2(cmd_file, dst_file)
                    actions.append(("copy", dst_file))

    # Native Claude Code and Codex agent definitions.
    for agents_rel in [Path(".claude/agents"), Path(".codex/agents")]:
        agents_dir = src / agents_rel
        if not agents_dir.is_dir():
            continue

        for agent_file in sorted(agents_dir.rglob("*")):
            if not agent_file.is_file():
                continue
            rel_agent = agent_file.relative_to(agents_dir)
            dst_file = target / agents_rel / rel_agent
            if dst_file.exists() and not force:
                actions.append(("skip", dst_file))
                continue
            if dry_run:
                actions.append(("copy", dst_file))
            else:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(agent_file, dst_file)
                actions.append(("copy", dst_file))

    # Print summary
    copies = [a for a in actions if a[0] == "copy"]
    skips = [a for a in actions if a[0] == "skip"]
    mkdirs = [a for a in actions if a[0] == "mkdir"]

    label = "[dry-run] Would install" if dry_run else "Installed"
    print(f"{label} {len(copies)} files to {target}")
    for action, path in copies:
        rel = _relpath(path, target)
        print(f"  COPY  {rel}")
    for action, path in skips:
        rel = _relpath(path, target)
        print(f"  SKIP  {rel} (exists)")

    return 0


def _copy_with_subst(src: Path, dst: Path, manifest_path: Path, target: Path) -> None:
    """Copy a file, substituting {{VIBE_MANIFEST}} with relative path."""
    content = src.read_text(encoding="utf-8")
    try:
        rel = manifest_path.resolve().relative_to(target.resolve())
        content = content.replace("{{VIBE_MANIFEST}}", str(rel))
    except ValueError:
        content = content.replace("{{VIBE_MANIFEST}}", str(manifest_path.resolve()))
    dst.write_text(content, encoding="utf-8")


def _relpath(p: Path, base: Path) -> str:
    try:
        return str(p.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(p)


def _policy_relative(value: object) -> Path:
    if (not isinstance(value, str) or not value or Path(value).is_absolute()
            or not Path(value).parts or ".." in Path(value).parts
            or Path(value).as_posix() != value):
        raise ValueError(f"policy path must be project-relative: {value!r}")
    return Path(value)


def _installed_skill_file(root: Path, relative: Path) -> Path:
    current = root
    if root.is_symlink() or root.parent.is_symlink():
        raise ValueError(f"symlink in installed skill root: {root}")
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink in installed skill path: {relative}")
    return current


def _validate_installed_skill_contracts(roots, manifest: ManifestInfo, target: Path,
                                       policy: dict, skill_force: bool, dry_run: bool) -> int:
    """Detect incompatible preserved bundles; never merge or overwrite custom files."""
    from .discovery import resolve_skill
    from .skill import _is_excluded

    if not policy.get("validate_required_files", False) and not policy.get("required_catalog_schemas"):
        return 0
    skill_root = target / ".agents/skills"
    problems: list[str] = []
    pending = set()
    for name in manifest.required_skills:
        try:
            info = resolve_skill(roots, name)
        except ValueError:
            continue  # The normal installation error already explains this.
        dest = skill_root / info.name
        # A fresh/replaced dry-run bundle will come from the current source;
        # check preserved bundles now without requiring hypothetical files.
        if dry_run and (not dest.exists() or skill_force):
            pending.add(info.name)
            continue
        if not policy.get("validate_required_files", False):
            continue
        for source in sorted(info.source_path.rglob("*")):
            if not source.is_file():
                continue
            source_relative = source.relative_to(info.source_path)
            if any(_is_excluded(Path(part)) for part in source_relative.parts):
                continue
            relative = Path(info.name) / source_relative
            try:
                installed = _installed_skill_file(skill_root, relative)
                if not installed.is_file():
                    problems.append(f"missing required skill file: {relative}")
                    continue
                data = installed.read_bytes()
                if not data and (source.stat().st_size or source.name == "SKILL.md"):
                    problems.append(f"empty required skill file: {relative}")
                if source.name == "SKILL.md" and data and not data.decode("utf-8").strip():
                    problems.append(f"empty required skill file: {relative}")
            except (OSError, UnicodeError, ValueError) as exc:
                problems.append(f"invalid required skill file {relative}: {exc}")
    for key, minimum in policy.get("required_catalog_schemas", {}).items():
        relative = _policy_relative(key)
        if relative.parts[0] in pending:
            continue
        try:
            catalog = _installed_skill_file(skill_root, relative)
            data = json.loads(catalog.read_text(encoding="utf-8"))
            actual = data.get("schema_version") if isinstance(data, dict) else None
            if type(actual) is not int or actual < minimum:
                problems.append(f"incompatible catalog {key}: schema_version={actual!r}, required>={minimum}")
        except (OSError, ValueError, UnicodeError) as exc:
            problems.append(f"invalid required catalog {key}: {exc}")
    if problems:
        print("needs_migration: preserved skill bundles do not satisfy this manifest:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print("Existing skill files were preserved. Back up the affected .agents/skills bundle, "
              "then manually merge the current source bundle (including its catalog and new subskills), "
              "or reinstall that skill explicitly with 'vibe add skill <name> --force' after reviewing "
              "your backup. Rerun the manifest command to verify compatibility.", file=sys.stderr)
        return 1
    return 0


def _install_required_skills(
    manifests_dir: Path,
    manifest: ManifestInfo,
    target: Path,
    force: bool,
    dry_run: bool,
) -> int:
    """Install required skills, respecting an optional non-destructive policy.

    A manifest may opt out of force-refreshing existing skills with
    skills-policy.json: {"preserve_existing": true}. Optional
    validate_required_files checks all copied bundle files (including support
    references/scripts); required_catalog_schemas detects old preserved catalogs.
    Both return needs_migration without replacing them. Other manifests
    retain their existing --force behavior. Explicit skill --force is unaffected.
    """
    if not manifest.required_skills:
        return 0

    # Resolve policy roots using the same canonical names as add_skill; required
    # skill names may use case-insensitive or unambiguous substring aliases.
    from .discovery import resolve_skill
    repo_root = manifests_dir.parent
    roots = (repo_root / "skills", repo_root / "mine")
    skill_force = force
    policy: dict = {}
    policy_path = manifest.path / "skills-policy.json"
    if policy_path.is_file():
        try:
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            if not isinstance(policy, dict) or type(policy.get("preserve_existing")) is not bool:
                raise ValueError("preserve_existing must be a boolean")
            if type(policy.get("validate_required_files", False)) is not bool:
                raise ValueError("validate_required_files must be a boolean")
            schemas = policy.get("required_catalog_schemas", {})
            if not isinstance(schemas, dict):
                raise ValueError("required_catalog_schemas must map paths to minimum schema integers")
            required_names = {name: name for name in manifest.required_skills}
            if schemas:
                for name in manifest.required_skills:
                    try:
                        canonical = resolve_skill(roots, name).name
                        required_names[name] = canonical
                        required_names[canonical] = canonical
                    except ValueError:
                        pass  # The normal installer will report missing skills.
            normalized_schemas = {}
            for key, minimum in schemas.items():
                relative = _policy_relative(key)
                canonical = required_names.get(relative.parts[0])
                if canonical is None:
                    raise ValueError(f"catalog does not belong to a required skill: {key}")
                if type(minimum) is not int or minimum < 1:
                    raise ValueError(f"invalid catalog minimum schema: {key}")
                normalized_schemas[(Path(canonical) / Path(*relative.parts[1:])).as_posix()] = minimum
            policy["required_catalog_schemas"] = normalized_schemas
        except (OSError, ValueError) as exc:
            print(f"Error: invalid skill policy {policy_path}: {exc}", file=sys.stderr)
            return 1
        if policy["preserve_existing"]:
            skill_force = False

    from .skill import add_skill

    missing: list[str] = []
    installed = 0
    print(f"\nInstalling {len(manifest.required_skills)} required skills:")
    for name in manifest.required_skills:
        try:
            rc = add_skill(roots, name, target, force=skill_force, dry_run=dry_run)
            if rc == 1:
                missing.append(name)
            else:
                installed += 1
        except ValueError:
            missing.append(name)
            print(f"  WARN  {name}: not found")

    if missing:
        print(
            "  (tip: run 'vibe update' to fetch skill submodules, "
            "then 'vibe add skill <name>' for any still-missing)"
        )
    if missing:
        return 1
    return _validate_installed_skill_contracts(roots, manifest, target, policy, skill_force, dry_run)
