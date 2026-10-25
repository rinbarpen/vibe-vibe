import tempfile
import unittest
from pathlib import Path

from vibe_tool.discovery import resolve_skill
from vibe_tool.skill import add_skill


class ExactSkillPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skills = self.root / "skills"
        self.mine = self.root / "mine"
        self.upstream = self.make_skill(self.skills, "anthropics/skills/docx")

    def make_skill(self, root, relative):
        directory = root / relative
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text("# Fixture skill\n", encoding="utf-8")
        return directory

    def test_exact_path_has_stable_name_with_only_one_submodule(self):
        skill = resolve_skill((self.skills, self.mine), "anthropics/skills/docx")
        self.assertEqual(skill.name, "anthropics-skills-docx")
        self.assertEqual(skill.source_path, self.upstream)
        self.assertEqual(skill.id_path, "anthropics/skills/docx")
        self.assertEqual(resolve_skill(self.skills, "docx").name, "docx")

    def test_exact_install_destination_ignores_new_name_collisions(self):
        target = self.root / "target"
        self.assertEqual(add_skill(self.skills, "anthropics/skills/docx", target), 0)
        destination = target / ".agents/skills/anthropics-skills-docx/SKILL.md"
        self.assertTrue(destination.is_file())
        self.make_skill(self.skills, "another/skills/docx")
        self.assertEqual(resolve_skill(self.skills, "anthropics/skills/docx").name,
                         "anthropics-skills-docx")
        self.assertEqual(add_skill(self.skills, "anthropics/skills/docx", target), 2)
        self.assertEqual(len(list((target / ".agents/skills").iterdir())), 1)

    def test_missing_exact_path_never_falls_back_to_substring(self):
        for query in ("skills/docx", "anthropics/skills/doc", "Anthropics/skills/docx"):
            with self.subTest(query=query), self.assertRaisesRegex(ValueError, "id_path.*not found"):
                resolve_skill(self.skills, query)

    def test_legacy_case_insensitive_and_substring_queries_are_unchanged(self):
        self.assertEqual(resolve_skill(self.skills, "DOCX").name, "docx")
        self.assertEqual(resolve_skill(self.skills, "ocx").name, "docx")
        self.make_skill(self.skills, "another/docx")
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            resolve_skill(self.skills, "docx")
        self.assertEqual(resolve_skill(self.skills, "another-docx").id_path, "another/docx")

    def test_rejects_absolute_and_traversal_identifiers(self):
        for query in ("", ".", "..", "/anthropics/skills/docx", "../docx",
                      "anthropics/../docx", "anthropics//skills/docx", "foo/./docx",
                      "C:\\skills\\docx", "C:docx", "\\\\host\\share\\docx"):
            with self.subTest(query=query), self.assertRaisesRegex(ValueError, "Invalid skill identifier"):
                resolve_skill(self.skills, query)

    def test_windows_separators_normalize_to_exact_id(self):
        skill = resolve_skill(self.skills, "anthropics\\skills\\docx")
        self.assertEqual(skill.name, "anthropics-skills-docx")

    def test_duplicate_id_across_roots_is_ambiguous(self):
        self.make_skill(self.mine, "anthropics/skills/docx")
        with self.assertRaisesRegex(ValueError, "ambiguous across roots"):
            resolve_skill((self.skills, self.mine), "anthropics/skills/docx")

    def test_install_preserves_referenced_ai_context_assets_without_git_metadata(self):
        assets = {
            ".ai_context/prompts/writing/outline.md": "# Writing outline\n",
            ".ai_context/prompts/review.md": "# Review prose\n",
            ".ai_context/templates/project.json": '{"title": "template"}\n',
            "templates/brief.md": "# Brief template\n",
            ".claude/reference.md": "existing allowed configuration\n",
        }
        excluded = (".git/config", ".github/workflows/ci.yml", ".private/secret",
                    ".ai_context/.git/config", ".ai_context/.github/metadata")
        for relative, content in assets.items():
            path = self.upstream / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        for relative in excluded:
            path = self.upstream / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("excluded", encoding="utf-8")
        target = self.root / "target"
        self.assertEqual(add_skill(self.skills, "anthropics/skills/docx", target), 0)
        installed = target / ".agents/skills/anthropics-skills-docx"
        for relative, content in assets.items():
            with self.subTest(relative=relative):
                self.assertEqual((installed / relative).read_text(encoding="utf-8"), content)
        for relative in excluded:
            with self.subTest(relative=relative):
                self.assertFalse((installed / relative).exists())


if __name__ == "__main__":
    unittest.main()
