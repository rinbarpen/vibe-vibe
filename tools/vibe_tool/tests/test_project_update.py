"""Project-local updates, preservation rules, and standalone transaction recovery.

Fixtures are deliberately small local repositories. All subprocesses use -B so
running these tests never modifies tracked Python bytecode in source bundles.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "tools" / "vibe_tool" / "src"


def write(path: Path, content: str, *, mode: int | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)
    return path


def cli(root: Path, *args: str | Path, cwd: Path | None = None):
    return subprocess.run(
        [sys.executable, "-B", "-m", "vibe_tool", *(str(a) for a in args)],
        cwd=cwd or root, text=True, capture_output=True, check=False,
        env={**os.environ, "VIBE_HOME": str(root), "PYTHONPATH": str(SRC),
             "PYTHONDONTWRITEBYTECODE": "1"},
    )


def ok(result) -> None:
    assert result.returncode == 0, result.stdout + result.stderr


def records(target: Path) -> dict:
    return json.loads((target / ".vibe-tool/installations.json").read_text())


def snapshot(target: Path, *, backups: bool = True) -> dict:
    """Compare bytes, modes, links and file mtimes without traversing links."""
    result = {}
    for path in sorted(target.rglob("*")):
        relative = path.relative_to(target).as_posix()
        if not backups and (relative == ".vibe-tool/backups" or relative.startswith(".vibe-tool/backups/")):
            continue
        info = path.lstat()
        mode = stat.S_IMODE(info.st_mode)
        if path.is_symlink():
            result[relative] = ("link", mode, os.readlink(path))
        elif path.is_file():
            result[relative] = ("file", mode, info.st_mtime_ns, path.read_bytes())
        # Empty directories are intentionally omitted: restore keeps its own
        # backup directory, while files and links must match exactly.
    return result


def backups(target: Path) -> list[Path]:
    return sorted((target / ".vibe-tool/backups").glob("*/restore.py"))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "local sources"
    (root / "skills").mkdir(parents=True)
    (root / "mine").mkdir()
    manifest = root / "manifests/office"
    for relative, content in {
        "CLAUDE.md": "# Office v1\n",
        "AGENTS.md": "# Agents v1\n",
        "MANIFEST.md": "# Template ledger\n",
        "README.md": "# Template readme\n",
        "rules/office.mdc": "# Rules v1 {{VIBE_MANIFEST}}\n",
        "commands/review/COMMAND.md": "# Review v1\n",
        ".claude/agents/reviewer.md": "# Reviewer v1\n",
        ".codex/agents/reviewer.toml": 'name = "reviewer"\n',
    }.items():
        write(manifest / relative, content)
    write(root / "skills/demo/SKILL.md", "# Demo v1\n")
    write(root / "skills/demo/tool.sh", "#!/bin/sh\necho v1\n", mode=0o751)
    return root


@pytest.fixture
def target(tmp_path: Path) -> Path:
    target = tmp_path / "project with spaces"
    target.mkdir()
    write(target / "business.txt", "untouched\n")
    return target


def test_skill_add_records_canonical_source_and_skip_preserves_it(repo, target):
    ok(cli(repo, "add", "skill", "DEMO", target))
    metadata = records(target)
    assert metadata["schema_version"] == 1
    assert metadata["skills"]["demo"]["source"] == "skills/demo"
    before = snapshot(target)
    result = cli(repo, "add", "skill", "demo", target)
    assert result.returncode in (0, 2), result.stdout + result.stderr
    assert snapshot(target) == before


def test_skill_update_replaces_filters_and_noop_creates_no_backup(repo, target):
    ok(cli(repo, "add", "skill", "demo", target))
    installed = target / ".agents/skills/demo"
    write(installed / "custom.txt", "must be backed up\n")
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    write(repo / "skills/demo/.private", "filtered\n")
    write(repo / "skills/demo/__pycache__/cache.pyc", "filtered\n")
    write(repo / "skills/demo/references/detail.md", "new resource\n")
    result = cli(repo, "update", "skill", "demo", target)
    ok(result)
    assert (installed / "SKILL.md").read_text() == "# Demo v2\n"
    assert not (installed / "custom.txt").exists()
    assert not (installed / ".private").exists()
    assert not (installed / "__pycache__").exists()
    assert (installed / "references/detail.md").read_text() == "new resource\n"
    assert stat.S_IMODE((installed / "tool.sh").stat().st_mode) == 0o751
    assert (target / "business.txt").read_text() == "untouched\n"
    restore = backups(target)
    assert len(restore) == 1
    assert str(restore[0]) in result.stdout
    assert (restore[0].parent / "changes.json").is_file()
    assert (restore[0].parent / "before/.agents/skills/demo/custom.txt").read_text() == "must be backed up\n"
    before = snapshot(target)
    ok(cli(repo, "update", "skill", "demo", target))
    assert snapshot(target) == before


def test_skill_restore_is_standalone_and_restores_custom_files_and_metadata(repo, target):
    ok(cli(repo, "add", "skill", "demo", target))
    write(target / ".agents/skills/demo/custom.txt", "local customization\n")
    before = snapshot(target, backups=False)
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    ok(cli(repo, "update", "skill", "demo", target))
    script = backups(target)[0]
    restored = subprocess.run(
        [sys.executable, "-I", "-B", str(script)], cwd=target,
        capture_output=True, text=True, check=False,
    )
    ok(restored)
    assert snapshot(target, backups=False) == before


def test_skill_dry_run_and_default_cwd(repo, target):
    ok(cli(repo, "add", "skill", "demo", target))
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    before = snapshot(target)
    preview = cli(repo, "update", "skill", "demo", "--dry-run", cwd=target)
    ok(preview)
    assert "demo" in preview.stdout
    assert snapshot(target) == before
    assert not backups(target)
    ok(cli(repo, "update", "skill", "demo", cwd=target))
    assert (target / ".agents/skills/demo/SKILL.md").read_text() == "# Demo v2\n"


def test_skill_not_installed_reports_add_before_writing(repo, target):
    before = snapshot(target)
    result = cli(repo, "update", "skill", "demo", target)
    assert result.returncode != 0
    assert "vibe add skill" in result.stdout + result.stderr
    assert snapshot(target) == before


def test_unknown_skill_fails_without_project_changes(repo, target):
    before = snapshot(target)
    assert cli(repo, "update", "skill", "unknown", target).returncode != 0
    assert snapshot(target) == before


def test_update_rejects_all_flag(repo, target):
    result = cli(repo, "update", "skill", "demo", target, "--all")
    assert result.returncode != 0
    assert not (target / ".vibe-tool").exists()


def test_skill_update_preserves_relative_and_dangling_source_symlinks(repo, target):
    ok(cli(repo, "add", "skill", "demo", target))
    (repo / "skills/demo/entrypoint").symlink_to("tool.sh")
    (repo / "skills/demo/future").symlink_to("not-created-yet")
    ok(cli(repo, "update", "skill", "demo", target))
    installed = target / ".agents/skills/demo"
    assert (installed / "entrypoint").is_symlink()
    assert os.readlink(installed / "entrypoint") == "tool.sh"
    assert (installed / "future").is_symlink()
    assert os.readlink(installed / "future") == "not-created-yet"


def test_skill_update_does_not_traverse_external_target_parent_symlink(repo, target, tmp_path):
    outside = tmp_path / "outside"
    write(outside / "skills/demo/SKILL.md", "# External\n")
    (target / ".agents").symlink_to(outside, target_is_directory=True)
    before = snapshot(outside)
    result = cli(repo, "update", "skill", "demo", target)
    assert result.returncode != 0
    assert snapshot(outside) == before
    assert not backups(target)


def test_skill_source_target_overlap_is_rejected(repo):
    (repo / ".agents").mkdir()
    (repo / ".agents/skills").symlink_to(repo / "skills", target_is_directory=True)
    before = snapshot(repo)
    result = cli(repo, "update", "skill", "demo", repo)
    assert result.returncode != 0
    assert snapshot(repo) == before


def test_manifest_update_only_changes_resources_and_keeps_removed_files(repo, target):
    ok(cli(repo, "add", "manifest", "office", target))
    for relative in ("README.md", "MANIFEST.md", "CONTRIBUTING.md", "VERSION", "CHANGELOG.md", "notes/_index.md", "PAPER_OUTLINE.md", ".cursor/rules/local.mdc"):
        write(target / relative, f"user data {relative}\n")
    preserved = {p: (target / p).read_bytes() for p in ("README.md", "MANIFEST.md", "CONTRIBUTING.md", "VERSION", "CHANGELOG.md", "notes/_index.md", "PAPER_OUTLINE.md", ".cursor/rules/local.mdc", "business.txt")}
    write(repo / "manifests/office/CLAUDE.md", "# Office v2\n")
    write(repo / "manifests/office/.claude/agents/reviewer.md", "# Reviewer v2\n")
    (repo / "manifests/office/rules/office.mdc").unlink()
    ok(cli(repo, "update", "manifest", "office", target))
    assert (target / "CLAUDE.md").read_text() == "# Office v2\n"
    assert (target / ".claude/agents/reviewer.md").read_text() == "# Reviewer v2\n"
    assert (target / ".cursor/rules/office.mdc").exists()
    for relative, data in preserved.items():
        assert (target / relative).read_bytes() == data, relative
    assert len(backups(target)) == 1
    assert records(target)["manifests"]["office"]["source"] == "manifests/office"
    before = snapshot(target)
    ok(cli(repo, "update", "manifest", "office", target))
    assert snapshot(target) == before


def test_manifest_update_dependencies_are_selected_and_restored_together(repo, target):
    manifest = repo / "manifests/office"
    write(manifest / "skills.txt", "demo\nlocal-helper\nmissing-later\n")
    write(manifest / "skills/local-helper/SKILL.md", "# Local v1\n")
    write(repo / "skills/missing-later/SKILL.md", "# Missing later\n")
    write(repo / "mine/unrelated/SKILL.md", "# Unrelated v1\n")
    ok(cli(repo, "add", "manifest", "office", target))
    ok(cli(repo, "add", "skill", "unrelated", target))
    shutil.rmtree(target / ".agents/skills/missing-later")
    before = snapshot(target, backups=False)
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    write(manifest / "skills/local-helper/SKILL.md", "# Local v2\n")
    write(repo / "mine/unrelated/SKILL.md", "# Unrelated v2\n")
    write(manifest / "CLAUDE.md", "# Office v2\n")
    result = cli(repo, "update", "manifest", "office", target)
    ok(result)
    assert "missing-later" in result.stdout + result.stderr
    assert (target / ".agents/skills/demo/SKILL.md").read_text() == "# Demo v2\n"
    assert (target / ".agents/skills/local-helper/SKILL.md").read_text() == "# Local v2\n"
    assert records(target)["skills"]["local-helper"]["source"] == "manifests/office/skills/local-helper"
    assert (target / ".agents/skills/unrelated/SKILL.md").read_text() == "# Unrelated v1\n"
    assert not (target / ".agents/skills/missing-later").exists()
    scripts = backups(target)
    assert len(scripts) == 1
    ok(subprocess.run([sys.executable, "-I", "-B", str(scripts[0])], capture_output=True, text=True))
    assert snapshot(target, backups=False) == before


def install_real_manifest(root: Path, name: str) -> None:
    destination = root / "manifests" / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.symlink_to(REPO / "manifests" / name, target_is_directory=True)


@pytest.mark.parametrize("name,scenario,scenario_file", [
    ("tutor", "course-learning", ".cursor/scenario.md"),
    ("ui-testing", "component", "CLAUDE.ui-testing.md"),
])
def test_scenario_add_records_update_reuses_and_explicit_override_works(repo, target, name, scenario, scenario_file):
    install_real_manifest(repo, name)
    ok(cli(repo, "add", "manifest", name, target, f"--scenario={scenario}"))
    assert (target / scenario_file).is_file()
    assert records(target)["manifests"][name]["options"]["scenario"] == scenario
    write(target / scenario_file, "# Local override\n")
    write(target / "notes/_index.md", "# User knowledge index\n")
    ok(cli(repo, "update", "manifest", name, target))
    assert (target / scenario_file).read_text() != "# Local override\n"
    assert (target / "notes/_index.md").read_text() == "# User knowledge index\n"
    replacement = "self-study" if name == "tutor" else "web-e2e"
    ok(cli(repo, "update", "manifest", name, target, f"--scenario={replacement}"))
    assert records(target)["manifests"][name]["options"]["scenario"] == replacement
    repeated = cli(repo, "add", "manifest", name, target, f"--scenario={scenario}")
    if name == "tutor":
        assert repeated.returncode != 0
        assert "--force" in repeated.stdout + repeated.stderr
    else:
        ok(repeated)
    assert records(target)["manifests"][name]["options"]["scenario"] == replacement


def test_legacy_manifest_missing_parameters_fails_before_writing(repo, target):
    install_real_manifest(repo, "ui-testing")
    write(target / "CLAUDE.md", "# Existing legacy project\n")
    before = snapshot(target)
    result = cli(repo, "update", "manifest", "ui-testing", target)
    assert result.returncode != 0
    assert "scenario" in result.stdout + result.stderr
    assert snapshot(target) == before
    ok(cli(repo, "update", "manifest", "ui-testing", target, "--scenario="))
    assert records(target)["manifests"]["ui-testing"]["options"]["scenario"] == ""


def test_invalid_installation_record_fails_without_writing(repo, target):
    ok(cli(repo, "add", "skill", "demo", target))
    write(target / ".vibe-tool/installations.json", "{broken json")
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    before = snapshot(target)
    result = cli(repo, "update", "skill", "demo", target)
    assert result.returncode != 0
    assert snapshot(target) == before


REAL_MANIFESTS = sorted(p.parent.name for p in (REPO / "manifests").glob("*/CLAUDE.md") if p.parent.name != "agent-browser")


@pytest.mark.parametrize("name", REAL_MANIFESTS)
def test_every_real_manifest_dry_run_is_isolated(repo, target, name):
    if name == "office":
        shutil.rmtree(repo / "manifests/office")
    install_real_manifest(repo, name)
    write(target / "CLAUDE.md", "# Project context\n")
    write(target / "MANIFEST.md", "# Output ledger\n")
    from vibe_tool.installations import manifest_option_keys

    options = {key: "git" if key == "provider" else "" for key in manifest_option_keys(name)}
    write(target / ".vibe-tool/installations.json", json.dumps({
        "schema_version": 1, "skills": {}, "manifests": {
            name: {"source": f"manifests/{name}", "options": options},
        },
    }))
    before = snapshot(target)
    result = cli(repo, "update", "manifest", name, target, "--dry-run")
    ok(result)
    assert snapshot(target) == before
    assert not backups(target)
    assert not (target / ".git").exists()


def test_transaction_application_failure_rolls_back_all_touched_paths(tmp_path, monkeypatch):
    from vibe_tool import transaction

    target = tmp_path / "project"
    target.mkdir()
    source = tmp_path / "staging"
    write(target / "first.txt", "original first\n", mode=0o640)
    write(target / "second.txt", "original second\n")
    write(source / "first.txt", "new first\n")
    write(source / "second.txt", "new second\n")
    write(source / "created.txt", "new file\n")
    before = snapshot(target, backups=False)
    replace = transaction._replace
    touched = []

    def fail_second(src, dest):
        touched.append(dest)
        if dest == target / "second.txt":
            raise OSError("injected application failure")
        return replace(src, dest)

    monkeypatch.setattr(transaction, "_replace", fail_second)
    changes = [transaction.Change(Path(name), source / name) for name in ("first.txt", "created.txt", "second.txt")]
    assert transaction.apply_update(target, changes, label="failure test") == 1
    assert target / "first.txt" in touched
    assert target / "second.txt" in touched
    assert snapshot(target, backups=False) == before
    assert not (target / "created.txt").exists()


def test_transaction_backup_failure_never_applies_changes(tmp_path, monkeypatch):
    from vibe_tool import transaction

    target = tmp_path / "project"
    target.mkdir()
    write(target / "first.txt", "original\n")
    source = write(tmp_path / "staging/first.txt", "replacement\n")
    before = snapshot(target, backups=False)
    calls = []

    def fail_backup(*args, **kwargs):
        raise OSError("injected backup failure")

    monkeypatch.setattr(transaction.shutil, "copy2", fail_backup)
    monkeypatch.setattr(transaction, "_replace", lambda *args: calls.append(args))
    assert transaction.apply_update(target, [transaction.Change(Path("first.txt"), source)], label="backup failure") == 1
    assert not calls
    assert snapshot(target, backups=False) == before


def test_transaction_rejects_path_traversal(tmp_path):
    from vibe_tool import transaction

    target = tmp_path / "project"
    target.mkdir()
    outside = write(tmp_path / "outside.txt", "original\n")
    source = write(tmp_path / "staging/replacement.txt", "replacement\n")
    before = snapshot(target)
    assert transaction.apply_update(target, [transaction.Change(Path("../outside.txt"), source)], label="invalid path") == 1
    assert outside.read_text() == "original\n"
    assert snapshot(target) == before


@pytest.mark.parametrize("provider,expected", [
    ("git", None),
    ("github", ".github/CODEOWNERS"),
    ("gitlab", ".gitlab-ci.yml"),
    ("gitee", ".workflow/vibe-ci.yml"),
])
def test_vibe_manifest_provider_update_preserves_release_state_and_uses_real_paths(repo, target, provider, expected):
    install_real_manifest(repo, "vibe-coding")
    write(target / "CLAUDE.md", "# Legacy project\n")
    write(target / "MANIFEST.md", "# Old instructions\n")
    write(target / "README.md", "# Project documentation\n")
    write(target / "VERSION", "8.2.1\n")
    write(target / "CHANGELOG.md", "# Project release notes\n")
    options = (f"--provider={provider}", "--scenario=", "--owner=fixture team",
               "--org=fixture-org", "--repo=fixture-repo", "--email=fixture@example.invalid")
    ok(cli(repo, "update", "manifest", "vibe-coding", target, *options))
    assert not (target / ".git").exists()
    assert (target / "VERSION").read_text() == "8.2.1\n"
    assert (target / "CHANGELOG.md").read_text() == "# Project release notes\n"
    assert (target / "README.md").read_text() == "# Project documentation\n"
    assert (target / "MANIFEST.md").read_text() != "# Old instructions\n"
    assert (target / "CLAUDE.md").is_symlink()
    assert os.readlink(target / "CLAUDE.md") == "MANIFEST.md"
    if expected:
        assert (target / expected).is_file()
    assert (target / ".github").exists() == (provider == "github")
    if provider == "github":
        assert "fixture team" in (target / ".github/CODEOWNERS").read_text()
        assert "fixture@example.invalid" in (target / ".github/SECURITY.md").read_text()
    for rule in (target / ".cursor/rules").glob("*.mdc"):
        assert "vibe-update-" not in rule.read_text()
    assert records(target)["manifests"]["vibe-coding"]["options"]["provider"] == provider
    before = snapshot(target)
    ok(cli(repo, "update", "manifest", "vibe-coding", target))
    assert snapshot(target) == before


def test_manifest_generation_failure_has_no_project_side_effects(repo, target):
    ok(cli(repo, "add", "manifest", "office", target))
    script = repo / "manifests/office/scripts/office-init.sh"
    write(script, '#!/bin/sh\nprintf "partial" > "$1/CLAUDE.md"\nexit 9\n', mode=0o755)
    before = snapshot(target)
    result = cli(repo, "update", "manifest", "office", target)
    assert result.returncode != 0
    assert snapshot(target) == before
    assert not backups(target)


def test_single_skill_update_reuses_manifest_local_source_provenance(repo, target):
    manifest = repo / "manifests/office"
    write(manifest / "skills.txt", "local-helper\n")
    source = write(manifest / "skills/local-helper/SKILL.md", "# Local v1\n")
    ok(cli(repo, "add", "manifest", "office", target))
    assert records(target)["skills"]["local-helper"]["source"] == "manifests/office/skills/local-helper"
    write(source, "# Local v2\n")
    ok(cli(repo, "update", "skill", "local-helper", target))
    assert (target / ".agents/skills/local-helper/SKILL.md").read_text() == "# Local v2\n"


def test_bare_update_cli_still_only_updates_managed_submodules(repo, monkeypatch):
    from types import SimpleNamespace
    from vibe_tool import cli as cli_module

    paths = ["skills/anthropics", "skills/agent-skills", "skills/ai-investment-advisor"]
    captured = []
    monkeypatch.setattr(cli_module, "find_repo_root", lambda: repo)
    monkeypatch.setattr(cli_module, "discover_submodule_paths", lambda root: paths)
    monkeypatch.setattr(sys, "argv", ["vibe", "update"])

    def run(command, **kwargs):
        captured.append((command, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(subprocess, "run", run)
    assert cli_module.main() == 0
    assert captured == [([
        "git", "submodule", "update", "--remote", "--merge", "--", "skills/anthropics",
    ], {"cwd": str(repo), "check": False})]


def test_legacy_skill_update_restore_removes_new_installation_metadata(repo, target):
    shutil.copytree(repo / "skills/demo", target / ".agents/skills/demo")
    before = snapshot(target, backups=False)
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    ok(cli(repo, "update", "skill", "demo", target))
    assert records(target)["skills"]["demo"]["source"] == "skills/demo"
    ok(subprocess.run([sys.executable, "-I", "-B", str(backups(target)[0])], capture_output=True, text=True))
    assert not (target / ".vibe-tool/installations.json").exists()
    assert snapshot(target, backups=False) == before


def test_restore_rejects_corrupt_backup_before_touching_project(repo, target):
    ok(cli(repo, "add", "skill", "demo", target))
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    ok(cli(repo, "update", "skill", "demo", target))
    script = backups(target)[0]
    write(script.parent / "before/.agents/skills/demo/SKILL.md", "corrupt backup\n")
    before = snapshot(target)
    result = subprocess.run([sys.executable, "-I", "-B", str(script)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "checksum" in result.stdout + result.stderr
    assert snapshot(target) == before


def test_exact_catalog_skill_is_not_redirected_to_a_recorded_substring(repo, target):
    write(repo / "skills/demo-extra/SKILL.md", "# Extra v1\n")
    ok(cli(repo, "add", "skill", "demo-extra", target))
    write(repo / "skills/demo-extra/SKILL.md", "# Extra v2\n")
    before = snapshot(target)
    result = cli(repo, "update", "skill", "demo", target)
    assert result.returncode != 0
    assert "vibe add skill" in result.stdout + result.stderr
    assert snapshot(target) == before
    assert not (target / ".agents/skills/demo").exists()


def test_manifest_exact_dependency_does_not_update_recorded_substring(repo, target):
    write(repo / "skills/demo-extra/SKILL.md", "# Extra v1\n")
    ok(cli(repo, "add", "skill", "demo-extra", target))
    ok(cli(repo, "add", "manifest", "office", target))
    write(repo / "skills/demo-extra/SKILL.md", "# Extra v2\n")
    write(repo / "manifests/office/skills.txt", "demo\n")
    write(repo / "manifests/office/CLAUDE.md", "# Office v2\n")
    extra = target / ".agents/skills/demo-extra"
    before = snapshot(extra)
    skill_records = records(target)["skills"]
    result = cli(repo, "update", "manifest", "office", target)
    ok(result)
    assert "SKIP  demo " in result.stdout
    assert snapshot(extra) == before
    assert records(target)["skills"] == skill_records
    assert not (target / ".agents/skills/demo").exists()
    assert (target / "CLAUDE.md").read_text() == "# Office v2\n"


def test_manifest_skips_deleted_dependency_with_missing_recorded_source(repo, target):
    write(repo / "manifests/office/skills.txt", "demo\n")
    ok(cli(repo, "add", "manifest", "office", target))
    shutil.rmtree(target / ".agents/skills/demo")
    shutil.rmtree(repo / "skills/demo")
    write(repo / "manifests/office/CLAUDE.md", "# Office v2\n")
    result = cli(repo, "update", "manifest", "office", target)
    ok(result)
    assert "SKIP  demo " in result.stdout
    assert not (target / ".agents/skills/demo").exists()
    assert (target / "CLAUDE.md").read_text() == "# Office v2\n"


def test_legacy_manifest_explicit_empty_provider_selects_github_default(repo, target):
    install_real_manifest(repo, "vibe-coding")
    write(target / "CLAUDE.md", "# Legacy instructions\n")
    result = cli(repo, "update", "manifest", "vibe-coding", target,
                 "--provider=", "--scenario=", "--owner=", "--org=", "--repo=", "--email=")
    ok(result)
    assert (target / ".github/CODEOWNERS").is_file()
    assert (target / ".github/workflows/ci.yml").is_file()
    assert not (target / ".git").exists()
    before = snapshot(target)
    ok(cli(repo, "update", "manifest", "vibe-coding", target))
    assert snapshot(target) == before


def test_manifest_update_rejects_legacy_target_without_any_installed_resource(repo, target):
    before = snapshot(target)
    result = cli(repo, "update", "manifest", "office", target)
    assert result.returncode != 0
    assert "vibe add manifest" in result.stdout + result.stderr
    assert snapshot(target) == before
    assert not (target / "CLAUDE.md").exists()


def test_manifest_update_migrates_legacy_target_with_one_existing_resource(repo, target):
    write(target / ".cursor/rules/office.mdc", "# Legacy installed rule\n")
    ok(cli(repo, "update", "manifest", "office", target))
    assert (target / "CLAUDE.md").read_text() == "# Office v1\n"
    assert records(target)["manifests"]["office"]["source"] == "manifests/office"
    assert len(backups(target)) == 1


@pytest.mark.parametrize("name,scenario", [
    ("ui-testing", "unknown-scenario"),
    ("tutor", "../course-learning"),
    ("vibe-coding", "fullstack-web,unknown-scenario"),
])
def test_invalid_scenario_fails_preflight_without_project_changes(repo, target, name, scenario):
    install_real_manifest(repo, name)
    write(target / "CLAUDE.md", "# Legacy installed context\n")
    options = [f"--scenario={scenario}"]
    if name == "vibe-coding":
        options += ["--provider=git", "--owner=", "--org=", "--repo=", "--email="]
    before = snapshot(target)
    result = cli(repo, "update", "manifest", name, target, *options)
    assert result.returncode != 0
    assert "scenario" in result.stdout + result.stderr
    assert snapshot(target) == before
    assert not backups(target)


def test_standalone_restore_rejects_symlink_in_target_ancestor(repo, tmp_path):
    parent = tmp_path / "original-root"
    project = parent / "project"
    project.mkdir(parents=True)
    ok(cli(repo, "add", "skill", "demo", project))
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    ok(cli(repo, "update", "skill", "demo", project))
    relative_script = backups(project)[0].relative_to(parent)
    moved = tmp_path / "moved-root"
    parent.rename(moved)
    outside = tmp_path / "outside-root"
    write(outside / "project/.agents/skills/demo/SKILL.md", "# External sentinel\n")
    write(outside / "project/sentinel.txt", "must not change\n")
    parent.symlink_to(outside, target_is_directory=True)
    before = snapshot(outside)
    result = subprocess.run([sys.executable, "-I", "-B", str(moved / relative_script)],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert snapshot(outside) == before


def test_restore_preflights_recorded_created_directories_before_any_file_change(repo, target):
    ok(cli(repo, "add", "skill", "demo", target))
    write(repo / "skills/demo/SKILL.md", "# Demo v2\n")
    ok(cli(repo, "update", "skill", "demo", target))
    script = backups(target)[0]
    receipt = script.parent / "changes.json"
    data = json.loads(receipt.read_text())
    data.setdefault("created_directories", []).append("../outside-root")
    write(receipt, json.dumps(data))
    before = snapshot(target)
    result = subprocess.run([sys.executable, "-I", "-B", str(script)], capture_output=True, text=True)
    assert result.returncode != 0
    assert snapshot(target) == before


def test_manifest_update_shared_external_leaf_symlink_is_a_noop(repo, target, tmp_path):
    ok(cli(repo, "add", "manifest", "office", target))
    outside = write(tmp_path / "external-agent.md", "# Shared external agent\n")
    source_link = repo / "manifests/office/.claude/agents/shared.md"
    source_link.symlink_to(outside)
    installed_link = target / ".claude/agents/shared.md"
    installed_link.symlink_to(outside)
    before = snapshot(target)
    external_before = (outside.read_bytes(), outside.stat().st_mode, outside.stat().st_mtime_ns)
    ok(cli(repo, "update", "manifest", "office", target))
    assert snapshot(target) == before
    assert installed_link.is_symlink()
    assert os.readlink(installed_link) == str(outside)
    assert (outside.read_bytes(), outside.stat().st_mode, outside.stat().st_mtime_ns) == external_before
    assert not backups(target)


def test_abbreviated_skill_name_reuses_resolved_canonical_provenance(repo, target):
    manifest = repo / "manifests/office"
    write(manifest / "skills.txt", "demo\n")
    pinned = write(manifest / "skills/demo/SKILL.md", "# Pinned v1\n")
    ok(cli(repo, "add", "manifest", "office", target))
    assert records(target)["skills"]["demo"]["source"] == "manifests/office/skills/demo"
    write(pinned, "# Pinned v2\n")
    write(repo / "skills/demo/SKILL.md", "# Different catalog source\n")
    ok(cli(repo, "update", "skill", "dem", target))
    assert (target / ".agents/skills/demo/SKILL.md").read_text() == "# Pinned v2\n"
    assert records(target)["skills"]["demo"]["source"] == "manifests/office/skills/demo"
