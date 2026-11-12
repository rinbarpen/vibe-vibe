"""The unified writer ships real engines and survives independent installation."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from vibe_tool.discovery import discover_skills, resolve_manifest
from vibe_tool.project_update import update_skill
from vibe_tool.skill import add_skill


ROOT = Path(__file__).resolve().parents[3]


def run(command, *, expected=0):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30)
    assert result.returncode == expected, result.stdout + result.stderr
    return result


@pytest.fixture
def sources(tmp_path):
    repo = tmp_path / "source repo"
    (repo / "manifests").mkdir(parents=True)
    for relative in ("mine/z-writing", "mine/z-humanizer", "skills/ai-vibe-writing",
                     "skills/unslop", "skills/academic-humanizer", "skills/humanizer-zh-academic"):
        shutil.copytree(ROOT / relative, repo / relative, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    return repo


def install(repo, target, name="z-writing"):
    assert add_skill((repo / "skills", repo / "mine"), name, target) == 0
    return target / ".agents/skills" / name


def test_bundling_keeps_the_canonical_catalog_names(sources):
    assert {s.name for s in discover_skills(sources / "skills", sources / "mine")} == {
        "z-writing", "z-humanizer", "ai-vibe-writing", "unslop",
        "academic-humanizer", "humanizer-zh-academic"}


def test_standalone_writer_materializes_all_real_resources_without_project_changes(sources, tmp_path):
    target = tmp_path / "existing project"
    target.mkdir()
    (target / "AGENTS.md").write_text("existing project contract\n")
    (target / ".ai_context").mkdir()
    profile = target / ".ai_context/style_profile.md"
    profile.write_text("author-confirmed existing style\n")
    installed = install(sources, target)
    shutil.rmtree(sources)
    assert {p.name for p in installed.parent.iterdir()} == {"z-writing"}
    assert (target / "AGENTS.md").read_text() == "existing project contract\n"
    assert profile.read_text() == "author-confirmed existing style\n"
    assert not (target / "MANIFEST.md").exists()
    assert not any(p.is_symlink() for p in installed.rglob("*"))
    assert not any(p.name == ".git" for p in installed.rglob("*"))
    for relative in (
        "references/ai-vibe-writing/.ai_context/prompts/1_style_extractor.md",
        "references/ai-vibe-writing/.ai_context/prompts/17_sentence_flow_agent.md",
        "references/ai-vibe-writing/.ai_context/document_spec_template.md",
        "references/z-humanizer/references/unslop/references/commands/teach.md",
        "references/z-humanizer/references/unslop/references/commands/mimic.md",
        "references/z-humanizer/skills/academic-humanizer/SKILL.md",
        "references/z-humanizer/skills/humanizer-zh-academic/SKILL.md",
    ):
        assert (installed / relative).is_file(), relative
    for file in (installed / "SKILL.md", installed / "references/context.md",
                 installed / "references/scenes.md"):
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text()):
            if link.startswith(("http:", "https:", "#")):
                continue
            path = (file.parent / link.split("#", 1)[0]).resolve()
            assert path.is_relative_to(installed.resolve()) and path.exists(), (file, link)


def test_scholarly_resources_also_work_in_direct_humanizer_install(sources, tmp_path):
    installed = install(sources, tmp_path / "project", name="z-humanizer")
    for name in ("academic-humanizer", "humanizer-zh-academic"):
        assert (installed / "skills" / name / "SKILL.md").read_bytes() == (
            sources / "skills" / name / "SKILL.md").read_bytes()
        assert not (installed / "skills" / name).is_symlink()
    canonical = sources / "skills/academic-humanizer/SKILL.md"
    canonical.write_text(canonical.read_text() + "\nSynthetic update.\n")
    assert update_skill(sources, "z-humanizer", tmp_path / "project") == 0
    assert (installed / "skills/academic-humanizer/SKILL.md").read_bytes() == canonical.read_bytes()
    assert not any(p.is_symlink() for p in installed.rglob("*"))


def test_bundled_voice_profile_and_card_run_after_source_removal(sources, tmp_path):
    installed = install(sources, tmp_path / "project")
    shutil.rmtree(sources)
    scripts = installed / "references/z-humanizer/references/unslop/scripts"
    samples = tmp_path / "samples"
    samples.mkdir()
    # Synthetic English samples test execution, not someone's actual voice.
    (samples / "sample.md").write_text(
        "We inspect the source before changing a claim. The table records each input. "
        "Short paragraphs carry one point. A result needs a clear comparison. "
        "When evidence is missing, the draft says so.\n" * 3)
    profile = tmp_path / "profile.json"
    run([sys.executable, scripts / "voice_profile.py", samples, "-o", profile])
    assert json.loads(profile.read_text())["metadata"]["low_confidence"] is True
    cards = tmp_path / "voice"
    run([sys.executable, scripts / "voice_card.py", "--profile", profile, "--samples",
         samples, "--out", cards, "--name", "synthetic-test", "--provenance"])
    assert (cards / "card.md").is_file()
    assert (cards / "provenance.json").is_file()
    # A changed sample invalidates the prior profile rather than quietly using it.
    (samples / "sample.md").write_text("Different evidence and a different sample.\n")
    result = run([sys.executable, scripts / "voice_card.py", "--profile", profile,
                  "--samples", samples, "--out", tmp_path / "stale"], expected=2)
    assert "does not match" in result.stderr


def test_bundled_preservation_check_rejects_changed_numbers(sources, tmp_path):
    installed = install(sources, tmp_path / "project")
    scripts = installed / "references/z-humanizer/references/unslop/scripts"
    original, candidate, constraints = [tmp_path / name for name in ("original.txt", "candidate.txt", "constraints.json")]
    original.write_text("The dataset contains 64 entries.\n")
    candidate.write_text("There are 64 entries in the dataset.\n")
    constraints.write_text(json.dumps({"constraints": [{"type": "number", "value": "64"}]}))
    result = run([sys.executable, scripts / "validate_preservation.py", original, candidate, constraints])
    assert json.loads(result.stdout)["passed"] is True
    candidate.write_text("There are 65 entries in the dataset.\n")
    result = run([sys.executable, scripts / "validate_preservation.py", original, candidate, constraints], expected=1)
    assert json.loads(result.stdout)["passed"] is False


def test_update_tracks_the_canonical_engine_and_rollback_restores_prior_bundle(sources, tmp_path):
    target = tmp_path / "project"
    installed = install(sources, target)
    source = sources / "skills/ai-vibe-writing/.ai_context/prompts/2_writer.md"
    destination = installed / "references/ai-vibe-writing/.ai_context/prompts/2_writer.md"
    before = hashlib.sha256(destination.read_bytes()).hexdigest()
    source.write_text(source.read_text() + "\nSynthetic upstream update marker.\n")
    assert update_skill(sources, "z-writing", target, dry_run=True) == 0
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == before
    assert update_skill(sources, "z-writing", target) == 0
    assert destination.read_bytes() == source.read_bytes()
    assert not any(p.is_symlink() for p in installed.rglob("*"))
    restore, = (target / ".vibe-tool/backups").glob("*/restore.py")
    run([sys.executable, restore])
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == before


@pytest.mark.parametrize("alias", ["references/ai-vibe-writing", "references/z-humanizer"])
def test_update_rejects_retargeted_engines_before_changing_installation(sources, tmp_path, alias):
    target = tmp_path / "project"
    installed = install(sources, target)
    before = {str(p.relative_to(installed)): p.read_bytes() for p in installed.rglob("*") if p.is_file()}
    link = sources / "mine/z-writing" / alias
    link.unlink()
    outside = tmp_path / "unrelated source"
    outside.mkdir()
    link.symlink_to(outside, target_is_directory=True)
    assert update_skill(sources, "z-writing", target) == 1
    assert {str(p.relative_to(installed)): p.read_bytes() for p in installed.rglob("*") if p.is_file()} == before


def test_office_composes_the_unified_writer_without_changing_research_plans():
    office = resolve_manifest(ROOT / "manifests", "office")
    assert "z-writing" in office.required_skills
    assert "ai-vibe-writing" not in office.required_skills
    assert len(office.required_skills) == 10
    assert "z-writing" in (ROOT / "mine/office/SKILL.md").read_text()
    # Research keeps its own plan engine; z-writing is not a shadow lifecycle.
    assert not (ROOT / "mine/z-writing/scripts/writing_plan.py").exists()
