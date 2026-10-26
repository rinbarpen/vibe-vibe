"""Dependency-free contract tests for manifest workflow sources and SVG output.

Run with::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_manifest_workflow.py
"""
from __future__ import annotations

import copy
import importlib.util
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
SCRIPT = ROOT / "scripts" / "render-manifest-workflow.py"
GUIDE = ROOT / "docs" / "manifest-workflow.md"
EXAMPLE = ROOT / "docs" / "examples" / "manifest-workflow"
SVG_NS = "{http://www.w3.org/2000/svg}"


def workflow() -> dict:
    """A minimal structural fixture with an explicit human-decision rework loop."""
    return {
        "schema_version": 1,
        "title": "Manifest 人机协作工作流",
        "description": "AI 自主执行；出现新决策时由人工确认，再恢复原进度。",
        "nodes": [
            {"id": "start", "label": "接受目标", "kind": "terminal", "row": 0, "detail": "读取既有约定"},
            {"id": "execute", "label": "AI 自主执行", "kind": "ai", "row": 1, "detail": "执行并保留可回退记录"},
            {"id": "validate", "label": "验证既定约定", "kind": "check", "row": 2, "detail": "验收结果并识别新增决策"},
            {
                "id": "decide", "label": "人工决策", "kind": "human", "row": 3,
                "detail": "提供现状、选项和建议", "trigger": "目标有歧义或需改变约定",
                "resume": "记录确认结果，恢复 AI 执行",
            },
            {"id": "done", "label": "交付结果", "kind": "terminal", "row": 4, "detail": "验证通过且回退方式明确"},
        ],
        "edges": [
            {"from": "start", "to": "execute", "label": "目标明确", "kind": "normal"},
            {"from": "execute", "to": "validate", "label": "提交验证", "kind": "normal"},
            {"from": "validate", "to": "done", "label": "符合既定约定", "kind": "normal"},
            {"from": "validate", "to": "decide", "label": "需要人工取舍", "kind": "normal"},
            {"from": "decide", "to": "execute", "label": "确认后继续", "kind": "rework"},
        ],
    }


class ManifestWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.is_file():
            raise AssertionError(f"Missing workflow renderer: {SCRIPT}")
        spec = importlib.util.spec_from_file_location("manifest_workflow_renderer_contract", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        # Importing the script must not create a repository __pycache__ either.
        previous = sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode = True
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        cls.renderer = module

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="manifest-workflow-test-")
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.source = self.directory / "workflow.json"
        self.output = self.directory / "workflow.svg"

    def write_source(self, value=None):
        if value is None:
            value = workflow()
        self.source.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return self.source

    def cli(self, *, source=None, output=None, check=False):
        args = [sys.executable, str(SCRIPT), "--source", str(source or self.source),
                "--output", str(output or self.output)]
        if check:
            args.append("--check")
        return subprocess.run(
            args, cwd=self.directory, text=True, encoding="utf-8", capture_output=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=15,
        )

    def assert_exit(self, result, expected):
        self.assertEqual(result.returncode, expected,
                         f"stdout={result.stdout!r}\nstderr={result.stderr!r}")

    def parse_svg(self, value):
        root = ET.fromstring(value)
        self.assertEqual(root.tag, SVG_NS + "svg")
        self.assertTrue(root.get("viewBox"), "SVG needs a scalable viewBox")
        return root

    def test_public_functions_and_deterministic_parseable_svg(self):
        self.write_source()
        loaded = self.renderer.load_workflow(self.source)
        self.assertEqual(loaded, workflow())
        self.assertTrue(callable(self.renderer.main))
        first = self.renderer.render(loaded)
        self.assertIsInstance(first, str)
        self.assertEqual(first, self.renderer.render(copy.deepcopy(loaded)))
        root = self.parse_svg(first)
        visible = " ".join(root.itertext())
        for node in loaded["nodes"]:
            self.assertIn(node["label"], visible)
        self.assertIn(loaded["title"], visible)
        self.assertIn(loaded["nodes"][3]["trigger"], visible)
        self.assertIn(loaded["nodes"][3]["resume"], visible)
        self.assert_exit(self.cli(), 0)
        self.assertEqual(self.output.read_text(encoding="utf-8"), first)
        original = self.output.read_bytes()
        self.assert_exit(self.cli(), 0)
        self.assertEqual(self.output.read_bytes(), original)

    def test_xml_escapes_all_user_facing_text(self):
        value = workflow()
        text = 'XML <&> "quoted" \'single\''
        value["title"] = text
        value["description"] = text
        value["nodes"][1]["label"] = text
        value["nodes"][1]["detail"] = text
        value["nodes"][3]["trigger"] = text
        value["nodes"][3]["resume"] = text
        value["edges"][0]["label"] = text
        self.write_source(value)
        self.assert_exit(self.cli(), 0)
        rendered = self.output.read_text(encoding="utf-8")
        root = self.parse_svg(rendered)
        self.assertIn(text, "".join(root.itertext()))
        self.assertIn("&lt;", rendered)
        self.assertIn("&amp;", rendered)

    def test_check_is_read_only_for_current_drifted_and_missing_output(self):
        self.write_source()
        self.assert_exit(self.cli(), 0)
        for drifted in (False, True):
            with self.subTest(drifted=drifted):
                if drifted:
                    self.output.write_text("<svg>stale</svg>\n", encoding="utf-8")
                os.utime(self.output, ns=(1_000_000_000, 2_000_000_000))
                original = self.output.read_bytes()
                before = self.output.stat().st_mtime_ns
                self.assert_exit(self.cli(check=True), 1 if drifted else 0)
                self.assertEqual(self.output.read_bytes(), original)
                self.assertEqual(self.output.stat().st_mtime_ns, before)
        missing = self.directory / "must-not-exist" / "nested" / "workflow.svg"
        self.assert_exit(self.cli(output=missing, check=True), 1)
        self.assertFalse(missing.parent.parent.exists(), "--check created a directory")

    def test_long_labels_are_wrapped_or_rejected_without_truncation(self):
        value = workflow()
        label = "长标签需要合理换行" * 60
        value["nodes"][1]["label"] = label
        self.write_source(value)
        result = self.cli()
        if result.returncode == 2:
            self.assertTrue((result.stdout + result.stderr).strip())
            self.assertFalse(self.output.exists())
            return
        self.assert_exit(result, 0)
        root = self.parse_svg(self.output.read_text(encoding="utf-8"))
        chunks = [element.text or "" for element in root.iter()
                  if element.tag in (SVG_NS + "text", SVG_NS + "tspan")]
        self.assertIn(label, "".join(chunks), "Long labels were silently truncated")
        self.assertLessEqual(max(map(len, chunks)), 100, "Long labels need wrapping")

    def test_invalid_schema_and_graphs_exit_two_without_output(self):
        cases = []

        def case(name, mutate):
            value = workflow()
            mutate(value)
            cases.append((name, value))

        case("unsupported schema", lambda v: v.update(schema_version=2))
        case("boolean schema", lambda v: v.update(schema_version=True))
        case("missing schema", lambda v: v.pop("schema_version"))
        case("empty title", lambda v: v.update(title="  "))
        case("wrong title type", lambda v: v.update(title=12))
        case("empty description", lambda v: v.update(description=" "))
        case("wrong description type", lambda v: v.update(description=[]))
        case("wrong nodes type", lambda v: v.update(nodes={}))
        case("empty nodes", lambda v: v.update(nodes=[]))
        case("wrong edges type", lambda v: v.update(edges={}))
        case("empty edges", lambda v: v.update(edges=[]))
        case("duplicate id", lambda v: v["nodes"][1].update(id="start"))
        case("empty id", lambda v: v["nodes"][1].update(id=""))
        case("invalid id characters", lambda v: v["nodes"][1].update(id="bad id"))
        case("invalid node kind", lambda v: v["nodes"][1].update(kind="unknown"))
        case("wrong node type", lambda v: v["nodes"].__setitem__(1, "execute"))
        case("empty label", lambda v: v["nodes"][1].update(label="\t"))
        case("wrong label type", lambda v: v["nodes"][1].update(label=[]))
        case("empty detail", lambda v: v["nodes"][1].update(detail=""))
        case("wrong detail type", lambda v: v["nodes"][1].update(detail=[]))
        case("negative row", lambda v: v["nodes"][1].update(row=-1))
        case("boolean row", lambda v: v["nodes"][1].update(row=True))
        case("string row", lambda v: v["nodes"][1].update(row="1"))
        case("float row", lambda v: v["nodes"][1].update(row=1.5))
        case("same cell", lambda v: v["nodes"][4].update(row=2))
        case("missing human trigger", lambda v: v["nodes"][3].pop("trigger"))
        case("missing human resume", lambda v: v["nodes"][3].pop("resume"))
        case("empty human trigger", lambda v: v["nodes"][3].update(trigger=" "))
        case("empty human resume", lambda v: v["nodes"][3].update(resume=""))
        case("unknown source", lambda v: v["edges"][0].update(**{"from": "missing"}))
        case("unknown destination", lambda v: v["edges"][0].update(to="missing"))
        case("invalid edge kind", lambda v: v["edges"][0].update(kind="unknown"))
        case("empty edge label", lambda v: v["edges"][0].update(label=" "))
        case("wrong edge label type", lambda v: v["edges"][0].update(label=[]))
        case("wrong edge type", lambda v: v["edges"].__setitem__(0, []))
        case("no terminal start", lambda v: v["nodes"][0].update(kind="ai"))
        case("no terminal finish", lambda v: v["nodes"][4].update(kind="ai"))
        def add_second_start(value):
            value["nodes"].append({"id": "second_start", "label": "额外起点", "kind": "terminal",
                                   "row": 6, "detail": "多个起点存在歧义"})
            value["edges"].append({"from": "second_start", "to": "execute", "label": "另一入口", "kind": "normal"})

        def add_second_finish(value):
            value["nodes"].append({"id": "second_finish", "label": "额外终点", "kind": "terminal",
                                   "row": 6, "detail": "多个终点存在歧义"})
            value["edges"].append({"from": "validate", "to": "second_finish", "label": "另一出口", "kind": "normal"})

        case("multiple starts", add_second_start)
        case("multiple finishes", add_second_finish)
        case("unreachable node", lambda v: v["nodes"].append(
            {"id": "orphan", "label": "孤立节点", "kind": "ai", "row": 5, "detail": "没有入口"}))
        case("no path to finish", lambda v: v["edges"].__setitem__(4,
            {"from": "decide", "to": "decide", "label": "停滞", "kind": "rework"}))
        cases.extend([("array root", []), ("string root", "workflow"), ("null root", None)])
        for name, value in cases:
            with self.subTest(case=name):
                self.source.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
                self.assert_exit(self.cli(), 2)
                self.assertFalse(self.output.exists(), "Invalid input created output")

    def test_invalid_json_and_missing_source_exit_two(self):
        self.source.write_text("{broken", encoding="utf-8")
        self.assert_exit(self.cli(), 2)
        self.assertFalse(self.output.exists())
        self.source.unlink()
        self.assert_exit(self.cli(), 2)
        self.assertFalse(self.output.exists())

    def test_invalid_source_preserves_existing_output(self):
        self.write_source()
        self.output.write_bytes(b"original output\n")
        original = self.output.read_bytes()
        self.source.write_text('{"schema_version": 99}', encoding="utf-8")
        for check in (False, True):
            with self.subTest(check=check):
                self.assert_exit(self.cli(check=check), 2)
                self.assertEqual(self.output.read_bytes(), original)

    def test_source_output_identity_and_aliases_are_protected(self):
        self.write_source()
        original = self.source.read_bytes()
        aliases = [self.source, self.source.parent / "." / self.source.name]
        symlink = self.directory / "source-link.svg"
        symlink.symlink_to(self.source)
        aliases.append(symlink)
        hardlink = self.directory / "source-hardlink.svg"
        hardlink.hardlink_to(self.source)
        aliases.append(hardlink)
        for output in aliases:
            for check in (False, True):
                with self.subTest(output=output.name, check=check):
                    self.assert_exit(self.cli(output=output, check=check), 2)
                    self.assertEqual(self.source.read_bytes(), original)

    def test_committed_example_is_current_and_contains_human_handoff(self):
        source, output = EXAMPLE / "workflow.json", EXAMPLE / "workflow.svg"
        self.assertTrue(source.is_file())
        self.assertTrue(output.is_file())
        before = (output.read_bytes(), output.stat().st_mtime_ns)
        self.assert_exit(self.cli(source=source, output=output, check=True), 0)
        self.assertEqual((output.read_bytes(), output.stat().st_mtime_ns), before)
        value = self.renderer.load_workflow(source)
        self.parse_svg(output.read_text(encoding="utf-8"))
        humans = [node for node in value["nodes"] if node["kind"] == "human"]
        self.assertTrue(humans)
        for node in humans:
            self.assertTrue(node.get("trigger") and node.get("resume"))
            outgoing = [edge for edge in value["edges"] if edge["from"] == node["id"]]
            self.assertGreaterEqual(len(outgoing), 2, "Examples need both a decision and a return path")
            self.assertTrue(all(edge.get("label", "").strip() for edge in outgoing))
            self.assertTrue(any(edge["kind"] == "rework" for edge in outgoing))
            self.assertTrue(any(edge["kind"] == "normal" for edge in outgoing))

    def test_authoring_entries_link_to_guide_and_guide_links_to_real_example(self):
        self.assertTrue(GUIDE.is_file())
        for name in ("AGENTS.md", "README.md", "README_EN.md"):
            with self.subTest(entry=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                links = re.findall(r"\]\(([^)]+)\)", text)
                self.assertTrue(any(link.split("#", 1)[0].removeprefix("./") ==
                                    "docs/manifest-workflow.md" for link in links),
                                f"{name} must link to the manifest authoring guide")
        text = GUIDE.read_text(encoding="utf-8")
        links = [link.split("#", 1)[0] for link in re.findall(r"\]\(([^)]+)\)", text)]
        for expected in (EXAMPLE / "workflow.json", EXAMPLE / "workflow.svg"):
            self.assertTrue(any((GUIDE.parent / link).resolve() == expected.resolve()
                                for link in links if link and "://" not in link),
                            f"Guide must link to its real example: {expected.name}")
        self.assertIn("--check", text)
        self.assertIn("render-manifest-workflow.py", text)


if __name__ == "__main__":
    unittest.main()
