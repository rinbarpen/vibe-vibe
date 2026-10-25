"""Native Word constraint evidence is explicit, read-only and never final QA."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "manifests/office/docx/scripts/feature_audit.py"
spec = importlib.util.spec_from_file_location("office_features_test", SCRIPT)
features = importlib.util.module_from_spec(spec)
spec.loader.exec_module(features)

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"


class WordFeaturesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="native Word features ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def package(self, suffix="docx", protection="", content_lock="sdtContentLocked", macros=False):
        path = self.root / ("sample." + suffix)
        document = f'''<w:document xmlns:w="{W}" xmlns:wp="{WP}"><w:body>
          <w:sdt><w:sdtPr><w:tag w:val="title"/><w:lock w:val="{content_lock}"/></w:sdtPr>
          <w:sdtContent><w:p><w:r><w:t>Template title</w:t></w:r></w:p></w:sdtContent></w:sdt>
          <w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> SE</w:instrText></w:r><w:r><w:instrText>Q Figure </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>1</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>
          <w:p><w:fldSimple w:instr=" REF Figure1 "/><w:bookmarkStart w:id="1" w:name="Figure1"/><w:r><w:drawing><wp:docPr id="1" name="Chart" descr="Actual 100, 200, 300 synthetic values"/></w:drawing></w:r></w:p>
          <w:tbl><w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr><w:tc><w:p/></w:tc></w:tr><w:tr><w:trPr><w:cantSplit/></w:trPr><w:tc><w:p/></w:tc></w:tr></w:tbl>
          <w:sectPr/></w:body></w:document>'''
        styles = f'''<w:styles xmlns:w="{W}"><w:style w:styleId="Normal"><w:rPr><w:rFonts w:ascii="Test Font" w:eastAsia="Test CJK"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:styleId="Heading1"><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/></w:pPr></w:style></w:styles>'''
        with zipfile.ZipFile(path, "w") as package:
            package.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            package.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
            package.writestr("word/document.xml", document)
            package.writestr("word/styles.xml", styles)
            package.writestr("word/settings.xml", f'<w:settings xmlns:w="{W}">{protection}</w:settings>')
            if macros:
                package.writestr("word/vbaProject.bin", b"inert test fixture, no executable macro")
        return path

    def expected(self):
        return {"styles": {"Heading1": {"font": "Test Font", "east_asia_font": "Test CJK", "size_pt": 11, "keep_with_next": True}},
                "content_controls": {"title": {"lock": "sdtContentLocked"}},
                "fields": ["SEQ", "REF"], "figures": {"min_count": 1, "require_alt_text": True},
                "tables": {"min_count": 1, "repeat_header": True, "prevent_row_split": True},
                "document_protection": {"enforced": False}}

    def test_native_constraints_and_inherited_styles_are_evidence_not_final_qa(self):
        path = self.package()
        before = path.read_bytes()
        report = features.audit(path, self.expected())
        self.assertEqual(report["status"], "native_constraints_pass", report)
        self.assertEqual(report["quality_status"], "pending")
        self.assertEqual(report["macro_execution"], "not_run")
        self.assertEqual(report["features"]["bookmarks"], ["Figure1"])
        self.assertEqual(report["features"]["fields"][0]["instruction"], "SEQ Figure")
        self.assertTrue(report["input_unchanged"])
        self.assertEqual(path.read_bytes(), before)

    def test_no_expectations_only_inventory_no_implicit_constraints(self):
        path = self.package(content_lock="unlocked")
        report = features.audit(path)
        self.assertEqual(report["status"], "native_features_recorded")
        self.assertEqual(report["features"]["content_controls"][0]["lock"], "unlocked")

    def test_missing_lock_and_fields_fail_without_changing_file(self):
        path = self.package(content_lock="unlocked")
        before = path.read_bytes()
        expected = self.expected()
        expected["fields"].append("TOC")
        report = features.audit(path, expected)
        self.assertEqual(report["status"], "failed")
        self.assertIn("Content control title.lock differs", report["errors"])
        self.assertIn("Missing field command TOC", report["errors"])
        self.assertEqual(path.read_bytes(), before)

    def test_document_protection_reads_enforcement_not_generic_val(self):
        for value, expected in (("0", False), ("1", True), ("false", False), ("true", True)):
            with self.subTest(value=value):
                path = self.package(protection=f'<w:documentProtection w:edit="forms" w:enforcement="{value}"/>')
                report = features.audit(path)
                self.assertEqual(report["features"]["document_protection"], {"enforced": expected, "edit": "forms"})

    def test_macro_enabled_documents_and_templates_are_inspected_never_executed(self):
        for suffix in ("docm", "dotx", "dotm"):
            with self.subTest(suffix=suffix):
                path = self.package(suffix=suffix, macros=suffix != "dotx")
                report = features.audit(path)
                self.assertEqual(report["status"], "native_features_recorded")
                self.assertEqual(report["features"]["macros_present"], suffix != "dotx")
                self.assertEqual(report["macro_execution"], "not_run")
                # General verifier accepts native Word containers as well.
                general = features.package_inventory(path, "word/document.xml")
                self.assertGreater(general["parts"], 0)

    def test_typo_constraints_do_not_silently_pass(self):
        path = self.package()
        for expected in ({"stylez": {}}, {"figures": {"min_count": True}}, {"tables": {"repeat_header": "yes"}}, {"styles": {"Normal": {"unknown": 1}}}):
            with self.subTest(expected=expected):
                self.assertEqual(features.audit(path, expected)["status"], "failed")

    def test_cli_report_collisions_rejected_and_constraints_failure_records_nonzero(self):
        path = self.package()
        before = path.read_bytes()
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        command = [sys.executable, str(SCRIPT), str(path), "--output", str(path)]
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(path.read_bytes(), before)
        expectation = self.root / "expect.json"
        expectation.write_text(json.dumps({"fields": ["TOC"]}))
        output = self.root / "report.json"
        command = [sys.executable, str(SCRIPT), str(path), "--expect", str(expectation), "--output", str(output)]
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(output.read_text())["status"], "failed")
        self.assertEqual(path.read_bytes(), before)

    def test_native_resources_and_eight_roles_install_preserving_project_entry(self):
        target = self.root / "installed project"
        target.mkdir()
        entry = target / "AGENTS.md"
        entry.write_text("Existing project instructions\n", encoding="utf-8")
        command = [sys.executable, str(ROOT / "manifests/office/scripts/install_office.py"), str(target)]
        result = subprocess.run(command, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(entry.read_text(), "Existing project instructions\n")
        expected = ["office/docx/scripts/feature_audit.py", "office/docx/scripts/native_format.py",
                    "office/docx/macros/OfficeLayout.bas", "office/docx/templates/content-brief.md",
                    "office/docx/references/voice-and-visuals.md", "office/docx/references/native-formatting.md"]
        roles = ("planner", "writer", "visuals", "docx", "xlsx", "pptx", "pdf", "qa")
        for role in roles:
            expected += [f".claude/agents/office-{role}.md", f".codex/agents/office-{role}.toml"]
        for relative in expected:
            with self.subTest(path=relative):
                self.assertTrue((target / relative).is_file())

    def test_native_rules_and_eight_agent_prompts_have_runtime_parity(self):
        try:
            import tomllib
        except ImportError:
            self.skipTest("Native agent TOML parity check requires Python 3.11+ (as does validate-agent-compat.py)")
        manifest = ROOT / "manifests/office"
        for name in ("quality", "file-safety", "docx", "xlsx", "pptx", "pdf"):
            cursor = (manifest / f"rules/office-{name}.mdc").read_text(encoding="utf-8")
            canonical = (manifest / f"rules/{name}.md").read_text(encoding="utf-8")
            self.assertEqual(cursor.split("---\n", 2)[2].strip(), canonical.strip())
        for role in ("planner", "writer", "visuals", "docx", "xlsx", "pptx", "pdf", "qa"):
            claude = (manifest / f".claude/agents/office-{role}.md").read_text(encoding="utf-8")
            codex = tomllib.loads((manifest / f".codex/agents/office-{role}.toml").read_text(encoding="utf-8"))
            self.assertEqual(claude.split("---\n", 2)[2].strip(), codex["developer_instructions"].strip())
