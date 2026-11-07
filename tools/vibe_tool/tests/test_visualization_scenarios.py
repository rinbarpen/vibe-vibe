"""Scene-specific visualization sources stay resolvable and portable after install."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from vibe_tool.discovery import discover_skills, resolve_skill
from vibe_tool.project_update import update_skill
from vibe_tool.skill import _is_excluded, add_skill


ROOT = Path(__file__).resolve().parents[3]
OMNIDRAW = ROOT / "mine/omnidraw"
GUIDE = OMNIDRAW / "references/visualization-scenarios.md"
SOURCES = {
    "omnidraw": "mine/omnidraw",
    "visual-explainer/plugins/visual-explainer": "skills/visual-explainer/plugins/visual-explainer",
    "claude-scientific-skills/skills/matplotlib": "skills/claude-scientific-skills/skills/matplotlib",
    "claude-scientific-skills/skills/seaborn": "skills/claude-scientific-skills/skills/seaborn",
    "claude-scientific-skills/skills/scientific-visualization": "skills/claude-scientific-skills/skills/scientific-visualization",
    "ai-design-components/skills/creating-dashboards": "skills/ai-design-components/skills/creating-dashboards",
    "claude-scientific-skills/skills/networkx": "skills/claude-scientific-skills/skills/networkx",
    "CCFA-Skills/ccf-visual-composer": "skills/CCFA-Skills/ccf-visual-composer",
    "claude-scientific-skills/skills/geopandas": "skills/claude-scientific-skills/skills/geopandas",
}


def install_queries():
    return [shlex.split(line)[3] for line in GUIDE.read_text().splitlines()
            if line.startswith("vibe add skill ")]


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


@pytest.fixture(scope="module")
def catalog():
    return discover_skills(ROOT / "skills", ROOT / "mine")


@pytest.fixture(scope="module")
def repository(tmp_path_factory):
    root = tmp_path_factory.mktemp("visualization sources")
    (root / "manifests").mkdir()
    for relative in SOURCES.values():
        shutil.copytree(ROOT / relative, root / relative,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules"))
    return root


def test_all_advertised_install_commands_resolve_to_actual_sources(catalog, monkeypatch):
    queries = install_queries()
    assert len(queries) == len(set(queries))
    assert set(queries) == set(SOURCES)
    monkeypatch.setattr("vibe_tool.discovery.discover_skills", lambda *roots: catalog)
    for query in queries:
        assert resolve_skill((ROOT / "skills", ROOT / "mine"), query).source_path == ROOT / SOURCES[query]


@pytest.mark.parametrize("query", list(SOURCES))
def test_optional_routes_install_complete_payload_with_recorded_identity(repository, tmp_path, query):
    target = tmp_path / "existing target"
    target.mkdir()
    (target / "user-data.csv").write_text("value\n5\n")
    result = subprocess.run(
        [sys.executable, "-B", "-m", "vibe_tool", "add", "skill", query, str(target)],
        cwd=repository, capture_output=True, text=True, timeout=30,
        env={**os.environ, "VIBE_HOME": str(repository), "PYTHONDONTWRITEBYTECODE": "1",
             "PYTHONPATH": str(ROOT / "tools/vibe_tool/src")},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    info = resolve_skill((repository / "skills", repository / "mine"), query)
    installed = target / ".agents/skills" / info.name
    for source in info.source_path.rglob("*"):
        relative = source.relative_to(info.source_path)
        if source.is_file() and not any(_is_excluded(Path(p)) for p in relative.parts):
            assert (installed / relative).read_bytes() == source.read_bytes(), relative
    record = json.loads((target / ".vibe-tool/installations.json").read_text())
    assert record["skills"][info.name]["source"] == SOURCES[query]
    assert (target / "user-data.csv").read_text() == "value\n5\n"


def test_router_install_does_not_install_every_optional_capability(repository, tmp_path):
    target = tmp_path / "project"
    assert add_skill((repository / "skills", repository / "mine"), "omnidraw", target) == 0
    assert {p.name for p in (target / ".agents/skills").iterdir()} == {"omnidraw"}
    installed = target / ".agents/skills/omnidraw"
    for relative in ("references/visualization-scenarios.md", "references/routing-matrix.md",
                     "assets/workflow.mmd", "assets/workflow.svg", "mermaid/SKILL.md", "matplotlib/SKILL.md"):
        assert (installed / relative).read_bytes() == (OMNIDRAW / relative).read_bytes()
    # The installed guide remains self-contained rather than linking out of the
    # project to the aggregate repository's optional source checkout.
    links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", (installed / "references/visualization-scenarios.md").read_text())
    assert all(link.startswith(("https://", "http://", "#")) or
               (installed / "references" / link).exists() for link in links)


def test_router_dry_run_and_update_rollback_preserve_user_work(repository, tmp_path):
    roots = (repository / "skills", repository / "mine")
    target = tmp_path / "project"
    target.mkdir()
    (target / "user-data.csv").write_text("value\n5\n")
    before = snapshot(target)
    assert add_skill(roots, "omnidraw", target, dry_run=True) == 0
    assert snapshot(target) == before
    assert add_skill(roots, "omnidraw", target) == 0
    installed = target / ".agents/skills/omnidraw"
    (installed / "references/visualization-scenarios.md").write_text("User route preferences.\n")
    (installed / "assets/workflow.svg").write_text("User diagram.\n")
    before = snapshot(installed)
    assert update_skill(repository, "omnidraw", target, dry_run=True) == 0
    assert snapshot(installed) == before
    assert update_skill(repository, "omnidraw", target) == 0
    assert (installed / "references/visualization-scenarios.md").read_bytes() == GUIDE.read_bytes()
    restores = list((target / ".vibe-tool/backups").glob("*/restore.py"))
    assert len(restores) == 1
    result = subprocess.run([sys.executable, "-B", str(restores[0])], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert snapshot(installed) == before
    assert (target / "user-data.csv").read_text() == "value\n5\n"


def test_workflow_has_distinct_routes_and_source_labels_reach_the_svg():
    source = (OMNIDRAW / "assets/workflow.mmd").read_text()
    targets = set(re.findall(r"B -->\|[^\n]+\| ([A-Z])\[", source))
    assert targets == {"C", "D", "E", "I", "J", "K"}
    svg = ET.parse(OMNIDRAW / "assets/workflow.svg").getroot()
    assert svg.tag == "{http://www.w3.org/2000/svg}svg"
    rendered = re.sub(r"\s+", "", "".join(svg.itertext()))
    for label in re.findall(r'\["([^"]+)"\]', source):
        for line in label.split("<br/>"):
            assert re.sub(r"\s+", "", line) in rendered, line


@pytest.mark.skipif(not os.environ.get("OMNIDRAW_MERMAID_RENDERER"), reason="Optional canonical renderer not configured")
def test_workflow_regenerates_without_changing_checked_in_assets(tmp_path):
    source = OMNIDRAW / "assets/workflow.mmd"
    svg = OMNIDRAW / "assets/workflow.svg"
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in (source, svg)}
    output = tmp_path / "workflow.svg"
    result = subprocess.run(
        ["node", os.environ["OMNIDRAW_MERMAID_RENDERER"], "--input", str(source),
         "--output", str(output), "--format", "svg", "--theme", "github-light",
         "--font", "Noto Sans CJK SC", "--bg", "#ffffff", "--fg", "#173B47"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert output.read_bytes() == svg.read_bytes()
    assert {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in before} == before
