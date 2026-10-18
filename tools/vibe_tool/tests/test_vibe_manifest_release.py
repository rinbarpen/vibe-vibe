"""Contract checks for the host-independent vibe-coding release scaffold."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests" / "vibe-coding"
INIT = MANIFEST / "scripts" / "vibe-init.sh"
GUARD = MANIFEST / "scripts" / "version_guard.py"


def run(*args: str | Path, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(a) for a in args], cwd=cwd, text=True, capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(ROOT / "tools" / "vibe_tool" / "src")}, check=False,
    )


def load_guard():
    spec = importlib.util.spec_from_file_location("version_guard", GUARD)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("provider", ["git", "github", "gitlab", "gitee"])
def test_init_provider_and_preserve_existing(tmp_path: Path, provider: str) -> None:
    target = tmp_path / provider
    first = run("bash", INIT, target, f"--provider={provider}")
    assert first.returncode == 0, first.stderr
    assert (target / "VERSION").read_text().strip() == "0.1.0"
    assert "## [Unreleased]" in (target / "CHANGELOG.md").read_text()
    assert (target / "scripts" / "version_guard.py").is_file()
    assert (target / ".git").is_dir()
    assert (target / ".github").exists() == (provider == "github")
    assert (target / ".gitlab-ci.yml").exists() == (provider == "gitlab")
    assert (target / ".workflow" / "vibe-ci.yml").exists() == (provider == "gitee")
    assert (target / ".workflow" / "vibe-release.yml").exists() == (provider == "gitee")
    run("git", "remote", "add", "origin", "https://example.invalid/project.git", cwd=target)
    (target / "VERSION").write_text("1.4.2\n")
    (target / "CHANGELOG.md").write_text("# custom changelog\n")
    if provider == "github":
        (target / ".github" / "workflows" / "ci.yml").write_text("# custom CI\n")
    again = run("bash", INIT, target, f"--provider={provider}")
    assert again.returncode == 0, again.stderr
    assert (target / "VERSION").read_text() == "1.4.2\n"
    assert (target / "CHANGELOG.md").read_text() == "# custom changelog\n"
    assert run("git", "remote", "get-url", "origin", cwd=target).stdout.strip() == "https://example.invalid/project.git"
    if provider == "github":
        assert (target / ".github" / "workflows" / "ci.yml").read_text() == "# custom CI\n"


def test_dry_run_does_not_create_target(tmp_path: Path) -> None:
    target = tmp_path / "absent"
    result = run("bash", INIT, target, "--provider=gitee", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert not target.exists()
    assert "WILL  .workflow/vibe-ci.yml" in result.stdout


def test_cli_init_and_add_provider_dry_run(tmp_path: Path) -> None:
    new_target = tmp_path / "new"
    initialized = run(sys.executable, "-m", "vibe_tool", "init", "vibe-coding", new_target,
                      "--provider=gitee", "--dry-run", cwd=ROOT)
    assert initialized.returncode == 0, initialized.stderr
    assert not new_target.exists()
    assert "WILL  .workflow/vibe-ci.yml" in initialized.stdout
    existing = tmp_path / "existing"
    existing.mkdir()
    added = run(sys.executable, "-m", "vibe_tool", "add", "manifest", "vibe-coding", existing,
                "--provider=gitlab", "--dry-run", cwd=ROOT)
    assert added.returncode == 0, added.stderr
    assert "WILL  .gitlab-ci.yml" in added.stdout
    assert list(existing.iterdir()) == []


def test_existing_package_version_and_conflict_preflight(tmp_path: Path) -> None:
    target = tmp_path / "project"
    target.mkdir()
    (target / "package.json").write_text('{"version": "2.1.0"}')
    good = run("bash", INIT, target, "--provider=git", "--no-git")
    assert good.returncode == 0, good.stderr
    assert (target / "VERSION").read_text() == "2.1.0\n"
    other = tmp_path / "conflict"
    other.mkdir()
    (other / "package.json").write_text('{"version": "2.1.0"}')
    (other / "pyproject.toml").write_text('[project]\nversion = "2.2.0"\n')
    bad = run("bash", INIT, other, "--provider=git")
    assert bad.returncode != 0
    assert "conflicting package versions" in bad.stderr
    assert not (other / "VERSION").exists()
    assert not (other / "MANIFEST.md").exists()
    java = tmp_path / "java"
    java.mkdir()
    (java / "pom.xml").write_text('<project xmlns="http://maven.apache.org/POM/4.0.0"><version>3.2.1</version></project>')
    adopted = run("bash", INIT, java, "--provider=git", "--no-git")
    assert adopted.returncode == 0, adopted.stderr
    assert (java / "VERSION").read_text() == "3.2.1\n"


def committed_repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / "VERSION").write_text("0.1.0\n")
    (root / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n")
    for command in (("git", "init", "-q"), ("git", "config", "user.email", "test@example.invalid"),
                    ("git", "config", "user.name", "Test"), ("git", "add", "."),
                    ("git", "commit", "-qm", "initial")):
        result = run(*command, cwd=root)
        assert result.returncode == 0, result.stderr
    return root


def test_version_bump_and_exact_notes(tmp_path: Path) -> None:
    root = committed_repo(tmp_path)
    assert run(sys.executable, GUARD, "--root", root, "check", "--base-ref", "HEAD").returncode == 0
    (root / "VERSION").write_text("0.2.0-rc.1\n")
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n## [0.2.0-rc.1] - 2026-10-01\n\n"
        "### Added\n- Add provider selection.\n\n## [0.1.0] - 2026-09-01\n"
        "\n### Fixed\n- Old fix.\n"
    )
    assert run(sys.executable, GUARD, "--root", root, "check", "--base-ref", "HEAD").returncode == 0
    assert run(sys.executable, GUARD, "--root", root, "check", "--tag", "v0.2.0-rc.1").returncode == 0
    notes = tmp_path / "notes.md"
    result = run(sys.executable, GUARD, "--root", root, "notes", "--tag", "v0.2.0-rc.1", "--output", notes)
    assert result.returncode == 0, result.stderr
    assert "provider selection" in notes.read_text()
    assert "Old fix" not in notes.read_text()
    assert run(sys.executable, GUARD, "--root", root, "check", "--tag", "v0.2.0").returncode != 0
    (root / "VERSION").write_text("0.2.0-hotfix.1\n")
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [0.2.0-hotfix.1] - 2026-10-01\n\n### Fixed\n- Fix urgent crash.\n"
    )
    assert run(sys.executable, GUARD, "--root", root, "check", "--tag", "v0.2.0-hotfix.1").returncode == 0


@pytest.mark.parametrize("changelog", [
    "# Changelog\n## [Unreleased]\n",
    "# Changelog\n## [0.2.0]\n### Fixed\n",
    "# Changelog\n## [0.2.0]\n### Fixed\n- TODO\n",
    "# Changelog\n## [0.2.0]\n### Fixed\n- Real fix.\n## [0.2.0]\n### Added\n- Again.\n",
])
def test_invalid_changelog_fails(tmp_path: Path, changelog: str) -> None:
    root = committed_repo(tmp_path)
    (root / "VERSION").write_text("0.2.0\n")
    (root / "CHANGELOG.md").write_text(changelog)
    assert run(sys.executable, GUARD, "--root", root, "check", "--base-ref", "HEAD").returncode == 1


def test_package_mismatch_and_preexisting_section_fail(tmp_path: Path) -> None:
    root = committed_repo(tmp_path)
    (root / "package.json").write_text('{"version":"9.9.9"}')
    assert run(sys.executable, GUARD, "--root", root, "check").returncode == 1
    (root / "package.json").write_text('{"version":"0.1.0"}')
    (root / "CHANGELOG.md").write_text("# Changelog\n## [0.2.0]\n### Added\n- Prepared.\n")
    run("git", "add", ".", cwd=root)
    run("git", "commit", "-qm", "prepared", cwd=root)
    (root / "VERSION").write_text("0.2.0\n")
    (root / "package.json").write_text('{"version":"0.2.0"}')
    assert run(sys.executable, GUARD, "--root", root, "check", "--base-ref", "HEAD").returncode == 1


class FakeResponse:
    status = 201

    def __init__(self, data: bytes = b'{"id":42}') -> None:
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.data


def test_mocked_provider_release_requests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = committed_repo(tmp_path)
    (root / "CHANGELOG.md").write_text("# Changelog\n## [0.1.0]\n### Added\n- Initial release.\n")
    module = load_guard()
    sent = []

    def fake_open(req, timeout):
        sent.append(req)
        return FakeResponse()

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_open)
    monkeypatch.setenv("CI_JOB_TOKEN", "job-token")
    module.publish_gitlab(root, "v0.1.0", "99", "https://gitlab.example/api/v4", "")
    assert sent[-1].get_header("Job-token") == "job-token"
    assert json.loads(sent[-1].data)["description"].startswith("## [0.1.0]")
    monkeypatch.setenv("GITEE_TOKEN", "gitee-token")
    (root / "dist").mkdir()
    (root / "dist" / "sample.zip").write_bytes(b"artifact")
    module.publish_gitee(root, "v0.1.0", "org", "repo", "https://gitee.example/api/v5")
    assert len(sent) == 3  # GitLab release, Gitee release, Gitee asset
    assert b"sample.zip" in sent[-1].data
    assert "Initial release" in urllib.parse.parse_qs(sent[-2].data.decode())["body"][0]
    (root / "dist" / "sample.zip").unlink()
    sent.clear()
    module.publish_gitee(root, "v0.1.0", "org", "repo", "https://gitee.example/api/v5")
    assert len(sent) == 1  # no asset when dist is empty

    def fail_open(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 403, "forbidden", {}, io.BytesIO())

    monkeypatch.setattr(module.urllib.request, "urlopen", fail_open)
    with pytest.raises(module.GuardError, match="HTTP 403"):
        module.publish_gitee(root, "v0.1.0", "org", "repo", "https://gitee.example/api/v5")
    with pytest.raises(module.GuardError, match="HTTP 403"):
        module.publish_gitlab(root, "v0.1.0", "99", "https://gitlab.example/api/v4", "")


def test_all_pipeline_yaml_parses() -> None:
    yaml = pytest.importorskip("yaml")
    github = sorted((MANIFEST / ".github" / "workflows").glob("*.yml"))
    assert len(github) == 12
    for path in [*github, *sorted((MANIFEST / "platforms").rglob("*.yml"))]:
        data = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        assert isinstance(data, dict), path
        if path in github:
            assert "on" in data and "jobs" in data, path
        elif "gitee" in path.parts:
            assert "triggers" in data and "stages" in data, path
        else:
            assert "validate" in data and "release" in data, path
