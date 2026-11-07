"""The visualization integration installs the complete canonical upstream payload."""

from __future__ import annotations

import configparser
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from vibe_tool.discovery import discover_skills, resolve_skill
from vibe_tool.project_update import update_skill
from vibe_tool.skill import _is_excluded, add_skill
from vibe_tool.update import build_update_command, discover_submodule_paths


ROOT = Path(__file__).resolve().parents[3]
UPSTREAM = ROOT / "skills/visual-explainer"
PAYLOAD = UPSTREAM / "plugins/visual-explainer"
REQUIRED = (
    "SKILL.md", "references/style-guide.md", "references/kit.md",
    "references/diagrams.md", "references/motion.md", "references/machines.md",
    "templates/page.html", "templates/slide-deck.html",
    "commands/generate-web-diagram.md", "commands/diff-review.md",
    "kit/render.mjs", "kit/kit.css", "kit/kit.js", "kit/vendor/pele.mjs",
    "kit/vendor/PELE-LICENSE", "plan/render.mjs", "mcp/server.mjs",
    "pptx/export.mjs", "video/render.mjs",
)
PAGE = '''<!DOCTYPE html>
<html lang="en" data-register="blueprint">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Visualization integration fixture</title>
<link rel="stylesheet" href="kit.css" data-ve-kit></head>
<body><main><h1>The installed renderer keeps the diagram portable</h1>
<figure><svg viewBox="0 0 600 160" role="img" aria-label="A source is rendered to HTML">
<rect x="20" y="40" width="180" height="80" fill="none" stroke="currentColor"/>
<text x="40" y="85">Source</text><path d="M200 80 H380" stroke="currentColor"/>
<text x="240" y="65">renders</text>
<rect x="380" y="40" width="180" height="80" fill="none" stroke="currentColor"/>
<text x="410" y="85">HTML page</text></svg>
<figcaption>The copied skill renders a source into an HTML page.</figcaption>
</figure></main></body></html>'''


def snapshot(root: Path) -> dict:
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def repository(tmp_path):
    root = tmp_path / "source repository"
    (root / "manifests").mkdir(parents=True)
    shutil.copytree(PAYLOAD, root / "skills/visual-explainer/plugins/visual-explainer")
    return root


def test_source_is_registered_on_main_and_in_managed_updates():
    config = configparser.ConfigParser()
    config.read(ROOT / ".gitmodules")
    source = config['submodule "skills/visual-explainer"']
    assert source["url"] == "https://github.com/nicobailon/visual-explainer.git"
    assert source["path"] == "skills/visual-explainer"
    assert source["branch"] == "main"
    assert source["path"] in build_update_command(discover_submodule_paths(ROOT))
    assert (UPSTREAM / "LICENSE").is_file()


def test_discovery_exposes_only_the_canonical_payload():
    catalog = discover_skills(ROOT / "skills", ROOT / "mine")
    candidates = [s for s in catalog if s.source_path.is_relative_to(UPSTREAM)]
    assert [(s.name, s.source_path, s.id_path) for s in candidates] == [
        ("visual-explainer", PAYLOAD, "visual-explainer/plugins/visual-explainer")
    ]


def test_both_readmes_and_indexes_document_the_canonical_source():
    for name in ("README.md", "README_EN.md", "skills/ANNOTATIONS.md", "skills/ANNOTATIONS_EN.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "skills/visual-explainer/plugins/visual-explainer" in text
        assert "vibe add skill visual-explainer" in text
        assert "Node.js" in text


def test_cli_install_preserves_all_payload_resources(repository, tmp_path):
    target = tmp_path / "existing project"
    target.mkdir()
    (target / "user.md").write_text("Keep user work.\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-B", "-m", "vibe_tool", "add", "skill", "visual-explainer", str(target)],
        cwd=repository, capture_output=True, text=True,
        env={**os.environ, "VIBE_HOME": str(repository), "PYTHONDONTWRITEBYTECODE": "1",
             "PYTHONPATH": str(ROOT / "tools/vibe_tool/src")}, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    installed = target / ".agents/skills/visual-explainer"
    for name in REQUIRED:
        assert (installed / name).read_bytes() == (PAYLOAD / name).read_bytes(), name
    for source in PAYLOAD.rglob("*"):
        relative = source.relative_to(PAYLOAD)
        if source.is_file() and not any(_is_excluded(Path(p)) for p in relative.parts):
            assert (installed / relative).read_bytes() == source.read_bytes(), relative
    assert not (installed / ".git").exists()
    assert (target / "user.md").read_text() == "Keep user work.\n"
    record = json.loads((target / ".vibe-tool/installations.json").read_text())
    assert record["skills"]["visual-explainer"]["source"] == "skills/visual-explainer/plugins/visual-explainer"


def test_dry_run_leaves_an_existing_project_unchanged(repository, tmp_path):
    target = tmp_path / "project"
    target.mkdir()
    (target / "user.md").write_text("Keep user work.\n")
    before = snapshot(target)
    assert add_skill(repository / "skills", "visual-explainer", target, dry_run=True) == 0
    assert snapshot(target) == before


def test_update_and_standalone_rollback_preserve_user_customizations(repository, tmp_path):
    target = tmp_path / "project"
    assert add_skill(repository / "skills", "visual-explainer", target) == 0
    installed = target / ".agents/skills/visual-explainer"
    (installed / "user-notes.md").write_text("Local custom notes.\n")
    (installed / "kit/kit.css").write_text("/* Local theme override. */\n")
    before = snapshot(installed)
    assert update_skill(repository, "visual-explainer", target, dry_run=True) == 0
    assert snapshot(installed) == before
    assert update_skill(repository, "visual-explainer", target) == 0
    assert (installed / "kit/kit.css").read_bytes() == (PAYLOAD / "kit/kit.css").read_bytes()
    assert not (installed / "user-notes.md").exists()
    for name in REQUIRED:
        assert (installed / name).read_bytes() == (PAYLOAD / name).read_bytes(), name
    restores = list((target / ".vibe-tool/backups").glob("*/restore.py"))
    assert len(restores) == 1
    result = subprocess.run([sys.executable, "-B", str(restores[0])], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert snapshot(installed) == before


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is needed for the optional renderer smoke test")
def test_copied_renderer_runs_without_the_upstream_checkout(repository, tmp_path):
    target = tmp_path / "project"
    assert add_skill(repository / "skills", "visual-explainer", target) == 0
    renderer = target / ".agents/skills/visual-explainer/kit/render.mjs"
    source = tmp_path / "diagram.src.html"
    source.write_text(PAGE, encoding="utf-8")
    result = subprocess.run(["node", str(renderer), str(source), "--no-check"],
                            cwd=tmp_path, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    html = (tmp_path / "diagram.html").read_text(encoding="utf-8")
    assert "kit inlined" in result.stdout
    assert "Page: 1 figure" in result.stdout
    assert "without a caption" not in result.stdout
    assert "<style" in html and "<script" in html
    assert '<link rel="stylesheet" href="kit.css" data-ve-kit>' not in html
    assert "The copied skill renders a source into an HTML page." in html


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is needed for renderer validation")
def test_invalid_source_writes_no_output(repository, tmp_path):
    target = tmp_path / "project"
    assert add_skill(repository / "skills", "visual-explainer", target) == 0
    source = tmp_path / "invalid.src.html"
    source.write_text(PAGE.replace('data-register="blueprint"', 'data-register="invalid"'))
    result = subprocess.run(["node", str(target / ".agents/skills/visual-explainer/kit/render.mjs"),
                             str(source), "--no-check"], capture_output=True, text=True, timeout=30)
    assert result.returncode == 1, result.stdout + result.stderr
    assert not (tmp_path / "invalid.html").exists()
