"""Execution/reviewer routing and reproducible installed SVG integration."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests/unity-game"
PACKAGE = ROOT / "mine/unity-game-development"
CATALOG = PACKAGE / "references/skill-map.json"
RENDERER = MANIFEST / "scripts/render_workflow.py"
SVG = MANIFEST / "references/workflow.svg"
SPEC = importlib.util.spec_from_file_location("unity_workflow_svg", RENDERER)
renderer = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(renderer)
NS = {"s": "http://www.w3.org/2000/svg"}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.catalog = renderer.load_catalog(CATALOG)

    def command(self, *args, script=RENDERER, cwd=ROOT):
        return subprocess.run([sys.executable, "-B", str(script), *map(str, args)], cwd=cwd,
                              capture_output=True, text=True, timeout=60,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def test_each_stage_has_a_unique_real_execution_skill_and_independent_review(self):
        executions = []
        approvals = {}
        review_names = {n["name"] for n in self.catalog["review_skills"]}
        self.assertEqual(len(review_names), 5)
        for stage in self.catalog["stages"]:
            execute = stage["execution"]
            executions.append(execute["skill"])
            self.assertTrue((PACKAGE / execute["path"]).is_file())
            self.assertTrue(execute["skill"].endswith("-execute"))
            self.assertEqual(stage["review"]["profile"], stage["id"])
            self.assertEqual(stage["review"]["skill"], "unity-game-review")
            self.assertTrue((PACKAGE / stage["review"]["path"]).is_file())
            self.assertTrue(set(stage["review"]["specialties"]).issubset(review_names))
            if stage["approval"]:
                approvals[stage["id"]] = stage["approval"]
        self.assertEqual(len(set(executions)), 9)
        self.assertEqual(approvals, renderer.APPROVALS)
        policy = self.catalog["review_policy"]
        self.assertTrue(policy["independent_context"])
        self.assertTrue(policy["pass_binds_revision"])
        self.assertEqual(policy["reviewer_role"], "game-reviewer")
        self.assertEqual(policy["rework_route"], "original_execution_skill")
        self.assertEqual(policy["absence_status"], "not_run")
        self.assertEqual(set(policy["verdicts"]), {"passed", "changes_requested", "blocked"})

    def test_committed_svg_is_reproducible_accessible_and_covers_actual_routes(self):
        self.assertEqual(SVG.read_text(), renderer.render(self.catalog))
        svg = ET.fromstring(SVG.read_text())
        self.assertEqual(svg.tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIsNotNone(svg.find("s:title", NS))
        self.assertIsNotNone(svg.find("s:desc", NS))
        self.assertFalse(svg.findall(".//s:script", NS))
        groups = [g for g in svg.findall("s:g", NS) if g.get("id", "").startswith("stage-")]
        self.assertEqual([g.get("id") for g in groups], ["stage-" + x["id"] for x in self.catalog["stages"]])
        for stage, group in zip(self.catalog["stages"], groups):
            texts = " ".join(group.itertext())
            for label in (stage["execution"]["skill"], stage["review"]["skill"],
                          "profile: " + stage["id"], "changes_requested", "blocked"):
                self.assertIn(label, texts)
            if stage["approval"]:
                self.assertIn(stage["approval"], texts)
        self.assertIn("review_status=not_run", " ".join(svg.itertext()))

    def test_modeling_subpipeline_uses_actual_nested_skills_routes_and_roles(self):
        svg = ET.fromstring(renderer.render(self.catalog))
        group = svg.find("s:g[@id='modeling-subpipeline']", NS)
        self.assertIsNotNone(group)
        text = " ".join(group.itertext())
        modeling = next(n for s in self.catalog["stages"] for n in s["subskills"] if n["name"] == "unity-game-modeling")
        self.assertEqual(len(modeling["subskills"]), 5)
        for node in modeling["subskills"]:
            self.assertIn(node["name"], text)
            self.assertIn(node["label"], text)
        for item in ("MCP", "Skill", "Blender CLI", "GUI", "model-artist", "technical-artist", "game-reviewer", "not_run"):
            self.assertIn(item, text)

    def test_legacy_catalog_without_modeling_branch_has_no_modeling_pane(self):
        data = copy.deepcopy(self.catalog)
        for stage in data["stages"]:
            stage["subskills"] = [n for n in stage["subskills"] if n["name"] != "unity-game-modeling"]
        svg = ET.fromstring(renderer.render(data))
        self.assertIsNone(svg.find("s:g[@id='modeling-subpipeline']", NS))
        self.assertEqual(len([g for g in svg.findall("s:g", NS) if g.get("id", "").startswith("stage-")]), 9)

    def test_game_testing_pane_uses_all_seven_real_subskills_and_review_route(self):
        svg = ET.fromstring(renderer.render(self.catalog))
        group = svg.find("s:g[@id='testing-subpipeline']", NS)
        self.assertIsNotNone(group)
        text = " ".join(group.itertext())
        branch = renderer.testing_branch(self.catalog)
        self.assertEqual(len(branch["subskills"]), 7)
        for node in branch["subskills"]:
            self.assertIn(node["name"], text)
            self.assertIn(node["label"], text)
        for item in ("QA", "game-reviewer", "MCP", "skill", "not_run", "revision"):
            self.assertIn(item, text)
        self.assertFalse(self.catalog["testing_policy"]["human_playtest_equivalence"])
        self.assertTrue(self.catalog["testing_policy"]["normal_input_required"])

    def test_legacy_catalog_without_testing_branch_keeps_model_pane(self):
        data = copy.deepcopy(self.catalog)
        for stage in data["stages"]:
            stage["subskills"] = [n for n in stage["subskills"] if n["name"] != "unity-game-testing"]
        svg = ET.fromstring(renderer.render(data))
        self.assertIsNone(svg.find("s:g[@id='testing-subpipeline']", NS))
        self.assertIsNotNone(svg.find("s:g[@id='modeling-subpipeline']", NS))

    def test_source_check_is_read_only(self):
        before = SVG.stat().st_mtime_ns, SVG.read_bytes()
        result = self.command("--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((SVG.stat().st_mtime_ns, SVG.read_bytes()), before)

    def test_missing_or_stale_check_preserves_output_and_does_not_create_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "new-dir/workflow.svg"
            result = self.command("--catalog", CATALOG, "--output", output, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertFalse(output.parent.exists())
            output.parent.mkdir()
            output.write_text("old SVG")
            before = output.stat().st_mtime_ns
            result = self.command("--catalog", CATALOG, "--output", output, "--check")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(output.read_text(), "old SVG")
            self.assertEqual(output.stat().st_mtime_ns, before)

    def test_invalid_catalog_does_not_replace_existing_output(self):
        bad_cases = []
        for modification in ("missing_execute", "wrong_profile", "wrong_gate", "wrong_order"):
            data = copy.deepcopy(self.catalog)
            if modification == "missing_execute":
                del data["stages"][0]["execution"]
            elif modification == "wrong_profile":
                data["stages"][0]["review"]["profile"] = "production"
            elif modification == "wrong_gate":
                data["stages"][1]["approval"] = None
            else:
                data["stages"].reverse()
            bad_cases.append((modification, data))
        with tempfile.TemporaryDirectory() as tmp:
            catalog, output = Path(tmp) / "catalog.json", Path(tmp) / "workflow.svg"
            output.write_text("preserved")
            for label, data in bad_cases:
                with self.subTest(label=label):
                    catalog.write_text(json.dumps(data))
                    result = self.command("--catalog", catalog, "--output", output)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(output.read_text(), "preserved")

    def test_labels_are_xml_escaped(self):
        data = copy.deepcopy(self.catalog)
        data["stages"][0]["label"] = "设计 <plan> & review"
        rendered = renderer.render(data)
        self.assertIn("设计 &lt;plan&gt; &amp; review", rendered)
        ET.fromstring(rendered)

    def make_installed_renderer(self, base):
        project = base / "repo/demo"
        script = project / ".unity-game/scripts/render_workflow.py"
        script.parent.mkdir(parents=True)
        shutil.copy2(RENDERER, script)
        return project, script

    def test_installed_renderer_uses_own_bundle_not_parent_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project, script = self.make_installed_renderer(base)
            wrong = base / "repo/mine/unity-game-development/references/skill-map.json"
            wrong.parent.mkdir(parents=True)
            data = copy.deepcopy(self.catalog)
            data["stages"][0]["label"] = "WRONG PARENT CATALOG"
            wrong.write_text(json.dumps(data))
            own = project / ".agents/skills/unity-game-development/references/skill-map.json"
            own.parent.mkdir(parents=True)
            own.write_bytes(CATALOG.read_bytes())
            result = self.command(script=script, cwd=ROOT)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((project / ".unity-game/references/workflow.svg").read_bytes(), SVG.read_bytes())

    def test_installed_renderer_missing_bundle_does_not_fall_back_to_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            project, script = self.make_installed_renderer(Path(tmp))
            result = self.command(script=script, cwd=ROOT)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((project / ".unity-game/references/workflow.svg").exists())
            explicit = self.command("--catalog", CATALOG, script=script, cwd=ROOT)
            self.assertEqual(explicit.returncode, 0, explicit.stderr)

    def test_public_manifest_install_includes_svg_and_regenerator(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "game with spaces"
            result = subprocess.run([sys.executable, "-B", "-m", "vibe_tool", "init", "unity-game", str(project)],
                                    cwd=ROOT, capture_output=True, text=True, timeout=90,
                                    env={**os.environ, "VIBE_HOME": str(ROOT), "PYTHONPATH": str(ROOT / "tools/vibe_tool/src"), "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(result.returncode, 0, result.stderr)
            script = project / ".unity-game/scripts/render_workflow.py"
            self.assertEqual((project / ".unity-game/references/workflow.svg").read_bytes(), SVG.read_bytes())
            checked = self.command("--check", script=script, cwd=project)
            self.assertEqual(checked.returncode, 0, checked.stderr)


if __name__ == "__main__":
    unittest.main()
