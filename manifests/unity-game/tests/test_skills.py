"""Verify hierarchical skill discovery, closure, installability and role routing."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests/unity-game"
PACKAGE = ROOT / "mine/unity-game-development"
CATALOG = PACKAGE / "references/skill-map.json"


def local_links(path: Path):
    for target in re.findall(r"\[[^\]]+\]\(([^\s)]+)(?:\s+[^)]*)?\)", path.read_text(encoding="utf-8")):
        if not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) and not target.startswith("#"):
            yield (path.parent / target.split("#", 1)[0]).resolve()


def walk_nodes(nodes):
    for node in nodes:
        yield node
        yield from walk_nodes(node.get("subskills", []))


class HierarchicalSkillsTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.skills = {self.catalog["root_skill"]: self.catalog["root_path"]}
        for stage in self.catalog["stages"]:
            self.skills[stage["skill"]] = stage["path"]
            self.skills.update({node["name"]: node["path"] for node in walk_nodes(stage["subskills"])})
            self.skills[stage["execution"]["skill"]] = stage["execution"]["path"]
        self.skills.update({node["name"]: node["path"] for node in self.catalog["review_skills"]})
        sys.path.insert(0, str(ROOT / "tools/vibe_tool/src"))
        self.addCleanup(lambda: sys.path.remove(str(ROOT / "tools/vibe_tool/src")))

    def run_vibe(self, *args):
        return subprocess.run([sys.executable, "-B", "-m", "vibe_tool", *map(str, args)],
                              cwd=ROOT, capture_output=True, text=True, timeout=90,
                              env={**os.environ, "VIBE_HOME": str(ROOT), "PYTHONPATH": str(ROOT / "tools/vibe_tool/src"), "PYTHONDONTWRITEBYTECODE": "1"})

    def assert_closed_links(self, folder):
        for file in folder.rglob("*.md"):
            for target in local_links(file):
                self.assertTrue(target.is_relative_to(folder.resolve()), f"Dependency escapes installed skill: {file} -> {target}")
                self.assertTrue(target.is_file(), f"Missing dependency: {file} -> {target}")

    def test_catalog_has_real_unique_skills_for_every_lifecycle_stage(self):
        self.assertEqual(len(self.skills), 67)
        self.assertEqual(len(self.catalog["stages"]), 9)
        self.assertEqual(sum(len(x["subskills"]) for x in self.catalog["stages"]), 31)
        actual = {str(p.relative_to(PACKAGE)) for p in PACKAGE.rglob("SKILL.md")}
        self.assertEqual(set(self.skills.values()), actual)
        stages = re.findall(r"^## \d+\. ([a-z-]+) —", (MANIFEST / "references/lifecycle.md").read_text(), re.M)
        self.assertEqual([x["id"] for x in self.catalog["stages"]], stages)
        for name, relative in self.skills.items():
            p = PACKAGE / relative
            text = p.read_text(encoding="utf-8")
            self.assertEqual(p.parent.name, name)
            match = re.match(r"^---\n(.*?)\n---\n(.+)$", text, re.S)
            self.assertIsNotNone(match, name)
            self.assertRegex(match[1], r"(?m)^name: " + re.escape(name) + r"\s*$")
            self.assertRegex(match[1], r"(?m)^description:\s*\S")

    def test_all_skills_resolve_to_the_exact_canonical_names(self):
        from vibe_tool.discovery import discover_skills, resolve_skill
        roots = ROOT / "skills", ROOT / "mine"
        discovered = discover_skills(*roots)
        for name, relative in self.skills.items():
            self.assertEqual(sum(item.name == name for item in discovered), 1, name)
            self.assertEqual(resolve_skill(roots, name).source_path, (PACKAGE / relative).parent)

    def test_routers_link_their_actual_children_and_source_package_is_closed(self):
        self.assert_closed_links(PACKAGE)
        root_links = set(local_links(PACKAGE / "SKILL.md"))
        for stage in self.catalog["stages"]:
            path = PACKAGE / stage["path"]
            self.assertIn(path.resolve(), root_links)
            parent_links = set(local_links(path))
            self.assertTrue({(PACKAGE / n["path"]).resolve() for n in stage["subskills"]}.issubset(parent_links))
            self.assertIn((PACKAGE / stage["execution"]["path"]).resolve(), parent_links)
            self.assertIn((PACKAGE / stage["execution"]["path"]).resolve(), root_links)
        for stage in self.catalog["stages"]:
            for node in walk_nodes(stage["subskills"]):
                links = set(local_links(PACKAGE / node["path"]))
                self.assertTrue({(PACKAGE / n["path"]).resolve() for n in node.get("subskills", [])}.issubset(links))
        self.assertIn((PACKAGE / "unity-game-review/SKILL.md").resolve(), root_links)

    def test_all_native_roles_reference_actual_assigned_skill_files(self):
        claude_dir, codex_dir = MANIFEST / ".claude/agents", MANIFEST / ".codex/agents"
        names = {p.stem for p in claude_dir.glob("*.md")}
        self.assertEqual(set(self.catalog["role_skills"]), names)
        for role, skills in self.catalog["role_skills"].items():
            claude = (claude_dir / (role + ".md")).read_text()
            codex = tomllib.loads((codex_dir / (role + ".toml")).read_text())["developer_instructions"]
            self.assertEqual(claude.split("---", 2)[2].strip(), codex.strip(), role)
            for name in skills:
                path = ".agents/skills/unity-game-development/" + self.skills[name]
                self.assertIn(path, claude, role)
                self.assertIn(path, codex, role)
        for stage in self.catalog["stages"]:
            for node in walk_nodes(stage["subskills"]):
                for role in node["roles"]:
                    self.assertIn(node["name"], self.catalog["role_skills"][role])
            for role in stage["execution"]["roles"]:
                self.assertIn(stage["execution"]["skill"], self.catalog["role_skills"][role])
            self.assertEqual(stage["review"]["profile"], stage["id"])
            self.assertEqual(stage["review"]["skill"], "unity-game-review")
            self.assertIn("unity-game-review", self.catalog["role_skills"]["game-reviewer"])

    def test_manifest_installs_only_bundle_not_duplicate_descendants(self):
        from vibe_tool.discovery import resolve_manifest
        manifest = resolve_manifest(ROOT / "manifests", "unity-game")
        entries = [name for name in manifest.required_skills if name in self.skills]
        self.assertEqual(entries, ["unity-game-development"])

    def test_bundle_and_each_stage_or_leaf_install_with_closed_dependencies(self):
        from vibe_tool.skill import add_skill
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            for name, relative in self.skills.items():
                with self.subTest(skill=name):
                    target = Path(tmp) / name
                    self.assertEqual(add_skill((ROOT / "skills", ROOT / "mine"), name, target), 0)
                    installed = target / ".agents/skills" / name
                    source = (PACKAGE / relative).parent
                    source_files = {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
                    installed_files = {p.relative_to(installed): p.read_bytes() for p in installed.rglob("*") if p.is_file()}
                    self.assertEqual(source_files, installed_files)
                    self.assert_closed_links(installed)

    def test_public_cli_lists_bundle_stages_and_subskills(self):
        result = self.run_vibe("list", "skills", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        names = {x["name"] for x in json.loads(result.stdout)}
        self.assertTrue(set(self.skills).issubset(names))

    def test_public_cli_installs_a_stage_and_a_standalone_leaf(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, count in (("unity-game-design", 8), ("unity-game-performance", 1),
                                ("unity-game-production-execute", 1), ("unity-game-review", 5),
                                ("unity-game-modeling", 6), ("unity-game-model-build", 1),
                                ("unity-game-production", 12), ("unity-game-testing", 8),
                                ("unity-game-play-execution", 1), ("unity-game-alpha", 12)):
                with self.subTest(skill=name):
                    target = Path(tmp) / name
                    preview = self.run_vibe("add", "skill", name, target, "--dry-run")
                    self.assertEqual(preview.returncode, 0, preview.stderr)
                    self.assertFalse(target.exists())
                    added = self.run_vibe("add", "skill", name, target)
                    self.assertEqual(added.returncode, 0, added.stderr)
                    installed = target / ".agents/skills" / name
                    self.assertEqual(len(list(installed.rglob("SKILL.md"))), count)
                    self.assert_closed_links(installed)

    def test_manifest_upgrade_adds_missing_bundle_preserving_customized_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing game"
            old_skill = target / ".agents/skills/git-manager/SKILL.md"
            import shutil
            shutil.copytree(ROOT / "mine/git-manager", old_skill.parent)
            old_skill.write_text("custom existing skill")
            result = self.run_vibe("add", "manifest", "unity-game", target, "--force")
            self.assertEqual(result.returncode, 0, result.stderr)
            bundle = target / ".agents/skills/unity-game-development"
            self.assertEqual(len(list(bundle.rglob("SKILL.md"))), 67)
            self.assertEqual(old_skill.read_text(), "custom existing skill")
            sentinel = bundle / "custom-notes.txt"
            sentinel.write_text("user notes")
            rerun = self.run_vibe("add", "manifest", "unity-game", target, "--force")
            self.assertEqual(rerun.returncode, 0, rerun.stderr)
            self.assertEqual(sentinel.read_text(), "user notes")
            self.assertTrue((target / ".unity-game/references/skills.md").is_file())


if __name__ == "__main__":
    unittest.main()
