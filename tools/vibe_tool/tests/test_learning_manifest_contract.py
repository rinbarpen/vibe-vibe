"""Static instruction/fixture contracts, not an end-to-end model evaluation."""

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "manifests" / "knowledge-learning"


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
