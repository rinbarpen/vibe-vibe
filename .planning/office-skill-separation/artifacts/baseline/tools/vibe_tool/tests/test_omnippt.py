"""Omnippt contract invariants and the real installed, self-contained skill."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[3]
SKILL = REPO / "mine/omnippt"
SCRIPT = SKILL / "scripts/validate_deck.py"
CLI_SOURCE = REPO / "tools/vibe_tool/src"
spec = importlib.util.spec_from_file_location("omnippt_contract_test", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def contract():
    """Complete synthetic design fixture, not a claimed live user decision."""
    return {
        "schema_version": 1, "id": "sales-review", "revision": 1, "mode": "create",
        "brief": {"audience": "管理团队", "outcome": "核对演示数据并确认后续分析范围"},
        "canvas": {"width": 13.333, "height": 7.5, "unit": "in"},
        "tokens": {"font": "Noto Sans CJK SC", "background": "#FFFFFF", "foreground": "#17233D",
                   "accent": "#2563EB", "body_pt": 20, "title_pt": 30},
        "sources": [{"id": "sales-data", "kind": "data", "location": "sales.csv"}],
        "facts": [{"id": "sales-total", "text": "演示销售合计为600，不代表真实经营结果", "source_ids": ["sales-data"]}],
        "outline": [{"id": "summary", "conclusion": "三个月演示销售合计600", "fact_ids": ["sales-total"]}],
        "storyboard": [{"id": "summary", "layout": "原生标题与两张并列信息卡片", "elements": [
            {"id": "summary-title", "kind": "text", "native": True, "text": "三个月演示销售合计600",
             "box": [0.6, 0.4, 12, 0.8], "fact_ids": ["sales-total"]},
            {"id": "summary-card", "kind": "card", "native": True, "box": [0.6, 1.6, 5.8, 4.8]},
            {"id": "summary-value", "kind": "text", "native": True, "text": "600｜合计",
             "box": [0.9, 2, 5, 0.8], "parent": "summary-card", "fact_ids": ["sales-total"]},
            {"id": "summary-limit", "kind": "card", "native": True, "box": [6.9, 1.6, 5.8, 4.8]},
            {"id": "summary-caveat", "kind": "text", "native": True, "text": "模拟数据；不作因果推断",
             "box": [7.2, 2, 5, 0.8], "parent": "summary-limit"}]}],
        "stage_revisions": {"outline": 1, "storyboard": 1, "design": 1},
        "decisions": {
            "chart": {"decision": "pending", "scope": "sales-review", "source": None},
            "macro": {"decision": "pending", "scope": "sales-review", "source": None, "requested_modes": []}},
    }


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="omnippt 合同 ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "sales.csv").write_text("month,sales\nJan,100\nFeb,200\nMar,300\n")

    def validate(self, value):
        return checker.validate_deck(value, base_dir=self.root)

    def assert_invalid(self, value, expected):
        report = self.validate(value)
        self.assertEqual(report["status"], "invalid", report)
        self.assertFalse(report["structure_valid"])
        self.assertTrue(any(expected in item["message"] or expected in item["path"] for item in report["errors"]), report)

    def test_valid_contract_is_draft_not_visual_or_native_qa(self):
        original = contract()
        before = deepcopy(original)
        report = self.validate(original)
        self.assertEqual(report["status"], "draft", report)
        self.assertTrue(report["structure_valid"])
        self.assertTrue(report["ready_for_nonchart_build"])
        self.assertTrue(report["ready_for_all_requested_build"])
        self.assertEqual(report["quality_status"], "pending")
        self.assertFalse(report["evidence_authenticated"])
        self.assertEqual(original, before, "Validator must not mutate the contract")

    def test_source_ids_location_hash_url_and_slide_facts_resolve(self):
        mutations = (
            (lambda c: c["facts"][0].update(source_ids=["missing-source"]), "Unresolved reference"),
            (lambda c: c["sources"][0].update(location="missing.csv"), "does not exist"),
            (lambda c: c["sources"][0].update(sha256="0" * 64), "SHA-256 mismatch"),
            (lambda c: c["sources"][0].update(kind="url", location="https://["), "absolute HTTP"),
            (lambda c: c["outline"][0].update(fact_ids=[]), "belong to this slide"),
        )
        for mutation, message in mutations:
            with self.subTest(message=message):
                value = contract()
                mutation(value)
                self.assert_invalid(value, message)
        value = contract()
        value["sources"][0]["sha256"] = hashlib.sha256((self.root / "sales.csv").read_bytes()).hexdigest()
        self.assertTrue(self.validate(value)["structure_valid"])
        no_root = checker.validate_deck(value)
        self.assertTrue(no_root["warnings"])

    def test_unique_ids_outline_coverage_order_and_stale_stages(self):
        mutations = (
            (lambda c: c["outline"].append(deepcopy(c["outline"][0])), "Duplicate stable ID"),
            (lambda c: c["storyboard"][0].update(id="orphan"), "coverage"),
            (lambda c: c.update(revision=2), "stale stage"),
            (lambda c: c["stage_revisions"].update(design=True), "stale stage"),
            (lambda c: c["storyboard"][0]["elements"][1].update(id="summary-title"), "Duplicate stable ID"),
        )
        for mutation, message in mutations:
            with self.subTest(message=message):
                value = contract()
                mutation(value)
                self.assert_invalid(value, message)
        value = contract()
        value["outline"].append({"id": "next", "conclusion": "下一步核验", "fact_ids": []})
        value["storyboard"].insert(0, {"id": "next", "layout": "原生文本", "elements": [
            {"id": "next-text", "kind": "text", "native": True, "text": "先核对输入数据", "box": [1, 1, 10, 2]}]})
        self.assert_invalid(value, "order differs")

    def test_boxes_finite_positive_in_bounds_and_parent_containment(self):
        for box, message in (([0, 0, 14, 1], "overflows"), ([-1, 0, 1, 1], "overflows"),
                             ([0, 0, 0, 1], "finite"), ([0, 0, float("nan"), 1], "finite"),
                             ([0, 0, True, 1], "finite"), ([0, 0, 10 ** 1000, 1], "finite")):
            with self.subTest(message=message, box=str(box)[:45]):
                value = contract()
                value["storyboard"][0]["elements"][0]["box"] = box
                self.assert_invalid(value, message)
        value = contract()
        value["storyboard"][0]["elements"][2]["box"][0] = 0
        self.assert_invalid(value, "fit inside")
        for parent in ("missing", ["summary-card"]):
            with self.subTest(parent=parent):
                value = contract()
                value["storyboard"][0]["elements"][2]["parent"] = parent
                self.assert_invalid(value, "parent")

    def test_peer_card_overlap_rejected_explicit_parent_nesting_allowed(self):
        value = contract()
        value["storyboard"][0]["elements"][3]["box"][0] = 5
        self.assert_invalid(value, "Peer cards overlap")
        value = contract()
        value["storyboard"][0]["elements"].append({"id": "nested-card", "kind": "card", "native": True,
                                                    "parent": "summary-card", "box": [0.8, 3.5, 5, 2]})
        self.assertTrue(self.validate(value)["structure_valid"])

    def test_native_intent_requires_objects_not_image_claims(self):
        value = contract()
        value["storyboard"][0]["elements"][0]["native"] = False
        self.assert_invalid(value, "editable")
        value = contract()
        value["storyboard"][0]["elements"][0].update(kind="image", native=True)
        self.assert_invalid(value, "Image fallback")

    def test_new_native_and_image_charts_need_yes_nonchart_can_continue(self):
        for kind in ("chart", "image"):
            for answer in ("yes", "no", "pending"):
                with self.subTest(kind=kind, answer=answer):
                    value = contract()
                    value["decisions"]["chart"].update(decision=answer, source="SIMULATED chart reply" if answer != "pending" else None,
                                                        evidence_type="simulated")
                    value["storyboard"][0]["elements"].append({"id": "sales-chart", "kind": kind,
                        "native": kind != "image", "chart": True, "box": [1, 4, 3, 2], "fact_ids": ["sales-total"]})
                    report = self.validate(value)
                    self.assertTrue(report["structure_valid"], report)
                    self.assertTrue(report["ready_for_nonchart_build"])
                    self.assertEqual(report["ready_for_all_requested_build"], answer == "yes")
                    self.assertEqual(bool(report["blocked_operations"]), answer != "yes")
                    value["storyboard"][0]["elements"][-1]["operation"] = "preserve"
                    self.assert_invalid(value, "new deck has no existing chart")
                    value.update(mode="edit", edit_scope={"slide_ids": ["summary"], "notes": "仅保留既有图表，改标题"})
                    self.assertTrue(self.validate(value)["ready_for_all_requested_build"])

    def test_explicit_decisions_need_evidence_and_matching_scope(self):
        for kind in ("chart", "macro"):
            with self.subTest(kind=kind):
                value = contract()
                value["decisions"][kind].update(decision="yes")
                self.assert_invalid(value, "evidence")
                value["decisions"][kind].update(source="SIMULATED", evidence_type="simulated", scope="another-deck")
                self.assert_invalid(value, "scope")

    def test_macro_yes_still_needs_operation_mode_details(self):
        value = contract()
        macro = value["decisions"]["macro"]
        macro.update(decision="yes", source="SIMULATED selected macro approval", evidence_type="simulated", requested_modes=["invoke"])
        report = self.validate(value)
        self.assertTrue(report["structure_valid"])
        self.assertFalse(report["ready_for_all_requested_build"])
        self.assertEqual(report["blocked_operations"][0]["reason"], "pending_operation_details")
        macro["operation_details"] = {"invoke": {"target": "working-copy.pptm", "entry": "OfficePresentation.RefreshSelected",
                                                 "intent": "更新已选文本", "effects": "仅目标文本框，无保存"}}
        self.assertTrue(self.validate(value)["ready_for_all_requested_build"])
        macro["decision"] = "pending"
        self.assertFalse(self.validate(value)["ready_for_all_requested_build"])
        self.assertTrue(self.validate(value)["ready_for_nonchart_build"])

    def test_selected_edit_contract_and_native_template_hash(self):
        value = contract()
        value.update(mode="edit", edit_scope={"slide_ids": ["summary"], "notes": "只改所选页的标题措辞"})
        self.assertTrue(self.validate(value)["structure_valid"])
        value["edit_scope"]["slide_ids"] = []
        self.assert_invalid(value, "selected slides")
        value = contract()
        template = self.root / "source-template.pptx"
        template.write_bytes(b"inert hash fixture, not an actual presentation")
        value.update(mode="template", template={"path": template.name, "sha256": hashlib.sha256(template.read_bytes()).hexdigest()})
        self.assertTrue(self.validate(value)["structure_valid"])
        value["template"]["sha256"] = "0" * 64
        self.assert_invalid(value, "SHA-256 mismatch")

    def test_cli_readonly_fresh_report_and_invalid_json(self):
        source = self.root / "deck contract.json"
        source.write_text(json.dumps(contract(), ensure_ascii=False))
        before = source.read_bytes()
        report = self.root / "report.json"
        run = lambda *args: subprocess.run([sys.executable, str(SCRIPT), str(source), *map(str, args)], capture_output=True, text=True)
        result = run("--report", report)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(report.read_text())["source_unchanged"])
        self.assertEqual(run("--report", report).returncode, 1)
        self.assertEqual(run("--report", source).returncode, 1)
        self.assertEqual(source.read_bytes(), before)
        source.write_text('{"schema_version":NaN}')
        self.assertEqual(run().returncode, 1)


class InstalledOmnipptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="omnippt installed subtree ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo, self.target = self.root / "fixture repo", self.root / "project with spaces"
        (self.repo / "skills").mkdir(parents=True)
        (self.repo / "manifests").mkdir()
        shutil.copytree(SKILL, self.repo / "mine/omnippt", ignore=shutil.ignore_patterns("__pycache__"))
        self.env = dict(os.environ, VIBE_HOME=str(self.repo), PYTHONPATH=str(CLI_SOURCE), PYTHONDONTWRITEBYTECODE="1")

    def cli(self, *args):
        return subprocess.run([sys.executable, "-m", "vibe_tool", *map(str, args)], env=self.env,
                              cwd=self.root, capture_output=True, text=True)

    def test_real_root_skill_six_subskills_template_and_helper_install_and_run(self):
        result = self.cli("add", "skill", "omnippt", self.target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        installed = self.target / ".agents/skills/omnippt"
        self.assertTrue((installed / "SKILL.md").is_file())
        self.assertEqual(len([path for path in installed.rglob("SKILL.md")
                              if path.parent != installed]), 6)
        source_files = {p.relative_to(SKILL): p.read_bytes() for p in SKILL.rglob("*")
                        if p.is_file() and "__pycache__" not in p.parts}
        for relative, data in source_files.items():
            with self.subTest(path=relative):
                self.assertEqual((installed / relative).read_bytes(), data)
        example = installed / "templates/deck-contract.example.json"
        self.assertTrue(example.is_file())
        result = subprocess.run([sys.executable, str(installed / "scripts/validate_deck.py"), str(example),
                                 "--report", str(self.root / "installed-report.json")], cwd=self.target,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads((self.root / "installed-report.json").read_text())
        self.assertTrue(report["structure_valid"])
        self.assertEqual(report["quality_status"], "pending")
        self.assertGreaterEqual(report["slide_count"], 2)

    def test_dry_run_zero_write_and_force_update_subtree(self):
        result = self.cli("add", "skill", "omnippt", self.target, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.target.exists())
        result = self.cli("add", "skill", "omnippt", self.target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        installed_script = self.target / ".agents/skills/omnippt/scripts/validate_deck.py"
        installed_script.write_text("local edit\n")
        result = self.cli("add", "skill", "omnippt", self.target, "--force")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(installed_script.read_bytes(), SCRIPT.read_bytes())


if __name__ == "__main__":
    unittest.main()
