"""Office capability is portable; its business manifest composes, not owns it."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

import pytest

from vibe_tool.discovery import resolve_manifest, resolve_skill
from vibe_tool.skill import add_skill


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "mine/office"
MANIFEST = ROOT / "manifests/office"
COMPANIONS = ("office-quality", "omnidraw", "omnisheet", "omnippt")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    return {str(p.relative_to(root)): digest(p) for p in root.rglob("*") if p.is_file()}


def invoke(command, *, env=None, cwd=None):
    result = subprocess.run(list(map(str, command)), env=env, cwd=cwd,
                            capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.fixture
def project_repo(tmp_path):
    repo = tmp_path / "source repo"
    shutil.copytree(MANIFEST, repo / "manifests/office",
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(SKILL, repo / "mine/office",
                    ignore=shutil.ignore_patterns("__pycache__"))
    # The separation tests exercise the real Office implementation and installer;
    # external engines use clearly marked fixtures, not claimed Office execution.
    for name in COMPANIONS:
        path = repo / "mine" / name / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(f"---\nname: {name}\ndescription: synthetic dependency\n---\n")
    for name in ("docx", "xlsx", "pptx", "pdf"):
        path = repo / "skills/anthropics/skills" / name / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(f"---\nname: {name}\ndescription: synthetic engine\n---\n")
    path = repo / "skills/ai-vibe-writing/SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nname: ai-vibe-writing\ndescription: synthetic writer\n---\n")
    env = dict(os.environ, VIBE_HOME=str(repo), PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=str(ROOT / "tools/vibe_tool/src"),
               VIBE_PROJECTS_FILE=str(tmp_path / "registry.json"))

    def cli(*args):
        return invoke([sys.executable, "-m", "vibe_tool", *args], env=env, cwd=tmp_path)

    return repo, env, cli


def test_manifest_composes_office_and_exact_engines(project_repo):
    repo, _, _ = project_repo
    manifest = resolve_manifest(repo / "manifests", "office")
    skill = resolve_skill((repo / "skills", repo / "mine"), "office")
    assert skill.source_path == repo / "mine/office"
    assert manifest.required_skills[0] == "office"
    assert len(manifest.required_skills) == len(set(manifest.required_skills)) == 10
    for name in ("docx", "xlsx", "pptx", "pdf", "planning"):
        assert not (manifest.path / name / "CLAUDE.md").exists()
        assert (skill.source_path / name / "CLAUDE.md").is_file()
    assert {p.name for p in (manifest.path / "scripts").iterdir()} == {
        "init-office.sh", "install_office.py", "render_workflow.py"}


def test_standalone_skill_is_self_contained_and_does_not_bootstrap_project(tmp_path):
    source, target = tmp_path / "source", tmp_path / "existing project"
    shutil.copytree(SKILL, source / "mine/office", ignore=shutil.ignore_patterns("__pycache__"))
    (source / "skills").mkdir()
    target.mkdir()
    (target / "AGENTS.md").write_text("existing research instructions\n")
    assert add_skill((source / "skills", source / "mine"), "office", target) == 0
    installed = target / ".agents/skills/office"
    assert {p.name for p in installed.parent.iterdir()} == {"office"}
    assert (target / "AGENTS.md").read_text() == "existing research instructions\n"
    assert not (target / "office").exists()
    assert not (target / ".claude").exists()
    assert not (target / ".codex").exists()
    shutil.rmtree(source)
    file = target / "fixture.docx"
    # Minimal native OOXML fixture exercises the standard-library verifier;
    # this portability test does not depend on optional authoring libraries.
    with zipfile.ZipFile(file, "w") as package:
        package.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        package.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        package.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Portable synthetic Office fixture.</w:t></w:r></w:p></w:body></w:document>')
    before = digest(file)
    invoke([sys.executable, installed / "scripts/verify.py", file,
            "--output", target / "structure.json"], cwd=target)
    report = json.loads((target / "structure.json").read_text())
    assert report["quality_status"] == "pending"  # structure is not visual QA
    assert digest(file) == before
    assert (installed / "docx/macros/OfficeLayout.bas").is_file()
    assert (installed / "xlsx/macros/OfficeWorkbook.bas").is_file()
    invoke([sys.executable, installed / "scripts/render_workflow.py", "--source",
            installed / "assets/workflow.json", "--output", installed / "assets/workflow.svg", "--check"])


@pytest.mark.parametrize("mode", ["init", "add"])
def test_project_install_composes_skills_and_registers_canonical_roles(project_repo, tmp_path, mode):
    repo, _, cli = project_repo
    target = tmp_path / (mode + " project")
    if mode == "add":
        target.mkdir()
        (target / "AGENTS.md").write_text("existing project\n")
        legacy = target / "office/docx/user-note.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("legacy user data\n")
        cli("add", "manifest", "office", target)
        assert (target / "AGENTS.md").read_text() == "existing project\n"
        assert legacy.read_text() == "legacy user data\n"
    else:
        cli("init", "office", target)
        assert not (target / "office/docx").exists()
    installed = target / ".agents/skills/office"
    assert (installed / "SKILL.md").is_file()
    assert (target / "office/templates/task-brief.md").is_file()
    assert not (target / "office/scripts/verify.py").exists()
    assert not (target / "office/rules/quality.md").exists()
    for host, extension in (("claude", "md"), ("codex", "toml")):
        for role in ("planner", "writer", "visuals", "docx", "xlsx", "pptx", "pdf", "qa"):
            relative = f"office-{role}.{extension}"
            assert (target / f".{host}/agents" / relative).read_bytes() == (
                repo / "mine/office/agents" / host / relative).read_bytes()
    invoke([sys.executable, target / "office/scripts/render_workflow.py",
            "--source", target / "office/assets/workflow.json",
            "--output", target / "office/assets/workflow.svg", "--check"])


def test_generic_setup_installs_capability_and_project_contract(project_repo, tmp_path):
    _, _, cli = project_repo
    target = tmp_path / "portable project"
    cli("setup", "office", target, "--harness", "generic", "--dry-run")
    assert not target.exists()
    cli("setup", "office", target, "--harness", "generic")
    cli("setup", "office", target, "--check")
    assert (target / "PROJECT_RULES.md").is_file()
    assert (target / ".agents/skills/office/scripts/verify.py").is_file()
    assert not (target / "office/docx").exists()
    assert not (target / ".cursor").exists()


def test_project_update_and_standalone_restore_preserve_business_data(project_repo, tmp_path):
    repo, env, cli = project_repo
    target = tmp_path / "update project"
    cli("init", "office", target)
    runtime = target / ".agents/skills/office/rules/quality.md"
    runtime.write_text("local previous runtime\n")
    project_rule = target / "office/rules/office-project.md"
    project_rule.write_text("local previous project rule\n")
    (target / "MANIFEST.md").write_text("project output history\n")
    (target / "README.md").write_text("project README\n")
    before = snapshot(target)
    cli("update", "manifest", "office", target, "--dry-run")
    assert snapshot(target) == before
    cli("update", "manifest", "office", target)
    assert runtime.read_bytes() == (repo / "mine/office/rules/quality.md").read_bytes()
    assert project_rule.read_bytes() == (repo / "manifests/office/rules/office-project.md").read_bytes()
    assert (target / "MANIFEST.md").read_text() == "project output history\n"
    assert (target / "README.md").read_text() == "project README\n"
    restore = list((target / ".vibe-tool/backups").glob("*/restore.py"))
    assert len(restore) == 1
    invoke([sys.executable, restore[0]], env=env, cwd=tmp_path)
    assert runtime.read_text() == "local previous runtime\n"
    assert project_rule.read_text() == "local previous project rule\n"
    for relative, value in before.items():
        assert digest(target / relative) == value, relative


@pytest.mark.parametrize("source", [SKILL, MANIFEST])
def test_workflow_check_is_read_only_and_detects_drift(tmp_path, source):
    target = tmp_path / "bundle"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
    args = [sys.executable, target / "scripts/render_workflow.py", "--source",
            target / "assets/workflow.json", "--output", target / "assets/workflow.svg", "--check"]
    before = snapshot(target)
    invoke(args)
    assert snapshot(target) == before
    graph = target / "assets/workflow.json"
    data = json.loads(graph.read_text())
    data["description"] += " changed fixture"
    graph.write_text(json.dumps(data, ensure_ascii=False))
    before = snapshot(target)
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    assert result.returncode == 1
    assert snapshot(target) == before


def test_skill_resource_links_are_inside_the_bundle():
    for file in SKILL.rglob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text()):
            if link.startswith(("https://", "http://", "#", "mailto:")):
                continue
            path = (file.parent / link.split("#", 1)[0]).resolve()
            assert path.is_relative_to(SKILL.resolve()), (file, link)
            assert path.exists(), (file, link)
