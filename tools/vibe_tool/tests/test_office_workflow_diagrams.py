"""Documentation diagrams and explicit Omni skill routing, not an SVG runtime."""
import hashlib
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[3]
OFFICE = ROOT / "manifests/office"
SKILL_NAMES = ("office-quality", "omnidraw", "omnisheet", "omnippt")


class OfficeWorkflowDiagramTests(unittest.TestCase):
    def test_manifest_and_four_skills_have_actual_linked_workflow_illustrations(self):
        entries = [(OFFICE, "README.md")] + [(ROOT / "mine" / name, "SKILL.md") for name in SKILL_NAMES]
        for base, entry in entries:
            with self.subTest(entry=str(base / entry)):
                markdown = (base / entry).read_text(encoding="utf-8")
                self.assertRegex(markdown, r"!\[[^\]]+\]\(assets/workflow\.svg\)")
                svg = base / "assets/workflow.svg"
                source = base / "assets/workflow.mmd"
                self.assertTrue(source.is_file())
                self.assertIn("flowchart", source.read_text(encoding="utf-8"))
                tree = ET.fromstring(svg.read_bytes())
                self.assertEqual(tree.tag, "{http://www.w3.org/2000/svg}svg")
                box = [float(x) for x in tree.attrib["viewBox"].replace(",", " ").split()]
                self.assertEqual(len(box), 4)
                self.assertTrue(all(math.isfinite(x) for x in box))
                self.assertTrue(box[2] > 0 and box[3] > 0)
                self.assertGreaterEqual(len(list(tree.iter("{http://www.w3.org/2000/svg}text"))), 4)

    def test_office_requires_omni_entry_skills_without_new_svg_processing_feature(self):
        required = [line.split("#", 1)[0].strip() for line in (OFFICE / "skills.txt").read_text().splitlines()]
        required = [line for line in required if line]
        self.assertEqual(len(required), 9)
        self.assertEqual(len(set(required)), 9)
        self.assertIn("omnidraw", required)
        self.assertIn("omnisheet", required)
        self.assertIn("omnippt", required)
        self.assertFalse((OFFICE / "scripts/svg_workflow.py").exists())
        self.assertFalse((OFFICE / "scripts/svg_office.py").exists())
        self.assertFalse((OFFICE / "workflows/svg").exists())
        for base in (OFFICE, ROOT / "mine/office-quality"):
            for file in base.rglob("*"):
                if file.suffix in (".md", ".mdc", ".toml", ".py"):
                    text = file.read_text(encoding="utf-8")
                    self.assertNotRegex(text, r"svg_workflow\.py|svg_office\.py|workflows/svg")

    def test_real_office_assets_and_nested_omni_skills_install_with_valid_image_paths(self):
        with tempfile.TemporaryDirectory(prefix="Office illustrated workflows ") as directory:
            base = Path(directory)
            repo, target = base / "fixture repo", base / "new project"
            shutil.copytree(OFFICE, repo / "manifests/office", ignore=shutil.ignore_patterns("__pycache__"))
            for name in SKILL_NAMES:
                shutil.copytree(ROOT / "mine" / name, repo / "mine" / name,
                                ignore=shutil.ignore_patterns("__pycache__"))
            # Hermetic stand-ins only for external dependencies; actual first-party
            # packages and their nested references/assets are copied above.
            for name in ("docx", "xlsx", "pptx", "pdf"):
                skill = repo / "skills/anthropics/skills" / name
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text(f"---\nname: {name}\ndescription: fixture\n---\n")
            ai = repo / "skills/ai-vibe-writing"
            ai.mkdir()
            (ai / "SKILL.md").write_text("---\nname: ai-vibe-writing\ndescription: fixture\n---\n")
            command = [sys.executable, "-m", "vibe_tool", "init", "office", str(target)]
            env = {**os.environ, "VIBE_HOME": str(repo), "PYTHONPATH": str(ROOT / "tools/vibe_tool/src"),
                   "PYTHONDONTWRITEBYTECODE": "1"}
            result = subprocess.run(command, cwd=base, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in SKILL_NAMES:
                for relative in ("SKILL.md", "assets/workflow.svg", "assets/workflow.mmd"):
                    original = ROOT / "mine" / name / relative
                    installed = target / ".agents/skills" / name / relative
                    self.assertEqual(hashlib.sha256(original.read_bytes()).digest(), hashlib.sha256(installed.read_bytes()).digest())
            for relative in ("omnidraw/mermaid/SKILL.md", "omnidraw/references/routing-matrix.md",
                             "omnisheet/financial/SKILL.md", "omnisheet/data-analysis/SKILL.md",
                             "omnisheet/references/style-guide.md"):
                self.assertTrue((target / ".agents/skills" / relative).is_file(), relative)
            for entry in (target / "README.md", target / "office/README.md",
                          *(target / ".agents/skills" / name / "SKILL.md" for name in SKILL_NAMES)):
                text = entry.read_text(encoding="utf-8")
                links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
                self.assertTrue(links, str(entry))
                for link in links:
                    self.assertTrue((entry.parent / link).is_file(), f"{entry}: {link}")
            self.assertIn("](office/assets/workflow.svg)", (target / "README.md").read_text())
            self.assertIn("](assets/workflow.svg)", (target / "office/README.md").read_text())
