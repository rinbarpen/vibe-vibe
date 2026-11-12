#!/usr/bin/env python3
"""Explicit native Writer formatting of a DOCX working copy, with preservation gates.

Run with --engine libreoffice --input source.docx --output formatted.docx
--report native.json. Optional --profile JSON overrides only the documented keys
in DEFAULT_PROFILE. This never enables document macros or changes Word's trust
settings. DOCM/DOTM and lossy roundtrips belong in native Word, not this engine.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
import unicodedata
import xml.etree.ElementTree as ET
import zipfile


DEFAULT_PROFILE = {
    "font": "Noto Sans CJK SC", "body_size_pt": 11,
    "caption_size_pt": 9, "heading_sizes_pt": [18, 15, 13],
    "repeat_table_headers": True, "keep_short_rows_together": True,
    "short_row_max_chars": 180, "allow_multipage_tables": False,
}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def profile_settings(path=None):
    profile = dict(DEFAULT_PROFILE)
    if path is not None:
        values = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(values, dict) or values.keys() - profile.keys():
            raise ValueError("Profile must be an object containing only DEFAULT_PROFILE keys")
        profile.update(values)
    if not isinstance(profile["font"], str) or not profile["font"].strip():
        raise ValueError("font must be a nonempty font-family name")
    sizes = profile["heading_sizes_pt"]
    if not isinstance(sizes, list) or len(sizes) != 3:
        raise ValueError("heading_sizes_pt must contain exactly three point sizes")
    for value in [profile["body_size_pt"], profile["caption_size_pt"], *sizes]:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 4 <= value <= 96:
            raise ValueError("Font sizes must be finite numbers between 4 and 96 points")
    for key in ("repeat_table_headers", "keep_short_rows_together", "allow_multipage_tables"):
        if not isinstance(profile[key], bool):
            raise ValueError(f"{key} must be boolean")
    limit = profile["short_row_max_chars"]
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000:
        raise ValueError("short_row_max_chars must be an integer between 1 and 1000")
    return profile


def _field_signature(instruction):
    # Writer may append MERGEFORMAT; it does not change the field's meaning.
    value = re.sub(r"\\\*\s+MERGEFORMAT\b", "", instruction, flags=re.I)
    value = " ".join(value.split())
    head, _, tail = value.partition(" ")
    return head.upper() + (" " + tail if tail else "")


def _math_topology(node):
    """Math roles without formatting properties or run/text splitting artifacts."""
    namespace = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    local = node.tag.removeprefix(namespace)
    if not node.tag.startswith(namespace) or local.endswith("Pr") or local == "ctrlPr":
        return []
    if local == "t":
        value = "".join(unicodedata.normalize("NFKC", node.text or "").split())
        return [value] if value else []
    children = []
    for child in node:
        for value in _math_topology(child):
            if isinstance(value, str) and children and isinstance(children[-1], str):
                children[-1] += value
            else:
                children.append(value)
    roles = {"f", "sSup", "sSub", "sSubSup", "rad", "nary", "d", "eqArr", "m", "mr",
             "limLow", "limUpp", "func", "acc", "bar", "groupChr", "e", "num", "den", "sub", "sup", "deg", "lim", "fName"}
    return [{"role": local, "children": children}] if local in roles and children else children


def inspect_package(path):
    """Read package-level inventories; this is not a native Word UI audit."""
    result = {key: [] for key in ("fields", "controls", "bookmarks", "protection", "revisions", "comments", "text", "objects", "math")}
    with zipfile.ZipFile(path) as package:
        files = package.infolist()
        if len(files) > 20000 or sum(p.file_size for p in files) > 256 * 1024 * 1024:
            raise ValueError("DOCX exceeds the package inspection budget")
        names = set(package.namelist())
        if not {"word/document.xml", "[Content_Types].xml"} <= names:
            raise ValueError("Expected a Word OOXML package")
        types = package.read("[Content_Types].xml")
        if any("vbaproject" in name.lower() for name in names) or b"macroEnabled" in types:
            raise ValueError("Macro-bearing files require native Word; keep DOCM/DOTM intact")
        if any(name.startswith("_xmlsignatures/") for name in names):
            raise ValueError("Signed packages require a native Word signature review")
        for name in names:
            if name.startswith("word/media/"):
                result["objects"].append("media:" + Path(name).suffix.lower())
            elif name.startswith("word/embeddings/"):
                result["objects"].append("embedding:" + Path(name).suffix.lower())
        for name in sorted(names):
            if not name.startswith("word/") or not name.endswith(".xml"):
                continue
            root = ET.fromstring(package.read(name))
            math_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
            structural = {"f", "sSup", "sSub", "sSubSup", "rad", "nary", "d", "eqArr", "m", "limLow", "limUpp", "func", "acc", "bar", "groupChr"}
            for equation in root.iter(math_ns + "oMath"):
                tokens = unicodedata.normalize("NFKC", "".join(item.text or "" for item in equation.iter(math_ns + "t")))
                counts = Counter(item.tag.removeprefix(math_ns) for item in equation.iter()
                                 if item.tag.startswith(math_ns) and item.tag.removeprefix(math_ns) in structural)
                symbols = [item.get(math_ns + "val", "") for item in equation.iter(math_ns + "chr")]
                result["math"].append(json.dumps({"tokens": "".join(tokens.split()), "structures": dict(counts),
                                                 "operator_symbols": symbols, "topology": _math_topology(equation)}, sort_keys=True, ensure_ascii=False))
            stack = []
            field_text_ids = {id(child) for field in root.iter(W + "fldSimple") for child in field.iter(W + "t")}
            for element in root.iter():
                if element.tag == W + "t" and stack:
                    field_text_ids.add(id(element))
                if element.tag in {W + "tbl", W + "drawing", W + "pict",
                                   "{http://schemas.openxmlformats.org/drawingml/2006/chart}chart",
                                   "{urn:schemas-microsoft-com:office:office}OLEObject"}:
                    result["objects"].append(element.tag)
                elif element.tag == "{http://schemas.openxmlformats.org/drawingml/2006/main}graphicData":
                    uri = element.get("uri", "")
                    if "diagram" in uri:
                        result["objects"].append("smartart:" + uri)
                if element.tag == W + "fldSimple":
                    result["fields"].append(_field_signature(element.get(W + "instr", "")))
                elif element.tag == W + "fldChar":
                    kind = element.get(W + "fldCharType")
                    if kind == "begin":
                        stack.append([])
                    elif kind == "separate" and stack and stack[-1] is not None:
                        result["fields"].append(_field_signature("".join(stack[-1])))
                        stack[-1] = None
                    elif kind == "end" and stack:
                        parts = stack.pop()
                        if parts is not None:
                            result["fields"].append(_field_signature("".join(parts)))
                elif element.tag == W + "instrText" and stack and stack[-1] is not None:
                    stack[-1].append(element.text or "")
                elif element.tag == W + "sdtPr":
                    def value(local):
                        item = element.find(W + local)
                        return item.get(W + "val", "") if item is not None else ""
                    kinds = sorted(child.tag.removeprefix(W) for child in element
                                   if child.tag.removeprefix(W) in {"text", "richText", "picture", "date", "comboBox", "dropDownList", "group", "checkbox", "repeatingSection"})
                    result["controls"].append(json.dumps({"tag": value("tag"), "alias": value("alias"),
                                                         "lock": value("lock"), "type": kinds}, sort_keys=True))
                elif element.tag == W + "bookmarkStart":
                    bookmark = element.get(W + "name", "")
                    if bookmark and not bookmark.startswith("_GoBack"):
                        result["bookmarks"].append(bookmark)
                elif element.tag == W + "documentProtection":
                    result["protection"].append(json.dumps(element.attrib, sort_keys=True))
                elif element.tag in {W + "ins", W + "del", W + "moveFrom", W + "moveTo", W + "pPrChange", W + "rPrChange", W + "tblPrChange", W + "trPrChange", W + "tcPrChange"}:
                    result["revisions"].append(element.tag.removeprefix(W))
                elif element.tag == W + "comment":
                    result["comments"].append("".join(element.itertext()))
            for paragraph in root.iter(W + "p"):
                text = " ".join("".join(item.text or "" for item in paragraph.iter(W + "t")
                                     if id(item) not in field_text_ids).split())
                if text:
                    result["text"].append(text)
    return result


def preservation_errors(before, after):
    errors = []
    for key in before:
        if key == "text" and Counter(before[key]) != Counter(after[key]):
            errors.append("Native roundtrip changed non-field paragraph text")
        missing = Counter(before[key]) - Counter(after[key])
        if missing:
            errors.append(f"Native roundtrip lost or changed {key}: {dict(missing)}")
    return errors


def _text(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def _run(command, records, timeout):
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        records.append({"command": command, "exit_status": None, "timed_out": True,
                        "stdout": _text(exc.stdout), "stderr": _text(exc.stderr)})
        raise ValueError(f"Command timed out after {timeout}s") from exc
    records.append({"command": command, "exit_status": done.returncode,
                    "stdout": done.stdout, "stderr": done.stderr})
    return done


def uno_python(records):
    candidates = dict.fromkeys([sys.executable, "/usr/bin/python3", shutil.which("python3")])
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            done = _run([candidate, "-c", "import uno; print('UNO available')"], records, 5)
            if done.returncode == 0:
                return candidate
    raise ValueError("Missing Python UNO bridge; install python3-uno for the selected LibreOffice")


def _exclusive_copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".office-native-", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as stream, Path(source).open("rb") as incoming:
            shutil.copyfileobj(incoming, stream)
            stream.flush()
            os.fsync(stream.fileno())
        # Same-directory hard link publishes atomically without replacing a racer.
        os.link(temporary, target)
    finally:
        os.unlink(temporary)


def write_report(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="office-report-") as temporary:
        source = Path(temporary) / "report.json"
        source.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _exclusive_copy(source, path)


def format_document(source, output, *, profile=None, timeout=60):
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output:
        raise ValueError("Input and output must be different working-copy paths")
    if output.exists():
        raise ValueError("Output exists; choose a new working-copy path")
    if source.suffix.lower() != ".docx" or output.suffix.lower() != ".docx":
        raise ValueError("LibreOffice engine accepts .docx only; keep DOCM/DOTM in native Word")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout must be a positive finite number")
    settings = profile_settings(profile)
    before_hash = sha256(source)
    report = {"engine": "libreoffice", "status": "failed", "quality_status": "pending",
              "input": str(source), "output": str(output), "source_sha256": before_hash,
              "profile": settings, "commands": [],
              "preservation_scope": ["non-field paragraph text", "field instructions", "content-control metadata/locks",
                                     "bookmarks", "document protection", "revision/comment inventory",
                                     "media/native chart/OLE/SmartArt object counts (not pixel or UI equivalence)",
                                     "native OMML count, normalized tokens, operator symbols and math role topology"],
              "limits": ["Writer is not Microsoft Word; Word-native UI enforcement needs a separate Word review.",
                         "Formatting success is not visual review or independent QA.",
                         "OMML inventory/topology is not full mathematical or style equivalence; compare every equation with its LaTeX source and rendering.",
                         "Style edits target existing built-ins; native-engine roundtrip may normalize OOXML. Direct formatting and custom styles are not intentionally rewritten.",
                         "Short-row keep-together uses a conservative text/height heuristic; inspect every rendered page."]}
    process = None
    try:
        baseline = inspect_package(source)
        report["baseline_inventory"] = baseline
        external_fields = [value for value in baseline["fields"]
                           if value.partition(" ")[0] in {"DDE", "DDEAUTO", "DATABASE", "LINK", "IMPORT",
                                                         "INCLUDE", "INCLUDETEXT", "INCLUDEPICTURE", "RD", "ADDIN", "CITATION", "BIBLIOGRAPHY"}]
        if external_fields:
            report["external_fields_not_updated"] = external_fields
            raise ValueError("Externally linked or manager-controlled fields need selective Word updates; native output withheld")
        office = shutil.which("libreoffice") or shutil.which("soffice")
        if not office:
            raise ValueError("Missing LibreOffice")
        interpreter = uno_python(report["commands"])
        version = _run([office, "--version"], report["commands"], 10)
        if version.returncode:
            raise ValueError("LibreOffice version check failed")
        report["engine_version"] = version.stdout.strip()
        with tempfile.TemporaryDirectory(prefix="office-native-") as temporary:
            work = Path(temporary)
            incoming = work / "input.docx"
            candidate = work / "formatted.docx"
            shutil.copy2(source, incoming)
            settings_path = work / "profile.json"
            settings_path.write_text(json.dumps(settings), encoding="utf-8")
            pipe = "office_native_" + uuid.uuid4().hex
            command = [office, "--headless", "--nologo", "--nodefault", "--nofirststartwizard",
                       "--norestore", f"-env:UserInstallation={(work / 'lo-profile').as_uri()}",
                       f"--accept=pipe,name={pipe};urp;StarOffice.ServiceManager"]
            with (work / "office.stdout").open("w+") as stdout, (work / "office.stderr").open("w+") as stderr:
                process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
                lo_record = {"command": command, "exit_status": None, "stdout": "", "stderr": ""}
                report["commands"].append(lo_record)
                try:
                    worker = _run([interpreter, str(Path(__file__).resolve()), "--_uno-worker", pipe,
                                   str(incoming), str(candidate), str(settings_path)], report["commands"], timeout)
                    if worker.stdout.strip():
                        try:
                            report["native_changes"] = json.loads(worker.stdout)
                        except json.JSONDecodeError:
                            pass
                    if worker.returncode:
                        raise ValueError(f"Native formatting worker exited {worker.returncode}: {worker.stderr.strip()}")
                    report["native_changes"] = json.loads(worker.stdout)
                    if not candidate.is_file() or candidate.stat().st_size == 0:
                        raise ValueError("Native engine produced no DOCX")
                    after = inspect_package(candidate)
                    report["modified_inventory"] = after
                    problems = preservation_errors(baseline, after)
                    if problems:
                        report["preservation_errors"] = problems
                        raise ValueError("Native feature preservation failed; use the reviewed VBA module in Word")
                    if sha256(source) != before_hash:
                        raise ValueError("Input hash changed during formatting; output withheld")
                    _exclusive_copy(candidate, output)
                    report.update(status="formatted", output_sha256=sha256(output), preservation_passed=True)
                finally:
                    # Never signal a shared/visible office session. Only our new session is owned.
                    if process.poll() is None:
                        try:
                            process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGTERM)
                            try:
                                process.wait(timeout=3)
                            except subprocess.TimeoutExpired:
                                os.killpg(process.pid, signal.SIGKILL)
                                process.wait(timeout=3)
                    lo_record["exit_status"] = process.returncode
                    stdout.seek(0)
                    stderr.seek(0)
                    lo_record["stdout"], lo_record["stderr"] = stdout.read(), stderr.read()
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    report["source_sha256_after"] = sha256(source)
    report["input_unchanged"] = report["source_sha256_after"] == before_hash
    if not report["input_unchanged"]:
        report.update(status="failed", error="Input hash changed during native formatting")
    return report


def apply_native_caption_layout(document, *, allow_multipage_tables=False):
    """Use native UNO paragraph/table properties; report geometry, never page QA."""
    report = {"status": "caption_layout_applied", "quality_status": "pending", "pages_verified": False,
              "bindings": [], "pending": [], "blocking_pending": False,
              "allow_multipage_tables": allow_multipage_tables,
              "note": "Native keep properties are not same-page proof. Review actual pages; oversized groups are retained as source drafts, not cropped or auto-shrunk."}
    blocks = []
    enumeration = document.Text.createEnumeration()
    while enumeration.hasMoreElements():
        blocks.append(enumeration.nextElement())

    def position(anchor):
        try:
            cursor = anchor.Text.createTextCursorByRange(anchor)
            cursor.gotoStartOfParagraph(False)
            for index, block in enumerate(blocks):
                if block.supportsService("com.sun.star.text.Paragraph") and document.Text.compareRegionStarts(block.Start, cursor.Start) == 0:
                    return index
        except Exception:
            return None
        return None

    def body_height(paragraph):
        try:
            cursor = document.Text.createTextCursorByRange(paragraph.Start)
            name = cursor.PageStyleName or "Standard"
            style = document.StyleFamilies.getByName("PageStyles").getByName(name)
            return style.Height - style.TopMargin - style.BottomMargin
        except Exception:
            return None

    def boundary(paragraph, *, before=False):
        try:
            value = paragraph.BreakType.value
            return value != "NONE" if before else value.endswith("AFTER") or value.endswith("BOTH")
        except Exception:
            return False

    captions = {}
    fields = document.TextFields.createEnumeration()
    while fields.hasMoreElements():
        field = fields.nextElement()
        if not field.supportsService("com.sun.star.text.TextField.SetExpression"):
            continue
        if field.SubType != 1 or field.VariableName.lower() not in {"figure", "table"}:
            continue
        index = position(field.Anchor)
        kind = field.VariableName.title()
        if index is None:
            report["pending"].append({"sequence": kind, "reason": "caption_outside_direct_main_body"})
        else:
            captions.setdefault(index, []).append(kind)
    visuals = {}
    for index in range(document.DrawPage.Count):
        shape = document.DrawPage.getByIndex(index)
        try:
            block = position(shape.Anchor)
            visuals.setdefault(block, []).append(shape)
        except Exception:
            continue
    for index, kinds in sorted(captions.items()):
        kind = kinds[0]
        caption = blocks[index]
        record = {"sequence": kind, "caption_block": index, "page_fit": "unverified"}
        if len(kinds) != 1:
            report["pending"].append({**record, "reason": "ambiguous_caption_fields"})
            continue
        neighbour_index = index - 1 if kind == "Figure" else index + 1
        if not 0 <= neighbour_index < len(blocks):
            report["pending"].append({**record, "reason": "caption_object_not_adjacent"})
            continue
        neighbour = blocks[neighbour_index]
        try:
            if kind == "Figure":
                shapes = visuals.get(neighbour_index, [])
                if not neighbour.supportsService("com.sun.star.text.Paragraph") or not shapes or neighbour.String.strip(" \t\r\n\ufffc"):
                    report["pending"].append({**record, "reason": "adjacent_paragraph_is_not_an_inline_figure_only"})
                    continue
                if any(shape.AnchorType.value != "AS_CHARACTER" for shape in shapes):
                    report["pending"].append({**record, "reason": "floating_figure_needs_template_review"})
                    continue
                if boundary(neighbour) or boundary(caption, before=True):
                    report["pending"].append({**record, "reason": "explicit_page_column_or_section_boundary"})
                    continue
                height = body_height(caption)
                if height is not None and max(shape.Size.Height for shape in shapes) > height:
                    report["pending"].append({**record, "reason": "figure_exceeds_declared_page_body"})
                    report["blocking_pending"] = True
                    continue
                neighbour.ParaKeepTogether, neighbour.ParaSplit = True, False
                caption.ParaKeepTogether, caption.ParaSplit = False, False
                record.update(object_block=neighbour_index, placement="caption_below", object_kind="inline_drawing")
            else:
                if not neighbour.supportsService("com.sun.star.text.TextTable") or boundary(caption):
                    report["pending"].append({**record, "reason": "table_not_immediately_after_caption_or_boundary"})
                    continue
                row_count = neighbour.Rows.Count
                height = body_height(caption)
                minimum = sum(max(0, neighbour.Rows.getByIndex(row).Height) for row in range(row_count))
                if not allow_multipage_tables and height is not None and minimum > height:
                    report["pending"].append({**record, "reason": "minimum_table_height_exceeds_declared_page_body", "height": minimum, "available_height": height})
                    report["blocking_pending"] = True
                    continue
                cells = []
                for name in neighbour.getCellNames():
                    match = re.fullmatch(r"[A-Z]+([1-9][0-9]*)", name)
                    if not match:
                        raise ValueError("Complex merged/split cell geometry needs template review")
                    enumeration = neighbour.getCellByName(name).Text.createEnumeration()
                    while enumeration.hasMoreElements():
                        paragraph = enumeration.nextElement()
                        if not paragraph.supportsService("com.sun.star.text.Paragraph") or boundary(paragraph, before=True):
                            raise ValueError("Nested table or explicit cell boundary needs template review")
                        cells.append((int(match[1]) - 1, paragraph))
                caption.ParaKeepTogether, caption.ParaSplit = True, False
                # TextTable.KeepTogether links the FOLLOWING paragraph; Split
                # controls whether the table itself can span pages.
                neighbour.Split = allow_multipage_tables
                neighbour.KeepTogether = False
                for row in range(row_count):
                    neighbour.Rows.getByIndex(row).IsSplitAllowed = False
                for row, paragraph in cells:
                    paragraph.ParaKeepTogether = not allow_multipage_tables and row < row_count - 1
                record.update(object_block=neighbour_index, placement="caption_above", object_kind="native_table",
                              whole_table_kept=not allow_multipage_tables, rows=row_count)
            report["bindings"].append(record)
        except Exception as exc:
            report["pending"].append({**record, "reason": "native_caption_layout_needs_template_review", "detail": str(exc)})
    if report["pending"]:
        report["status"] = "pending"
    return report


def uno_worker(pipe, input_path, output_path, settings_path):
    """Internal child entry; imports UNO only under a matching system interpreter."""
    import uno
    from com.sun.star.beans import PropertyValue

    def props(**values):
        return tuple(PropertyValue(Name=key, Value=value) for key, value in values.items())

    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    context = None
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            context = resolver.resolve(f"uno:pipe,name={pipe};urp;StarOffice.ComponentContext")
            break
        except Exception:
            time.sleep(0.1)
    if context is None:
        raise RuntimeError("Timed out connecting to isolated LibreOffice UNO pipe")
    desktop = context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", context)
    document = None
    never_execute = uno.getConstantByName("com.sun.star.document.MacroExecMode.NEVER_EXECUTE")
    no_update = uno.getConstantByName("com.sun.star.document.UpdateDocMode.NO_UPDATE")
    changes = {"styles": [], "tables": 0, "short_rows_kept": 0, "rows_not_changed": 0,
               "fields_refreshed": False, "field_refresh_passes": 0, "indexes_updated": 0, "pagination_refreshed": False}
    try:
        # Resolve API constants instead of relying on unverified magic numbers.
        document = desktop.loadComponentFromURL(Path(input_path).as_uri(), "_blank", 0,
            props(Hidden=True, ReadOnly=False, MacroExecutionMode=never_execute, UpdateDocMode=no_update))
        if document is None or not document.supportsService("com.sun.star.text.TextDocument"):
            raise ValueError("Input did not load as a Writer text document")
        settings = json.loads(Path(settings_path).read_text(encoding="utf-8"))
        styles = document.StyleFamilies.getByName("ParagraphStyles")
        styles_to_change = [("Standard", settings["body_size_pt"], False),
                            ("Text body", settings["body_size_pt"], False),
                            ("Caption", settings["caption_size_pt"], False)]
        styles_to_change.extend((f"Heading {index}", size, True)
                                for index, size in enumerate(settings["heading_sizes_pt"], 1))
        for name, size, heading in styles_to_change:
            if not styles.hasByName(name):
                continue
            style = styles.getByName(name)
            for key in ("CharFontName", "CharFontNameAsian", "CharFontNameComplex"):
                style.setPropertyValue(key, settings["font"])
            for key in ("CharHeight", "CharHeightAsian", "CharHeightComplex"):
                style.setPropertyValue(key, float(size))
            if heading:
                style.ParaKeepTogether = True
                style.ParaSplit = False
            changes["styles"].append({"name": name, "size_pt": size, "keep_with_next": heading})
        tables = document.TextTables
        page_styles = document.StyleFamilies.getByName("PageStyles")
        cursor = document.Text.createTextCursor()
        page_style = page_styles.getByName(cursor.PageStyleName or "Standard")
        page_body_height = page_style.Height - page_style.TopMargin - page_style.BottomMargin
        for name in tables.getElementNames():
            table = tables.getByName(name)
            changes["tables"] += 1
            if settings["repeat_table_headers"] and table.Rows.Count > 1:
                table.RepeatHeadline = True
                table.HeaderRowCount = max(1, table.HeaderRowCount)
            if not settings["keep_short_rows_together"]:
                continue
            for index in range(table.Rows.Count):
                row = table.Rows.getByIndex(index)
                # Existing large rows remain splittable; do not lock an entire long table to a page.
                cells = [table.getCellByPosition(column, index) for column in range(table.Columns.Count)]
                text = "".join(cell.String for cell in cells)
                compact = len(text) <= settings["short_row_max_chars"] and text.count("\n") <= 4
                height_ok = row.IsAutoHeight or 0 < row.Height < page_body_height // 3
                if compact and height_ok:
                    row.IsSplitAllowed = False
                    changes["short_rows_kept"] += 1
                else:
                    changes["rows_not_changed"] += 1
        changes["caption_layout"] = apply_native_caption_layout(
            document, allow_multipage_tables=settings["allow_multipage_tables"])
        if changes["caption_layout"]["blocking_pending"]:
            print(json.dumps(changes))
            raise ValueError("Caption group exceeds page body; native output withheld, retain the readable source draft for review")
        # First round resolves sequence values; a later round refreshes forward refs.
        document.TextFields.refresh()
        changes["field_refresh_passes"] += 1
        changes["fields_refreshed"] = True
        indexes = document.DocumentIndexes
        for index in range(indexes.Count):
            indexes.getByIndex(index).update()
            changes["indexes_updated"] += 1
        document.refresh()
        changes["pagination_refreshed"] = True
        document.TextFields.refresh()
        changes["field_refresh_passes"] += 1
        document.storeAsURL(Path(output_path).as_uri(), props(FilterName="Office Open XML Text", Overwrite=False))
        document.close(True)
        document = None
        # Prove the saved result opens under the same native engine, macros still disabled.
        reopened = desktop.loadComponentFromURL(Path(output_path).as_uri(), "_blank", 0,
            props(Hidden=True, ReadOnly=True, MacroExecutionMode=never_execute, UpdateDocMode=no_update))
        if reopened is None or not reopened.supportsService("com.sun.star.text.TextDocument"):
            raise ValueError("Saved DOCX did not reopen in Writer")
        reopened.close(True)
        changes["native_reopen_passed"] = True
    finally:
        if document is not None:
            document.close(True)
        desktop.terminate()
    print(json.dumps(changes))


def main():
    if len(sys.argv) == 6 and sys.argv[1] == "--_uno-worker":
        uno_worker(*sys.argv[2:])
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=["libreoffice"], required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    source, output, report_path = (path.resolve() for path in (args.input, args.output, args.report))
    occupied = {source, output}
    if args.profile:
        occupied.add(args.profile.resolve())
        if args.profile.resolve() in {source, output}:
            parser.error("Profile must differ from input and output")
    if report_path in occupied or report_path.exists():
        parser.error("Report path must be new and differ from input, output and profile")
    if any(a in b.parents or b in a.parents for a, b in ((source, output), (report_path, source), (report_path, output))):
        parser.error("Input, output and report must be separate file paths, not parent/child paths")
    try:
        result = format_document(source, output, profile=args.profile, timeout=args.timeout)
    except Exception as exc:
        result = {"engine": args.engine, "status": "failed", "quality_status": "pending", "error": str(exc),
                  "input": str(source), "output": str(output), "commands": []}
        if source.is_file():
            result.update(source_sha256=sha256(source), source_sha256_after=sha256(source), input_unchanged=True)
    try:
        write_report(report_path, result)
    except Exception as exc:
        result.update(status="failed", report_error=f"{type(exc).__name__}: {exc}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "formatted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
