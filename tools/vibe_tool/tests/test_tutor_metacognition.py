"""Resource/graph/CLI contracts, not an executed model or learning-effect study."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / "manifests/tutor"
ASSETS = ("references/metacognitive-framework.md", "references/metacognition-cases.md",
          "references/workflow.json", "references/workflow.svg", "scripts/render_workflow.py")


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in root.rglob("*") if p.is_file()}


def local_links(document):
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
        href = match.group(1).split("#", 1)[0]
        if href and not re.match(r"[a-z]+://", href):
            yield document.parent / href


class TutorMetacognitionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tutor framework 空格 ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, VIBE_HOME=str(REPO), PYTHONDONTWRITEBYTECODE="1",
                        PYTHONPATH=str(REPO / "tools/vibe_tool/src"))

    def run_command(self, args, cwd=REPO, expected=0):
        result = subprocess.run([sys.executable, "-B", *map(str, args)], cwd=cwd,
                                env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def render(self, root, expected=0, check=True):
        args = [root / "scripts/render_workflow.py", "--source", root / "references/workflow.json",
                "--output", root / "references/workflow.svg"]
        return self.run_command(args + (["--check"] if check else []), expected=expected)

    def test_foundation_is_reachable_from_all_shared_entrypoints(self):
        for rel in ("AGENTS.md", "CLAUDE.md", "README.md", ".cursorrules", "skills/SKILL.md",
                    "skills/active-learning/SKILL.md", "rules/tutor-core.mdc"):
            with self.subTest(document=rel):
                self.assertIn("references/metacognitive-framework.md",
                              (MANIFEST / rel).read_text(encoding="utf-8"))
        for rel in ("references/tutor-interaction.md", "references/learning-records.md"):
            self.assertIn("metacognitive-framework.md", (MANIFEST / rel).read_text(encoding="utf-8"))
        for rel in ("references/metacognitive-framework.md", "templates/LEARNING_RECORD.md.example"):
            text = (MANIFEST / rel).read_text(encoding="utf-8")
            for phrase in ("JOL", "FOK", "EOL", "完成信心", "重要性", "未评估", "回溯", "恢复点"):
                self.assertIn(phrase, text)
        text = (MANIFEST / "references/metacognitive-framework.md").read_text(encoding="utf-8")
        self.assertIn("完成标准与个人预测是两回事", text)
        self.assertIn("不要求先提供 JOL", text)
        self.assertIn("当前答对不证明未来记住", text)

    def test_graph_preserves_retrieval_calibration_control_and_decision_routes(self):
        data = json.loads((MANIFEST / "references/workflow.json").read_text(encoding="utf-8"))
        nodes = {n["id"]: n for n in data["nodes"]}
        routes = {(e["from"], e["to"]) for e in data["edges"]}
        for route in (("retrieval", "jol"), ("retrieval", "fok"), ("retrieval", "learn"),
                      ("compare", "finish"), ("compare", "calibrate"), ("calibrate", "finish"),
                      ("compare", "eol"), ("eol", "control"),
                      ("control", "retry"), ("retry", "retrospect"), ("retrospect", "compare"),
                      ("retrospect", "switch"), ("switch", "select"), ("switch", "memory"),
                      ("switch", "decision"), ("decision", "learn"), ("decision", "select"),
                      ("decision", "finish")):
            self.assertIn(route, routes)
        self.assertEqual(nodes["decision"]["kind"], "human")
        self.assertIn("预算", nodes["decision"]["trigger"])
        self.assertIn("等待", nodes["decision"]["label"])
        self.assertIn("未评估", nodes["compare"]["detail"])
        self.assertIn("不算", nodes["retry"]["detail"])
        self.assertIn("三类知识", nodes["memory"]["detail"])
        ET.parse(MANIFEST / "references/workflow.svg")
        self.render(MANIFEST)

    def test_new_document_links_resolve_in_source(self):
        for rel in (*ASSETS[:2], "README.md", "CLAUDE.md", "AGENTS.md",
                    "references/learning-records.md", "references/tutor-interaction.md"):
            for link in local_links(MANIFEST / rel):
                self.assertTrue(link.is_file(), f"{rel}: {link}")

    def test_check_is_read_only_for_success_missing_drift_and_broken_node_reference(self):
        work = self.root / "fixture"
        shutil.copytree(MANIFEST / "references", work / "references")
        (work / "scripts").mkdir()
        shutil.copy2(MANIFEST / "scripts/render_workflow.py", work / "scripts/render_workflow.py")
        before = snapshot(work)
        self.render(work)
        self.assertEqual(snapshot(work), before)
        svg = work / "references/workflow.svg"
        svg.unlink()
        before = snapshot(work)
        self.assertIn("MISSING", self.render(work, expected=1).stderr)
        self.assertEqual(snapshot(work), before)
        self.render(work, check=False)
        source = work / "references/workflow.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        data["nodes"][1]["detail"] += " 源数据变更。"
        source.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        before = snapshot(work)
        self.assertIn("DRIFT", self.render(work, expected=1).stderr)
        self.assertEqual(snapshot(work), before)
        data["edges"][0]["to"] = "missing_node"
        source.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        before = snapshot(work)
        self.assertIn("unknown node", self.render(work, expected=2).stderr)
        self.assertEqual(snapshot(work), before)

    def test_cli_init_and_add_distribute_workflow_and_rebuild_without_repo_dependencies(self):
        for mode in ("init", "add"):
            with self.subTest(mode=mode):
                target = self.root / (mode + " 学习项目")
                if mode == "add":
                    target.mkdir()
                    (target / "user.md").write_text("用户原有文件\n", encoding="utf-8")
                    args = ["-m", "vibe_tool", "add", "manifest", "tutor", target]
                else:
                    args = ["-m", "vibe_tool", "init", "tutor", target]
                self.run_command(args)
                for rel in ASSETS:
                    self.assertEqual((target / rel).read_bytes(), (MANIFEST / rel).read_bytes(), rel)
                for rel in ("README.md", "CLAUDE.md", "AGENTS.md", *ASSETS[:2],
                            "references/learning-records.md", "references/tutor-interaction.md"):
                    for link in local_links(target / rel):
                        self.assertTrue(link.is_file(), f"{rel}: {link}")
                # Run from the installed project; delete SVG to prove independent rebuilding.
                svg = target / "references/workflow.svg"
                expected = hashlib.sha256(svg.read_bytes()).hexdigest()
                svg.unlink()
                self.run_command(["scripts/render_workflow.py", "--source", "references/workflow.json",
                                  "--output", "references/workflow.svg"], cwd=target)
                self.assertEqual(hashlib.sha256(svg.read_bytes()).hexdigest(), expected)
                before = snapshot(target)
                self.render(target)
                self.assertEqual(snapshot(target), before)
                if mode == "add":
                    self.assertEqual((target / "user.md").read_text(encoding="utf-8"), "用户原有文件\n")

    def test_force_upgrade_and_standalone_rollback_include_new_workflow_resources(self):
        target = self.root / "旧项目"
        (target / "projects/统计").mkdir(parents=True)
        record = target / "projects/统计/LEARNING_RECORD.md"
        record.write_text("# 原学习记录\n待答原题：为什么平方？\n", encoding="utf-8")
        (target / "references").mkdir()
        (target / "references/workflow.svg").write_text("edited prior diagram\n", encoding="utf-8")
        before = snapshot(target)
        self.run_command(["-m", "vibe_tool", "add", "manifest", "tutor", target, "--force"])
        self.render(target)
        self.assertEqual(record.read_bytes(), before["projects/统计/LEARNING_RECORD.md"][0])
        backups = list((target / ".vibe-tool/backups/tutor").iterdir())
        self.assertEqual(len(backups), 1)
        self.run_command([backups[0] / "restore.py"], cwd=self.root)
        restored = {k: v for k, v in snapshot(target).items() if not k.startswith(".vibe-tool/")}
        self.assertEqual(restored, before)

    def test_acceptance_cases_are_explicitly_not_executed_model_results(self):
        text = (MANIFEST / "references/metacognition-cases.md").read_text(encoding="utf-8")
        self.assertIn("待执行", text)
        self.assertIn("不等于已验证教学效果", text)
        self.assertIn("不得冒充独立会话通过", text)

    def test_update_adds_workflow_to_older_install_and_standalone_restore_removes_it(self):
        target = self.root / "旧版模板安装"
        self.run_command(["-m", "vibe_tool", "init", "tutor", target])
        for rel in ASSETS:
            (target / rel).unlink()
        record = target / "projects/统计/LEARNING_RECORD.md"
        record.parent.mkdir(parents=True)
        record.write_text("# 旧记录\n没有监测区，仍保留待答题。\n", encoding="utf-8")
        (target / "README.md").write_text("用户自定义说明\n", encoding="utf-8")
        before = snapshot(target)
        self.run_command(["-m", "vibe_tool", "update", "manifest", "tutor", target, "--dry-run"])
        self.assertEqual(snapshot(target), before)
        self.run_command(["-m", "vibe_tool", "update", "manifest", "tutor", target])
        for rel in ASSETS:
            self.assertTrue((target / rel).is_file(), rel)
            self.assertEqual((target / rel).read_bytes(), (MANIFEST / rel).read_bytes(), rel)
        self.render(target)
        self.assertEqual(record.read_bytes(), before["projects/统计/LEARNING_RECORD.md"][0])
        self.assertEqual((target / "README.md").read_bytes(), before["README.md"][0])
        backups = list((target / ".vibe-tool/backups").glob("*/restore.py"))
        self.assertEqual(len(backups), 1)
        self.run_command([backups[0]], cwd=self.root)
        restored = {k: v for k, v in snapshot(target).items() if "/backups/" not in k}
        baseline = {k: v for k, v in before.items() if "/backups/" not in k}
        self.assertEqual(restored, baseline)


if __name__ == "__main__":
    unittest.main()
