"""Reader-first docs, a real read-only checker, and portable manifest assets."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from test_codegraph_manifest import MANIFEST, ROOT, cli, ok, repo, run, snapshot


CHECKER = MANIFEST / "commands/update-docs/update_docs.py"
ASSETS = (
    "references/readme-guide.md",
    "references/setup-guide.md",
    "references/docs-readability-workflow.json",
    "references/docs-readability-workflow.svg",
)
RENDERER = "scripts/render_codegraph_workflow.py"


def audit(root, *paths):
    return run([sys.executable, "-B", CHECKER, "--root", root, "--format", "json", *paths], cwd=root)


def test_reader_contract_replaces_mandatory_decoration_and_fake_scanning():
    guide = (MANIFEST / ASSETS[0]).read_text()
    for term in ("读者", "首屏", "预期结果", "不强制", "不是可读性通过证明"):
        assert term in guide
    for obsolete in ("每个点一行，附带 emoji", "没有 badge", "### 8. 许可证"):
        assert obsolete not in guide
    command = (MANIFEST / "commands/update-docs/COMMAND.md").read_text()
    assert "--root" in command and "预期结果" in command
    assert "由用户确认后写入" not in command
    assert "占位脚本" not in CHECKER.read_text()
    for name in ("AGENTS.md", "CLAUDE.md"):
        assert "reader-first writing contract" in (ROOT / name).read_text()


def test_homepages_route_to_details_instead_of_embedding_every_catalog():
    for name, suffix in (("README.md", ""), ("README_EN.md", "_EN")):
        text = (ROOT / name).read_text()
        # A budget for this landing page, not a universal Markdown quality rule.
        assert len(text.splitlines()) < 200
        assert "vibe list manifests" in "\n".join(text.splitlines()[:65])
        assert f"docs/cli-reference{suffix}.md" in text
        assert f"docs/catalog{suffix}.md" in text
    assert len((MANIFEST / "README.md").read_text().splitlines()) < 160


def test_checker_handles_nested_fences_encoded_links_and_heading_anchors_read_only(tmp_path):
    (tmp_path / "guide space.md").write_text("# Guide\n\n## Save settings\n")
    (tmp_path / "README.md").write_text(
        "# Example\n\n[Guide](guide%20space.md#save-settings)\n\n"
        "````markdown\n```bash\nexample\n```\n[Not a real link](missing.md)\n````\n"
    )
    before = snapshot(tmp_path)
    result = audit(tmp_path, "README.md")
    ok(result)
    report = json.loads(result.stdout)
    assert report["errors"] == []
    assert report["files_checked"] == 1
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("content,code", [
    ("# Example\n\n[Missing](missing.md)\n", "missing-link"),
    ("# Example\n\n[Wrong](README.md#not-present)\n", "missing-anchor"),
    ("# Example\n\n```bash\necho hi\n", "unclosed-fence"),
])
def test_checker_reports_real_structure_errors_without_writes(tmp_path, content, code):
    (tmp_path / "README.md").write_text(content)
    before = snapshot(tmp_path)
    result = audit(tmp_path, "README.md")
    assert result.returncode == 1, result.stdout + result.stderr
    assert code in {issue["code"] for issue in json.loads(result.stdout)["errors"]}
    assert snapshot(tmp_path) == before


def test_readability_signals_are_advisory_not_a_fake_quality_score(tmp_path):
    (tmp_path / "README.md").write_text("# Example\n\n" + "Long paragraph. " * 90 + "\n")
    result = audit(tmp_path, "README.md")
    ok(result)
    report = json.loads(result.stdout)
    assert any(w["code"] == "long-paragraph" for w in report["warnings"])
    assert report["status"] == "STRUCTURE_OK"
    assert "score" not in report


def test_checker_rejects_missing_or_outside_scope_inputs_without_writes(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n")
    for path in ("missing.md", outside):
        before = snapshot(tmp_path)
        result = audit(project, path)
        assert result.returncode == 2
        assert snapshot(tmp_path) == before


def check_installed_docs(target):
    for relative in ASSETS:
        assert (target / relative).read_bytes() == (MANIFEST / relative).read_bytes()
    assert (target / ".cursor/references/readme-guide.md").read_bytes() == (MANIFEST / ASSETS[0]).read_bytes()
    result = run([sys.executable, "-B", target / ".cursor/commands/update-docs/update_docs.py",
                  "--root", target, "--format", "json", "README.md", *ASSETS[:2], ".cursor/references/readme-guide.md"], cwd=target)
    ok(result)
    assert json.loads(result.stdout)["errors"] == []
    before = snapshot(target)
    command = [sys.executable, "-B", target / RENDERER, "--source", target / ASSETS[2],
               "--output", target / ASSETS[3], "--check"]
    ok(run(command, cwd=target))
    assert snapshot(target) == before
    assert "readme-guide.md" in (target / "MANIFEST.md").read_text()


@pytest.mark.parametrize("operation", ["init", "add"])
def test_real_install_distributes_readability_contract_and_checker(repo, tmp_path, operation):
    target = tmp_path / "readable project with spaces"
    if operation == "add":
        target.mkdir()
    args = ["init", "vibe-coding", target] if operation == "init" else ["add", "manifest", "vibe-coding", target]
    before = snapshot(target)
    ok(cli(repo, *args, "--provider=git", "--dry-run"))
    assert snapshot(target) == before
    ok(cli(repo, *args, "--provider=git"))
    check_installed_docs(target)


def test_update_preserves_project_readme_and_restores_doc_resources(repo, tmp_path):
    target = tmp_path / "existing readable project"
    ok(cli(repo, "init", "vibe-coding", target, "--provider=git"))
    readme = "# User product\n\nKeep the product's actual instructions.\n"
    (target / "README.md").write_text(readme)
    for relative in ASSETS:
        (target / relative).unlink()
    checker = target / ".cursor/commands/update-docs/update_docs.py"
    checker.write_text("# Older user-local checker\n")
    before = snapshot(target)
    ok(cli(repo, "update", "manifest", "vibe-coding", target, "--dry-run"))
    assert snapshot(target) == before
    ok(cli(repo, "update", "manifest", "vibe-coding", target))
    assert (target / "README.md").read_text() == readme
    for relative in ASSETS:
        assert (target / relative).read_bytes() == (MANIFEST / relative).read_bytes()
    ok(run([sys.executable, "-B", checker, "--root", target, "README.md"], cwd=target))
    restores = list((target / ".vibe-tool/backups").glob("*/restore.py"))
    assert len(restores) == 1
    ok(run([sys.executable, "-I", "-B", restores[0]], cwd=target))
    assert snapshot(target) == before
