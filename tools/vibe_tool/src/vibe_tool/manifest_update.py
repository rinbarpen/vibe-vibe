"""Render updateable manifest resources without touching the real project.

The initialization scripts deliberately run against an empty staging directory.
Their outputs are then intersected with a resource allowlist: an initializer's
business scaffolds and runtime records are never manifest-update inputs.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path

from .manifest import _SCRIPT_FLAG_MAP
from .types import ManifestInfo


_COMMON_FILES = {"CLAUDE.md", "AGENTS.md", ".cursorrules"}
_COMMON_TREES = (
    Path(".cursor/rules"),
    Path(".cursor/commands"),
    Path(".cursor/templates"),
    Path(".cursor/references"),
    Path(".claude/agents"),
    Path(".codex/agents"),
)
_PRESERVED_NAMES = {"README.md", "CONTRIBUTING.md", "VERSION", "CHANGELOG.md", ".gitkeep"}


def render_manifest(
    manifest: ManifestInfo,
    stage: Path,
    target: Path,
    options: dict[str, str],
) -> list[Path]:
    """Generate a manifest and return updateable paths relative to ``stage``.

    ``stage`` must be an empty directory (or absent), separate from both the
    project and the manifest source. Only staging is written. References inside
    rendered files are calculated for ``target``, never for its temporary peer.
    Required skills and installation records are intentionally handled elsewhere.
    """
    stage = Path(stage).absolute()
    target = Path(target).resolve()
    source = manifest.path.resolve()
    _check_stage(stage, target, source)
    stage.mkdir(parents=True, exist_ok=True)

    try:
        if manifest.init_script_path is not None:
            _render_script(manifest, stage, target, options)
        else:
            _render_generic(manifest, stage, target)
        if manifest.name == "ui-testing":
            _rewrite_ui_rules(manifest, stage, target, options.get("scenario", ""))
    except OSError as exc:
        raise ValueError(f"Manifest '{manifest.name}' rendering failed: {exc}") from exc

    return sorted(
        (
            path.relative_to(stage)
            for path in stage.rglob("*")
            if (path.is_file() or path.is_symlink())
            and _is_resource(manifest.name, path.relative_to(stage), options)
        ),
        key=lambda path: path.as_posix(),
    )


def _check_stage(stage: Path, target: Path, source: Path) -> None:
    if stage.is_symlink():
        raise ValueError("Manifest staging directory must not be a symbolic link")
    resolved = stage.resolve()
    # Also reject links in staging's parents: mkdir/write must not traverse an
    # unexpected link even when the final directory itself does not exist yet.
    if resolved != stage:
        raise ValueError("Manifest staging path must not traverse symbolic links")
    for other, label in ((target, "target"), (source, "source")):
        if resolved == other or resolved in other.parents or other in resolved.parents:
            raise ValueError(f"Manifest staging directory overlaps {label}: {other}")
    if stage.exists() and (not stage.is_dir() or any(stage.iterdir())):
        raise ValueError("Manifest staging directory must be empty")


def _render_script(
    manifest: ManifestInfo,
    stage: Path,
    target: Path,
    options: dict[str, str],
) -> None:
    script = manifest.init_script_path
    assert script is not None
    flags: list[str] = []
    for key, pattern in _SCRIPT_FLAG_MAP.get(manifest.name, {}).items():
        if key in ("force", "dry_run"):
            continue
        value = options.get(key, "")
        if value:
            # Split the template, not the interpolated value: an owner or repo
            # containing spaces is one argument, rather than shell syntax.
            flags.extend(token.format(value=value) for token in shlex.split(pattern))
    if manifest.name == "vibe-coding":
        flags.append("--no-git")
    if manifest.name == "knowledge-learning":
        args = [*flags, str(stage)]  # this parser stops at the first positional
    else:
        args = [str(stage), *flags]
    env = {**os.environ, "VIBE_MANIFEST": str(manifest.path.resolve()),
           "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        ["bash", str(script.resolve()), *args],
        cwd=target if manifest.name == "vibe-coding" else stage,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(
            f"Manifest '{manifest.name}' rendering failed (exit {result.returncode}).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def _copy_resource(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination, follow_symlinks=False)


def _render_generic(manifest: ManifestInfo, stage: Path, target: Path) -> None:
    source = manifest.path
    for filename in ("CLAUDE.md", "AGENTS.md", "MANIFEST.md", ".cursorrules",
                     "README.md", "CONTRIBUTING.md"):
        path = source / filename
        if path.is_file() or path.is_symlink():
            _copy_resource(path, stage / filename)

    try:
        reference = str(source.resolve().relative_to(target))
    except ValueError:
        reference = str(source.resolve())
    for rule in sorted((source / "rules").glob("*.mdc")):
        destination = stage / ".cursor/rules" / rule.name
        if rule.is_symlink():
            _copy_resource(rule, destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            # Write before applying metadata: a source may be read-only.
            destination.write_text(
                rule.read_text(encoding="utf-8").replace("{{VIBE_MANIFEST}}", reference),
                encoding="utf-8",
            )
            shutil.copystat(rule, destination, follow_symlinks=False)

    commands = source / "commands"
    if commands.is_dir():
        for command in sorted(commands.iterdir()):
            if command.is_dir() and not command.is_symlink():
                for path in sorted(command.iterdir()):
                    if path.is_file() or path.is_symlink():
                        _copy_resource(path, stage / ".cursor/commands" / command.name / path.name)
    for relative in (Path(".claude/agents"), Path(".codex/agents")):
        for path in sorted((source / relative).rglob("*")):
            if path.is_file() or path.is_symlink():
                _copy_resource(path, stage / relative / path.relative_to(source / relative))


def _rewrite_ui_rules(
    manifest: ManifestInfo,
    stage: Path,
    target: Path,
    scenario: str,
) -> None:
    # The existing initializer hardcodes ../manifests/ui-testing. Re-render from
    # the original templates so no temporary or hardcoded reference survives.
    reference = os.path.relpath(manifest.path.resolve(), target)
    roots = [manifest.path / "rules"]
    if scenario:
        roots.append(manifest.path / "scenarios" / scenario / "rules")
    for rules in roots:
        for source in sorted(rules.glob("*.mdc")):
            destination = stage / ".cursor/rules" / source.name
            if destination.is_file() and not destination.is_symlink():
                destination.write_text(
                    source.read_text(encoding="utf-8").replace("{{UI_TESTING_MANIFEST}}", reference),
                    encoding="utf-8",
                )


def _under(path: Path, root: Path) -> bool:
    return root in path.parents


def _is_resource(name: str, relative: Path, options: dict[str, str]) -> bool:
    if any(part in {".git", ".vibe-tool", ".auto-research"} for part in relative.parts):
        return False
    if relative.name in _PRESERVED_NAMES:
        return False
    if relative.as_posix() in _COMMON_FILES or any(_under(relative, root) for root in _COMMON_TREES):
        return True
    if name == "knowledge-learning" and relative == Path(".cursor/scenario.md"):
        return True
    if name == "ui-testing" and relative == Path("CLAUDE.ui-testing.md"):
        return True
    if name == "vibe-coding":
        if relative.as_posix() in {"MANIFEST.md", ".editorconfig", ".gitignore", "scripts/version_guard.py"}:
            return True
        provider = options.get("provider") or "github"
        return (
            provider == "github" and _under(relative, Path(".github"))
            or provider == "gitlab" and relative == Path(".gitlab-ci.yml")
            or provider == "gitee" and _under(relative, Path(".workflow"))
        )
    if name == "auto-research":
        return any(_under(relative, Path(root)) for root in (
            ".github", "scripts", "references", "templates", "writing", "lifecycle",
        ))
    if name == "auto-research-ars":
        return any(_under(relative, Path(root)) for root in ("references", "templates"))
    return False
