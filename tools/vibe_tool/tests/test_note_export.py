"""PDF export contracts with fake tool protocols and one real rendering check.

The fake pandoc cases exercise process failure and resource policy, not Markdown
parser quality or rendered appearance. The real-tool test covers that boundary.
"""

import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPORTER = REPO_ROOT / "manifests/tutor/scripts/export-notes.py"
PANDOC = shutil.which("pandoc")
BROWSER = next((path for name in ("google-chrome", "chromium", "chromium-browser")
                if (path := shutil.which(name))), None)
PDFINFO = shutil.which("pdfinfo")
PDFTOTEXT = shutil.which("pdftotext")


FAKE_PANDOC = r'''
import html, json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ["NOTE_TEST_TOOL_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(["pandoc", *args]) + "\n")
if os.environ.get("NOTE_TEST_PANDOC_FAIL"):
    print("fixture pandoc failure", file=sys.stderr)
    raise SystemExit(23)
destination_format = args[args.index("--to") + 1] if "--to" in args else ""
if destination_format == "json":
    print(pathlib.Path(os.environ["NOTE_TEST_AST"]).read_text(encoding="utf-8"))
else:
    document = json.load(sys.stdin)
    def inline(node):
        kind, value = node.get("t"), node.get("c")
        if kind == "Str":
            return html.escape(value)
        if kind in ("Space", "SoftBreak", "LineBreak"):
            return " "
        if kind == "Image":
            return '<img src="' + html.escape(value[2][0], quote=True) + '" alt="diagram">'
        if kind == "Link":
            return '<a href="' + html.escape(value[2][0], quote=True) + '">reference</a>'
        return ""
    fragments = []
    for block in document.get("blocks", []):
        kind, value = block.get("t"), block.get("c")
        if kind in ("Para", "Plain"):
            fragments.append("<p>" + "".join(map(inline, value)) + "</p>")
        elif kind == "CodeBlock":
            fragments.append("<pre><code>" + html.escape(value[1]) + "</code></pre>")
        elif kind == "RawBlock":
            fragments.append(value[1])
    result = "<!doctype html><html><head><meta charset='utf-8'></head><body>" + "".join(fragments) + "</body></html>"
    output = None
    for index, argument in enumerate(args):
        if argument in ("-o", "--output"):
            output = args[index + 1]
        elif argument.startswith("--output="):
            output = argument.split("=", 1)[1]
    if output:
        pathlib.Path(output).write_text(result, encoding="utf-8")
    else:
        print(result)
'''


FAKE_BROWSER = r'''
import json, os, pathlib, sys, urllib.parse
with open(os.environ["NOTE_TEST_TOOL_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(["browser", *sys.argv[1:]]) + "\n")
for arg in sys.argv[1:]:
    if arg.startswith("file:"):
        source = pathlib.Path(urllib.parse.unquote(urllib.parse.urlparse(arg).path))
        pathlib.Path(os.environ["NOTE_TEST_HTML"]).write_bytes(source.read_bytes())
if os.environ.get("NOTE_TEST_BROWSER_FAIL"):
    print("fixture browser failure", file=sys.stderr)
    raise SystemExit(31)
output = next(arg.split("=", 1)[1] for arg in sys.argv[1:]
              if arg.startswith("--print-to-pdf="))
if os.environ.get("NOTE_TEST_INVALID_PDF"):
    content = b"<html>not a PDF</html>"
else:
    content = b"%PDF-1.4\n" + (b"fixture PDF body " * 10) + b"\n%%EOF\n"
pathlib.Path(output).write_bytes(content)
'''


FAKE_MERMAID = r'''
import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ["NOTE_TEST_TOOL_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(["mermaid", *args]) + "\n")
output = pathlib.Path(args[args.index("-o") + 1])
output.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="240" height="60"><text x="5" y="30">A to B</text></svg>', encoding="utf-8")
'''


def paragraph(*inlines):
    return {"t": "Para", "c": list(inlines)}


def image(source):
    return {"t": "Image", "c": [["", [], []], [{"t": "Str", "c": "diagram"}], [source, ""]]}


class NoteExportCLITests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="note export tests ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.tools = self.root / "fake tools"
        self.tools.mkdir()
        self.pandoc = self._executable("pandoc", FAKE_PANDOC)
        self.browser = self._executable("fixture browser", FAKE_BROWSER)
        self.ast = self.root / "document ast.json"
        self.tool_log = self.root / "tool calls.jsonl"
        self.captured_html = self.root / "captured.html"
        self.env = dict(os.environ)
        self.env.update({
            "PATH": str(self.tools), "PYTHONDONTWRITEBYTECODE": "1",
            "NOTE_TEST_AST": str(self.ast), "NOTE_TEST_TOOL_LOG": str(self.tool_log),
            "NOTE_TEST_HTML": str(self.captured_html),
        })
        self.source = self.root / "学习笔记 with spaces.md"
        self.source.write_text("# 学习笔记\n\nA short explanation.\n", encoding="utf-8")
        self.output = self.root / "导出笔记 with spaces.pdf"
        self._document(paragraph({"t": "Str", "c": "A short explanation."}))

    def _executable(self, name, contents):
        path = self.tools / name
        path.write_text(f"#!{sys.executable}\n" + contents, encoding="utf-8")
        path.chmod(0o755)
        return path

    def _document(self, *blocks):
        self.ast.write_text(json.dumps({
            "pandoc-api-version": [1, 22], "meta": {}, "blocks": list(blocks),
        }), encoding="utf-8")

    def _run(self, *extra, source=None, output=None, browser=True):
        args = [sys.executable, "-B", str(EXPORTER), str(source or self.source),
                "--output", str(output or self.output)]
        if browser:
            args.extend(["--browser", str(self.browser)])
        return subprocess.run([*args, *map(str, extra)], env=self.env, cwd=self.root,
                              capture_output=True, text=True, timeout=30)

    def _assert_failure(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.output.exists(), result.stdout + result.stderr)

    def test_missing_input_creates_no_output(self):
        self._assert_failure(self._run(source=self.root / "missing.md"))
        self.assertFalse(self.tool_log.exists())

    def test_source_and_destination_must_differ_even_with_force(self):
        before = self.source.read_bytes()
        result = self._run("--force", output=self.source)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.source.read_bytes(), before)

    def test_force_rejects_svg_output_without_overwriting_a_source_diagram(self):
        figure = self.root / "source diagram.svg"
        figure.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text x="5" y="20">Keep this source</text></svg>', encoding="utf-8")
        self.source.write_text("# Chapter note\n\n![Original diagram](source%20diagram.svg)\n", encoding="utf-8")
        self._document(paragraph(image("source%20diagram.svg")))
        before = {path: path.read_bytes() for path in (self.source, figure)}

        result = self._run("--force", output=figure)

        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("pdf", (result.stdout + result.stderr).lower())
        self.assertFalse(self.tool_log.exists())
        for path, contents in before.items():
            self.assertEqual(path.read_bytes(), contents)

    def test_missing_pandoc_is_a_clear_failure(self):
        self.pandoc.unlink()
        result = self._run()
        self._assert_failure(result)
        self.assertIn("pandoc", result.stdout + result.stderr)

    def test_missing_browser_is_a_clear_failure(self):
        result = self._run(browser=False)
        self._assert_failure(result)
        self.assertRegex((result.stdout + result.stderr).lower(), r"chrome|chromium|browser")

    def test_explicit_nonexistent_browser_does_not_fall_back(self):
        result = self._run("--browser", self.root / "missing-browser")
        self._assert_failure(result)

    def test_existing_pdf_is_protected_by_default(self):
        self.output.write_bytes(b"existing personal PDF")
        stat = self.output.stat()
        result = self._run()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.output.read_bytes(), b"existing personal PDF")
        self.assertEqual(self.output.stat().st_mtime_ns, stat.st_mtime_ns)

    def test_force_exports_with_spaces_without_changing_markdown_or_svg(self):
        assets = self.root / "assets with spaces"
        assets.mkdir()
        figure = assets / "概念图.svg"
        figure.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="50"><text x="5" y="25">关系</text></svg>', encoding="utf-8")
        self.source.write_text("# 学习笔记\n\n![概念关系](assets%20with%20spaces/概念图.svg)\n", encoding="utf-8")
        self._document(paragraph(image("assets%20with%20spaces/概念图.svg")))
        before = {path: path.read_bytes() for path in (self.source, figure)}
        self.output.write_bytes(b"old PDF")
        result = self._run("--force")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.output.read_bytes().startswith(b"%PDF-"))
        html = self.captured_html.read_text(encoding="utf-8")
        self.assertIn("<svg", html)
        self.assertIn("关系", html)
        for path, contents in before.items():
            self.assertEqual(path.read_bytes(), contents)

    def test_pandoc_and_browser_failures_preserve_previous_pdf(self):
        for flag in ("NOTE_TEST_PANDOC_FAIL", "NOTE_TEST_BROWSER_FAIL", "NOTE_TEST_INVALID_PDF"):
            with self.subTest(failure=flag):
                self.output.write_bytes(b"previous successful PDF")
                stat = self.output.stat()
                self.env[flag] = "1"
                result = self._run("--force")
                self.env.pop(flag)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.output.read_bytes(), b"previous successful PDF")
                self.assertEqual(self.output.stat().st_mtime_ns, stat.st_mtime_ns)

    def test_mermaid_requires_a_real_renderer_instead_of_silent_code_fallback(self):
        self.source.write_text("```mermaid\ngraph LR\n A --> B\n```\n", encoding="utf-8")
        self._document({"t": "CodeBlock", "c": [["", ["mermaid"], []], "graph LR\n A --> B"]})
        result = self._run()
        self._assert_failure(result)
        self.assertRegex((result.stdout + result.stderr).lower(), r"mermaid|mmdc")

    def test_explicit_mermaid_renderer_creates_an_embedded_image(self):
        mermaid = self._executable("fixture mmdc", FAKE_MERMAID)
        self.source.write_text("```mermaid\ngraph LR\n A --> B\n```\n", encoding="utf-8")
        self._document({"t": "CodeBlock", "c": [["", ["mermaid"], []], "graph LR\n A --> B"]})
        before = self.source.read_bytes()
        result = self._run("--mermaid-cli", mermaid)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = self.captured_html.read_text(encoding="utf-8")
        self.assertIn("<svg", html)
        self.assertIn("A to B", html)
        calls = [json.loads(line)[0] for line in self.tool_log.read_text(encoding="utf-8").splitlines()]
        self.assertIn("mermaid", calls)
        self.assertEqual(self.source.read_bytes(), before)

    def test_ordinary_source_code_is_not_misidentified_as_a_diagram(self):
        code = "```mermaid\ngraph LR\n A --> B\n```"
        self.source.write_text("````markdown\n" + code + "\n````\n", encoding="utf-8")
        self._document({"t": "CodeBlock", "c": [["", ["markdown"], []], code]})
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = self.captured_html.read_text(encoding="utf-8")
        self.assertIn("<pre><code>", html)
        self.assertNotIn("data:image/", html)

    def test_remote_image_resources_are_rejected_before_browser_load(self):
        for uri in ("https://example.test/diagram.svg", "http://example.test/image.png",
                    "//example.test/diagram.svg"):
            with self.subTest(uri=uri):
                self._document(paragraph(image(uri)))
                if self.tool_log.exists():
                    self.tool_log.unlink()
                self._assert_failure(self._run())
                calls = self.tool_log.read_text(encoding="utf-8") if self.tool_log.exists() else ""
                self.assertNotIn('"browser"', calls)

    def test_remote_raw_html_image_is_rejected(self):
        self._document({"t": "RawBlock", "c": ["html", '<img src="https://example.test/image.svg">']})
        self._assert_failure(self._run())

    def test_local_svg_cannot_hide_remote_image_or_css_resources(self):
        figure = self.root / "local-diagram.svg"
        self._document(paragraph(image(figure.name)))
        for embedded in (
            '<image href="https://example.test/image.png" width="10" height="10"/>',
            '<style>@import "https://example.test/style.css";</style>',
            '<rect width="20" height="20" style="fill:url(https://example.test/paint.svg)"/>',
        ):
            with self.subTest(resource=embedded):
                figure.write_text('<svg xmlns="http://www.w3.org/2000/svg">' + embedded + '</svg>', encoding="utf-8")
                before = figure.read_bytes()
                if self.tool_log.exists():
                    self.tool_log.unlink()
                self._assert_failure(self._run())
                calls = self.tool_log.read_text(encoding="utf-8") if self.tool_log.exists() else ""
                self.assertNotIn('"browser"', calls)
                self.assertEqual(figure.read_bytes(), before)

    def test_missing_local_diagram_reports_failure_not_a_broken_image_pdf(self):
        self._document(paragraph(image("assets/missing-diagram.svg")))
        result = self._run()
        self._assert_failure(result)
        self.assertIn("missing-diagram.svg", result.stdout + result.stderr)

    def test_normal_remote_reference_link_is_preserved_without_fetching(self):
        self._document(paragraph({"t": "Link", "c": [
            ["", [], []], [{"t": "Str", "c": "reference"}],
            ["https://example.test/reference", ""],
        ]}))
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('href="https://example.test/reference"', self.captured_html.read_text(encoding="utf-8"))
        calls = self.tool_log.read_text(encoding="utf-8")
        self.assertNotIn("npx", calls)


@unittest.skipUnless(PANDOC and BROWSER, "optional real pandoc and Chrome/Chromium")
class RealNoteExportTests(unittest.TestCase):
    @unittest.skipUnless(PDFTOTEXT, "optional real PDF text extraction tool")
    def test_yaml_title_and_matching_h1_are_rendered_only_once(self):
        with tempfile.TemporaryDirectory(prefix="chapter note title regression ") as directory:
            root = Path(directory)
            title = "Unique Chapter Title"
            source = root / f"{title}.md"
            source.write_text(f'---\ntitle: "{title}"\n---\n\n# {title}\n\nA brief explanation.\n', encoding="utf-8")
            before = source.read_bytes()
            output = source.with_suffix(".pdf")
            result = subprocess.run(
                [sys.executable, "-B", str(EXPORTER), str(source), "--output", str(output),
                 "--browser", str(BROWSER)], env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                cwd=root, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            text = subprocess.run([PDFTOTEXT, str(output), "-"], capture_output=True, text=True, check=True)
            self.assertEqual(" ".join(text.stdout.split()).count(title), 1, text.stdout)
            self.assertEqual(source.read_bytes(), before)

    def test_real_markdown_local_svg_and_png_render_to_pdf_without_source_changes(self):
        with tempfile.TemporaryDirectory(prefix="real illustrated note ") as directory:
            root = Path(directory)
            assets = root / "assets"
            assets.mkdir()
            figure = assets / "关系图.svg"
            figure.write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="560" height="130" viewBox="0 0 560 130">
<rect x="10" y="20" width="170" height="80" fill="#e4eef7"/>
<text x="30" y="65" font-family="Noto Sans CJK SC,sans-serif" font-size="22">教材概念</text>
<path d="M185 60 H350" stroke="#245" stroke-width="3"/>
<rect x="360" y="20" width="180" height="80" fill="#eef5e7"/>
<text x="380" y="65" font-family="Noto Sans CJK SC,sans-serif" font-size="22">实践检验</text>
</svg>''', encoding="utf-8")
            # A small valid PNG establishes that raster and vector assets coexist.
            raster = assets / "sample.png"
            raster.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jOucAAAAASUVORK5CYII="))
            source = root / "chapter note 中文.md"
            source.write_text('''# 学习笔记 / Chapter Note

Short explanations stay as text. Source: chapter 1, section 1.

![概念与检验之间的关系](assets/关系图.svg)

图 1：教材概念通过实践检验；示意图，不代表已掌握。

![Raster example](assets/sample.png)

## Reflection

The diagram expresses a relationship, not a daily study schedule.
''', encoding="utf-8")
            before = {path: path.read_bytes() for path in (source, figure, raster)}
            output = root / "chapter note 中文.pdf"
            result = subprocess.run(
                [sys.executable, "-B", str(EXPORTER), str(source), "--output", str(output),
                 "--browser", str(BROWSER)], env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                cwd=root, capture_output=True, text=True, timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.read_bytes().startswith(b"%PDF-"))
            self.assertGreater(output.stat().st_size, 1000)
            for path, contents in before.items():
                self.assertEqual(path.read_bytes(), contents)
            if PDFINFO:
                info = subprocess.run([PDFINFO, str(output)], capture_output=True, text=True, check=True)
                self.assertRegex(info.stdout, r"Pages:\s+[1-9]\d*")
            if PDFTOTEXT:
                text = subprocess.run([PDFTOTEXT, str(output), "-"], capture_output=True, text=True, check=True)
                self.assertIn("Chapter Note", text.stdout)
                self.assertIn("Short explanations", text.stdout)
                self.assertIn("学习笔记", text.stdout)
                self.assertIn("教材概念", text.stdout)
                self.assertIn("实践检验", text.stdout)


if __name__ == "__main__":
    unittest.main()
