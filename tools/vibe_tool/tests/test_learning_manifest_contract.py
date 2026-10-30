"""Static instruction/fixture contracts, not an end-to-end model evaluation."""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "manifests" / "tutor"


class LearningManifestContractTests(unittest.TestCase):
    def test_planning_entrypoints_and_resources_agree(self):
        for rel in (
            "CLAUDE.md", "AGENTS.md", "commands/learn/COMMAND.md",
            "references/learning-path-design.md",
        ):
            with self.subTest(document=rel):
                text = (MANIFEST / rel).read_text(encoding="utf-8")
                for token in ("--plan", "MATERIAL_INDEX.md", "LEARNING_PATH.md"):
                    self.assertIn(token, text)
        for name in ("MATERIAL_INDEX", "LEARNING_PATH", "COURSE_PLAN"):
            self.assertTrue((MANIFEST / "templates" / f"{name}.md.example").is_file())

    def test_command_index_covers_all_nine_commands(self):
        commands = {p.parent.name for p in (MANIFEST / "commands").glob("*/COMMAND.md")}
        self.assertEqual(commands, {
            "import", "learn", "study", "review", "flashcard",
            "mindmap", "exam", "diagram", "track",
        })
        index = (MANIFEST / "commands" / "COMMANDS.md").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"`/(\w+)", index)), commands)
        skill = (MANIFEST / "skills" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("9 个", skill)
        self.assertIn("--plan", skill)

    def test_material_index_distinguishes_location_evidence(self):
        text = (MANIFEST / "templates/MATERIAL_INDEX.md.example").read_text(encoding="utf-8")
        for token in ("PDF 页序", "印刷页码", "正文待核", "partial", "未覆盖范围"):
            self.assertIn(token, text)

    def test_route_template_has_chapter_units_not_calendar_defaults(self):
        text = (MANIFEST / "templates/LEARNING_PATH.md.example").read_text(encoding="utf-8")
        for token in ("学习目标", "已有基础", "重点问题", "教材练习", "完成标准", "顺序依据", "用户记录"):
            self.assertIn(token, text)
        self.assertNotIn("start_date:", text)
        self.assertNotIn("target_date:", text)
        self.assertIn("习题待核", text)

    def test_personal_record_entrypoints_and_resources_agree(self):
        # Resource contracts establish discoverability, not model behavior.
        for rel in (
            "CLAUDE.md", "AGENTS.md", "README.md", ".cursorrules", "skills/SKILL.md",
            "commands/COMMANDS.md", "references/source-grounding.md",
            "commands/learn/COMMAND.md", "commands/study/COMMAND.md",
            "commands/track/COMMAND.md",
        ):
            with self.subTest(document=rel):
                text = (MANIFEST / rel).read_text(encoding="utf-8")
                self.assertIn("LEARNING_RECORD.md", text)
        for command in ("learn", "study", "track"):
            with self.subTest(command=command):
                text = (MANIFEST / "commands" / command / "COMMAND.md").read_text(encoding="utf-8")
                self.assertIn("references/learning-records.md", text)
        self.assertTrue((MANIFEST / "templates/LEARNING_RECORD.md.example").is_file())
        self.assertTrue((MANIFEST / "references/learning-records.md").is_file())

    def test_personal_record_template_separates_history_from_mastery(self):
        text = (MANIFEST / "templates/LEARNING_RECORD.md.example").read_text(encoding="utf-8")
        for token in (
            "学习目标", "已有基础", "已学", "偏好", "单元 ID", "定位",
            "学习状态", "掌握依据", "学习日志", "用户原文", "助手摘要",
            "练习", "问题", "下一步",
        ):
            with self.subTest(field=token):
                self.assertIn(token, text)
        reference = (MANIFEST / "references/learning-records.md").read_text(encoding="utf-8")
        for token in ("追加", "--plan", "--next", "/track", "掌握", "时间", "用户原文"):
            with self.subTest(rule=token):
                self.assertIn(token, reference)

    def test_illustrated_notes_have_discoverable_local_resources(self):
        # Static instructions establish the contract, not automatic note quality.
        for rel in ("CLAUDE.md", "AGENTS.md", "README.md", ".cursorrules", "skills/SKILL.md"):
            with self.subTest(document=rel):
                text = (MANIFEST / rel).read_text(encoding="utf-8")
                self.assertIn("references/illustrated-notes.md", text)
        self.assertTrue((MANIFEST / "scripts/export-notes.py").is_file())
        template = (MANIFEST / "templates/CHAPTER_NOTE.md.example").read_text(encoding="utf-8")
        self.assertIn("[Source:", template)
        self.assertRegex(template, r"!\[[^\]]+\]\([^\n)]*assets/[^\n)]+\.(?:svg|png)\)")
        self.assertRegex(template, r"图注|图\s*1")
        self.assertRegex(template.lower(), r"alt|替代文[字本]")

    def test_illustrated_notes_define_automatic_md_and_opt_in_pdf(self):
        reference = (MANIFEST / "references/illustrated-notes.md").read_text(encoding="utf-8")
        for token in ("自动保存", "本轮回复结束前", "notes/summaries/", "notes/assets/",
                      "LEARNING_RECORD.md", "--export pdf", "scripts/export-notes.py",
                      "只有 Mermaid 代码不算", "相对", "不在每轮另生成 PDF"):
            with self.subTest(rule=token):
                self.assertIn(token, reference)
        for name in ("learn", "study"):
            with self.subTest(command=name):
                text = (MANIFEST / f"commands/{name}/COMMAND.md").read_text(encoding="utf-8")
                self.assertIn("--export pdf", text)
                self.assertIn("references/illustrated-notes.md", text)
                self.assertIn("scripts/export-notes.py", text)

    def test_cli_installs_record_resources_and_force_keeps_personal_history(self):
        # This executes the real installer, but does not evaluate an AI session.
        env = dict(os.environ)
        env.update({
            "VIBE_HOME": str(REPO_ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": str(REPO_ROOT / "tools/vibe_tool/src"),
        })
        resources = [
            ("templates/LEARNING_RECORD.md.example", ".cursor/templates/LEARNING_RECORD.md.example"),
            ("references/learning-records.md", "references/learning-records.md"),
            *((f"commands/{name}/COMMAND.md", f".cursor/commands/{name}/COMMAND.md")
              for name in ("learn", "study", "track")),
        ]
        with tempfile.TemporaryDirectory(prefix="personal learning records ") as directory:
            target = Path(directory) / "project with spaces"

            def install(*extra):
                result = subprocess.run(
                    [sys.executable, "-m", "vibe_tool", "init", "tutor",
                     str(target), *extra],
                    cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            def assert_resources():
                for source, destination in resources:
                    with self.subTest(resource=destination):
                        self.assertEqual((target / destination).read_bytes(),
                                         (MANIFEST / source).read_bytes())
                for command in ("learn", "study", "track"):
                    installed = (target / f".cursor/commands/{command}/COMMAND.md").read_text(encoding="utf-8")
                    self.assertIn("LEARNING_RECORD.md", installed)
                    self.assertIn("references/learning-records.md", installed)

            install()
            assert_resources()
            # Initialization supplies templates, never fabricated study events.
            self.assertEqual(list((target / "projects").rglob("LEARNING_RECORD.md")), [])
            personal = {
                "projects/我的教材/LEARNING_RECORD.md": "# 学习记录\n用户原文：第二节证明还没弄懂。\n",
                "notes/atoms/my-note.md": "# 我的笔记\n保留原文与问题。\n",
            }
            for relative, contents in personal.items():
                path = target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents, encoding="utf-8")
            template = target / ".cursor/templates/LEARNING_RECORD.md.example"
            template.write_text("local template edit\n", encoding="utf-8")

            install()
            self.assertEqual(template.read_text(encoding="utf-8"), "local template edit\n")
            install("--force")
            assert_resources()
            for relative, contents in personal.items():
                with self.subTest(personal_file=relative):
                    self.assertEqual((target / relative).read_text(encoding="utf-8"), contents)

    def test_project_local_resource_references_exist(self):
        checked = 0
        for doc in MANIFEST.rglob("*"):
            if not doc.is_file() or doc.suffix not in (".md", ".mdc"):
                continue
            text = doc.read_text(encoding="utf-8")
            for rel in re.findall(r"(?<![\w/])((?:references|skills|agents)/[\w/-]+\.md)\b", text):
                with self.subTest(document=str(doc.relative_to(MANIFEST)), resource=rel):
                    self.assertTrue((MANIFEST / rel).is_file(), rel)
                checked += 1
        self.assertGreater(checked, 10)

    @unittest.skipUnless(shutil.which("pdftotext"), "optional fixture text extraction tool")
    def test_pdf_fixture_matches_its_declared_pages(self):
        fixtures = MANIFEST / "evaluations" / "fixtures"
        expected = json.loads((fixtures / "textbook.json").read_text(encoding="utf-8"))["pages"]
        result = subprocess.run(
            ["pdftotext", "-layout", str(fixtures / "textbook.pdf"), "-"],
            text=True, capture_output=True, check=True,
        )
        actual = result.stdout.split("\f")
        self.assertEqual(actual.pop().strip(), "")
        self.assertEqual(len(actual), len(expected))
        for number, (page, lines) in enumerate(zip(actual, expected), 1):
            with self.subTest(pdf_page=number):
                self.assertEqual(page.strip().splitlines(), lines)


if __name__ == "__main__":
    unittest.main()
