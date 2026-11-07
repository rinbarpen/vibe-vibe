"""Offline tests for the optional intuition-led Idea route and its packaging.

Run from the repository root:
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src \
        python3 -m unittest discover -s manifests/auto-research/tests \
        -p test_idea_skill.py -v
"""

import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from vibe_tool.discovery import discover_manifests, resolve_skill
from vibe_tool.manifest import add_manifest, init_manifest


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests/auto-research"
SKILL = ROOT / "skills/intuit-to-idea"
RENDERER = MANIFEST / "scripts/render_idea_workflow.py"
SOURCE = MANIFEST / "references/idea-workflow.json"
SVG = MANIFEST / "references/idea-workflow.svg"


def snapshot(root):
    return {
        path.relative_to(root).as_posix(): (
            "file" if path.is_file() else "directory",
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
            path.stat().st_mtime_ns,
        )
        for path in root.rglob("*")
    }


class IdeaWorkflowTests(unittest.TestCase):
    def render(self, source, output, check=False):
        command = [sys.executable, str(RENDERER), "--source", str(source), "--output", str(output)]
        if check:
            command.append("--check")
        return subprocess.run(command, capture_output=True, text=True, check=False)

    def test_manifest_declares_skill_and_existing_stage_gates_remain(self):
        manifest = next(item for item in discover_manifests(ROOT / "manifests") if item.name == "auto-research")
        self.assertEqual(manifest.required_skills.count("intuit-to-idea"), 1)
        stages = {s["id"]: s for s in json.loads((MANIFEST / "lifecycle/defaults.json").read_text())["stages"]}
        self.assertEqual(stages["idea/hypotheses/candidates"]["approval"], "auto")
        self.assertEqual(stages["idea/hypotheses/comparison"]["approval"], "human_confirmation")

    def test_checked_in_svg_is_current_and_parseable(self):
        before = SVG.read_bytes()
        result = self.render(SOURCE, SVG, check=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(SVG.read_bytes(), before)
        document = ET.fromstring(before)
        self.assertEqual(document.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIsNotNone(document.find("{http://www.w3.org/2000/svg}title"))

    def test_check_missing_output_does_not_create_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = snapshot(root)
            result = self.render(SOURCE, root / "missing/idea.svg", check=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(snapshot(root), before)

    def test_drift_and_invalid_graph_fail_without_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "source.json", root / "idea.svg"
            shutil.copy2(SOURCE, source)
            self.assertEqual(self.render(source, output).returncode, 0)
            workflow = json.loads(source.read_text())
            workflow["title"] += " — changed"
            source.write_text(json.dumps(workflow, ensure_ascii=False))
            before = snapshot(root)
            self.assertEqual(self.render(source, output, check=True).returncode, 1)
            self.assertEqual(snapshot(root), before)
            self.assertEqual(self.render(source, output).returncode, 0)
            self.assertEqual(self.render(source, output, check=True).returncode, 0)
            workflow["edges"][0]["to"] = "absent-node"
            source.write_text(json.dumps(workflow, ensure_ascii=False))
            before = snapshot(root)
            self.assertEqual(self.render(source, output, check=True).returncode, 2)
            self.assertEqual(snapshot(root), before)


@unittest.skipUnless((SKILL / "SKILL.md").is_file(), "Initialize skills/intuit-to-idea submodule first")
class IdeaInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.manifests = self.repository / "manifests"
        self.source = self.manifests / "auto-research"
        shutil.copytree(MANIFEST, self.source, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(SKILL, self.repository / "skills/intuit-to-idea", ignore=shutil.ignore_patterns(".git"))
        # Isolate this dependency from unrelated research skill bundles. The real
        # manifest's dependency declaration is checked separately above.
        (self.source / "skills.txt").write_text("intuit-to-idea\n")

    def test_discovery_resolves_the_complete_root_skill(self):
        skill = resolve_skill((self.repository / "skills", self.repository / "mine"), "intuit-to-idea")
        self.assertEqual(skill.source_path, self.repository / "skills/intuit-to-idea")

    def test_init_and_add_install_skill_support_files_and_runnable_graph(self):
        for operation in (init_manifest, add_manifest):
            with self.subTest(operation=operation.__name__):
                target = self.root / (operation.__name__ + " project with spaces")
                if operation is add_manifest:
                    target.mkdir()
                    (target / "research-notes.md").write_text("user evidence\n")
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = operation(self.manifests, "auto-research", target)
                self.assertEqual(rc, 0)
                installed = target / ".agents/skills/intuit-to-idea"
                for relative in ("SKILL.md", "agents/openai.yaml", "references/idea-card.md",
                                 "references/novelty-check.md", "references/dialogue-example.md"):
                    self.assertEqual((installed / relative).read_bytes(), (SKILL / relative).read_bytes())
                command = [sys.executable, str(target / "scripts/render_idea_workflow.py"),
                           "--source", str(target / "references/idea-workflow.json"),
                           "--output", str(target / "references/idea-workflow.svg")]
                for suffix in ([], ["--check"]):
                    result = subprocess.run(command + suffix, cwd=self.root, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((target / "references/intuit-to-idea.md").is_file())
                self.assertTrue((target / ".vibe-tool/installations.json").is_file())
                self.assertFalse((target / ".auto-research/lifecycle/events.jsonl").exists())
                if operation is add_manifest:
                    self.assertEqual((target / "research-notes.md").read_text(), "user evidence\n")

    def test_dry_run_leaves_existing_project_unchanged(self):
        target = self.root / "existing project"
        target.mkdir()
        (target / "CLAUDE.md").write_text("existing instructions\n")
        before = snapshot(target)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = add_manifest(self.manifests, "auto-research", target, dry_run=True)
        self.assertEqual(rc, 0)
        self.assertEqual(snapshot(target), before)


if __name__ == "__main__":
    unittest.main()
