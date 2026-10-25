"""Hermetic installation tests: no external submodules or Office tools needed."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CLI_SOURCE = REPO_ROOT / "tools/vibe_tool/src"
OFFICE_SOURCE = REPO_ROOT / "manifests/office"
FORMATS = ("docx", "xlsx", "pptx", "pdf")
ROLES = ("office-planner", "office-docx", "office-xlsx", "office-pptx", "office-pdf", "office-qa")


class OfficeInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="office install ")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / "fixture repo"
        self.manifest = self.repo / "manifests/office"
        self.target = self.base / "project with spaces"
        self.env = dict(os.environ, VIBE_HOME=str(self.repo), PYTHONPATH=str(CLI_SOURCE),
                        PYTHONDONTWRITEBYTECODE="1")
        self.manifest.mkdir(parents=True)
        (self.repo / "skills").mkdir()
        (self.repo / "mine").mkdir()
        for filename in ("CLAUDE.md", "AGENTS.md", "README.md", "MANIFEST.md"):
            self.write(self.manifest / filename, f"# Office fixture {filename}\nRead office/rules/quality.md.\n")
        for fmt in (*FORMATS, "planning"):
            self.write(self.manifest / fmt / "CLAUDE.md", f"# {fmt} guide\n")
        self.write(self.manifest / "docx/rules/patent.md", "# Optional reference\n")
        self.write(self.manifest / "xlsx/scripts/recalc.sh", "#!/bin/sh\nexit 0\n")
        self.write(self.manifest / "rules/quality.md", "# Shared quality rules\n")
        self.write(self.manifest / "rules/office-quality.mdc", "---\nalwaysApply: true\n---\nQuality\n")
        self.write(self.manifest / "scripts/check_dependencies.py", "print('check')\n")
        self.write(self.manifest / "scripts/nested/script with spaces.py", "print('nested')\n")
        self.write(self.manifest / "scripts/__pycache__/ignored.pyc", "cache")
        for role in ROLES:
            self.write(self.manifest / "agents/subagent-roles" / f"{role}.md", f"# {role}\n")
            self.write(self.manifest / ".claude/agents" / f"{role}.md", f"---\nname: {role}\ndescription: fixture\n---\n")
            self.write(self.manifest / ".codex/agents" / f"{role}.toml", f'name = "{role}"\n')
        for name in ("init-office.sh", "install_office.py"):
            destination = self.manifest / "scripts" / name
            shutil.copy2(OFFICE_SOURCE / "scripts" / name, destination)
        for fmt in FORMATS:
            self.write(self.repo / "skills/anthropics/skills" / fmt / "SKILL.md", f"# {fmt}\n")
        self.write(self.repo / "mine/office-quality/SKILL.md", "# Office quality\n")
        self.write(self.manifest / "skills.txt", "\n".join(
            [f"anthropics/skills/{fmt}" for fmt in FORMATS] + ["office-quality", ""]
        ))

    def write(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "vibe_tool", *map(str, args)],
                              env=self.env, cwd=self.base, capture_output=True, text=True)

    def direct(self, *args):
        return subprocess.run([str(self.manifest / "scripts/init-office.sh"), *map(str, args)],
                              cwd=self.base, capture_output=True, text=True)

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def snapshot(self):
        return {str(p.relative_to(self.target)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.target.rglob("*") if p.is_file()}

    def test_office_discovery_declares_script_and_required_exact_skills(self):
        result = self.cli("list", "manifests", "--json")
        self.assert_ok(result)
        manifest = json.loads(result.stdout)[0]
        self.assertEqual(manifest["name"], "office")
        self.assertTrue(manifest["has_init_script"])
        self.assertEqual(manifest["required_skills"],
                         [f"anthropics/skills/{fmt}" for fmt in FORMATS] + ["office-quality"])

    def test_init_installs_resources_skills_rules_and_both_native_agents(self):
        self.assert_ok(self.cli("init", "office", self.target))
        expected = ["CLAUDE.md", "AGENTS.md", "README.md", "MANIFEST.md", "office/README.md",
                    "office/rules/quality.md", ".cursor/rules/office-quality.mdc",
                    "office/docx/rules/patent.md", "office/xlsx/scripts/recalc.sh",
                    "office/scripts/check_dependencies.py",
                    "office/scripts/nested/script with spaces.py"]
        expected += [f"office/{fmt}/CLAUDE.md" for fmt in (*FORMATS, "planning")]
        expected += [f".agents/skills/anthropics-skills-{fmt}/SKILL.md" for fmt in FORMATS]
        expected += [".agents/skills/office-quality/SKILL.md"]
        expected += [f"{prefix}/{role}.{ext}" for role in ROLES for prefix, ext in (
            ("office/agents/subagent-roles", "md"), (".claude/agents", "md"), (".codex/agents", "toml"))]
        for relative in expected:
            with self.subTest(relative=relative):
                self.assertTrue((self.target / relative).is_file())
        for relative in ("office/scripts/install_office.py", "office/scripts/init-office.sh",
                         "office/scripts/__pycache__", "docx", "rules", ".claude/skills"):
            self.assertFalse((self.target / relative).exists(), relative)

    def test_add_preserves_project_entries_and_repeated_install_is_idempotent(self):
        self.write(self.target / "CLAUDE.md", "# Existing project\n")
        self.write(self.target / "AGENTS.md", "# Existing agents\n")
        first = self.cli("add", "manifest", "office", self.target)
        self.assert_ok(first)
        self.assertIn("SKIP  CLAUDE.md", first.stdout)
        self.assertIn("office/README.md", first.stdout)
        self.assertEqual((self.target / "CLAUDE.md").read_text(), "# Existing project\n")
        self.assertTrue((self.target / "office/README.md").is_file())
        before = self.snapshot()
        self.assert_ok(self.cli("add", "manifest", "office", self.target))
        self.assertEqual(self.snapshot(), before)

    def test_force_updates_managed_files_but_preserves_unrelated_files(self):
        self.assert_ok(self.cli("init", "office", self.target))
        self.write(self.target / "CLAUDE.md", "edited root")
        self.write(self.target / "office/docx/CLAUDE.md", "edited guide")
        self.write(self.target / ".agents/skills/anthropics-skills-docx/SKILL.md", "edited skill")
        self.write(self.target / "office/custom note.txt", "project data")
        self.write(self.target / "MANIFEST.md", "# Output history\nPreserve prior deliverables.\n")
        self.assert_ok(self.cli("add", "manifest", "office", self.target, "--force"))
        self.assertEqual((self.target / "CLAUDE.md").read_bytes(), (self.manifest / "CLAUDE.md").read_bytes())
        self.assertEqual((self.target / "office/docx/CLAUDE.md").read_text(), "# docx guide\n")
        self.assertEqual((self.target / ".agents/skills/anthropics-skills-docx/SKILL.md").read_text(), "# docx\n")
        self.assertEqual((self.target / "office/custom note.txt").read_text(), "project data")
        self.assertEqual((self.target / "MANIFEST.md").read_text(), "# Output history\nPreserve prior deliverables.\n")

    def test_cli_and_direct_dry_run_do_not_create_or_modify_target(self):
        for run in (lambda: self.cli("init", "office", self.target, "-n"),
                    lambda: self.direct(self.target, "--dry-run")):
            self.assert_ok(run())
            self.assertFalse(self.target.exists())
        self.assert_ok(self.cli("init", "office", self.target))
        self.write(self.target / "CLAUDE.md", "preserve me")
        before = self.snapshot()
        self.assert_ok(self.cli("add", "manifest", "office", self.target, "--force", "--dry-run"))
        self.assert_ok(self.direct(self.target, "-f", "-n"))
        self.assertEqual(self.snapshot(), before)

    def test_direct_script_supports_both_flag_forms_without_installing_skills(self):
        self.assert_ok(self.direct(self.target))
        self.assertFalse((self.target / ".agents/skills").exists())
        self.write(self.target / "CLAUDE.md", "custom")
        self.assert_ok(self.direct("--force", self.target))
        self.assertEqual((self.target / "CLAUDE.md").read_bytes(), (self.manifest / "CLAUDE.md").read_bytes())
        self.write(self.target / "CLAUDE.md", "custom again")
        self.assert_ok(self.direct(self.target, "-f"))
        self.assertEqual((self.target / "CLAUDE.md").read_bytes(), (self.manifest / "CLAUDE.md").read_bytes())

    def test_missing_required_exact_dependency_returns_failure_even_with_nearby_skill(self):
        missing = self.repo / "skills/anthropics/skills/xlsx"
        shutil.rmtree(missing)
        self.write(self.repo / "skills/anthropics/skills/xlsx-helper/SKILL.md", "# nearby skill\n")
        result = self.cli("init", "office", self.target)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("anthropics/skills/xlsx", result.stdout)
        self.assertFalse((self.target / ".agents/skills/anthropics-skills-xlsx").exists())
        self.assertTrue((self.target / ".agents/skills/anthropics-skills-docx/SKILL.md").is_file())

    def test_missing_required_dependency_dry_run_reports_failure_without_writes(self):
        shutil.rmtree(self.repo / "mine/office-quality")
        result = self.cli("init", "office", self.target, "--dry-run")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("office-quality", result.stdout)
        self.assertFalse(self.target.exists())

    def test_cli_exact_skill_install_does_not_depend_on_collision_discovery(self):
        self.write(self.repo / "skills/other/docx/SKILL.md", "# collision\n")
        self.assert_ok(self.cli("add", "skill", "anthropics/skills/docx", self.target))
        self.assertTrue((self.target / ".agents/skills/anthropics-skills-docx/SKILL.md").is_file())
        result = self.cli("add", "skill", "anthropics/skills/doc", self.target)
        self.assertEqual(result.returncode, 1)
        self.assertIn("id_path", result.stderr)


if __name__ == "__main__":
    unittest.main()
