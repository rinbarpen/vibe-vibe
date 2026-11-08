"""Usability/interaction contracts and their portable install/update resources.

Exercise real CLI copies with unrelated Skill dependencies omitted. These are
manifest delivery tests, not a claim that a product's UI has been user-tested.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

import pytest

from test_codegraph_manifest import MANIFEST, cli, ok, repo, run, snapshot
from vibe_tool.discovery import resolve_manifest
from vibe_tool.manifest_update import render_manifest


ASSETS = (
    "references/ui-usability.md",
    "references/ui-usability-workflow.json",
    "references/ui-usability-workflow.svg",
)
RENDERER = "scripts/render_codegraph_workflow.py"
COPY_RESTRAINT = (
    "Avoid unnecessary secondary labels and descriptions. "
    "Let the layout do the explaining."
)


def render(root, *, check=False):
    command = [sys.executable, "-B", root / RENDERER, "--source", root / ASSETS[1],
               "--output", root / ASSETS[2]]
    return run(command + (["--check"] if check else []), cwd=root)


def assert_resources(root):
    for relative in ASSETS:
        assert (root / relative).read_bytes() == (MANIFEST / relative).read_bytes()
    for relative in ("MANIFEST.md", "README.md", ASSETS[0]):
        text = (root / relative).read_text()
        links = re.findall(r"\]\(([^)#]+)\)", text)
        ui_links = [link for link in links if "ui-usability" in link]
        assert ui_links, relative
        for link in ui_links:
            assert (root / relative).parent.joinpath(link).is_file(), (relative, link)
        assert "--check" in text
    for relative in ("MANIFEST.md", "AGENTS.md", "CLAUDE.md",
                     ".cursor/rules/vibe-coding-ui-design.mdc", ASSETS[0]):
        assert COPY_RESTRAINT in (root / relative).read_text(), relative
    assert "redundant secondary" in (root / ".cursor/commands/frontend-check/COMMAND.md").read_text()
    before = snapshot(root)
    ok(render(root, check=True))
    assert snapshot(root) == before
    ok(render(root))
    assert (root / ASSETS[2]).read_bytes() == (MANIFEST / ASSETS[2]).read_bytes()
    assert (root / "AGENTS.md").resolve() == root / "MANIFEST.md"
    assert (root / "CLAUDE.md").resolve() == root / "MANIFEST.md"


def test_contract_modes_and_local_e2e_policy():
    command = (MANIFEST / "commands/frontend-check/COMMAND.md").read_text()
    for mode in ("usability", "interaction", "accessibility", "performance", "bundle", "visual", "all"):
        assert f"| `{mode}` |" in command
    assert "all six" in command.lower()
    for phrase in ("NOT RUN", "BLOCKED", "baseline", "persistence", "trace", "getByRole"):
        assert phrase in command
    ui_rules = (MANIFEST / "rules/vibe-coding-ui-design.mdc").read_text()
    assert "dart,wxml,wxss" in ui_rules
    rules = (MANIFEST / "rules/vibe-coding-testing.mdc").read_text()
    assert "Run E2E tests on staging, not locally" not in rules
    assert "local" in rules and "staging" in rules
    contract = (MANIFEST / ASSETS[0]).read_text()
    for heading in ("信息优先级", "设置", "任务验收", "人工", "回退", "证据"):
        assert heading in contract
    assert "不是用户研究" in contract


@pytest.mark.parametrize("relative", ["MANIFEST.md", "rules/vibe-coding-ui-design.mdc", ASSETS[0]])
def test_redundant_secondary_copy_restraint_is_explicit(relative):
    assert COPY_RESTRAINT in (MANIFEST / relative).read_text()


def test_redundant_copy_audit_keeps_necessary_information():
    rules = (MANIFEST / "rules/vibe-coding-ui-design.mdc").read_text()
    for necessary in ("表单标签", "无障碍名称", "错误", "风险", "单位", "必要帮助"):
        assert necessary in rules
    command = (MANIFEST / "commands/frontend-check/COMMAND.md").read_text()
    assert "redundant secondary" in command
    assert "essential help" in command


def test_workflow_contract_has_rework_wait_decision_and_rollback():
    workflow = json.loads((MANIFEST / ASSETS[1]).read_text())
    nodes = {node["id"]: node for node in workflow["nodes"]}
    assert {"baseline", "design", "implement", "interaction", "usability", "decision", "wait", "rollback", "done"} <= nodes.keys()
    assert nodes["decision"]["kind"] == "human"
    assert nodes["interaction"]["kind"] == nodes["usability"]["kind"] == "check"
    edges = {(edge["from"], edge["to"]) for edge in workflow["edges"]}
    assert {("interaction", "implement"), ("usability", "design"),
            ("decision", "wait"), ("wait", "decision"),
            ("decision", "baseline"), ("decision", "rollback"),
            ("rollback", "restore"), ("restore", "rollback"),
            ("restore", "done")} <= edges
    svg = ET.parse(MANIFEST / ASSETS[2]).getroot()
    assert svg.tag == "{http://www.w3.org/2000/svg}svg"
    for node in nodes.values():
        assert node["label"] in "".join(svg.itertext())
    ok(render(MANIFEST, check=True))


@pytest.mark.parametrize("operation", ["init", "add"])
def test_install_and_dry_run_portable_ui_resources(repo, tmp_path, operation):
    target = tmp_path / "UI project with spaces"
    if operation == "add":
        target.mkdir()
    args = ["init", "vibe-coding", target] if operation == "init" else ["add", "manifest", "vibe-coding", target]
    before = snapshot(target)
    ok(cli(repo, *args, "--provider=git", "--scenario=frontend", "--dry-run"))
    assert snapshot(target) == before
    assert target.exists() == (operation == "add")
    ok(cli(repo, *args, "--provider=git", "--scenario=frontend"))
    assert_resources(target)
    assert "usability" in (target / ".cursor/commands/frontend-check/COMMAND.md").read_text()
    assert "信息优先级" in (target / ".cursor/rules/vibe-coding-ui-design.mdc").read_text()
    assert (target / ".cursor/rules/vibe-coding-frontend-scenario.mdc").is_file()
    custom = target / ASSETS[0]
    custom.write_text("# Local usability notes\n")
    ok(cli(repo, *args, "--provider=git", "--scenario=frontend"))
    assert custom.read_text() == "# Local usability notes\n"
    ok(cli(repo, *args, "--provider=git", "--scenario=frontend", "--force"))
    assert_resources(target)


def test_update_adds_ui_resources_preserves_data_and_rollback(repo, tmp_path):
    target = tmp_path / "legacy UI project"
    ok(cli(repo, "init", "vibe-coding", target, "--provider=git", "--scenario=frontend"))
    (target / ASSETS[0]).write_text("# Prior local rule\n")
    for relative in ASSETS[1:]:
        (target / relative).unlink()
    for name in ("README.md", "VERSION", "CHANGELOG.md", "business.txt", "references/local.md"):
        (target / name).write_text(f"Preserve: {name}\n")
    before = snapshot(target)
    ok(cli(repo, "update", "manifest", "vibe-coding", target, "--dry-run"))
    assert snapshot(target) == before
    assert not (target / ".vibe-tool/backups").exists()
    result = cli(repo, "update", "manifest", "vibe-coding", target)
    ok(result)
    for relative in ASSETS:
        assert (target / relative).read_bytes() == (MANIFEST / relative).read_bytes()
    ok(render(target, check=True))
    for name in ("README.md", "VERSION", "CHANGELOG.md", "business.txt", "references/local.md"):
        assert snapshot(target)[name] == before[name]
    updated = snapshot(target)
    ok(cli(repo, "update", "manifest", "vibe-coding", target))
    assert snapshot(target) == updated
    restores = list((target / ".vibe-tool/backups").glob("*/restore.py"))
    assert len(restores) == 1
    assert str(restores[0]) in result.stdout
    ok(run([sys.executable, "-I", "-B", restores[0]], cwd=target))
    assert snapshot(target) == before


@pytest.mark.parametrize("failure", ["missing", "source-drift", "svg-drift", "invalid-reference"])
def test_ui_drift_check_failures_are_read_only(repo, failure):
    root = repo / "manifests/vibe-coding"
    if failure == "missing":
        (root / ASSETS[2]).unlink()
    elif failure == "svg-drift":
        (root / ASSETS[2]).write_text("<svg/>\n")
    else:
        path = root / ASSETS[1]
        source = json.loads(path.read_text())
        if failure == "source-drift":
            source["title"] += " Updated"
        else:
            source["edges"][0]["to"] = "missing_node"
        path.write_text(json.dumps(source))
    before = snapshot(root)
    result = render(root, check=True)
    assert result.returncode == (2 if failure == "invalid-reference" else 1)
    assert snapshot(root) == before


def test_update_keeps_ui_asset_allowlist_narrow(repo, tmp_path):
    source = repo / "manifests/vibe-coding"
    (source / "references/unrelated-ui.md").write_text("not distributed\n")
    target = tmp_path / "target"
    target.mkdir()
    paths = render_manifest(resolve_manifest(repo / "manifests", "vibe-coding"),
                            tmp_path / "stage", target, {"provider": "git"})
    assert set(map(Path, ASSETS)) <= set(paths)
    assert Path("references/unrelated-ui.md") not in paths
