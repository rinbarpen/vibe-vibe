"""Offline Git behavior and portable delivery of optional hosted collaboration."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

from vibe_tool.discovery import resolve_manifest
from vibe_tool.manifest_update import render_manifest
from vibe_tool.setup import check, setup


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests/vibe-coding"
SCRIPT = "scripts/git_collaboration.py"
RENDERER = "scripts/render_codegraph_workflow.py"
ASSETS = (SCRIPT, "references/git-collaboration.md",
          "references/git-collaboration-workflow.json", "references/git-collaboration-workflow.svg",
          "scripts/vibe-post-commit.sh")
spec = importlib.util.spec_from_file_location("git_collaboration", MANIFEST / SCRIPT)
flow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flow)


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()
            and ".vibe-tool/backups/" not in p.relative_to(root).as_posix()}


class Fixture(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="vibe branch flow ")
        self.addCleanup(directory.cleanup)
        # macOS exposes its temporary directory through /var -> /private/var.
        # The staging guard intentionally rejects aliases in the caller path.
        self.temp = Path(directory.name).resolve()
        patch = mock.patch.dict(os.environ, {
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
            "VIBE_PROJECTS_FILE": str(self.temp / "projects.json"),
            "PYTHONPATH": str(ROOT / "tools/vibe_tool/src"),
        })
        patch.start()
        self.addCleanup(patch.stop)

    def run_command(self, command, cwd=None):
        return subprocess.run([str(a) for a in command], cwd=cwd or self.temp,
                              text=True, capture_output=True, check=False, timeout=90)

    def ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def git(self, root, *args):
        return self.ok(self.run_command(["git", "-C", root, *args]))

    def repository(self, name="repo", commit=True):
        root = self.temp / name
        self.ok(self.run_command(["git", "init", "--quiet", "--template=",
                                  "--initial-branch=main", root]))
        self.git(root, "config", "user.name", "Fixture")
        self.git(root, "config", "user.email", "fixture@example.invalid")
        if commit:
            (root / "base.txt").write_text("baseline\n")
            self.git(root, "add", "--", "base.txt")
            self.git(root, "commit", "--quiet", "-m", "initial")
        return root

    def sources(self):
        repo = self.temp / "sources"
        path = repo / "manifests/vibe-coding"
        path.parent.mkdir(parents=True)
        shutil.copytree(MANIFEST, path, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (path / "skills.txt").write_text("# Unrelated dependencies omitted.\n")
        (repo / "skills").mkdir()
        (repo / "mine").mkdir()
        return repo

    def install(self, source, target):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup(source, "vibe-coding", target,
                                   agent="generic", provider="git"), 0)


class InspectionTests(Fixture):
    def test_local_default_needs_no_remote_issue_or_host_cli(self):
        root = self.repository()
        result = flow.inspect_repo(root, branch="feat/local-task")
        self.assertEqual(result["mode"], "local")
        self.assertIsNone(result["issue"])
        self.assertEqual(result["base"], "main")
        self.assertEqual(result["remotes"], [])
        self.assertFalse(result["network_performed"])
        self.assertFalse(result["dirty"])

    def test_remote_presence_does_not_enable_hosted_mode(self):
        root = self.repository()
        self.git(root, "remote", "add", "origin", "git@github.com:example/project.git")
        result = flow.inspect_repo(root)
        self.assertEqual(result["mode"], "local")
        self.assertTrue(result["hosted_available"])
        self.assertTrue(any("opt-in" in d for d in result["decisions"]))

    def test_hosted_mode_allows_pr_without_issue(self):
        root = self.repository()
        self.git(root, "remote", "add", "origin", "git@github.com:example/project.git")
        result = flow.inspect_repo(root, mode="hosted")
        self.assertEqual(result["selected_remote"]["provider"], "github")
        self.assertIsNone(result["issue"])
        referenced = flow.inspect_repo(root, mode="hosted", issue="42")
        self.assertEqual(referenced["issue"], {"reference": "42", "verified": False})

    def test_hosted_mode_missing_or_ambiguous_remote_is_explicit(self):
        root = self.repository()
        with self.assertRaisesRegex(flow.InspectionError, "configured remote"):
            flow.inspect_repo(root, mode="hosted")
        self.git(root, "remote", "add", "origin", "git@github.com:example/project.git")
        self.git(root, "remote", "add", "upstream", "git@gitlab.com:example/project.git")
        self.assertIsNone(flow.inspect_repo(root)["selected_remote"])
        with self.assertRaisesRegex(flow.InspectionError, "Multiple remotes"):
            flow.inspect_repo(root, mode="hosted")
        result = flow.inspect_repo(root, mode="hosted", remote="upstream")
        self.assertEqual(result["selected_remote"]["provider"], "gitlab")

    def test_unknown_host_needs_provider_but_local_path_is_plain_git(self):
        root = self.repository()
        self.git(root, "remote", "add", "origin", "ssh://git@forge.example/project/repo.git")
        with self.assertRaisesRegex(flow.InspectionError, "Unknown host"):
            flow.inspect_repo(root, mode="hosted")
        self.assertEqual(flow.inspect_repo(root, mode="hosted", provider="github")
                         ["selected_remote"]["provider"], "github")
        bare = self.temp / "remote.git"
        self.ok(self.run_command(["git", "init", "--bare", "--quiet", bare]))
        for url in (str(bare), bare.as_uri(), bare.as_uri().replace("file://", "file://localhost", 1)):
            self.git(root, "remote", "set-url", "origin", url)
            self.assertFalse(flow.inspect_repo(root)["hosted_available"])
            with self.assertRaisesRegex(flow.InspectionError, "local Git path"):
                flow.inspect_repo(root, mode="hosted", provider="github")

    def test_credentials_and_query_strings_are_not_reported(self):
        root = self.repository()
        self.git(root, "remote", "add", "origin",
                 "https://hidden-user:secret-token@github.com/example/repo.git?access_token=secret-query")
        result = flow.inspect_repo(root, mode="hosted")
        rendered = json.dumps(result)
        for secret in ("hidden-user", "secret-token", "secret-query", "access_token"):
            self.assertNotIn(secret, rendered)
        self.assertEqual(result["selected_remote"]["repository"], "example/repo")

    def test_separate_push_url_is_visible_without_credentials_or_network(self):
        root = self.repository()
        self.git(root, "remote", "add", "origin", "git@github.com:upstream/project.git")
        self.git(root, "remote", "set-url", "--push", "origin",
                 "https://user:push-secret@github.com:443/fork/project.git")
        result = flow.inspect_repo(root)
        self.assertEqual(result["selected_remote"]["push_target"]["repository"], "fork/project")
        self.assertNotIn("push-secret", json.dumps(result))
        self.assertTrue(any("targets differ" in d for d in result["decisions"]))

    def test_unborn_and_detached_head_are_facts_not_automatic_changes(self):
        root = self.repository(commit=False)
        result = flow.inspect_repo(root)
        self.assertTrue(result["head"]["unborn"])
        self.assertIsNone(result["base"])
        (root / "base.txt").write_text("baseline\n")
        self.git(root, "add", "--", "base.txt")
        self.git(root, "commit", "--quiet", "-m", "initial")
        self.git(root, "switch", "--detach")
        self.assertTrue(flow.inspect_repo(root)["head"]["detached"])

    def test_dirty_work_and_existing_branch_are_preserved(self):
        root = self.repository()
        (root / "user.txt").write_text("keep unrelated work\n")
        before = snapshot(root)
        result = flow.inspect_repo(root, branch="main")
        self.assertTrue(result["dirty"])
        self.assertTrue(any("branch exists" in d for d in result["decisions"]))
        self.assertEqual(snapshot(root), before)

    def test_actual_local_branches_merge_without_affecting_other_worktree(self):
        root = self.repository()
        self.git(root, "switch", "-c", "feat/one")
        (root / "one.txt").write_text("task one\n")
        self.git(root, "add", "--", "one.txt")
        self.git(root, "commit", "--quiet", "-m", "task one")
        self.git(root, "switch", "main")
        other = self.temp / "task two"
        self.git(root, "worktree", "add", "-b", "feat/two", str(other), "main")
        (other / "user.txt").write_text("task two unfinished\n")
        before = snapshot(other)
        report = flow.inspect_repo(root)
        branches = {b["name"]: b for b in report["branches"]}
        self.assertEqual(set(branches), {"main", "feat/one", "feat/two"})
        self.assertEqual(Path(branches["feat/two"]["worktrees"][0]).resolve(), other.resolve())
        self.git(root, "merge", "--ff-only", "feat/one")
        self.git(root, "branch", "-d", "feat/one")
        self.assertTrue((root / "one.txt").is_file())
        self.assertEqual(snapshot(other), before)
        self.assertIn("feat/two", {b["name"] for b in flow.inspect_repo(root)["branches"]})

    def test_inspection_uses_only_read_queries_and_changes_no_git_files(self):
        root = self.repository()
        self.git(root, "remote", "add", "origin", "git@gitee.com:example/project.git")
        before = snapshot(root)
        original = subprocess.run
        seen = []
        def query(command, **kwargs):
            self.assertEqual(command[0], "git")
            self.assertIn("--no-optional-locks", command)
            self.assertIn(command[6], {"rev-parse", "symbolic-ref", "for-each-ref",
                                     "worktree", "remote", "check-ref-format", "status"})
            if command[6] == "worktree":
                self.assertEqual(command[7], "list")
            seen.append(command)
            return original(command, **kwargs)
        with mock.patch.object(flow.subprocess, "run", side_effect=query):
            result = flow.inspect_repo(root, mode="hosted", issue="42")
        self.assertFalse(result["network_performed"])
        self.assertTrue(seen)
        self.assertEqual(snapshot(root), before)

    def test_older_git_porcelain_fallback_is_read_only_and_rejects_bad_records(self):
        root = self.repository()
        original = flow.git
        def old_git(path, *args, **kwargs):
            if args == ("worktree", "list", "--porcelain", "-z"):
                raise flow.InspectionError("old Git does not support -z")
            return original(path, *args, **kwargs)
        before = snapshot(root)
        with mock.patch.object(flow, "git", side_effect=old_git):
            self.assertEqual(flow.inspect_repo(root)["worktrees"][0]["branch"], "main")
        self.assertEqual(snapshot(root), before)
        with mock.patch.object(flow, "git", side_effect=[flow.InspectionError("no -z"),
                               "worktree /tmp/ambiguous\nunrecognized-path-fragment\n"]):
            with self.assertRaisesRegex(flow.InspectionError, "Ambiguous"):
                flow.worktrees(root)
        with mock.patch.object(flow, "git", return_value="worktree /tmp/odd\r\0HEAD abc\0\0"):
            self.assertEqual(flow.worktrees(root)[0]["path"], "/tmp/odd\r")

    def test_invalid_branch_or_missing_git_repo_returns_no_mutations(self):
        root = self.repository()
        with self.assertRaises(flow.InspectionError):
            flow.inspect_repo(root, branch="bad..branch")
        empty = self.temp / "not a repo"
        empty.mkdir()
        result = self.run_command([sys.executable, MANIFEST / SCRIPT, "inspect", "--root", empty])
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["network_performed"])
        self.assertEqual(list(empty.iterdir()), [])


class DeliveryTests(Fixture):
    def render(self, root, check_only=True):
        command = [sys.executable, root / RENDERER, "--source", root / ASSETS[2],
                   "--output", root / ASSETS[3]]
        return self.run_command(command + (["--check"] if check_only else []), cwd=root)

    def test_workflow_reproduces_and_checks_are_read_only(self):
        self.ok(self.render(MANIFEST))
        root = self.temp / "diagram"
        for name in (*ASSETS[1:], RENDERER):
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(MANIFEST / name, dest)
        before = snapshot(root)
        self.ok(self.render(root, False))
        self.assertEqual(snapshot(root), before)
        workflow = json.loads((root / ASSETS[2]).read_text())
        nodes = {node["id"]: node for node in workflow["nodes"]}
        self.assertEqual(nodes["decision"]["kind"], "human")
        edges = {(e["from"], e["to"]) for e in workflow["edges"]}
        self.assertTrue({("verify", "local_scope"), ("local_scope", "local_merge"),
                         ("verify", "issue"), ("issue", "decision"),
                         ("decision", "scope_wait"), ("review_wait", "review"),
                         ("checks", "ci_wait"), ("restore", "done")} <= edges)
        self.assertEqual(ET.parse(root / ASSETS[3]).getroot().tag,
                         "{http://www.w3.org/2000/svg}svg")
        (root / ASSETS[3]).unlink()
        before = snapshot(root)
        self.assertEqual(self.render(root).returncode, 1)
        self.assertEqual(snapshot(root), before)

    @unittest.skipIf(os.name == "nt", "optional post-commit helper uses POSIX shell")
    def test_post_commit_host_probe_is_opt_in_even_when_gh_is_installed(self):
        binary = self.temp / "fake bin"
        binary.mkdir()
        gh = binary / "gh"
        gh.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$VIBE_GH_TEST_LOG"\n')
        gh.chmod(0o755)
        checker = binary / "vibe-check"
        checker.write_text("#!/bin/sh\nexit 0\n")
        checker.chmod(0o755)
        log = self.temp / "gh-calls.txt"
        with mock.patch.dict(os.environ, {
            "PATH": str(binary) + os.pathsep + os.environ["PATH"],
            "VIBE_GH_TEST_LOG": str(log),
        }):
            self.ok(self.run_command(["bash", MANIFEST / "scripts/vibe-post-commit.sh"]))
            self.assertFalse(log.exists())
            self.ok(self.run_command(["bash", MANIFEST / "scripts/vibe-post-commit.sh", "--hosted-github"]))
            self.assertEqual(log.read_text(), "pr status\n")

    def test_portable_setup_ships_links_inspector_command_and_reproducible_diagram(self):
        source = self.sources()
        target = self.temp / "project"
        self.install(source, target)
        for name in ASSETS:
            if name.endswith(".md"):
                # Portable rules deliberately rewrite command links into the
                # neutral bundle rather than retaining a legacy Cursor path.
                text = (target / name).read_text()
                for link in re.findall(r"\]\(([^)#]+)\)", text):
                    if "://" not in link:
                        self.assertTrue((target / name).parent.joinpath(link).is_file(), link)
            else:
                self.assertEqual((target / name).read_bytes(), (MANIFEST / name).read_bytes())
        self.assertTrue((target / "rules/vibe-coding/commands/git-flow/COMMAND.md").is_file())
        command = target / "rules/vibe-coding/commands/git-flow/COMMAND.md"
        for link in re.findall(r"\]\(([^)#]+)\)", command.read_text()):
            self.assertTrue(command.parent.joinpath(link).is_file(), link)
        self.ok(self.render(target))
        self.ok(self.run_command(["git", "init", "--quiet", "--initial-branch=main", target]))
        result = self.run_command([sys.executable, target / SCRIPT, "inspect", "--root", target])
        self.assertEqual(json.loads(self.ok(result))["mode"], "local")
        self.assertFalse((target / ".github").exists())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check(target), 0)

    def test_portable_refresh_and_standalone_rollback_preserve_business_data(self):
        source = self.sources()
        target = self.temp / "project"
        target.mkdir()
        (target / "README.md").write_text("user business readme\n")
        self.install(source, target)
        before = snapshot(target)
        script = source / "manifests/vibe-coding" / SCRIPT
        script.write_text(script.read_text() + "\n# Updated local inspection fixture\n")
        self.install(source, target)
        self.assertEqual((target / SCRIPT).read_bytes(), script.read_bytes())
        self.assertEqual((target / "README.md").read_text(), "user business readme\n")
        restore = sorted((target / ".vibe-tool/backups").glob("*/restore.py"))[-1]
        self.ok(self.run_command([sys.executable, restore]))
        self.assertEqual(snapshot(target), before)

    @unittest.skipIf(os.name == "nt", "legacy init/add use POSIX shell; portable setup is tested on Windows")
    def test_legacy_init_add_render_and_update_include_all_resources(self):
        source = self.sources()
        for operation in ("init", "add"):
            target = self.temp / (operation + " project")
            target.mkdir()
            args = [operation, "vibe-coding"] if operation == "init" else ["add", "manifest", "vibe-coding"]
            env = dict(os.environ, VIBE_HOME=str(source))
            def cli(*extra):
                return subprocess.run([sys.executable, "-m", "vibe_tool", *extra],
                                      env=env, cwd=source, capture_output=True, text=True, timeout=90)
            self.ok(cli(*args, str(target), "--provider=git", "--dry-run"))
            self.assertEqual(list(target.iterdir()), [])
            self.ok(cli(*args, str(target), "--provider=git"))
            self.assertTrue((target / ".cursor/commands/git-flow/COMMAND.md").is_file())
            for name in ASSETS:
                self.assertEqual((target / name).read_bytes(), (MANIFEST / name).read_bytes())
            self.ok(self.render(target))
            before = snapshot(target)
            old = target / ASSETS[1]
            old.write_text("# Old local collaboration contract\n")
            self.ok(cli("update", "manifest", "vibe-coding", str(target)))
            self.assertEqual(old.read_bytes(), (MANIFEST / ASSETS[1]).read_bytes())
            restore = sorted((target / ".vibe-tool/backups").glob("*/restore.py"))[-1]
            self.ok(self.run_command([sys.executable, restore]))
            self.assertEqual(old.read_text(), "# Old local collaboration contract\n")
            old.write_bytes((MANIFEST / ASSETS[1]).read_bytes())
            self.assertEqual(snapshot(target), before)
        stage = self.temp / "rendered update"
        target = self.temp / "target"
        target.mkdir()
        paths = render_manifest(resolve_manifest(source / "manifests", "vibe-coding"),
                                stage, target, {"provider": "git"})
        self.assertTrue(set(map(Path, ASSETS)) <= set(paths))


if __name__ == "__main__":
    unittest.main()
