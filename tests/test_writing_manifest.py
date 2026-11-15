"""Focused, standard-library checks for the bid-writing manifest.

Run: python -m unittest discover -s tests -p test_writing_manifest.py -v
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/writing"
CHECK = MANIFEST / "scripts/check_bid.py"
RENDER = MANIFEST / "scripts/render_workflow.py"


def tree_hash(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class WritingManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="writing bid test ")
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        for directory in ("sources", "draft"):
            (self.project / directory).mkdir()
        (self.project / "sources/tender.txt").write_text("测试夹具要求：提供实施方案。\n")
        (self.project / "sources/proof.txt").write_text("测试夹具证明材料。\n")
        (self.project / "draft/01.md").write_text("# 实施方案\n<!-- REQ:R-001 -->\n测试夹具响应。\n")
        self.data = {
            "schema_version": 1,
            "project": {"name": "测试夹具", "lot": "01", "tender_revision": "fixture-v1",
                        "deadline": "2030-01-02T09:00:00+08:00"},
            "sources": [
                {"id": "T-001", "kind": "tender", "path": "sources/tender.txt",
                 "sha256": hashlib.sha256((self.project / "sources/tender.txt").read_bytes()).hexdigest()},
                {"id": "E-001", "kind": "bidder", "path": "sources/proof.txt",
                 "sha256": hashlib.sha256((self.project / "sources/proof.txt").read_bytes()).hexdigest()},
            ],
            "requirements": [
                {"id": "R-001", "source_id": "T-001", "locator": "第 1 行",
                 "text": "提供实施方案", "category": "scored", "status": "covered",
                 "response_path": "draft/01.md", "requires_evidence": True,
                 "evidence": [{"source_id": "E-001", "locator": "第 1 行"}], "note": ""},
            ],
        }

    def run_script(self, script, *args, expected=0):
        result = subprocess.run([sys.executable, str(script), *map(str, args)],
                                cwd=self.project, capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def check(self, data=None, mode="release", expected=0):
        path = self.project / "bid.json"
        path.write_text(json.dumps(self.data if data is None else data, ensure_ascii=False) + "\n")
        before = tree_hash(self.project)
        result = self.run_script(CHECK, path, "--mode", mode, expected=expected)
        self.assertEqual(before, tree_hash(self.project), "checker must be read-only")
        return result

    def test_complete_fixture_passes_both_modes(self):
        for mode in ("draft", "release"):
            result = self.check(mode=mode)
            self.assertIn("covered=1 errors=0 warnings=0", result.stdout)

    def test_starter_is_draft_only(self):
        data = json.loads((MANIFEST / "templates/project.json").read_text())
        self.assertIn("warnings=6", self.check(data, mode="draft").stdout)
        self.assertIn("errors=6", self.check(data, expected=1).stdout)

    def test_source_tamper_is_error_even_in_draft(self):
        (self.project / "sources/proof.txt").write_text("changed fixture")
        for mode in ("draft", "release"):
            self.assertIn("SHA-256 mismatch", self.check(mode=mode, expected=1).stdout)

    def test_missing_files_evidence_and_markers(self):
        mutations = [
            lambda d: d["sources"][1].update(path="sources/missing.txt"),
            lambda d: d["sources"][1].update(sha256=""),
            lambda d: d["requirements"][0].update(evidence=[]),
            lambda d: d["requirements"][0].update(response_path="draft/missing.md"),
            lambda d: d["requirements"][0].update(id="R-002"),
            lambda d: d["requirements"][0].update(status="gap"),
            lambda d: d["requirements"][0].update(locator=""),
            lambda d: d["requirements"][0]["evidence"][0].update(locator=""),
            lambda d: d["sources"][1].update(kind="reference"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data = copy.deepcopy(self.data)
                mutate(data)
                self.check(data, mode="draft")
                self.check(data, expected=1)

    def test_unknown_duplicate_and_malformed_fields(self):
        mutations = [
            lambda d: d.update(schema_version=True),
            lambda d: d.update(extra="unsupported"),
            lambda d: d["sources"].append(copy.deepcopy(d["sources"][0])),
            lambda d: d["requirements"].append(copy.deepcopy(d["requirements"][0])),
            lambda d: d["requirements"][0].update(source_id="unknown"),
            lambda d: d["requirements"][0].update(source_id="E-001"),
            lambda d: d["requirements"][0]["evidence"][0].update(source_id="unknown"),
            lambda d: d["requirements"][0].update(category=[]),
            lambda d: d["requirements"][0].update(requires_evidence="true"),
            lambda d: d["sources"][0].update(sha256="bad-hash"),
            lambda d: d["project"].update(deadline="2030-01-02T09:00:00"),
            lambda d: d["project"].update(deadline="invalid"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data = copy.deepcopy(self.data)
                mutate(data)
                self.check(data, expected=2)

    def test_escape_paths_are_rejected(self):
        for path in ("../external.txt", "/tmp/external.txt", "C:/external.txt",
                     "..\\external.txt", "https://host/file", "sources/../../file"):
            with self.subTest(path=path):
                data = copy.deepcopy(self.data)
                data["sources"][0]["path"] = path
                self.check(data, expected=2)

    def test_symlinks_are_rejected(self):
        link = self.project / "sources/link.txt"
        try:
            link.symlink_to(self.project / "sources/tender.txt")
        except OSError as exc:
            self.skipTest(str(exc))
        data = copy.deepcopy(self.data)
        data["sources"][0]["path"] = "sources/link.txt"
        self.check(data, expected=2)

    def test_duplicate_json_keys_and_invalid_utf8(self):
        matrix = self.project / "invalid.json"
        matrix.write_text('{"schema_version": 1, "schema_version": 1}')
        result = self.run_script(CHECK, matrix, expected=2)
        self.assertIn("duplicate JSON key", result.stderr)
        matrix.write_bytes(b"\xff")
        self.run_script(CHECK, matrix, expected=2)

    def test_workflow_is_parseable_current_and_readonly(self):
        ET.parse(MANIFEST / "references/workflow.svg")
        args = ["--source", MANIFEST / "references/workflow.json", "--output",
                self.project / "workflow.svg"]
        self.run_script(RENDER, *args)
        before = tree_hash(self.project)
        self.run_script(RENDER, *args, "--check")
        self.assertEqual(before, tree_hash(self.project))
        self.assertEqual((self.project / "workflow.svg").read_bytes(),
                         (MANIFEST / "references/workflow.svg").read_bytes())

    def test_workflow_missing_drift_and_broken_references_fail_without_writes(self):
        source = self.project / "workflow.json"
        source.write_bytes((MANIFEST / "references/workflow.json").read_bytes())
        output = self.project / "missing/sub/workflow.svg"
        before = tree_hash(self.project)
        self.run_script(RENDER, "--source", source, "--output", output, "--check", expected=1)
        self.assertFalse(output.parent.exists())
        self.assertEqual(before, tree_hash(self.project))
        output = self.project / "workflow.svg"
        self.run_script(RENDER, "--source", source, "--output", output)
        data = json.loads(source.read_text())
        data["title"] += " changed"
        source.write_text(json.dumps(data))
        before = tree_hash(self.project)
        self.run_script(RENDER, "--source", source, "--output", output, "--check", expected=1)
        self.assertEqual(before, tree_hash(self.project))
        data["edges"][0]["to"] = "nonexistent"
        source.write_text(json.dumps(data))
        before = tree_hash(self.project)
        self.run_script(RENDER, "--source", source, "--output", output, "--check", expected=2)
        self.assertEqual(before, tree_hash(self.project))

    def test_manifest_relative_links_exist(self):
        for file in MANIFEST.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", file.read_text()):
                if target.startswith(("http:", "https:", "#")):
                    continue
                path = (file.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(path.exists(), f"broken link in {file}: {target}")


class WritingSetupTests(unittest.TestCase):
    def test_setup_existing_project_check_conflict_idempotence_and_rollback(self):
        needed = [ROOT / "mine/z-writing/references/ai-vibe-writing/SKILL.md",
                  ROOT / "mine/z-humanizer/references/unslop/SKILL.md"]
        if not all(path.is_file() for path in needed):
            self.skipTest("initialize the writing source submodules for the installation test")
        with tempfile.TemporaryDirectory(prefix="writing setup existing ") as tmp:
            base = Path(tmp)
            project = base / "bid project"
            project.mkdir()
            for name, content in {"README.md": "User README\n", "AGENTS.md": "User constraints\n",
                                  "bid.json": "user business state\n"}.items():
                (project / name).write_text(content)
            original = tree_hash(project)
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                   "VIBE_PROJECTS_FILE": str(base / "isolated-projects.json")}

            def run(script, *args, expected=0):
                result = subprocess.run([sys.executable, str(script), *map(str, args)],
                                        cwd=ROOT, capture_output=True, text=True, env=env, timeout=90)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                return result

            setup = ROOT / "scripts/setup-project.py"
            options = ("--harness", "generic", "--scenario", "bid", "--skill", "z-writing")
            run(setup, "writing", project, *options, "--dry-run")
            self.assertEqual(tree_hash(project), original)
            self.assertFalse((base / "isolated-projects.json").exists())
            run(setup, "writing", project, *options)
            run(setup, "writing", project, "--check")
            self.assertTrue((project / "AGENTS.md").read_text().startswith("User constraints\n"))
            self.assertEqual((project / "README.md").read_text(), "User README\n")
            self.assertEqual((project / "bid.json").read_text(), "user business state\n")
            self.assertFalse((project / ".cursor").exists())
            rules = json.loads((project / "rules/writing/rules.json").read_text())
            self.assertEqual([r["source"] for r in rules["rules"]], ["scenarios/bid/rules/bid.md"])
            self.assertFalse((project / "rules/writing/rules/patent.md").exists())
            for relative in ("PROJECT_RULES.md", "rules/writing/CONTRACT.md",
                             "rules/writing/references/workflow.svg",
                             ".agents/skills/z-writing/references/ai-vibe-writing/SKILL.md",
                             ".agents/skills/z-writing/references/ai-vibe-writing/.ai_context/prompts/7_content_writer_agent.md",
                             ".agents/skills/z-writing/references/z-humanizer/references/unslop/SKILL.md"):
                self.assertTrue((project / relative).is_file(), relative)
            self.assertFalse(any(path.is_symlink() for path in (project / ".agents/skills/z-writing").rglob("*")))
            run(project / "scripts/check_bid.py", project / "templates/project.json", "--mode", "draft")
            run(project / "scripts/check_bid.py", project / "templates/project.json", "--mode", "release", expected=1)
            for prefix in ("", "rules/writing/"):
                run(project / (prefix + "scripts/render_workflow.py"),
                    "--source", project / (prefix + "references/workflow.json"),
                    "--output", project / (prefix + "references/workflow.svg"))
                run(project / (prefix + "scripts/render_workflow.py"),
                    "--source", project / (prefix + "references/workflow.json"),
                    "--output", project / (prefix + "references/workflow.svg"), "--check")
            for file in [project / "AGENTS.vibe-writing.md", *list((project / "rules/writing").rglob("*.md"))]:
                for target in re.findall(r"\]\(([^)]+)\)", file.read_text()):
                    if not target.startswith(("http:", "https:", "#")):
                        self.assertTrue((file.parent / target.split("#", 1)[0]).exists(),
                                        f"installed broken link: {file} -> {target}")
            installed = tree_hash(project)
            run(setup, "writing", project, *options)
            self.assertEqual(tree_hash(project), installed)
            local = project / "scripts/check_bid.py"
            content = local.read_bytes()
            local.write_bytes(content + b"\n# local customization\n")
            changed = tree_hash(project)
            run(setup, "writing", project, *options, "--dry-run", expected=1)
            self.assertEqual(tree_hash(project), changed)
            run(setup, "writing", project, "--check", expected=1)
            local.write_bytes(content)
            run(setup, "writing", project, "--check")
            restores = list((project / ".vibe-tool/backups").glob("*/restore.py"))
            self.assertEqual(len(restores), 1)
            run(restores[0])
            remaining = {k: v for k, v in tree_hash(project).items()
                         if not k.startswith(".vibe-tool/backups/")}
            self.assertEqual(remaining, original)


if __name__ == "__main__":
    unittest.main()
