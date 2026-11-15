"""User uploads, source citations, repeated revisions and restoration fixtures."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "manifests/writing/scripts"
sys.path.insert(0, str(SCRIPTS))
import reference_tools as refs_tool
import revision_tools as rev_tool
import long_task
sys.path.pop(0)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in root.rglob("*") if p.is_file()}


class RevisionReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="reference revision fixture ")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "project"
        self.upload = self.base / "用户上传的真实材料样例.txt"
        self.upload.write_text("TEST FIXTURE: original reference material, not a real bid fact.\n")
        for name in ("sources", "draft", "review"):
            (self.root / name).mkdir(parents=True)
        (self.root / "sources/tender.txt").write_text("TEST FIXTURE tender.\n")
        (self.root / "brief.md").write_text("Fixture shared scope.\n")
        self.bid = dict(schema_version=1, project=dict(name="Fixture", lot="01", tender_revision="fixture-v1", deadline="2030-01-02T09:00:00+08:00"),
                        sources=[dict(id="T-001", kind="tender", path="sources/tender.txt", sha256=sha(self.root / "sources/tender.txt"))], requirements=[])
        self.plan = dict(schema_version=1, page_goal=dict(minimum=1, target=2, maximum=0, count_scope="fixture", layout_basis="fixture"),
                         context_paths=["brief.md"], chapters=[], supplements=[], assets=[],
                         rendered=dict(path="", sha256="", pages=0, count_scope="", qa_path="", qa_sha256=""))
        self.refs = refs_tool.empty()
        for i in range(2):
            cid, rid, path = f"CH-0{i+1}", f"R-0{i+1}", f"draft/0{i+1}.md"
            (self.root / path).write_text(f"# Fixture chapter\n<!-- REQ:{rid} -->\nUser editable fixture draft.\n")
            self.bid["requirements"].append(dict(id=rid, source_id="T-001", locator=f"fixture clause {i+1}", text="Fixture requirement", category="general", status="covered", response_path=path, requires_evidence=False, evidence=[], note=""))
            self.plan["chapters"].append(dict(id=cid, title="Fixture chapter", path=path, budget_pages=1, depends_on=[], requirement_ids=[rid], asset_ids=[], status="pending", checkpoint=None))
        self.save()

    def save(self):
        for name, data in (("bid.json", self.bid), ("long-task.json", self.plan), ("references.json", self.refs)):
            (self.root / name).write_bytes(refs_tool.json_bytes(data))

    def refresh(self):
        self.bid, self.plan, self.refs = refs_tool.project(self.root)

    def run_cli(self, script, *args, expected=0, readonly=False):
        before = tree(self.root)
        result = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args[:1]), str(self.root), *map(str, args[1:])],
                                cwd=ROOT, capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=45)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        if readonly:
            self.assertEqual(before, tree(self.root))
        self.refresh()
        return result

    def ingest(self, sid="S-001", use="fact", version="v1", supersedes=""):
        args = ["ingest", "--file", self.upload, "--id", sid, "--kind", "reference", "--title", "Uploaded fixture", "--use", use, "--version", version]
        if supersedes:
            args += ["--supersedes", supersedes]
        return self.run_cli("reference_tools.py", *args)

    def verify_source(self, sid="S-001"):
        source = next(s for s in self.bid["sources"] if s["id"] == sid)
        note = next(n for n in self.refs["source_notes"] if n["source_id"] == sid)
        path = self.root / f"review/source-{sid}.md"
        path.write_text("Fixture source review; no authenticity claim.\n" + source["sha256"] + "\n" + note["extract_sha256"] + "\n")
        self.run_cli("reference_tools.py", "verify", "--id", sid, "--review", f"review/source-{sid}.md")

    def cite(self, sid="S-001", usage="fact"):
        self.refs["citations"] = [dict(id="C-001", source_id=sid, locator="原件第 1 段", usage=usage, summary="Support the fixture explanation", chapter_ids=["CH-01"], historical=False, note="")]
        path = self.root / "draft/01.md"
        path.write_text(path.read_text() + "\nFixture sourced claim.[^C-001]\n")
        self.save()

    def checkpoint(self, index):
        chapter = self.plan["chapters"][index]
        chapter["status"] = "review"
        self.save()
        review = self.root / f"review/{chapter['id']}.md"
        review.write_text("Fixture chapter review\n" + sha(self.root / chapter["path"]) + "\n")
        result = subprocess.run([sys.executable, str(SCRIPTS / "long_task.py"), "checkpoint", str(self.root / "long-task.json"),
                                 "--chapter", chapter["id"], "--review", f"review/{chapter['id']}.md"],
                                capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.refresh()

    def snapshot(self, rid):
        return self.run_cli("revision_tools.py", "snapshot", "--id", rid, "--reason", "Fixture revision " + rid)

    def test_upload_preserves_original_and_is_idempotent(self):
        original = self.upload.read_bytes()
        self.ingest()
        source = self.bid["sources"][-1]
        self.assertEqual((self.root / source["path"]).read_bytes(), original)
        self.assertEqual(self.upload.read_bytes(), original)
        self.assertEqual(self.refs["source_notes"][-1]["status"], "pending")
        before = tree(self.root)
        self.assertIn("UNCHANGED", self.ingest().stdout)
        self.assertEqual(before, tree(self.root))
        self.upload.write_text("Changed uploaded fixture.\n")
        self.run_cli("reference_tools.py", "ingest", "--file", self.upload, "--id", "S-001", expected=2)
        self.assertEqual((self.root / source["path"]).read_bytes(), original)

    def test_binary_upload_and_real_extraction_are_distinct(self):
        binary = self.base / "fixture.dat"
        binary.write_bytes(b"\x00\x01fixture binary original\xff")
        self.run_cli("reference_tools.py", "ingest", "--file", binary, "--id", "S-BIN")
        note = self.refs["source_notes"][-1]
        self.assertEqual(note["extract_path"], "")
        extract = self.base / "extracted.txt"
        extract.write_text("[Original page 1] Fixture extraction requiring review.\n")
        self.run_cli("reference_tools.py", "attach-extract", "--id", "S-BIN", "--file", extract)
        self.assertEqual(self.refs["source_notes"][-1]["status"], "pending")
        self.verify_source("S-BIN")
        self.assertEqual(self.refs["source_notes"][-1]["status"], "reviewed")
        self.assertEqual(binary.read_bytes(), (self.root / self.bid["sources"][-1]["path"]).read_bytes())

    def test_fact_citation_requires_review_and_style_is_not_fact(self):
        self.ingest(use="style")
        self.cite()
        self.run_cli("reference_tools.py", "check", "--mode", "draft", readonly=True)
        result = self.run_cli("reference_tools.py", "check", "--mode", "release", expected=1, readonly=True)
        self.assertIn("文风参考", result.stdout)
        self.verify_source()
        self.run_cli("reference_tools.py", "check", "--mode", "release", expected=1, readonly=True)
        self.refs["citations"][0]["usage"] = "style"
        self.save()
        self.run_cli("reference_tools.py", "check", "--mode", "release", readonly=True)
        self.run_cli("reference_tools.py", "verify", "--id", "S-001", "--review", "bid.json", expected=2, readonly=True)

    def test_citation_registry_unknown_locators_orphans_and_code_examples(self):
        self.ingest()
        self.verify_source()
        self.cite()
        self.run_cli("reference_tools.py", "check", "--mode", "release", readonly=True)
        bibliography = self.run_cli("reference_tools.py", "bibliography", "--chapter", "CH-01", readonly=True).stdout
        self.assertIn("[^C-001]:", bibliography)
        self.assertIn("原件第 1 段", bibliography)
        self.assertIn("../sources/originals/S-001/", bibliography)
        p = self.root / "draft/01.md"
        original = p.read_text()
        p.write_text(original + "\n" + chr(96)*3 + "\n[^C-NOT-A-REAL-CITATION]\n" + chr(96)*3 + "\n")
        self.run_cli("reference_tools.py", "check", "--mode", "release", readonly=True)
        p.write_text(original + "\nUnknown.[^C-MISSING]\n")
        self.assertIn("未登记", self.run_cli("reference_tools.py", "check", "--mode", "release", expected=1, readonly=True).stdout)
        p.write_text(original.replace("[^C-001]", ""))
        self.assertIn("未出现在正文", self.run_cli("reference_tools.py", "check", "--mode", "release", expected=1, readonly=True).stdout)
        p.write_text(original)
        self.refs["citations"][0]["locator"] = ""
        self.save()
        self.run_cli("reference_tools.py", "check", "--mode", "release", expected=1, readonly=True)

    def test_deleted_registry_does_not_silently_validate_inline_citations(self):
        self.ingest()
        self.verify_source()
        self.cite()
        (self.root / "references.json").unlink()
        state = long_task.analyze(self.plan, self.bid, self.root)
        self.assertTrue(any("未登记" in item for item in state["completion"]["CH-01"]))

    def test_cited_source_change_invalidates_only_related_chapter(self):
        self.ingest()
        self.verify_source()
        self.cite()
        self.checkpoint(0)
        self.checkpoint(1)
        self.assertTrue(all(long_task.analyze(self.plan, self.bid, self.root)["current"].values()))
        self.snapshot("REV-BEFORE-SOURCE-UPDATE")
        self.upload.write_text("Revised uploaded fixture, new scope.\n")
        self.ingest(sid="S-002", version="v2", supersedes="S-001")
        state = long_task.analyze(self.plan, self.bid, self.root)
        self.assertEqual(state["current"], {"CH-01": False, "CH-02": True})
        self.assertIn("替代", self.run_cli("reference_tools.py", "check", "--mode", "release", expected=1, readonly=True).stdout)
        self.assertEqual(self.refs["citations"][0]["source_id"], "S-001", "new upload must not silently retarget a citation")
        self.assertTrue((self.root / self.bid["sources"][-2]["path"]).exists())
        report = json.loads(self.run_cli("revision_tools.py", "diff", "--from", "REV-BEFORE-SOURCE-UPDATE", readonly=True).stdout)
        self.assertIn("C-001", report["impact"]["citation_ids"])
        self.assertEqual(report["impact"]["direct_chapters"], ["CH-01"])

    def test_snapshot_diff_repeated_edits_preserves_user_work_and_restore(self):
        self.ingest()
        self.verify_source()
        self.cite()
        self.snapshot("REV-001")
        before = {p: (self.root / p).read_bytes() for p in ("bid.json", "long-task.json", "references.json", "draft/01.md")}
        p = self.root / "draft/01.md"
        p.write_text(p.read_text() + "\nUSER MANUAL EDIT, must be preserved in the next revision.\n")
        self.snapshot("REV-002")
        result = self.run_cli("revision_tools.py", "diff", "--from", "REV-001", "--to", "REV-002", readonly=True)
        report = json.loads(result.stdout)
        self.assertEqual(report["impact"]["direct_chapters"], ["CH-01"])
        self.assertIn("USER MANUAL EDIT", report["text_diffs"][0]["diff"])
        self.assertIn("USER MANUAL EDIT", p.read_text())
        count = len(list((self.root / "archives/revisions/objects").iterdir()))
        self.snapshot("REV-002")
        self.assertEqual(count, len(list((self.root / "archives/revisions/objects").iterdir())))
        self.run_cli("revision_tools.py", "diff", "--from", "REV-001", readonly=True)
        self.run_cli("revision_tools.py", "restore", "--id", "REV-001", readonly=True)
        self.run_cli("revision_tools.py", "restore", "--id", "REV-001", "--apply")
        for path, payload in before.items():
            self.assertEqual((self.root / path).read_bytes(), payload)
        safety = list((self.root / "archives/revisions").glob("RESTORE-*.json"))
        self.assertEqual(len(safety), 1)
        self.run_cli("revision_tools.py", "restore", "--id", safety[0].stem, "--apply")
        self.assertIn("USER MANUAL EDIT", p.read_text())

    def test_restore_preserves_new_uploads_and_unregistered_files(self):
        self.ingest()
        self.snapshot("REV-001")
        self.upload.write_text("Second original fixture upload.\n")
        self.ingest(sid="S-002", version="v2", supersedes="S-001")
        new_original = self.root / self.bid["sources"][-1]["path"]
        extra = self.root / "user-note.txt"
        extra.write_text("Keep my note.\n")
        self.run_cli("revision_tools.py", "restore", "--id", "REV-001", "--apply")
        self.assertEqual(new_original.read_text(), "Second original fixture upload.\n")
        self.assertEqual(extra.read_text(), "Keep my note.\n")

    def test_restore_handles_invalid_mid_edit_json_and_preserves_bad_bytes(self):
        self.snapshot("REV-001")
        state = self.root / "bid.json"
        state.write_text('{"user is still editing":')
        result = subprocess.run([sys.executable, str(SCRIPTS / "revision_tools.py"), "restore", str(self.root), "--id", "REV-001", "--apply"],
                                capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.refresh()
        safety = list((self.root / "archives/revisions").glob("RESTORE-*.json"))
        record = rev_tool.read_record(self.root, safety[0].stem)
        obj = rev_tool.object_path(self.root, record["files"]["bid.json"]["sha256"])
        self.assertEqual(obj.read_text(), '{"user is still editing":')

    def test_corrupted_snapshot_objects_prevent_any_restore_write(self):
        self.snapshot("REV-001")
        p = self.root / "draft/01.md"
        p.write_text(p.read_text() + "\nKeep current user text.\n")
        record = rev_tool.read_record(self.root, "REV-001")
        obj = rev_tool.object_path(self.root, record["files"]["draft/01.md"]["sha256"])
        obj.write_text("Corrupted test object.\n")
        self.run_cli("revision_tools.py", "restore", "--id", "REV-001", "--apply", expected=2, readonly=True)
        self.assertIn("Keep current user text", p.read_text())

    def test_reference_update_failure_rolls_back_all_project_files(self):
        before = {p: (self.root / p).read_bytes() for p in ("bid.json", "references.json")}
        original = refs_tool.atomic
        failed = [False]
        def fail_once(path, payload):
            if path == self.root / "references.json" and not failed[0]:
                failed[0] = True
                raise OSError("Injected fixture write failure")
            return original(path, payload)
        with patch.object(refs_tool, "atomic", side_effect=fail_once):
            with self.assertRaises(OSError):
                refs_tool.commit(self.root, {"bid.json": b'{"changed": true}\n', "references.json": b'{"changed": true}\n'})
        for p, data in before.items():
            self.assertEqual((self.root / p).read_bytes(), data)

    def test_upload_transaction_failure_removes_partial_copy_and_preserves_external_upload(self):
        original = refs_tool.atomic
        source_bytes = self.upload.read_bytes()
        old_bid = (self.root / "bid.json").read_bytes()
        failed = [False]
        def fail_after_write(path, payload):
            result = original(path, payload)
            if path == self.root / "references.json" and not failed[0]:
                failed[0] = True
                raise OSError("Injected failure after atomic replacement")
            return result
        args = ["ingest", str(self.root), "--file", str(self.upload), "--id", "S-FAIL"]
        with patch.object(refs_tool, "atomic", side_effect=fail_after_write):
            self.assertEqual(refs_tool.main(args), 2)
        self.assertFalse((self.root / "sources/originals/S-FAIL/original.txt").exists())
        self.assertEqual((self.root / "bid.json").read_bytes(), old_bid)
        self.assertEqual(refs_tool.load(self.root / "references.json"), refs_tool.empty())
        self.assertEqual(self.upload.read_bytes(), source_bytes)

    def test_current_mid_edit_diff_is_readonly_and_explains_incomplete_metadata(self):
        self.snapshot("REV-001")
        (self.root / "references.json").write_text('{"still editing":')
        before = tree(self.root)
        result = subprocess.run([sys.executable, str(SCRIPTS / "revision_tools.py"), "diff", str(self.root), "--from", "REV-001"],
                                capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, tree(self.root))
        self.assertIn("mid-edit", result.stdout)

    def test_revision_impact_follows_citation_and_real_dependencies(self):
        self.plan["chapters"][1]["depends_on"] = ["CH-01"]
        self.save()
        self.ingest()
        self.verify_source()
        self.cite()
        self.snapshot("REV-001")
        self.refs["citations"][0]["locator"] = "原件第 2 段（用户修订定位）"
        self.save()
        result = json.loads(self.run_cli("revision_tools.py", "diff", "--from", "REV-001", readonly=True).stdout)
        self.assertEqual(result["impact"]["citation_ids"], ["C-001"])
        self.assertEqual(result["impact"]["direct_chapters"], ["CH-01"])
        self.assertEqual(result["impact"]["dependent_chapters"], ["CH-02"])

    def test_asset_source_version_is_checked_without_an_inline_footnote(self):
        self.ingest()
        self.verify_source()
        scene = copy.deepcopy(self.plan)
        scene["assets"] = [dict(id="FIG-01", chapter_ids=["CH-01"], source_ids=["S-001"])]
        state = refs_tool.audit(self.refs, self.bid, scene, self.root)
        self.assertIn("S-001", state["pins"]["CH-01"]["notes"])
        self.upload.write_text("Revised fixture diagram source.\n")
        self.ingest(sid="S-002", version="v2", supersedes="S-001")
        state = refs_tool.audit(self.refs, self.bid, scene, self.root)
        self.assertTrue(any("素材来源" in item for item in state["issues"]["CH-01"]))
        self.assertEqual(state["issues"]["CH-02"], [])

    def test_invalid_source_supersession_and_paths_make_no_project_changes(self):
        self.run_cli("reference_tools.py", "ingest", "--file", self.upload, "--id", "../BAD", expected=2, readonly=True)
        self.run_cli("reference_tools.py", "ingest", "--file", self.upload, "--id", "S-001", "--supersedes", "MISSING", expected=2, readonly=True)
        self.snapshot("REV-001")
        record_path = self.root / "archives/revisions/REV-001.json"
        record = json.loads(record_path.read_text())
        entry = record["files"].pop("draft/01.md")
        record["files"]["scripts/long_task.py"] = entry
        record_path.write_bytes(refs_tool.json_bytes(record))
        self.run_cli("revision_tools.py", "restore", "--id", "REV-001", "--apply", expected=2, readonly=True)


if __name__ == "__main__":
    unittest.main()
