import tempfile
import unittest
from pathlib import Path

from vibe_tool.discovery import discover_skills, resolve_skill
from vibe_tool.project_update import update_skill
from vibe_tool.skill import add_skill


class WritingDesignSourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skills = self.root / "skills"
        self.mine = self.root / "mine"
        self.skills.mkdir()
        self.mine.mkdir()
        (self.root / "manifests").mkdir()
        self.roots = (self.skills, self.mine)

    def write(self, relative, content="# Fixture\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def impeccable(self):
        return self.write("skills/impeccable/.agents/skills/impeccable/SKILL.md").parent

    def test_impeccable_exposes_canonical_payload_not_provider_or_oracle_copies(self):
        canonical = self.impeccable()
        for relative in (
            "skills/impeccable/.claude/skills/impeccable/SKILL.md",
            "skills/impeccable/plugin/skills/impeccable/SKILL.md",
            "skills/impeccable/tests/oracle/.agents/skills/impeccable/SKILL.md",
            "skills/impeccable/tests/oracle/.claude/skills/audit/SKILL.md",
        ):
            self.write(relative)
        self.write("skills/unrelated/audit/SKILL.md")
        catalog = discover_skills(*self.roots)
        self.assertEqual({s.name for s in catalog}, {"impeccable", "audit"})
        resolved = resolve_skill(self.roots, "impeccable")
        self.assertEqual(resolved.source_path, canonical)
        self.assertEqual(resolved.id_path, "impeccable/.agents/skills/impeccable")

    def test_no_canonical_payload_keeps_recursive_discovery(self):
        self.write("skills/impeccable/legacy/SKILL.md")
        self.write("skills/another/.agents/skills/design/SKILL.md")
        self.assertEqual(
            {s.name for s in discover_skills(*self.roots)}, {"legacy", "design"}
        )

    def test_real_name_collisions_still_use_relative_identifiers(self):
        self.impeccable()
        self.write("skills/another/impeccable/SKILL.md")
        self.assertEqual(
            {s.name for s in discover_skills(*self.roots)},
            {"impeccable-.agents-skills-impeccable", "another-impeccable"},
        )
        self.assertEqual(
            resolve_skill(self.roots, "impeccable/.agents/skills/impeccable").name,
            "impeccable-.agents-skills-impeccable",
        )

    def test_canonical_install_preserves_launchers_and_playbooks(self):
        source = self.impeccable()
        resources = {
            "scripts/impeccable": "#!/bin/sh\nexit 0\n",
            "scripts/impeccable.cmd": "@echo off\r\n",
            "reference/craft-floor.md": "# Quality floor\n",
            "agents/openai.yaml": "interface:\n  display_name: Impeccable\n",
        }
        for relative, content in resources.items():
            self.write(str(source.relative_to(self.root) / relative), content)
        target = self.root / "project"
        self.assertEqual(add_skill(self.roots, "impeccable", target), 0)
        destination = target / ".agents/skills/impeccable"
        for relative in ("SKILL.md", *resources):
            with self.subTest(resource=relative):
                self.assertEqual(
                    (destination / relative).read_bytes(), (source / relative).read_bytes()
                )

    def bundle_unslop(self):
        self.write("skills/unslop/SKILL.md")
        scanner = self.write("skills/unslop/scripts/scan.py", "print('scanner v1')\n")
        self.write("skills/unslop/references/core-contract.md", "# Contract\n")
        self.write("skills/unslop/.git/config", "excluded metadata\n")
        self.write("mine/z-humanizer/SKILL.md")
        self.write("mine/z-humanizer/patterns/conference.md", "# Conference\n")
        link = self.root / "mine/z-humanizer/references/unslop"
        link.parent.mkdir(parents=True)
        link.symlink_to("../../../skills/unslop", target_is_directory=True)
        return scanner

    def test_bundle_installs_without_a_separate_unslop_install_or_extra_catalog_entry(self):
        self.bundle_unslop()
        self.assertEqual(
            {s.name for s in discover_skills(*self.roots)}, {"unslop", "z-humanizer"}
        )
        target = self.root / "project"
        self.assertEqual(add_skill(self.roots, "z-humanizer", target), 0)
        installed = target / ".agents/skills/z-humanizer"
        bundle = installed / "references/unslop"
        self.assertFalse(bundle.is_symlink())
        self.assertTrue((bundle / "scripts/scan.py").is_file())
        self.assertTrue((bundle / "references/core-contract.md").is_file())
        self.assertFalse((bundle / ".git").exists())
        self.assertFalse((target / ".agents/skills/unslop").exists())
        self.assertEqual(
            (installed / "patterns/conference.md").read_bytes(),
            (self.mine / "z-humanizer/patterns/conference.md").read_bytes(),
        )

    def test_bundle_uses_updated_canonical_source_on_reinstall(self):
        scanner = self.bundle_unslop()
        target = self.root / "project"
        self.assertEqual(add_skill(self.roots, "z-humanizer", target), 0)
        scanner.write_text("print('scanner v2')\n", encoding="utf-8")
        self.assertEqual(add_skill(self.roots, "z-humanizer", target, force=True), 0)
        self.assertEqual(
            (target / ".agents/skills/z-humanizer/references/unslop/scripts/scan.py").read_bytes(),
            scanner.read_bytes(),
        )

    def test_direct_update_materializes_bundle_and_preserves_specialized_patterns(self):
        scanner = self.bundle_unslop()
        target = self.root / "project"
        self.assertEqual(add_skill(self.roots, "z-humanizer", target), 0)
        scanner.write_text("print('scanner v2')\n", encoding="utf-8")
        installed = target / ".agents/skills/z-humanizer"
        (installed / "patterns/conference.md").write_text("local edit\n", encoding="utf-8")
        self.assertEqual(update_skill(self.root, "z-humanizer", target, dry_run=True), 0)
        self.assertEqual((installed / "patterns/conference.md").read_text(), "local edit\n")
        self.assertEqual(update_skill(self.root, "z-humanizer", target), 0)
        self.assertFalse((installed / "references/unslop").is_symlink())
        self.assertEqual((installed / "references/unslop/scripts/scan.py").read_bytes(), scanner.read_bytes())
        self.assertEqual((installed / "patterns/conference.md").read_text(), "# Conference\n")

    def test_update_rejects_a_retargeted_dependency_without_changing_installation(self):
        self.bundle_unslop()
        target = self.root / "project"
        self.assertEqual(add_skill(self.roots, "z-humanizer", target), 0)
        alias = self.mine / "z-humanizer/references/unslop"
        alias.unlink()
        outside = self.root / "outside"
        outside.mkdir()
        alias.symlink_to(outside, target_is_directory=True)
        self.assertEqual(update_skill(self.root, "z-humanizer", target), 1)
        self.assertTrue((target / ".agents/skills/z-humanizer/references/unslop/scripts/scan.py").is_file())


if __name__ == "__main__":
    unittest.main()
