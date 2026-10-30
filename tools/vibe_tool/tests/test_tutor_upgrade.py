"""Real CLI/installer regression tests; no model behavior is inferred here."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / "manifests/tutor"
SCENARIOS = ("self-study", "exam-prep", "course-learning", "research-reading")


def files(root):
    result = {}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if rel.parts[0] == ".vibe-tool":
            continue
        if path.is_symlink():
            result[str(rel)] = ("link", os.readlink(path))
        elif path.is_file():
            result[str(rel)] = (path.read_bytes(), path.stat().st_mode,
                                path.stat().st_mtime_ns)
    return result


class TutorUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tutor upgrade ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "旧学习项目 with spaces"
        self.env = dict(os.environ, VIBE_HOME=str(REPO), PYTHONDONTWRITEBYTECODE="1",
                        PYTHONPATH=str(REPO / "tools/vibe_tool/src"))

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, "-B", "-m", "vibe_tool", *map(str, args)],
                                cwd=REPO, env=self.env, capture_output=True, text=True, timeout=30)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def legacy(self, scenario=None):
        # Explicit synthetic old-install fixture: edited instructions, old and
        # custom rules, plus genuine personal files. Not a model transcript.
        data = {
            "CLAUDE.md": "# Knowledge-Learning Manifest\nlocal instructions\n",
            "AGENTS.md": "# Agent Instructions for Knowledge-Learning Manifest\n",
            "README.md": "my edited readme\n",
            ".cursor/rules/knowledge-learning-core.mdc": "old core with user edits\n",
            "agents/knowledge-agents.md": "old roles with user additions\n",
            ".cursor/commands/learn/COMMAND.md": "edited learn command\n",
            "skills/SKILL.md": "---\nname: knowledge-learning\n---\n",
            ".cursor/rules/knowledge-learning-custom.mdc": "custom rule, keep active\n",
            "materials/pdf/my textbook.pdf": "my source file\n",
            "projects/统计/LEARNING_RECORD.md": "# 我的记录\n原话：颜色的均值？\n",
            "projects/统计/LEARNING_PATH.md": "my route and notes\n",
            "notes/summaries/统计/U01-变量.md": "# 我的手改笔记\n",
            "notes/assets/统计/变量.svg": "<svg/>\n",
            "exports/统计/变量.pdf": "%PDF-1.4\nfixture\n%%EOF\n",
            "notes/_index.md": "my index, not a template\n",
            "scripts/my-helper.py": "# keep my helper\n",
        }
        if scenario:
            data[f".cursor/rules/knowledge-learning-{scenario}.mdc"] = "edited scenario\n"
            data[".cursor/scenario.md"] = "custom selected scenario description\n"
        for rel, contents in data.items():
            path = self.target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents, encoding="utf-8")

    def backup(self):
        folders = list((self.target / ".vibe-tool/backups/tutor").iterdir())
        self.assertEqual(len(folders), 1)
        return folders[0]

    def restore(self, backup, *args, ok=True):
        result = subprocess.run([sys.executable, "-B", str(backup / "restore.py"), *args],
                                cwd=self.root, env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def test_list_only_new_name_and_retired_name_has_actionable_error_without_writes(self):
        result = self.cli("list", "manifests", "--json")
        names = {m["name"] for m in json.loads(result.stdout)}
        self.assertIn("tutor", names)
        self.assertNotIn("knowledge-learning", names)
        for name in ("knowledge-learning", "KNOWLEDGE-LEARNING"):
            result = self.cli("init", name, self.target, ok=False)
            self.assertIn("vibe init tutor", result.stderr + result.stdout)
            self.assertIn("vibe add manifest tutor", result.stderr + result.stdout)
            self.assertFalse(self.target.exists())
        self.legacy()
        before = files(self.target)
        self.cli("add", "manifest", "knowledge-learning", self.target, "--force", ok=False)
        self.assertEqual(files(self.target), before)

    def test_legacy_requires_force_and_dry_run_keeps_everything_unchanged(self):
        self.legacy("self-study")
        before = files(self.target)
        result = self.cli("add", "manifest", "tutor", self.target, ok=False)
        self.assertIn("--force", result.stderr + result.stdout)
        self.assertEqual(files(self.target), before)
        self.assertFalse((self.target / ".vibe-tool").exists())
        self.cli("add", "manifest", "tutor", self.target, "--force", "--dry-run")
        self.assertEqual(files(self.target), before)
        self.assertFalse((self.target / ".vibe-tool").exists())

    def test_upgrade_retains_each_scenario_and_restore_is_standalone(self):
        for name in SCENARIOS:
            with self.subTest(scenario=name):
                self.target = self.root / name
                self.legacy(name)
                before = files(self.target)
                result = self.cli("add", "manifest", "tutor", self.target, "--force")
                self.assertIn("Restore:", result.stdout)
                backup = self.backup()
                self.assertFalse((self.target / ".cursor/rules/knowledge-learning-core.mdc").exists())
                self.assertFalse((self.target / "agents/knowledge-agents.md").exists())
                self.assertTrue((self.target / f".cursor/rules/tutor-{name}.mdc").is_file())
                self.assertEqual((self.target / ".cursor/scenario.md").read_bytes(),
                                 (MANIFEST / f"scenarios/{name}/CLAUDE.md").read_bytes())
                for rel, state in before.items():
                    if rel.startswith(("materials/", "projects/", "notes/", "exports/")) or "custom" in rel:
                        self.assertEqual(files(self.target)[rel], state, rel)
                self.restore(backup)
                self.assertEqual(files(self.target), before)
                self.restore(backup)  # Idempotent and independent of source checkout.
                self.assertEqual(files(self.target), before)

    def test_conflicting_scenarios_abort_before_writes_unless_explicitly_selected(self):
        self.legacy("course-learning")
        (self.target / ".cursor/rules/knowledge-learning-exam-prep.mdc").write_text("old extra\n")
        before = files(self.target)
        result = self.cli("add", "manifest", "tutor", self.target, "--force", ok=False)
        self.assertIn("--scenario", result.stderr + result.stdout)
        self.assertEqual(files(self.target), before)
        self.assertFalse((self.target / ".vibe-tool").exists())
        self.cli("add", "manifest", "tutor", self.target, "--force", "--scenario", "research-reading")
        self.assertEqual({p.name for p in (self.target / ".cursor/rules").glob("tutor-*.mdc")
                          if any(name in p.name for name in SCENARIOS)}, {"tutor-research-reading.mdc"})
        self.restore(self.backup())
        self.assertEqual(files(self.target), before)

    def test_modified_files_are_not_silently_destroyed_by_restore(self):
        self.legacy()
        self.cli("add", "manifest", "tutor", self.target, "--force")
        backup = self.backup()
        changed = self.target / "CLAUDE.md"
        changed.write_text("post-upgrade user changes\n")
        before = files(self.target)
        result = self.restore(backup, ok=False)
        self.assertIn("Changed since upgrade", result.stderr)
        self.assertEqual(files(self.target), before)
        personal = self.target / "notes/new-after-upgrade.md"
        personal.write_text("keep new user file\n")
        self.restore(backup, "--force")
        self.assertEqual(personal.read_text(), "keep new user file\n")

    def test_legacy_scenario_heading_without_rule_is_preserved(self):
        self.legacy()
        (self.target / ".cursor/scenario.md").write_text("# CLAUDE.md — Exam Preparation Scenario\n")
        self.cli("add", "manifest", "tutor", self.target, "--force")
        self.assertTrue((self.target / ".cursor/rules/tutor-exam-prep.mdc").is_file())

    def test_scenario_change_requires_force_and_retires_only_known_scenario_rules(self):
        self.cli("init", "tutor", self.target, "--scenario", "self-study")
        custom = self.target / ".cursor/rules/tutor-self-study-custom.mdc"
        custom.write_text("custom rule\n")
        before = files(self.target)
        self.cli("add", "manifest", "tutor", self.target, "--scenario", "exam-prep", ok=False)
        self.assertEqual(files(self.target), before)
        self.cli("add", "manifest", "tutor", self.target, "--scenario", "exam-prep", "--force")
        self.assertFalse((self.target / ".cursor/rules/tutor-self-study.mdc").exists())
        self.assertEqual(custom.read_text(), "custom rule\n")
        self.restore(self.backup())
        self.assertEqual(files(self.target), before)

    def test_backup_corruption_prevents_partial_restore(self):
        self.legacy()
        self.cli("add", "manifest", "tutor", self.target, "--force")
        backup = self.backup()
        (backup / "files/CLAUDE.md").write_text("corrupted backup\n")
        before = files(self.target)
        self.assertIn("checksum", self.restore(backup, ok=False).stderr)
        self.assertEqual(files(self.target), before)

    def test_restore_preserves_nanosecond_mtime_even_when_template_content_is_unchanged(self):
        self.legacy()
        path = self.target / ".cursor/templates/COURSE_PLAN.md.example"
        path.parent.mkdir(parents=True)
        shutil.copy2(MANIFEST / "templates/COURSE_PLAN.md.example", path)
        os.utime(path, ns=(1600000001123456789, 1600000001123456789))
        before = files(self.target)
        self.cli("add", "manifest", "tutor", self.target, "--force")
        self.restore(self.backup())
        self.assertEqual(files(self.target), before)

    def test_upgrade_does_not_follow_linked_backup_or_resource_directories(self):
        for rel in (".vibe-tool", "references", "scripts"):
            with self.subTest(link=rel):
                self.target = self.root / rel.replace(".", "").replace("/", "-")
                self.legacy()
                external = self.root / (self.target.name + " external")
                external.mkdir()
                (external / "keep.txt").write_text("external data\n")
                destination = self.target / rel
                if destination.is_dir():
                    shutil.rmtree(destination)
                destination.symlink_to(external, target_is_directory=True)
                before, outside = files(self.target), files(external)
                self.cli("add", "manifest", "tutor", self.target, "--force", ok=False)
                self.assertEqual(files(self.target), before)
                self.assertEqual(files(external), outside)

    def test_file_links_are_backed_up_without_following_or_editing_external_data(self):
        self.legacy()
        external = self.root / "external README"
        external.write_text("external original\n")
        (self.target / "README.md").unlink()
        (self.target / "README.md").symlink_to(external)
        before = files(self.target)
        self.cli("add", "manifest", "tutor", self.target, "--force")
        self.assertFalse((self.target / "README.md").is_symlink())
        self.assertEqual(external.read_text(), "external original\n")
        self.restore(self.backup())
        self.assertEqual(files(self.target), before)
        self.assertEqual(external.read_text(), "external original\n")

    def test_write_failure_rolls_back_the_entire_legacy_upgrade(self):
        self.legacy("self-study")
        before = files(self.target)
        spec = importlib.util.spec_from_file_location("tutor_installer", MANIFEST / "scripts/install-tutor.py")
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        original = installer.atomic_copy
        failed = False

        def fail_once(source, destination):
            nonlocal failed
            if not failed and destination == self.target / ".cursor/commands/learn/COMMAND.md":
                failed = True
                raise OSError("injected write failure")
            return original(source, destination)

        with patch.object(installer, "atomic_copy", side_effect=fail_once):
            with self.assertRaisesRegex(OSError, "injected"):
                installer.install(self.target, None, True)
        self.assertTrue(failed)
        self.assertEqual(files(self.target), before)


if __name__ == "__main__":
    unittest.main()
