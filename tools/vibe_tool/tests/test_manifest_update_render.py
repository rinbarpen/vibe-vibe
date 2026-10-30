"""Manifest update rendering stays separate from a user's project state."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from vibe_tool.discovery import discover_manifests, resolve_manifest
from vibe_tool.manifest_update import render_manifest
from vibe_tool.types import ManifestInfo


ROOT = Path(__file__).resolve().parents[3]
MANIFESTS = ROOT / "manifests"
NAMES = [manifest.name for manifest in discover_manifests(MANIFESTS)]


def snapshot(root: Path) -> dict[str, tuple]:
    result = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        stat = path.lstat()
        if path.is_symlink():
            result[relative] = ("link", os.readlink(path), stat.st_mode, stat.st_mtime_ns)
        elif path.is_file():
            result[relative] = ("file", path.read_bytes(), stat.st_mode, stat.st_mtime_ns)
        else:
            result[relative] = ("dir", stat.st_mode, stat.st_mtime_ns)
    return result


@pytest.mark.parametrize("name", NAMES)
def test_render_every_manifest_never_writes_project(tmp_path: Path, name: str) -> None:
    target = tmp_path / "real project with spaces"
    target.mkdir()
    for relative, value in {
        "CLAUDE.md": "project customized instructions",
        "MANIFEST.md": "project output ledger",
        "README.md": "project documentation",
        "VERSION": "8.4.2",
        "CHANGELOG.md": "project history",
        "notes/_index.md": "knowledge index",
        "outline/skeleton.md": "actual business outline",
        ".git/HEAD": "ref: refs/heads/main\n",
        ".auto-research/runtime.yaml": "preserve runtime",
        ".vibe-tool/installations.json": "preserve metadata",
    }.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    before = snapshot(target)
    stage = tmp_path / f"render stage {name}"
    paths = render_manifest(resolve_manifest(MANIFESTS, name), stage, target, {})
    assert snapshot(target) == before
    assert paths
    assert all(not path.is_absolute() for path in paths)
    assert all((stage / path).is_file() or (stage / path).is_symlink() for path in paths)
    assert Path("CLAUDE.md") in paths
    assert Path("AGENTS.md") in paths
    assert (Path("MANIFEST.md") in paths) == (name == "vibe-coding")
    assert not any(path.name in {"README.md", "CONTRIBUTING.md", "VERSION", "CHANGELOG.md", ".gitkeep"}
                   for path in paths)
    assert not any(path.parts[0] in {".auto-research", ".vibe-tool", "notes", "outline", ".git"}
                   for path in paths)
    assert not (stage / ".git").exists()
    assert not (stage / ".vibe-tool").exists()
    assert not (stage / ".claude/skills").exists()


@pytest.mark.parametrize("provider", ["git", "github", "gitlab", "gitee"])
def test_vibe_provider_args_and_real_target_references(tmp_path: Path, provider: str) -> None:
    target = tmp_path / "target with spaces"
    target.mkdir()
    stage = tmp_path / "stage with spaces"
    manifest = resolve_manifest(MANIFESTS, "vibe-coding")
    paths = render_manifest(manifest, stage, target, {
        "provider": provider, "scenario": "api-service", "owner": "@team member",
        "org": "test org", "repo": "test repo", "email": "contact@example.invalid",
    })
    assert (Path(".github/CODEOWNERS") in paths) == (provider == "github")
    assert (Path(".gitlab-ci.yml") in paths) == (provider == "gitlab")
    assert (Path(".workflow/vibe-ci.yml") in paths) == (provider == "gitee")
    assert (stage / "CLAUDE.md").is_symlink()
    assert os.readlink(stage / "CLAUDE.md") == "MANIFEST.md"
    assert (stage / "AGENTS.md").is_symlink()
    assert Path("scripts/version_guard.py") in paths
    assert Path(".editorconfig") in paths
    if provider == "github":
        assert "@team member" in (stage / ".github/CODEOWNERS").read_text()
        assert "contact@example.invalid" in (stage / ".github/SECURITY.md").read_text()
    original = next(path for path in (manifest.path / "rules").glob("*.mdc")
                    if "{{VIBE_MANIFEST}}" in path.read_text())
    rendered = (stage / ".cursor/rules" / original.name).read_text()
    assert os.path.relpath(manifest.path, target) in rendered
    assert str(stage) not in rendered


@pytest.mark.parametrize("scenario", ["self-study", "exam-prep", "course-learning", "research-reading"])
def test_tutor_scenarios_render_without_touching_project(tmp_path: Path, scenario: str) -> None:
    target = tmp_path / "target"
    target.mkdir()
    stage = tmp_path / "stage with spaces"
    manifest = resolve_manifest(MANIFESTS, "tutor")
    paths = render_manifest(manifest, stage, target, {"scenario": scenario})
    assert Path(".cursor/scenario.md") in paths
    assert (stage / ".cursor/scenario.md").read_bytes() == (
        manifest.path / "scenarios" / scenario / "CLAUDE.md"
    ).read_bytes()
    assert Path("notes/_index.md") not in paths
    for relative in ("skills/SKILL.md", "references/tutor-interaction.md",
                     "agents/tutor-agents.md", "scripts/export-notes.py"):
        assert Path(relative) in paths
    for source in (manifest.path / "scenarios" / scenario / "rules").glob("*.mdc"):
        assert Path(".cursor/rules", source.name) in paths


@pytest.mark.parametrize("scenario", ["web-e2e", "component", "mobile", "visual-regression", "accessibility"])
def test_ui_references_come_from_real_target_and_source(tmp_path: Path, scenario: str) -> None:
    target = tmp_path / "elsewhere" / "target project"
    target.mkdir(parents=True)
    stage = tmp_path / "stage"
    manifest = resolve_manifest(MANIFESTS, "ui-testing")
    paths = render_manifest(manifest, stage, target, {"scenario": scenario})
    assert Path("CLAUDE.ui-testing.md") in paths
    sources = {path.name: path for path in (manifest.path / "rules").glob("*.mdc")}
    sources.update({path.name: path for path in (
        manifest.path / "scenarios" / scenario / "rules"
    ).glob("*.mdc")})
    for filename, source in sources.items():
        assert (stage / ".cursor/rules" / filename).read_text() == source.read_text().replace(
            "{{UI_TESTING_MANIFEST}}", os.path.relpath(manifest.path, target),
        )


def test_generic_substitution_and_symlink_shape(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    source = tmp_path / "generic manifest"
    source.mkdir()
    (source / "CLAUDE.md").write_text("instructions")
    (source / "AGENTS.md").symlink_to("CLAUDE.md")
    (source / "rules").mkdir()
    (source / "rules/ref.mdc").write_text("source {{VIBE_MANIFEST}}")
    (source / "rules/ref.mdc").chmod(0o440)
    (source / "rules/alias.mdc").symlink_to("ref.mdc")
    manifest = ManifestInfo("custom", source, "", False, None)
    stage = tmp_path / "stage"
    paths = render_manifest(manifest, stage, target, {})
    assert Path("AGENTS.md") in paths
    assert (stage / "AGENTS.md").is_symlink()
    assert os.readlink(stage / "AGENTS.md") == "CLAUDE.md"
    assert (stage / ".cursor/rules/ref.mdc").read_text() == f"source {source}"
    assert (stage / ".cursor/rules/ref.mdc").stat().st_mode & 0o777 == 0o440
    assert (stage / ".cursor/rules/alias.mdc").is_symlink()
    assert os.readlink(stage / ".cursor/rules/alias.mdc") == "ref.mdc"
    assert (stage / ".cursor/rules/alias.mdc").read_text() == f"source {source}"
    assert (source / "rules/ref.mdc").read_text() == "source {{VIBE_MANIFEST}}"


def test_render_failure_reports_literal_outputs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    script = source / "init.sh"
    script.write_text("#!/bin/bash\nprintf 'literal stdout\\n'\nprintf 'literal stderr\\n' >&2\nexit 7\n")
    target = tmp_path / "target"
    target.mkdir()
    manifest = ManifestInfo("custom", source, "", True, script)
    with pytest.raises(ValueError) as error:
        render_manifest(manifest, tmp_path / "stage", target, {})
    assert "exit 7" in str(error.value)
    assert "stdout:\nliteral stdout\n" in str(error.value)
    assert "stderr:\nliteral stderr\n" in str(error.value)
    assert not list(target.iterdir())


@pytest.mark.parametrize("location", ["target", "inside-target", "source", "inside-source", "parent"])
def test_overlapping_stage_is_rejected_before_writes(tmp_path: Path, location: str) -> None:
    target = tmp_path / "target"
    target.mkdir()
    source = tmp_path / "source"
    source.mkdir()
    (source / "CLAUDE.md").write_text("instructions")
    manifest = ManifestInfo("custom", source, "", False, None)
    stage = {
        "target": target,
        "inside-target": target / "stage",
        "source": source,
        "inside-source": source / "stage",
        "parent": tmp_path,
    }[location]
    before = snapshot(tmp_path)
    with pytest.raises(ValueError, match="overlaps"):
        render_manifest(manifest, stage, target, {})
    assert snapshot(tmp_path) == before


def test_staging_requires_empty_directory_without_symlinks(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "custom").write_text("keep")
    manifest = resolve_manifest(MANIFESTS, "office")
    with pytest.raises(ValueError, match="empty"):
        render_manifest(manifest, stage, target, {})
    linked = tmp_path / "linked"
    linked.symlink_to(stage, target_is_directory=True)
    with pytest.raises(ValueError, match="symbolic"):
        render_manifest(manifest, linked, target, {})
    with pytest.raises(ValueError, match="symbolic"):
        render_manifest(manifest, linked / "nested stage", target, {})
    assert not (stage / "nested stage").exists()
