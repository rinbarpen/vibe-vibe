"""Installation provenance and init/add integration regression coverage."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from vibe_tool import manifest as manifest_module
from vibe_tool.discovery import resolve_manifest
from vibe_tool.installations import (
    load_installations,
    manifest_option_keys,
    normalized_options,
    record_manifest,
    record_skill,
    source_ref,
    write_installations,
)
from vibe_tool.manifest import add_manifest, init_manifest
from vibe_tool.skill import add_all_skills, add_skill


def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for dirname in ("skills", "mine", "manifests"):
        (root / dirname).mkdir(parents=True)
    return root


def skill(root: Path, relative: str = "skills/demo") -> Path:
    path = root / relative
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text("# Demo\n")
    return path


def manifest(root: Path, name: str = "demo") -> Path:
    path = root / "manifests" / name
    path.mkdir(parents=True)
    (path / "CLAUDE.md").write_text("# Demo\n")
    return path


def test_missing_record_does_not_create_metadata(tmp_path):
    target = tmp_path / "project"
    assert load_installations(target) == {"schema_version": 1, "skills": {}, "manifests": {}}
    assert not target.exists()


def test_atomic_records_merge_and_preserve_skipped_parameters(tmp_path):
    root = repo(tmp_path)
    target = tmp_path / "project"
    source = skill(root)
    template = manifest(root, "vibe-coding")
    record_skill(root, target, "demo", source)
    record_manifest(root, target, "vibe-coding", template, {"provider": "git", "owner": "My Team"})
    saved = load_installations(target)
    assert saved["skills"]["demo"] == {"source": "skills/demo"}
    assert saved["manifests"]["vibe-coding"]["options"] == {
        "provider": "git", "scenario": "", "owner": "My Team", "org": "", "repo": "", "email": "",
    }
    metadata = target / ".vibe-tool/installations.json"
    before = metadata.read_bytes(), metadata.stat().st_mtime_ns
    record_manifest(root, target, "vibe-coding", template, {"provider": "github"})
    assert (metadata.read_bytes(), metadata.stat().st_mtime_ns) == before
    record_manifest(root, target, "vibe-coding", template, {"provider": "gitlab"}, force=True)
    assert load_installations(target)["manifests"]["vibe-coding"]["options"]["provider"] == "gitlab"
    assert not list(metadata.parent.glob(".installations-*"))


@pytest.mark.parametrize("payload", [
    "{", "[]", '{"schema_version":2,"skills":{},"manifests":{}}',
    '{"schema_version":1,"skills":[],"manifests":{}}',
    '{"schema_version":1,"skills":{"../bad":{"source":"skills/demo"}},"manifests":{}}',
    '{"schema_version":1,"skills":{"demo":{"source":"../demo"}},"manifests":{}}',
    '{"schema_version":1,"skills":{"demo":{"source":"/tmp/demo"}},"manifests":{}}',
    '{"schema_version":1,"skills":{"demo":{"source":"skills//demo"}},"manifests":{}}',
    '{"schema_version":1,"skills":{},"manifests":{"vibe-coding":{"source":"manifests/vibe-coding","options":{}}}}',
])
def test_bad_records_are_not_silently_reset(tmp_path, payload):
    directory = tmp_path / ".vibe-tool"
    directory.mkdir()
    metadata = directory / "installations.json"
    metadata.write_text(payload)
    with pytest.raises(ValueError):
        load_installations(tmp_path)
    assert metadata.read_text() == payload


@pytest.mark.parametrize("link_kind", ["directory", "file"])
def test_metadata_symlink_outside_project_is_rejected(tmp_path, link_kind):
    target = tmp_path / "target"
    target.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    if link_kind == "directory":
        (target / ".vibe-tool").symlink_to(elsewhere, target_is_directory=True)
    else:
        (target / ".vibe-tool").mkdir()
        metadata = elsewhere / "installations.json"
        metadata.write_text("unchanged")
        (target / ".vibe-tool/installations.json").symlink_to(metadata)
    with pytest.raises(ValueError, match="leaves target"):
        write_installations(target, {"schema_version": 1, "skills": {}, "manifests": {}})
    with pytest.raises(ValueError, match="leaves target"):
        load_installations(target)
    assert not (elsewhere / "installations.json").exists() or (elsewhere / "installations.json").read_text() == "unchanged"


def test_source_reference_preserves_repo_symlink_alias(tmp_path):
    root = repo(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    alias = root / "manifests" / "linked"
    alias.symlink_to(external, target_is_directory=True)
    assert source_ref(root, alias) == "manifests/linked"
    with pytest.raises(ValueError, match="outside"):
        source_ref(root, external)


def test_normalization_keeps_only_applicable_options():
    assert manifest_option_keys("knowledge-learning") == ("scenario",)
    assert normalized_options("knowledge-learning", {"scenario": "exam-prep", "provider": "git", "force": True}) == {"scenario": "exam-prep"}
    assert normalized_options("vibe-coding", {})["provider"] == "github"
    assert normalized_options("vibe-coding", {"provider": ""})["provider"] == ""
    assert normalized_options("fund-proposal", {"scenario": "x"}) == {}
    with pytest.raises(ValueError):
        normalized_options("ui-testing", {"scenario": 42})


def test_add_skill_records_canonical_name_and_skips_without_writing(tmp_path):
    root = repo(tmp_path)
    skill(root)
    target = tmp_path / "project"
    assert add_skill(root / "skills", "DEMO", target) == 0
    assert load_installations(target)["skills"] == {"demo": {"source": "skills/demo"}}
    metadata = target / ".vibe-tool/installations.json"
    saved = metadata.read_bytes(), metadata.stat().st_mtime_ns
    assert add_skill(root / "skills", "demo", target) == 2
    assert (metadata.read_bytes(), metadata.stat().st_mtime_ns) == saved


def test_add_all_records_only_successful_items(tmp_path, monkeypatch):
    from vibe_tool import skill as skill_module
    root = repo(tmp_path)
    for name in ("first", "failed", "skipped"):
        skill(root, f"skills/{name}")
    monkeypatch.setattr(skill_module, "_install_one", lambda source, dest, name, force, dry: {"first": 0, "failed": 1, "skipped": 2}[name])
    target = tmp_path / "project"
    assert add_all_skills(root / "skills", target) == 1
    assert set(load_installations(target)["skills"]) == {"first"}


def test_add_skill_dry_run_and_failure_do_not_record(tmp_path, monkeypatch):
    from vibe_tool import skill as skill_module
    root = repo(tmp_path)
    skill(root)
    target = tmp_path / "project"
    assert add_skill(root / "skills", "demo", target, dry_run=True) == 0
    assert not target.exists()
    monkeypatch.setattr(skill_module, "_install_one", lambda *args: 1)
    assert add_skill(root / "skills", "demo", target) == 1
    assert not (target / ".vibe-tool").exists()


def test_generic_manifest_records_only_after_dependencies_succeed(tmp_path):
    root = repo(tmp_path)
    template = manifest(root)
    (template / "skills.txt").write_text("local\n")
    skill(root, "manifests/demo/skills/local")
    target = tmp_path / "project"
    assert init_manifest(root / "manifests", "DEMO", target) == 0
    records = load_installations(target)
    assert records["manifests"] == {"demo": {"source": "manifests/demo", "options": {}}}
    assert records["skills"]["local"]["source"] == "manifests/demo/skills/local"
    (template / "skills.txt").write_text("missing\n")
    failed_target = tmp_path / "failed"
    assert init_manifest(root / "manifests", "demo", failed_target) == 1
    assert load_installations(failed_target)["manifests"] == {}


def test_generic_commands_dry_run_creates_no_directories(tmp_path):
    root = repo(tmp_path)
    template = manifest(root)
    commands = template / "commands" / "nested"
    commands.mkdir(parents=True)
    (commands / "command.md").write_text("# Command\n")
    target = tmp_path / "project"
    assert init_manifest(root / "manifests", "demo", target, dry_run=True) == 0
    assert not target.exists()


def test_manifest_script_failure_and_repeat_preserve_records(tmp_path, monkeypatch):
    root = repo(tmp_path)
    template = manifest(root, "vibe-coding")
    scripts = template / "scripts"
    scripts.mkdir()
    (scripts / "init.sh").write_text("#!/bin/sh\nexit 1\n")
    target = tmp_path / "project"
    target.mkdir()
    monkeypatch.setattr(manifest_module, "_run_init_script", lambda *args, **kwargs: 1)
    assert add_manifest(root / "manifests", "vibe-coding", target, provider="git") == 1
    assert not (target / ".vibe-tool").exists()
    monkeypatch.setattr(manifest_module, "_run_init_script", lambda *args, **kwargs: 0)
    assert add_manifest(root / "manifests", "vibe-coding", target, provider="git") == 0
    assert add_manifest(root / "manifests", "vibe-coding", target, provider="gitlab") == 0
    assert load_installations(target)["manifests"]["vibe-coding"]["options"]["provider"] == "git"


@pytest.mark.parametrize("name", ["vibe-coding", "knowledge-learning"])
def test_script_arguments_are_real_tokens_and_knowledge_target_last(tmp_path, monkeypatch, name):
    root = repo(tmp_path)
    template = manifest(root, name)
    scripts = template / "scripts"
    scripts.mkdir()
    (scripts / "init.sh").write_text("#!/bin/sh\nexit 0\n")
    info = resolve_manifest(root / "manifests", name)
    commands = []
    monkeypatch.setattr(manifest_module.subprocess, "run", lambda cmd, **kwargs: (commands.append(cmd), SimpleNamespace(returncode=0))[1])
    target = tmp_path / "project with spaces"
    assert manifest_module._run_init_script(info, target, True, False, owner="Team With Spaces", scenario="exam-prep") == 0
    cmd = commands[0]
    assert str(target) in cmd
    if name == "knowledge-learning":
        assert cmd[-1] == str(target)
        assert cmd[1:3] == ["--scenario", "exam-prep"]
    else:
        assert cmd[cmd.index("-o") + 1] == "Team With Spaces"
        assert "-o Team With Spaces" not in cmd


@pytest.mark.parametrize("name", ["knowledge-learning", "ui-testing", "fund-proposal", "auto-research-ars"])
def test_scripts_without_dry_run_support_are_not_executed(tmp_path, monkeypatch, name):
    root = repo(tmp_path)
    template = manifest(root, name)
    scripts = template / "scripts"
    scripts.mkdir()
    (scripts / "init.sh").write_text("#!/bin/sh\nexit 0\n")
    monkeypatch.setattr(manifest_module.subprocess, "run", lambda *a, **k: pytest.fail("dry-run executed a mutating script"))
    target = tmp_path / "project"
    assert init_manifest(root / "manifests", name, target, dry_run=True) == 0
    assert not target.exists()


@pytest.mark.parametrize("link_kind", ["directory", "file"])
def test_metadata_symlink_inside_project_is_rejected(tmp_path, link_kind):
    target = tmp_path / "project"
    elsewhere = target / "internal"
    elsewhere.mkdir(parents=True)
    if link_kind == "directory":
        (target / ".vibe-tool").symlink_to(elsewhere, target_is_directory=True)
    else:
        (target / ".vibe-tool").mkdir()
        metadata = elsewhere / "installations.json"
        metadata.write_text("unchanged")
        (target / ".vibe-tool/installations.json").symlink_to(metadata)
    with pytest.raises(ValueError, match="symbolic link"):
        write_installations(target, {"schema_version": 1, "skills": {}, "manifests": {}})


def test_failed_atomic_write_keeps_original_and_cleans_temporary(tmp_path, monkeypatch):
    from vibe_tool import installations
    before = {"schema_version": 1, "skills": {}, "manifests": {}}
    write_installations(tmp_path, before)
    metadata = tmp_path / ".vibe-tool/installations.json"
    original = metadata.read_bytes()
    desired = {"schema_version": 1, "skills": {"demo": {"source": "skills/demo"}}, "manifests": {}}
    def failed_replace(*args):
        raise OSError("simulated write failure")
    monkeypatch.setattr(installations.os, "replace", failed_replace)
    with pytest.raises(OSError, match="simulated"):
        write_installations(tmp_path, desired)
    assert metadata.read_bytes() == original
    assert not list(metadata.parent.glob(".installations-*"))
