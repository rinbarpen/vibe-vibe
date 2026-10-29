"""CLI-first CodeGraph instructions and their portable manifest resources.

These tests never invoke CodeGraph, install it, or create a real project index.
The small CLI repository uses the real manifest with unrelated Skill dependencies
omitted, so scaffold/update behavior stays testable without global tools/network.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

from vibe_tool.discovery import resolve_manifest
from vibe_tool.manifest_update import render_manifest


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests/vibe-coding"
ASSETS = (
    "references/codegraph-workflow.json",
    "references/codegraph-workflow.svg",
    "scripts/render_codegraph_workflow.py",
)
INSTRUCTIONS = (
    "MANIFEST.md", ".cursorrules", "rules/vibe-coding-core.mdc",
    ".claude/agents/explore.md", ".codex/agents/explore.toml",
)


def run(command, *, cwd, env=None):
    return subprocess.run(
        [str(arg) for arg in command], cwd=cwd, text=True, capture_output=True,
        check=False, timeout=60,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})},
    )


def ok(result):
    assert result.returncode == 0, result.stdout + result.stderr


def cli(root, *args):
    return run([sys.executable, "-B", "-m", "vibe_tool", *args], cwd=root,
               env={"VIBE_HOME": str(root), "PYTHONPATH": str(ROOT / "tools/vibe_tool/src")})


def snapshot(root):
    result = {}
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        if name == ".vibe-tool/backups" or name.startswith(".vibe-tool/backups/"):
            continue
        info = path.lstat()
        if path.is_symlink():
            result[name] = ("link", os.readlink(path), info.st_mode)
        elif path.is_file():
            result[name] = ("file", path.read_bytes(), info.st_mode, info.st_mtime_ns)
    return result


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "local sources with spaces"
    source = root / "manifests/vibe-coding"
    source.parent.mkdir(parents=True)
    shutil.copytree(MANIFEST, source, symlinks=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (source / "skills.txt").write_text("# No unrelated dependencies in this fixture.\n")
    (root / "skills").mkdir()
    (root / "mine").mkdir()
    return root


@pytest.mark.parametrize("relative", INSTRUCTIONS)
def test_every_instruction_surface_defines_conditional_cli_first_lookup(relative):
    text = (MANIFEST / relative).read_text()
    for fragment in (".codegraph/", 'codegraph explore "', "before", "skip CodeGraph",
                     "CLI", "rg", "Do not automatically", "insufficient"):
        assert fragment in text, (relative, fragment)
    assert "MCP" in text


def test_explore_agents_have_identical_behavior_and_keep_shell_access():
    claude = (MANIFEST / ".claude/agents/explore.md").read_text()
    codex = (MANIFEST / ".codex/agents/explore.toml").read_text()
    assert claude.split("---", 2)[2].strip() == codex.split('"""')[1].strip()
    assert "Bash" in claude.split("---", 2)[1]
    assert "Do not modify files" in claude
    for name in ("AGENTS.md", "CLAUDE.md"):
        assert (MANIFEST / name).is_symlink()
        assert os.readlink(MANIFEST / name) == "MANIFEST.md"


def test_examples_use_verified_cli_interfaces_and_preserve_test_responsibility():
    text = (MANIFEST / "MANIFEST.md").read_text()
    for command in ('codegraph explore "', 'codegraph node "', 'codegraph node --file ',
                    'codegraph impact "', 'codegraph affected '):
        assert command in text
    assert "actual tests" in text
    assert "not proof" in text
    assert "codegraph init" in (MANIFEST / "README.md").read_text()
    assert "https://github.com/colbymchenry/codegraph" in (MANIFEST / "README.md").read_text()


def render(root, *, check=False, output=None):
    command = [sys.executable, "-B", root / ASSETS[2], "--source", root / ASSETS[0],
               "--output", output or root / ASSETS[1]]
    if check:
        command.append("--check")
    return run(command, cwd=root)


def assert_portable_resources(root):
    for name in ASSETS:
        assert (root / name).read_bytes() == (MANIFEST / name).read_bytes(), name
    for name in ("MANIFEST.md", "README.md"):
        text = (root / name).read_text()
        links = re.findall(r"\]\(([^)#]+codegraph[^)#]*)\)", text)
        assert links
        for link in links:
            if "://" not in link:
                assert (root / link).is_file(), (name, link)
        assert "python3 scripts/render_codegraph_workflow.py" in text
        assert "--check" in text
    before = snapshot(root)
    ok(render(root, check=True))
    assert snapshot(root) == before
    ok(render(root))
    assert (root / ASSETS[1]).read_bytes() == (MANIFEST / ASSETS[1]).read_bytes()
    for name in ("CLAUDE.md", "AGENTS.md"):
        assert os.readlink(root / name) == "MANIFEST.md"
    assert not (root / ".codegraph").exists()


def test_workflow_has_real_query_fallback_validation_and_opt_in_branches():
    source = json.loads((MANIFEST / ASSETS[0]).read_text())
    nodes = {node["id"]: node for node in source["nodes"]}
    assert {"available", "explore", "results", "fallback", "verify", "tests", "opt_in"} <= nodes.keys()
    assert nodes["opt_in"]["kind"] == "human"
    assert "explicit" in nodes["opt_in"]["trigger"]
    edges = {(edge["from"], edge["to"]) for edge in source["edges"]}
    assert {("available", "explore"), ("available", "unavailable"),
            ("unavailable", "fallback"),
            ("results", "fallback"), ("results", "verify"),
            ("fallback", "verify"), ("opt_in", "available"),
            ("opt_in", "fallback"), ("tests", "verify")} <= edges
    svg = ET.parse(MANIFEST / ASSETS[1]).getroot()
    assert svg.tag == "{http://www.w3.org/2000/svg}svg"
    assert svg.get("viewBox")
    for node in nodes.values():
        assert node["label"] in "".join(svg.itertext())
    # Branches sharing a lane/row used to paint labels on exactly the same spot.
    labels = svg.findall("{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}text")
    anchors = [(label.get("x"), label.get("y")) for label in labels]
    assert len(anchors) == len(set(anchors)), "Workflow branch labels overlap"
    # The distributed renderer is the canonical dependency-free implementation.
    assert (MANIFEST / ASSETS[2]).read_bytes() == (ROOT / "scripts/render-manifest-workflow.py").read_bytes()
    ok(render(MANIFEST, check=True))


def test_renderer_is_deterministic_and_check_is_read_only_for_drift_and_missing(repo):
    root = repo / "manifests/vibe-coding"
    output = root / ASSETS[1]
    original = output.read_bytes()
    ok(render(root))
    assert output.read_bytes() == original
    ok(render(root))
    assert output.read_bytes() == original
    for drift in (False, True):
        if drift:
            output.write_text("<svg>drift</svg>\n")
        before = snapshot(root)
        assert render(root, check=True).returncode == (1 if drift else 0)
        assert snapshot(root) == before
    missing = root / "must not exist/nested/graph.svg"
    before = snapshot(root)
    assert render(root, check=True, output=missing).returncode == 1
    assert snapshot(root) == before
    assert not missing.parent.parent.exists()


@pytest.mark.parametrize("operation", ["init", "add"])
def test_cli_installs_resources_with_working_links_and_preserves_overrides(repo, tmp_path, operation):
    target = tmp_path / "project with spaces"
    if operation == "add":
        target.mkdir()
    args = ["init", "vibe-coding", target] if operation == "init" else ["add", "manifest", "vibe-coding", target]
    ok(cli(repo, *args, "--provider=git"))
    assert_portable_resources(target)
    renderer = target / ASSETS[2]
    renderer.write_text("# user renderer\n")
    ok(cli(repo, *args, "--provider=git"))
    assert renderer.read_text() == "# user renderer\n"
    ok(cli(repo, *args, "--provider=git", "--force"))
    assert_portable_resources(target)


@pytest.mark.parametrize("operation", ["init", "add"])
@pytest.mark.parametrize("existing", [False, True])
def test_cli_dry_run_does_not_write_assets_or_create_index(repo, tmp_path, operation, existing):
    target = tmp_path / "dry project with spaces"
    if existing:
        target.mkdir()
        (target / "user.txt").write_text("preserve\n")
    before = snapshot(target)
    args = ["init", "vibe-coding", target] if operation == "init" else ["add", "manifest", "vibe-coding", target]
    result = cli(repo, *args, "--provider=git", "--dry-run")
    if operation == "add" and not existing:
        # Preserve add's existing contract: only init creates a new project.
        assert result.returncode != 0
        assert "target directory does not exist" in result.stdout + result.stderr
    else:
        ok(result)
        for name in ASSETS:
            assert name in result.stdout
    assert target.exists() == existing
    assert snapshot(target) == before


def test_update_distributes_exact_assets_and_restores_modified_and_added_resources(repo, tmp_path):
    target = tmp_path / "update project with spaces"
    ok(cli(repo, "init", "vibe-coding", target, "--provider=git"))
    (target / "MANIFEST.md").write_text("# Old instructions\n")
    (target / ASSETS[2]).write_text("# Old renderer\n")
    # Legacy project: these resources were not distributed before this feature.
    for relative in ASSETS[:2]:
        (target / relative).unlink()
    for name in ("README.md", "VERSION", "CHANGELOG.md", "business.txt"):
        (target / name).write_text(f"user content: {name}\n")
    local_reference = target / "references/local.json"
    local_reference.write_text('{"keep": true}\n')
    before = snapshot(target)
    ok(cli(repo, "update", "manifest", "vibe-coding", target, "--dry-run"))
    assert snapshot(target) == before
    assert not list((target / ".vibe-tool/backups").glob("*/restore.py"))
    result = cli(repo, "update", "manifest", "vibe-coding", target)
    ok(result)
    assert (target / "MANIFEST.md").read_bytes() == (MANIFEST / "MANIFEST.md").read_bytes()
    for name in ASSETS:
        assert (target / name).read_bytes() == (MANIFEST / name).read_bytes()
    ok(render(target, check=True))
    for name in ("README.md", "VERSION", "CHANGELOG.md", "business.txt", "references/local.json"):
        assert snapshot(target)[name] == before[name]
    assert not (target / ".codegraph").exists()
    scripts = list((target / ".vibe-tool/backups").glob("*/restore.py"))
    assert len(scripts) == 1
    assert str(scripts[0]) in result.stdout
    updated = snapshot(target)
    ok(cli(repo, "update", "manifest", "vibe-coding", target))
    assert snapshot(target) == updated
    assert len(list((target / ".vibe-tool/backups").glob("*/restore.py"))) == 1
    ok(run([sys.executable, "-I", "-B", scripts[0]], cwd=target))
    assert snapshot(target) == before


def test_update_allowlist_does_not_expand_to_unrelated_references_or_scripts(repo, tmp_path):
    source = repo / "manifests/vibe-coding"
    (source / "references/unrelated.md").write_text("not distributed\n")
    (source / "scripts/unrelated.py").write_text("not distributed\n")
    target = tmp_path / "target"
    target.mkdir()
    stage = tmp_path / "stage"
    paths = render_manifest(resolve_manifest(repo / "manifests", "vibe-coding"), stage, target, {"provider": "git"})
    assert set(map(Path, ASSETS)) <= set(paths)
    assert Path("references/unrelated.md") not in paths
    assert Path("scripts/unrelated.py") not in paths
    assert not (target / ".codegraph").exists()


@pytest.mark.parametrize("indexed", [False, True])
def test_scaffold_and_update_never_invoke_codegraph_or_touch_existing_state(repo, tmp_path, monkeypatch, indexed):
    target = tmp_path / "existing project"
    target.mkdir()
    protected = {
        ".mcp.json": '{"mcpServers": {"keep": {}}}\n',
        ".codex/config.toml": '# user config\n',
        ".claude/settings.json": '{"user": true}\n',
    }
    if indexed:
        # Only a sentinel, not a real index; no CodeGraph process is launched.
        protected[".codegraph/sentinel"] = "existing index owned by user\n"
    for name, value in protected.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    marker = tmp_path / "codegraph-was-invoked"
    binary = tmp_path / "bin/codegraph"
    binary.parent.mkdir()
    binary.write_text(f'#!/bin/sh\nprintf called > "{marker}"\nexit 99\n')
    binary.chmod(0o755)
    monkeypatch.setenv("PATH", str(binary.parent) + os.pathsep + os.environ["PATH"])
    ok(cli(repo, "add", "manifest", "vibe-coding", target, "--provider=git"))
    ok(cli(repo, "init", "vibe-coding", target, "--provider=git", "--force"))
    (target / "MANIFEST.md").write_text("# Old instructions\n")
    ok(cli(repo, "update", "manifest", "vibe-coding", target))
    for name, value in protected.items():
        assert (target / name).read_text() == value
    assert (target / ".codegraph").exists() == indexed
    assert not marker.exists()
