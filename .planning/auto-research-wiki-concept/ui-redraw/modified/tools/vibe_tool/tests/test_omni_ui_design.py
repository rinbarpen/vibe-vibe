"""UI constraints travel with the Omni packages and precede format production."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

import pytest

from vibe_tool.skill import add_skill


ROOT = Path(__file__).resolve().parents[3]
NAMES = ("omnidraw", "omnisheet")


@pytest.mark.parametrize("name", NAMES)
def test_ui_guide_is_available_without_aggregate_repo_or_design_dependencies(tmp_path, name):
    repo, target = tmp_path / "source", tmp_path / "project"
    (repo / "manifests").mkdir(parents=True)
    (repo / "skills").mkdir()
    shutil.copytree(ROOT / "mine" / name, repo / "mine" / name,
                    ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".git"))
    assert add_skill((repo / "skills", repo / "mine"), name, target) == 0
    installed = target / ".agents/skills" / name
    assert {p.name for p in installed.parent.iterdir()} == {name}
    expected = (repo / "mine" / name / "references/ui-design.md").read_bytes()
    shutil.rmtree(repo)

    entry = (installed / "SKILL.md").read_text(encoding="utf-8")
    assert "](references/ui-design.md)" in entry
    assert (installed / "references/ui-design.md").read_bytes() == expected
    # Every actionable link in the shipped guide resolves in the isolated install.
    guide = installed / "references/ui-design.md"
    for link in re.findall(r"\]\(([^)]+)\)", guide.read_text(encoding="utf-8")):
        if not link.startswith(("https://", "http://", "#")):
            assert (guide.parent / link).is_file(), link


def graph_edges(source):
    return re.findall(
        r"^\s*([A-Z])(?:\[.*?\]|\{.*?\})?\s*-->(?:\|[^\n]*?\|)?\s*([A-Z])",
        source, re.M,
    )


def reachable(edges, start, *, omit=None):
    visited, pending = set(), [start]
    while pending:
        node = pending.pop()
        if node in visited or node == omit:
            continue
        visited.add(node)
        pending += [right for left, right in edges if left == node]
    return visited


@pytest.mark.parametrize("name,makers", [("omnidraw", {"C", "D", "E", "I", "J", "K"}),
                                         ("omnisheet", {"E", "F"})])
def test_design_preflight_precedes_production_and_appears_in_actual_svg(name, makers):
    base = ROOT / "mine" / name
    source = (base / "assets/workflow.mmd").read_text(encoding="utf-8")
    edges = graph_edges(source)
    assert makers <= reachable(edges, "A")
    assert not makers & reachable(edges, "A", omit="P")
    svg = ET.parse(base / "assets/workflow.svg").getroot()
    rendered = re.sub(r"\s+", "", "".join(svg.itertext()))
    for label in re.findall(r'\["([^"]+)"\]', source):
        for line in label.split("<br/>"):
            assert re.sub(r"\s+", "", line) in rendered, line


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.skipif(not os.environ.get("OMNIDRAW_MERMAID_RENDERER"),
                    reason="Canonical renderer not configured")
def test_both_updated_workflows_regenerate_read_only(tmp_path, name):
    base = ROOT / "mine" / name
    paths = [base / "assets/workflow.mmd", base / "assets/workflow.svg"]
    before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths}
    output = tmp_path / f"{name}.svg"
    render_input = paths[0]
    source = paths[0].read_text(encoding="utf-8")
    if source.startswith("---\n"):
        # Pretty's parser takes the graph body; its rendering options are passed
        # below. Keep the full standard-Mermaid source untouched for other hosts.
        render_input = tmp_path / f"{name}.mmd"
        render_input.write_text(source.split("---", 2)[2].lstrip(), encoding="utf-8")
    result = subprocess.run([
        "node", os.environ["OMNIDRAW_MERMAID_RENDERER"],
        "--input", str(render_input), "--output", str(output), "--format", "svg",
        "--theme", "github-light", "--font", "Noto Sans CJK SC",
        "--bg", "#ffffff", "--fg", "#173B47",
    ], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert output.read_bytes() == before[paths[1]][0]
    assert {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in paths} == before
