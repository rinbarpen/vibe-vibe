"""The unified manifest installs the pinned, published Matt Pocock skill bundle."""

from __future__ import annotations

import configparser
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from vibe_tool import discovery
from vibe_tool.update import build_update_command, discover_submodule_paths

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests" / "vibe-coding"
SUBMODULE = ROOT / "skills" / "mattpocock-skills-zh-CN"
GROUPS = {
    "engineering": (
        "ask-matt", "code-review", "codebase-design", "diagnosing-bugs",
        "domain-modeling", "grill-with-docs", "implement", "implement-spec",
        "improve-codebase-architecture", "pr", "prototype", "research", "retro",
        "setup-matt-pocock-skills", "tdd", "to-spec", "to-tickets", "triage",
        "wayfinder", "wizard",
    ),
    "productivity": (
        "grill-me", "grilling", "handoff", "teach", "to-questionnaire",
        "wait-what", "writing-for-agents",
    ),
    "misc": (
        "git-guardrails-claude-code", "migrate-to-shoehorn", "scaffold-exercises",
        "setup-pre-commit",
    ),
}
FORMAL = {name for names in GROUPS.values() for name in names}
EXISTING = {
    "domain-dispatcher", "language-advisor", "lifecycle-orchestrator", "vibe-coding",
    "anthropics-skills-canvas-design", "wxa-skills-generate", "wxa-skills-validate",
    "wxa-skills-eval",
}


def required_skills() -> list[str]:
    return discovery.resolve_manifest(ROOT / "manifests", "vibe-coding").required_skills


def test_formal_bundle_is_complete_and_excludes_maintenance_and_beta() -> None:
    for group, names in GROUPS.items():
        assert {p.parent.name for p in (SUBMODULE / "skills" / group).glob("*/SKILL.md")} == set(names)
    required = required_skills()
    assert len(FORMAL) == 31
    assert len(required) == len(set(required)) == 39
    assert set(required) == FORMAL | EXISTING


def test_submodule_tracks_main_and_participates_in_managed_updates() -> None:
    config = configparser.ConfigParser()
    config.read(ROOT / ".gitmodules")
    module = config['submodule "skills/mattpocock-skills-zh-CN"']
    assert module["path"] == "skills/mattpocock-skills-zh-CN"
    assert module["url"] == "https://github.com/vinvcn/mattpocock-skills-zh-CN.git"
    assert module["branch"] == "main"
    assert module["path"] in build_update_command(discover_submodule_paths(ROOT))
    tracked = subprocess.check_output(
        ["git", "ls-files", "--stage", module["path"]], cwd=ROOT, text=True,
    ).split()
    assert tracked[0] == "160000"
    assert tracked[1] == subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=SUBMODULE, text=True,
    ).strip()


def test_both_indexes_document_all_formal_skills() -> None:
    for filename in ("ANNOTATIONS.md", "ANNOTATIONS_EN.md"):
        index = (ROOT / "skills" / filename).read_text(encoding="utf-8")
        for group, names in GROUPS.items():
            for name in names:
                assert f"`skills/mattpocock-skills-zh-CN/skills/{group}/{name}`" in index


@pytest.fixture(scope="module")
def catalog():
    # Scan the real aggregate once; resolution itself is checked against this
    # complete catalog, including skills outside the manifest and name collisions.
    return discovery.discover_skills(ROOT / "skills", ROOT / "mine", MANIFEST / "skills")


def test_every_dependency_resolves_to_its_intended_source(catalog, monkeypatch) -> None:
    monkeypatch.setattr(discovery, "discover_skills", lambda *roots: catalog)
    for name in required_skills():
        skill = discovery.resolve_skill((ROOT / "skills", ROOT / "mine", MANIFEST / "skills"), name)
        if name in FORMAL:
            assert skill.source_path == next(
                SUBMODULE / "skills" / group / name
                for group, names in GROUPS.items() if name in names
            )
        elif name == "anthropics-skills-canvas-design":
            assert skill.source_path == ROOT / "skills" / "anthropics" / "skills" / "canvas-design"
        elif name.startswith("wxa-skills-"):
            assert skill.source_path == ROOT / "skills" / "ai-mode-skills" / name
        else:
            assert skill.source_path == MANIFEST / "skills" / name


@pytest.fixture(scope="module")
def cli_repo(tmp_path_factory, catalog):
    """Use real source resources in a small repo for uncached CLI end-to-end tests."""
    root = tmp_path_factory.mktemp("matt-cli-repo")
    (root / "manifests").mkdir()
    (root / "manifests" / "vibe-coding").symlink_to(MANIFEST, target_is_directory=True)
    wanted = set(required_skills())
    for skill in catalog:
        if skill.name in wanted and skill.source_path.is_relative_to(ROOT / "skills"):
            shutil.copytree(skill.source_path, root / "skills" / skill.id_path)
    # Preserve the aggregate's canvas-design collision without copying unrelated
    # bundles. This exercises the real path-disambiguation logic in each process.
    collision = root / "skills" / "other" / "canvas-design"
    collision.mkdir(parents=True)
    (collision / "SKILL.md").write_text("---\nname: canvas-design\n---\n", encoding="utf-8")
    return root


def cli(root: Path, *args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", "-m", "vibe_tool", *(str(a) for a in args)],
        cwd=root, capture_output=True, text=True, check=False,
        env={**os.environ, "VIBE_HOME": str(root), "PYTHONDONTWRITEBYTECODE": "1",
             "PYTHONPATH": str(ROOT / "tools" / "vibe_tool" / "src")},
    )


def assert_installed(target: Path, catalog) -> None:
    required = set(required_skills())
    installed = target / ".agents" / "skills"
    assert {p.name for p in installed.iterdir()} == required
    for skill in catalog:
        if skill.name not in required:
            continue
        # Check all bundled resources, not just the entrypoint: templates,
        # references, scripts and per-agent configuration must survive copying.
        for source in skill.source_path.rglob("*"):
            relative = source.relative_to(skill.source_path)
            if source.is_file() and not any(part.startswith(".") for part in relative.parts):
                dest = installed / skill.name / relative
                assert dest.read_bytes() == source.read_bytes(), str(dest)
    assert not (target / "docs" / "agents" / "issue-tracker.md").exists()


@pytest.mark.parametrize("operation", ["init", "add"])
def test_cli_installs_all_resources_and_preserves_existing(cli_repo, catalog, tmp_path, operation) -> None:
    target = tmp_path / "project"
    if operation == "init":
        args = ("init", "vibe-coding", target, "--provider=git")
    else:
        target.mkdir()
        (target / "user.txt").write_text("keep me\n")
        args = ("add", "manifest", "vibe-coding", target, "--provider=git")
    result = cli(cli_repo, *args)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "WARN" not in result.stdout
    assert_installed(target, catalog)
    if operation == "add":
        assert (target / "user.txt").read_text() == "keep me\n"
    custom = target / ".agents" / "skills" / "grilling" / "SKILL.md"
    custom.write_text("# user customized skill\n")
    repeated = cli(cli_repo, *args)
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr
    assert "SKIP  grilling" in repeated.stdout
    assert custom.read_text() == "# user customized skill\n"


@pytest.mark.parametrize("operation", ["init", "add"])
def test_cli_dry_run_reports_all_dependencies_without_writing(cli_repo, tmp_path, operation) -> None:
    target = tmp_path / "project"
    if operation == "init":
        args = ("init", "vibe-coding", target, "--provider=git", "--dry-run")
    else:
        target.mkdir()
        args = ("add", "manifest", "vibe-coding", target, "--provider=git", "--dry-run")
    result = cli(cli_repo, *args)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "WARN" not in result.stdout
    for name in required_skills():
        assert f"WILL  {name}\n" in result.stdout
    if operation == "init":
        assert not target.exists()
    else:
        assert list(target.iterdir()) == []
