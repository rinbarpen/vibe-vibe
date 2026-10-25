"""Installer, native agent, skill discovery and public vibe CLI regressions."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch


MANIFEST = Path(__file__).resolve().parents[1]
ROOT = MANIFEST.parents[1]
spec = importlib.util.spec_from_file_location("unity_game_installer", MANIFEST / "scripts/install_manifest.py")
installer = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(installer)


def snapshot(root: Path) -> dict[str, tuple[str, int]]:
    return {str(p.relative_to(root)): (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / "source"
        self.target = self.base / "game with spaces"
        files = {
            "CLAUDE.md": "# Unity game\n", "AGENTS.md": "# Agents\n", "README.md": "# Read me\n",
            "agents/subagent-roles.md": "### 1. `game-producer`\n",
            ".claude/agents/game-producer.md": "claude prompt\n",
            ".codex/agents/game-producer.toml": "codex prompt\n",
            "references/lifecycle.md": "lifecycle\n", "templates/gdd.md": "gdd template\n",
            "scripts/unity_cli.py": "print('helper')\n",
            "scripts/init-unity-game.sh": "installer wrapper\n",
            "scripts/install_manifest.py": "installer implementation\n",
            **{f"templates/state/{n}.md": f"# {n}\npending\n" for n in ("status", "tasks", "decisions", "artifacts")},
        }
        for name, text in files.items():
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.mock_source = patch.object(installer, "SOURCE", self.source)
        self.mock_source.start()
        self.addCleanup(self.mock_source.stop)

    def install(self, force=False, dry_run=False):
        return installer.install(self.target, force, dry_run)

    def test_complete_install_and_state_seeds(self):
        self.assertEqual(self.install(), 0)
        for src, relative, _ in installer.source_files():
            self.assertEqual((self.target / relative).read_bytes(), src.read_bytes(), str(relative))
        ledger = json.loads((self.target / installer.LEDGER).read_text())
        self.assertNotIn(".unity-game/state/status.md", ledger["files"])
        self.assertFalse((self.target / ".unity-game/scripts/init-unity-game.sh").exists())
        self.assertTrue((self.target / ".unity-game/deliverables").is_dir())
        self.assertTrue((self.target / ".unity-game/runs").is_dir())

    def test_repeated_install_is_byte_and_mtime_identical(self):
        self.install()
        before = snapshot(self.target)
        self.install()
        self.assertEqual(snapshot(self.target), before)

    def test_dry_run_new_directory_has_no_side_effects(self):
        self.assertEqual(self.install(dry_run=True), 0)
        self.assertFalse(self.target.exists())

    def test_dry_run_force_existing_has_no_side_effects(self):
        self.install()
        (self.source / "CLAUDE.md").write_text("updated template")
        before = snapshot(self.target)
        self.install(force=True, dry_run=True)
        self.assertEqual(snapshot(self.target), before)

    def test_force_refreshes_owned_and_backs_up_edits(self):
        self.install()
        dest = self.target / "CLAUDE.md"
        dest.write_text("local managed edit")
        (self.source / "CLAUDE.md").write_text("updated scaffold")
        self.install()
        self.assertEqual(dest.read_text(), "local managed edit")
        self.install(force=True)
        self.assertEqual(dest.read_text(), "updated scaffold")
        backups = list((self.target / ".unity-game/backups").glob("*/CLAUDE.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "local managed edit")

    def test_force_preserves_unowned_root_and_agent_files(self):
        for name in ("CLAUDE.md", "AGENTS.md", ".claude/agents/game-producer.md"):
            p = self.target / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("existing user content")
        self.install(force=True)
        self.install(force=True)
        for name in ("CLAUDE.md", "AGENTS.md", ".claude/agents/game-producer.md"):
            self.assertEqual((self.target / name).read_text(), "existing user content")

    def test_project_assets_state_and_deliverables_preserved_on_force(self):
        self.install()
        paths = ("Assets/Scene.unity", "Assets/Scene.unity.meta", "Packages/manifest.json",
                 "ProjectSettings/ProjectVersion.txt", ".unity-game/state/status.md",
                 ".unity-game/deliverables/gdd.md", ".unity-game/runs/previous/result.json")
        for relative in paths:
            p = self.target / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("existing " + relative)
        self.install(force=True)
        for relative in paths:
            self.assertEqual((self.target / relative).read_text(), "existing " + relative)

    def test_symlink_file_rejected_before_any_copy(self):
        self.target.mkdir()
        other = self.base / "outside"
        other.write_text("outside")
        (self.target / "AGENTS.md").symlink_to(other)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.install(force=True)
        self.assertFalse((self.target / "CLAUDE.md").exists())
        self.assertEqual(other.read_text(), "outside")

    def test_symlink_parent_rejected_before_any_copy(self):
        self.target.mkdir()
        other = self.base / "outside"
        other.mkdir()
        (self.target / ".claude").symlink_to(other, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.install()
        self.assertEqual(list(other.iterdir()), [])
        self.assertFalse((self.target / "CLAUDE.md").exists())

    def test_required_skill_destinations_preflight_before_scaffold_write(self):
        (self.source / "skills.txt").write_text("git-manager\n")
        self.target.mkdir()
        other = self.base / "outside skills"
        other.mkdir()
        (self.target / ".agents").symlink_to(other, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.install(force=True)
        self.assertEqual(list(other.iterdir()), [])
        self.assertFalse((self.target / "CLAUDE.md").exists())

    def test_invalid_ledger_fails_closed(self):
        p = self.target / installer.LEDGER
        p.parent.mkdir(parents=True)
        for data in ("{bad", "[]", '{"manifest":"other","files":{}}',
                     '{"manifest":"unity-game","schema_version":true,"files":{}}',
                     '{"manifest":"unity-game","schema_version":1,"files":{"../outside":"' + 'a' * 64 + '"}}'):
            p.write_text(data)
            with self.assertRaisesRegex(ValueError, "ledger"):
                self.install(force=True)
            self.assertFalse((self.target / "CLAUDE.md").exists())

    def test_incomplete_source_fails_before_writes(self):
        (self.source / "templates/state/status.md").unlink()
        with self.assertRaisesRegex(ValueError, "missing scaffold"):
            self.install()
        self.assertFalse(self.target.exists())

    def test_rejects_source_as_destination(self):
        with self.assertRaisesRegex(ValueError, "separate"):
            installer.install(self.source, True, False)


    def test_interrupted_each_atomic_write_recovers_ownership(self):
        real_write = installer.atomic_write
        total = len(installer.source_files()) + 2  # journal, scaffold writes, ledger
        for phase in ("before", "after"):
            for fail_at in range(1, total + 1):
                with self.subTest(phase=phase, fail_at=fail_at):
                    self.target = self.base / f"interrupted-{phase}-{fail_at}"
                    count = 0
                    def failing_write(*args, **kwargs):
                        nonlocal count
                        count += 1
                        if count == fail_at and phase == "before":
                            raise OSError("injected write failure")
                        result = real_write(*args, **kwargs)
                        if count == fail_at and phase == "after":
                            raise OSError("injected write failure")
                        return result
                    with patch.object(installer, "atomic_write", side_effect=failing_write):
                        with self.assertRaisesRegex(OSError, "injected"):
                            self.install()
                    self.assertEqual(self.install(force=True), 0)
                    ledger = json.loads((self.target / installer.LEDGER).read_text())["files"]
                    expected = {relative.as_posix(): installer.digest(src.read_bytes())
                                for src, relative, protected in installer.source_files() if not protected}
                    self.assertEqual(ledger, expected)
                    self.assertFalse((self.target / installer.JOURNAL).exists())
                    for src, relative, _ in installer.source_files():
                        self.assertEqual((self.target / relative).read_bytes(), src.read_bytes())

    def interrupt_after_first_scaffold_write(self):
        real_write = installer.atomic_write
        count = 0
        def failing_write(*args, **kwargs):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError("injected write failure")
            return real_write(*args, **kwargs)
        with patch.object(installer, "atomic_write", side_effect=failing_write):
            with self.assertRaisesRegex(OSError, "injected"):
                self.install(force=True)

    def test_recovery_dry_run_is_read_only_and_then_commits(self):
        self.interrupt_after_first_scaffold_write()
        before = snapshot(self.target)
        self.assertEqual(self.install(force=True, dry_run=True), 0)
        self.assertEqual(snapshot(self.target), before)
        self.assertTrue((self.target / installer.JOURNAL).exists())
        self.assertEqual(self.install(force=True), 0)
        self.assertFalse((self.target / installer.JOURNAL).exists())
        self.assertIn("CLAUDE.md", json.loads((self.target / installer.LEDGER).read_text())["files"])

    def test_recovery_preserves_post_failure_new_file_edits_without_claiming(self):
        self.interrupt_after_first_scaffold_write()
        dest = self.target / "CLAUDE.md"
        dest.write_text("user edited after interruption")
        before = snapshot(self.target)
        self.assertEqual(self.install(force=True, dry_run=True), 1)
        self.assertEqual(snapshot(self.target), before)
        self.assertEqual(self.install(force=True), 1)
        self.assertEqual(dest.read_text(), "user edited after interruption")
        self.assertNotIn("CLAUDE.md", json.loads((self.target / installer.LEDGER).read_text())["files"])
        self.assertEqual(self.install(force=True), 0)
        self.assertEqual(dest.read_text(), "user edited after interruption")

    def test_recovery_preserves_post_failure_owned_file_edits_and_historical_hash(self):
        self.install()
        old = json.loads((self.target / installer.LEDGER).read_text())["files"]["CLAUDE.md"]
        (self.source / "CLAUDE.md").write_text("new scaffold")
        # Fail at ledger commit, after the one changed scaffold file was written.
        real_write = installer.atomic_write
        def failing_ledger(path, *args, **kwargs):
            if path == self.target / installer.LEDGER:
                raise OSError("injected ledger failure")
            return real_write(path, *args, **kwargs)
        with patch.object(installer, "atomic_write", side_effect=failing_ledger):
            with self.assertRaisesRegex(OSError, "injected"):
                self.install(force=True)
        (self.target / "CLAUDE.md").write_text("post-failure custom edit")
        self.assertEqual(self.install(force=True), 1)
        self.assertEqual((self.target / "CLAUDE.md").read_text(), "post-failure custom edit")
        self.assertEqual(json.loads((self.target / installer.LEDGER).read_text())["files"]["CLAUDE.md"], old)

    def test_recovery_journal_removal_failure_is_retryable_after_committed_ledger(self):
        real_unlink = Path.unlink
        def failing_unlink(path, *args, **kwargs):
            if path == self.target / installer.JOURNAL:
                raise OSError("injected journal removal failure")
            return real_unlink(path, *args, **kwargs)
        with patch.object(Path, "unlink", failing_unlink):
            with self.assertRaisesRegex(OSError, "injected"):
                self.install()
        self.assertTrue((self.target / installer.LEDGER).exists())
        self.assertTrue((self.target / installer.JOURNAL).exists())
        self.assertEqual(self.install(force=True), 0)
        self.assertFalse((self.target / installer.JOURNAL).exists())

    def test_recovery_ledger_write_failure_retains_journal_and_retryable_ownership(self):
        self.interrupt_after_first_scaffold_write()
        before = snapshot(self.target)
        real_write = installer.atomic_write
        def failing_ledger(path, *args, **kwargs):
            if path == self.target / installer.LEDGER:
                raise OSError("injected recovery ledger failure")
            return real_write(path, *args, **kwargs)
        with patch.object(installer, "atomic_write", side_effect=failing_ledger):
            with self.assertRaisesRegex(OSError, "injected"):
                self.install(force=True)
        self.assertEqual(snapshot(self.target), before)
        self.assertEqual(self.install(force=True), 0)

    def test_invalid_transaction_fails_closed_without_writes(self):
        path = self.target / installer.JOURNAL
        path.parent.mkdir(parents=True)
        cases = ["{bad", "[]", json.dumps({"manifest": "unity-game", "schema_version": True,
                 "base_files": {}, "writes": {}}), json.dumps({"manifest": "unity-game", "schema_version": 1,
                 "base_files": {}, "writes": {"../../outside": {"sha256": "a" * 64, "protected": False}}}),
                 json.dumps({"manifest": "unity-game", "schema_version": 1,
                 "base_files": {}, "writes": {"CLAUDE.md": {"sha256": "bad", "protected": False}}})]
        for data in cases:
            with self.subTest(data=data):
                path.write_text(data)
                before = snapshot(self.target)
                with self.assertRaisesRegex(ValueError, "transaction"):
                    self.install(force=True)
                self.assertEqual(snapshot(self.target), before)

    def test_journal_and_ledger_symlinks_rejected_before_writes(self):
        self.target.mkdir()
        outside = self.base / "outside-journal"
        outside.write_text("outside content")
        for relative in (installer.JOURNAL, installer.LEDGER):
            with self.subTest(relative=relative):
                path = self.target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(outside)
                with self.assertRaisesRegex(ValueError, "symlink"):
                    self.install(force=True)
                self.assertEqual(outside.read_text(), "outside content")
                self.assertFalse((self.target / "CLAUDE.md").exists())
                path.unlink()

    def test_cross_version_transaction_requires_original_source_without_mutation(self):
        self.interrupt_after_first_scaffold_write()
        # A later manifest can remove a previously scheduled file. It must not
        # accept arbitrary old paths as a basis for claiming file ownership.
        (self.source / "references/lifecycle.md").unlink()
        before = snapshot(self.target)
        with self.assertRaisesRegex(ValueError, "original manifest sources"):
            self.install(force=True)
        self.assertEqual(snapshot(self.target), before)
        self.assertTrue((self.target / installer.JOURNAL).is_file())

    def test_recovery_changed_destination_symlink_and_diverged_ledger_rejected(self):
        self.interrupt_after_first_scaffold_write()
        path = self.target / "CLAUDE.md"
        path.unlink()
        outside = self.base / "outside-recovery"
        outside.write_text("outside content")
        path.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.install(force=True)
        self.assertEqual(outside.read_text(), "outside content")
        path.unlink()
        path.write_text("# Unity game\n")
        (self.target / installer.LEDGER).write_bytes(installer.ledger_bytes({"AGENTS.md": "a" * 64}))
        before = snapshot(self.target)
        with self.assertRaisesRegex(ValueError, "diverged"):
            self.install(force=True)
        self.assertEqual(snapshot(self.target), before)


class ManifestIntegrationTests(unittest.TestCase):
    def assert_local_links(self, root):
        for path in root.rglob("*.md"):
            for link in re.findall(r"\[[^\]]+\]\(([^\s)]+)(?:\s+[^)]*)?\)", path.read_text(encoding="utf-8")):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                    continue
                self.assertTrue((path.parent / link.split("#", 1)[0]).exists(), f"{path}: {link}")

    def run_vibe(self, *args):
        env = {**os.environ, "VIBE_HOME": str(ROOT), "PYTHONPATH": str(ROOT / "tools/vibe_tool/src"),
               "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, "-B", "-m", "vibe_tool", *map(str, args)],
                              cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)

    def test_discovery_skills_and_all_equivalent_native_roles(self):
        sys.path.insert(0, str(ROOT / "tools/vibe_tool/src"))
        self.addCleanup(lambda: sys.path.remove(str(ROOT / "tools/vibe_tool/src")))
        from vibe_tool.discovery import resolve_manifest, resolve_skill
        manifest = resolve_manifest(ROOT / "manifests", "unity-game")
        self.assertEqual(manifest.init_script_path.name, "init-unity-game.sh")
        self.assertEqual(set(manifest.required_skills), {"unity-game-development", "version-management", "git-manager", "omnidraw", "state-machine-reasoning"})
        for name in manifest.required_skills:
            self.assertEqual(resolve_skill((ROOT / "skills", ROOT / "mine"), name).name, name)
        roles = re.findall(r"^###\s+\d+\.\s+`([^`]+)`", (MANIFEST / "agents/subagent-roles.md").read_text(), re.M)
        self.assertEqual(len(roles), 21)
        self.assertEqual(len(set(roles)), 21)
        self.assertEqual({p.stem for p in (MANIFEST / ".claude/agents").glob("*.md")}, set(roles))
        self.assertEqual({p.stem for p in (MANIFEST / ".codex/agents").glob("*.toml")}, set(roles))
        for name in roles:
            claude = (MANIFEST / f".claude/agents/{name}.md").read_text()
            codex = tomllib.loads((MANIFEST / f".codex/agents/{name}.toml").read_text())
            self.assertEqual(codex["name"], name)
            self.assertEqual(claude.split("---", 2)[2].strip(), codex["developer_instructions"].strip(), name)

    def test_lifecycle_state_and_gate_contracts(self):
        lifecycle = (MANIFEST / "references/lifecycle.md").read_text()
        state = (MANIFEST / "templates/state/status.md").read_text()
        stages = ["discovery", "design", "prototype", "vertical-slice", "production", "alpha", "beta", "release-ready", "live"]
        self.assertEqual(re.findall(r"^## \d+\. ([a-z-]+) —", lifecycle, re.M), stages)
        for stage in stages:
            self.assertIn(f"| {stage} | not_run |", state)
        for gate in ("direction", "vertical-slice", "release"):
            self.assertIn(f"| {gate} | pending |", state)
            self.assertIn(f"**{gate} 确认门**", lifecycle)
        self.assert_local_links(MANIFEST)

    def test_cli_init_add_dry_run_and_installed_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "game with spaces"
            preview = self.run_vibe("init", "unity-game", target, "--dry-run")
            self.assertEqual(preview.returncode, 0, preview.stderr + preview.stdout)
            self.assertFalse(target.exists())
            first = self.run_vibe("init", "unity-game", target)
            self.assertEqual(first.returncode, 0, first.stderr + first.stdout)
            for name in ("unity-game-development", "version-management", "git-manager", "omnidraw", "state-machine-reasoning"):
                self.assertTrue((target / f".agents/skills/{name}/SKILL.md").is_file(), name)
            for source, relative, _ in installer.source_files():
                self.assertEqual((target / relative).read_bytes(), source.read_bytes(), str(relative))
            before = snapshot(target)
            added = self.run_vibe("add", "manifest", "unity-game", target)
            self.assertEqual(added.returncode, 0, added.stderr + added.stdout)
            self.assertEqual(snapshot(target), before)
            self.assert_local_links(target / ".unity-game")
            helper = subprocess.run([sys.executable, "-B", str(target / ".unity-game/scripts/unity_cli.py"), "--help"],
                                    capture_output=True, text=True)
            self.assertEqual(helper.returncode, 0, helper.stderr)
            self.assertIn("doctor", helper.stdout)

    def test_direct_wrapper_and_invalid_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "direct game"
            command = [str(MANIFEST / "scripts/init-unity-game.sh"), str(target)]
            preview = subprocess.run(command + ["--dry-run"], capture_output=True, text=True)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertFalse(target.exists())
            invalid = subprocess.run(command + ["--invalid"], capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertFalse(target.exists())
            installed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertTrue((target / ".unity-game/state/status.md").is_file())

    def test_cli_force_preserves_existing_skills_and_unowned_game_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing game"
            shutil.copytree(ROOT / "mine/git-manager", target / ".agents/skills/git-manager")
            existing = {".agents/skills/git-manager/SKILL.md": "custom skill",
                        ".agents/skills/git-manager/custom-state.txt": "custom data",
                        "CLAUDE.md": "user instructions", "Assets/level.unity": "existing scene"}
            for name, text in existing.items():
                p = target / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
            added = self.run_vibe("add", "manifest", "unity-game", target, "--force")
            self.assertEqual(added.returncode, 0, added.stderr + added.stdout)
            for name, text in existing.items():
                self.assertEqual((target / name).read_text(), text, name)

    def test_cli_skill_symlink_conflict_fails_before_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing game"
            target.mkdir()
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (target / ".agents").symlink_to(outside, target_is_directory=True)
            added = self.run_vibe("add", "manifest", "unity-game", target, "--force")
            self.assertNotEqual(added.returncode, 0)
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertEqual(list(outside.iterdir()), [])


class RequiredSkillPolicyTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "tools/vibe_tool/src"))
        self.addCleanup(lambda: sys.path.remove(str(ROOT / "tools/vibe_tool/src")))
        from vibe_tool.manifest import _install_required_skills
        from vibe_tool.types import ManifestInfo
        self.install_skills = _install_required_skills
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "manifests/sample"
        self.source.mkdir(parents=True)
        self.manifest = ManifestInfo(name="sample", path=self.source, description="sample",
                                     has_init_script=False, init_script_path=None, required_skills=["git-manager"])

    def test_opt_in_preserves_skills_and_legacy_force_behavior_remains(self):
        policy_path = self.source / "skills-policy.json"
        for policy, expected_force in ((None, True), ({"preserve_existing": False}, True),
                                       ({"preserve_existing": True}, False)):
            with self.subTest(policy=policy), patch("vibe_tool.skill.add_skill", return_value=0) as add:
                if policy is not None:
                    policy_path.write_text(json.dumps(policy))
                rc = self.install_skills(self.source.parent, self.manifest, self.base / "target", True, False)
                self.assertEqual(rc, 0)
                self.assertEqual(add.call_args.kwargs["force"], expected_force)

    def test_invalid_policy_does_not_touch_skills(self):
        for content in ('[]', '{}', '{bad', '{"preserve_existing":"true"}'):
            with self.subTest(content=content), patch("vibe_tool.skill.add_skill") as add:
                (self.source / "skills-policy.json").write_text(content)
                rc = self.install_skills(self.source.parent, self.manifest, self.base / "target", True, False)
                self.assertEqual(rc, 1)
                add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
