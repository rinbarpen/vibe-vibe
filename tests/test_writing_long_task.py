"""Long bid queue/checkpoint tests; fixture page counts are not real pagination."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "manifests/writing/scripts/long_task.py"
sys.path.insert(0, str(SCRIPT.parent))
import long_task as queue
sys.path.pop(0)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in root.rglob("*") if p.is_file()}


class LongWritingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="long bid queue ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for d in ("sources", "draft", "review", "delivery"):
            (self.root / d).mkdir()
        (self.root / "brief.md").write_text("Fixture scope and shared terminology.\n")
        (self.root / "sources/tender.txt").write_text("Fixture requirements.\n")
        self.make(2)

    def make(self, count, chain=True):
        self.bid = dict(schema_version=1, project=dict(name="TEST FIXTURE", lot="01", tender_revision="fixture-v1", deadline="2030-01-02T09:00:00+08:00"),
                        sources=[dict(id="T-001", kind="tender", path="sources/tender.txt", sha256=sha(self.root / "sources/tender.txt"))], requirements=[])
        self.plan = dict(schema_version=1, page_goal=dict(minimum=101 if count >= 101 else 1, target=count, maximum=0, count_scope="fixture-body", layout_basis="TEST FIXTURE, not measured pages"),
                         context_paths=["brief.md"], chapters=[], supplements=[], assets=[],
                         rendered=dict(path="", sha256="", pages=0, count_scope="", qa_path="", qa_sha256=""))
        for i in range(count):
            cid, rid = f"CH-{i+1:03}", f"R-{i+1:03}"
            path = f"draft/{cid}.md"
            (self.root / path).write_text(f"# Fixture chapter {i+1}\n<!-- REQ:{rid} -->\nFixture response.\n")
            self.bid["requirements"].append(dict(id=rid, source_id="T-001", locator=f"fixture line {i+1}", text="Fixture requirement", category="general", status="covered", response_path=path, requires_evidence=False, evidence=[], note=""))
            self.plan["chapters"].append(dict(id=cid, title=f"Fixture chapter {i+1}", path=path, budget_pages=1, depends_on=[f"CH-{i:03}"] if i and chain else [], requirement_ids=[rid], asset_ids=[], status="pending", checkpoint=None))
        self.save()

    def save(self):
        (self.root / "bid.json").write_text(json.dumps(self.bid, ensure_ascii=False) + "\n")
        (self.root / "long-task.json").write_text(json.dumps(self.plan, ensure_ascii=False) + "\n")

    def run_cli(self, command, *args, expected=0, readonly=False):
        before = tree(self.root)
        result = subprocess.run([sys.executable, str(SCRIPT), command, str(self.root / "long-task.json"), *map(str, args)],
                                cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if readonly:
            self.assertEqual(before, tree(self.root))
        return result

    def checkpoint(self, index):
        c = self.plan["chapters"][index]
        c["status"] = "review"
        self.save()
        report = self.root / f"review/{c['id']}.md"
        report.write_text("Fixture review, not real QA.\nDraft SHA-256: " + sha(self.root / c["path"]) + "\n")
        result = self.run_cli("checkpoint", "--chapter", c["id"], "--review", f"review/{c['id']}.md")
        self.plan = json.loads((self.root / "long-task.json").read_text())
        return result

    def state(self):
        return queue.analyze(self.plan, self.bid, self.root)

    def test_120_chapters_checkpoint_resume_and_no_rewrite(self):
        self.make(120)
        original_drafts = {c["path"]: sha(self.root / c["path"]) for c in self.plan["chapters"]}
        self.assertEqual(json.loads(self.run_cli("next", readonly=True).stdout)["id"], "CH-001")
        for i in range(120):
            self.checkpoint(i)
            if i in (19, 59):
                result = self.run_cli("next", readonly=True)
                self.assertEqual(json.loads(result.stdout)["id"], f"CH-{i+2:03}")
        self.assertTrue(all(self.state()["current"].values()))
        self.assertEqual(json.loads(self.run_cli("next", readonly=True).stdout)["kind"], "assembly")
        self.assertEqual(original_drafts, {c["path"]: sha(self.root / c["path"]) for c in self.plan["chapters"]})
        self.assertEqual(len(list((self.root / "archives/writing-state").glob("*.bak"))), 120)
        # No invented 120-page output: the recorded-render gate remains pending.
        self.assertIn("rendered", self.run_cli("status", "--release", expected=1, readonly=True).stdout)

    def test_related_source_changes_invalidate_only_dependent_chapters(self):
        self.make(3, chain=False)
        unused = self.root / "sources/other.txt"
        unused.write_text("Other source.\n")
        self.bid["sources"].append(dict(id="T-OTHER", kind="tender", path="sources/other.txt", sha256=sha(unused)))
        self.bid["requirements"][2]["source_id"] = "T-OTHER"
        self.save()
        for i in range(3):
            self.checkpoint(i)
        self.assertEqual(sum(self.state()["current"].values()), 3)
        unused.write_text("Revised other source.\n")
        self.bid["sources"][1]["sha256"] = sha(unused)
        self.save()
        self.assertEqual(self.state()["current"], {"CH-001": True, "CH-002": True, "CH-003": False})
        self.assertEqual(json.loads(self.run_cli("next", readonly=True).stdout)["id"], "CH-003")

    def test_draft_review_and_shared_context_changes_invalidate_dependencies(self):
        for i in range(2):
            self.checkpoint(i)
        for path in ("draft/CH-001.md", "review/CH-001.md", "brief.md"):
            with self.subTest(path=path):
                p = self.root / path
                old = p.read_bytes()
                p.write_bytes(old + b"Changed fixture\n")
                self.assertFalse(any(self.state()["current"].values()))
                p.write_bytes(old)
                self.assertTrue(all(self.state()["current"].values()))

    def supplement(self, **extra):
        return dict(id="G-001", kind="material", title="Fixture certificate", chapter_ids=["CH-001"], requirement_ids=[], priority="blocking", status="open", request="Provide the actual certificate and validity information.", owner="User", needed_by="Before qualification chapter", evidence=[], **extra)

    def test_blocked_chapter_does_not_stop_independent_work_and_resolved_gap_reopens(self):
        self.make(2, chain=False)
        gap = self.supplement()
        self.plan["supplements"] = [gap]
        self.save()
        self.assertEqual(json.loads(self.run_cli("next", readonly=True).stdout)["id"], "CH-002")
        proof = self.root / "sources/certificate.txt"
        proof.write_text("Fixture certificate, not real evidence.\n")
        gap.update(status="provided", evidence=[dict(path="sources/certificate.txt", sha256=sha(proof))])
        self.save()
        self.assertEqual(json.loads(self.run_cli("next", readonly=True).stdout)["id"], "CH-002")
        gap["status"] = "verified"
        self.save()
        self.assertEqual(json.loads(self.run_cli("next", readonly=True).stdout)["id"], "CH-001")
        proof.write_text("Changed fixture certificate.\n")
        self.assertIn("G-001", self.run_cli("report", readonly=True).stdout)

    def test_requirement_only_gap_is_not_global_and_report_deduplicates(self):
        self.make(2, chain=False)
        gap = self.supplement()
        gap.update(chapter_ids=[], requirement_ids=["R-001"])
        self.plan["supplements"] = [gap]
        self.bid["requirements"][0].update(status="gap", note="Need missing fixture input")
        self.save()
        self.assertEqual(json.loads(self.run_cli("next", readonly=True).stdout)["id"], "CH-002")
        text = self.run_cli("report", readonly=True).stdout
        self.assertIn("G-001 · Fixture certificate", text)
        self.assertNotIn("- 条款 R-001：", text)

    def test_visual_requirements_block_checkpoint_until_real_paths_are_registered(self):
        self.make(1)
        a = dict(id="FIG-01", kind="diagram", title="Fixture architecture", chapter_ids=["CH-001"], source_ids=["T-001"], purpose="Explain fixture components", status="planned", path="", sha256="", editable_path="", editable_sha256="", preview_path="", preview_sha256="", caption="", alt_text="", note="Need actual labels and relationships")
        self.plan["assets"] = [a]
        self.plan["chapters"][0].update(asset_ids=["FIG-01"], status="review")
        self.save()
        text = self.run_cli("report", readonly=True).stdout
        self.assertIn("FIG-01", text)
        self.assertIn("可编辑图源", text)
        self.run_cli("checkpoint", "--chapter", "CH-001", "--review", "review/CH-001.md", expected=2)
        svg = self.root / "sources/fixture.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="40"><text x="5" y="20">Fixture</text></svg>')
        for field, hashfield in (("path", "sha256"), ("editable_path", "editable_sha256"), ("preview_path", "preview_sha256")):
            a[field], a[hashfield] = "sources/fixture.svg", sha(svg)
        a.update(status="verified", caption="Fixture diagram", alt_text="A single fixture label")
        self.save()
        self.checkpoint(0)
        self.assertTrue(self.state()["current"]["CH-001"])
        svg.write_text(svg.read_text().replace("Fixture", "Changed"))
        self.assertFalse(self.state()["current"]["CH-001"])

    def test_checkpoint_requires_current_review_and_saves_original_plan(self):
        self.plan["chapters"][0]["status"] = "review"
        self.save()
        (self.root / "review/stale.md").write_text("Old review without current draft hash")
        self.run_cli("checkpoint", "--chapter", "CH-001", "--review", "review/stale.md", expected=2, readonly=True)
        result = self.checkpoint(0)
        backup = Path(result.stdout.split("PREVIOUS PLAN ")[1].strip())
        self.assertEqual(json.loads(backup.read_text())["chapters"][0]["checkpoint"], None)

    def test_report_preserves_input_and_previous_report(self):
        self.run_cli("report", "--output", "review/supplements.md")
        first = (self.root / "review/supplements.md").read_bytes()
        self.plan["supplements"] = [self.supplement()]
        self.save()
        result = self.run_cli("report", "--output", "review/supplements.md")
        backup = Path(result.stdout.split("PREVIOUS REPORT ")[1].strip())
        self.assertEqual(backup.read_bytes(), first)
        for path in ("long-task.json", "bid.json", "brief.md", "sources/tender.txt", "draft/CH-001.md", "scripts/tool.py", "../escape.md"):
            with self.subTest(path=path):
                self.run_cli("report", "--output", path, expected=2, readonly=True)

    def test_unknown_references_cycle_duplicates_and_invalid_pages_are_rejected(self):
        original = copy.deepcopy(self.plan)
        mutations = [
            lambda p: p["chapters"][0].update(depends_on=["MISSING"]),
            lambda p: p["chapters"][0].update(depends_on=["CH-002"]),
            lambda p: p["chapters"][0].update(requirement_ids=["MISSING"]),
            lambda p: p["chapters"][0].update(asset_ids=["MISSING"]),
            lambda p: p["chapters"].append(copy.deepcopy(p["chapters"][0])),
            lambda p: p["chapters"][0].update(path="../escape.md"),
            lambda p: p["page_goal"].update(minimum=101, target=100),
            lambda p: p["page_goal"].update(maximum=1),
            lambda p: p["chapters"][0].update(budget_pages=True),
            lambda p: p.update(schema_version=True),
            lambda p: p.update(unknown="extra"),
        ]
        for mutate in mutations:
            self.plan = copy.deepcopy(original)
            mutate(self.plan)
            self.save()
            self.run_cli("status", expected=2, readonly=True)

    def test_render_record_is_bound_to_current_document_and_chapter_assembly(self):
        self.make(1)
        self.checkpoint(0)
        doc = self.root / "delivery/rendered-fixture.txt"
        doc.write_text("Pagination-binding fixture, not an actual paginated document.\n")
        qa = self.root / "review/render-fixture.md"
        stamp = queue.assembly_stamp(self.state(), self.root)
        qa.write_text("SYNTHETIC metadata test only; no actual page-count claim.\n" + sha(doc) + "\n" + stamp + "\n")
        self.plan["rendered"] = dict(path="delivery/rendered-fixture.txt", sha256=sha(doc), pages=1, count_scope="fixture-body", qa_path="review/render-fixture.md", qa_sha256=sha(qa))
        self.save()
        self.run_cli("status", "--release", readonly=True)
        self.plan["rendered"]["pages"] = 0
        self.save()
        self.run_cli("status", "--release", expected=1, readonly=True)
        self.plan["rendered"]["pages"] = 1
        qa.write_text("Wrong assembly stamp\n" + sha(doc) + "\n")
        self.plan["rendered"]["qa_sha256"] = sha(qa)
        self.save()
        self.assertIn("assembly", self.run_cli("status", "--release", expected=1, readonly=True).stdout)

    def test_starter_exposes_material_and_visual_requests(self):
        plan = ROOT / "manifests/writing/templates/long-task.json"
        result = subprocess.run([sys.executable, str(SCRIPT), "report", str(plan), "--bid", "project.json"], capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in ("101", "120", "完整招标资料", "企业及人员证明", "FIG-01", "现场或案例照片"):
            self.assertIn(text, result.stdout)

    def test_normal_runtime_query_does_not_create_bytecode_or_other_files(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("long_task.py", "check_bid.py"):
            shutil.copy2(SCRIPT.parent / name, scripts / name)
        before = tree(self.root)
        env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
        result = subprocess.run([sys.executable, str(scripts / "long_task.py"), "status", str(self.root / "long-task.json")],
                                cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((scripts / "__pycache__").exists())
        self.assertEqual(before, tree(self.root))


if __name__ == "__main__":
    unittest.main()
