#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx>=1.1"]
# ///
"""Reusable python-docx helpers: LaTeX fragments -> editable OMML, SEQ and REF.

Pandoc converts only the new equation fragment, never an existing document.
Callers own their original .tex/JSON sources, working copies and saving. New field
caches are '?' and dirty until a real native field refresh. The global update-on-open
flag is only added when absent and every existing field is an unlocked SEQ/REF/PAGEREF. Structural validation
remains quality_status=pending until actual rendering and independent QA.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import uuid
import zipfile

from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Pt


SEQUENCES = {"Figure": "图", "Table": "表", "Equation": "公式"}
BOOKMARK = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,39}\Z")
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def latex_to_omml(latex, display=True, *, pandoc=None, timeout=30):
    """Return one detached m:oMathPara (display) or m:oMath (inline).

    No TeX engine, raster fallback, or whole-document roundtrip is used. Warnings,
    dropped math and mixed non-math content are conversion failures, not success.
    """
    if not isinstance(latex, str) or not latex.strip() or len(latex) > 65536:
        raise ValueError("LaTeX must be a nonempty math fragment of at most 65536 characters")
    if not isinstance(display, bool):
        raise ValueError("display must be boolean")
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not math.isfinite(timeout) or not 0 < timeout <= 120:
        raise ValueError("Pandoc timeout must be positive and at most 120 seconds")
    if re.search(r"\\(?:input|include|includeonly|openin|openout|write|read|usepackage|documentclass)\b", latex):
        raise ValueError("Pass only the equation fragment, not document/file commands")
    executable = str(pandoc) if pandoc is not None else shutil.which("pandoc")
    if not executable:
        raise RuntimeError("Missing Pandoc; install it before converting the selected LaTeX fragment")
    opening, closing = (r"\[", r"\]") if display else (r"\(", r"\)")
    with tempfile.TemporaryDirectory(prefix="office-equation-") as temporary:
        output = Path(temporary) / "fragment.docx"
        command = [executable, "--from=latex", "--to=docx", "--standalone", "--fail-if-warnings", "--output", str(output)]
        try:
            result = subprocess.run(command, input=opening + latex + closing + "\n", text=True,
                                    capture_output=True, timeout=timeout, cwd=temporary)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Pandoc equation conversion timed out after {timeout}s") from exc
        except OSError as exc:
            raise RuntimeError(f"Pandoc equation converter failed to start: {exc}") from exc
        if result.returncode or result.stderr.strip():
            raise RuntimeError(f"Pandoc equation conversion failed (exit {result.returncode}): {result.stderr.strip()}")
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("Pandoc returned success without a DOCX equation fragment")
        with zipfile.ZipFile(output) as package:
            root = parse_xml(package.read("word/document.xml"))
        equations = list(root.iter(M + "oMath"))
        if len(equations) != 1 or not any((item.text or "").strip() for item in equations[0].iter(M + "t")):
            raise RuntimeError("Pandoc did not produce exactly one nonempty native OMML equation")
        if any((item.text or "").strip() for item in root.iter(W + "t")) or list(root.iter(W + "drawing")):
            raise RuntimeError("Pandoc produced non-math text or a picture instead of only native OMML")
        equation = deepcopy(equations[0])
        if not display:
            return equation
        parent = equations[0].getparent()
        if parent is not None and parent.tag == M + "oMathPara":
            return deepcopy(parent)
        wrapper = OxmlElement("m:oMathPara")
        wrapper.append(equation)
        return wrapper


def _name(name):
    if not isinstance(name, str) or not BOOKMARK.fullmatch(name):
        raise ValueError("Bookmark names need 1-40 ASCII letters/digits/underscores and a non-digit first character")
    return name


def _roots(owner):
    roots = []
    for part in owner.part.package.parts:
        if hasattr(part, "element"):
            roots.append(part.element)
        elif str(part.partname).startswith("/word/") and str(part.partname).endswith(".xml"):
            # python-docx leaves footnotes/endnotes and some extensions generic.
            # Parse their bytes read-only for cross-story protection/validation.
            roots.append(parse_xml(part.blob))
    return roots


def _registry(owner):
    starts, names = {}, {}
    for root in _roots(owner):
        opened = set()
        for node in root.iter():
            if node.tag not in {W + "bookmarkStart", W + "bookmarkEnd"}:
                continue
            raw = node.get(W + "id", "")
            if not raw.isdecimal() or int(raw) > 2147483647:
                raise ValueError("Existing bookmark has an invalid numeric ID")
            identifier = int(raw)
            if node.tag == W + "bookmarkStart":
                name = node.get(W + "name")
                if not name or name.casefold() in names or identifier in starts:
                    raise ValueError("Existing bookmark names/IDs must be unique")
                starts[identifier], names[name.casefold()] = name, name
                opened.add(identifier)
            else:
                if identifier not in opened:
                    raise ValueError("Bookmark end precedes its start or belongs to another document part")
                opened.remove(identifier)
        if opened:
            raise ValueError("Existing bookmark starts/ends are not paired in the same document part")
    return starts, names


def _field_instructions(owner, *, roots=None):
    instructions, errors = [], []
    for root in (_roots(owner) if roots is None else roots):
        stack = []
        for item in root.iter():
            if item.tag == W + "fldSimple":
                instruction = item.get(W + "instr", "").strip()
                if not instruction:
                    errors.append("Simple field has no instruction")
                instructions.append(instruction)
            elif item.tag == W + "fldChar":
                kind = item.get(W + "fldCharType")
                if kind == "begin":
                    stack.append({"parts": [], "separated": False})
                elif kind in {"separate", "end"}:
                    if not stack:
                        errors.append(f"Unpaired complex field {kind}")
                        continue
                    current = stack[-1]
                    if kind == "separate" and current["separated"]:
                        errors.append("Duplicate complex field separator")
                    if not current["separated"]:
                        instruction = "".join(current["parts"]).strip()
                        if not instruction:
                            errors.append("Complex field has no instruction")
                        instructions.append(instruction)
                        current["separated"] = True
                    if kind == "end":
                        stack.pop()
            elif item.tag == W + "instrText":
                if not stack:
                    errors.append("Field instruction outside a complex field")
                elif not stack[-1]["separated"]:
                    stack[-1]["parts"].append(item.text or "")
        if stack:
            errors.append("Unclosed complex field begin")
    return instructions, errors


def _plan(owner, sequence, bookmark):
    if sequence not in SEQUENCES:
        raise ValueError("SEQ sequence must be Figure, Table or Equation")
    starts, names = _registry(owner)
    if bookmark is None:
        bookmark = "Office" + sequence + "_" + uuid.uuid4().hex[:16]
    _name(bookmark)
    if bookmark.casefold() in names:
        raise ValueError(f"Duplicate bookmark name: {bookmark}")
    identifier = max(starts, default=-1) + 1
    if identifier > 2147483647:
        raise ValueError("Bookmark ID budget exhausted")
    return bookmark, identifier


def _update_on_open(owner):
    document = owner.part.package.main_document_part.document
    settings = document.settings.element
    # Existing explicit application/user choices always win, including false.
    if settings.find(W + "updateFields") is not None:
        return
    instructions, errors = _field_instructions(owner)
    if errors or any(value.split()[0].upper() not in {"SEQ", "REF", "PAGEREF"}
                     for value in instructions if value.split()):
        return
    for root in _roots(owner):
        if any(item.get(W + "fldLock", "false").lower() not in {"0", "false", "off"}
               for item in root.iter() if item.tag in {W + "fldSimple", W + "fldChar"}):
            return
    item = OxmlElement("w:updateFields")
    item.set(qn("w:val"), "true")
    settings.append(item)


def _field(paragraph, instruction, cached_text):
    if cached_text is not None and not isinstance(cached_text, str):
        raise ValueError("cached_text must be a string or None; it is never treated as verified")
    item = OxmlElement("w:fldSimple")
    item.set(qn("w:instr"), instruction)
    item.set(qn("w:dirty"), "true")
    run, text = OxmlElement("w:r"), OxmlElement("w:t")
    text.text = "?" if cached_text is None else cached_text
    run.append(text)
    item.append(run)
    paragraph._p.append(item)
    _update_on_open(paragraph)
    return item


def add_seq_field(paragraph, sequence, bookmark=None, *, cached_text=None):
    """Append a dirty independent SEQ number and bookmark only its field range.

    Stable explicit semantic names are preferred. Generated UUID names do not
    encode current ordinal numbers and remain stable when content is reordered.
    """
    name, identifier = _plan(paragraph, sequence, bookmark)
    if cached_text is not None and not isinstance(cached_text, str):
        raise ValueError("cached_text must be a string or None")
    start, end = OxmlElement("w:bookmarkStart"), OxmlElement("w:bookmarkEnd")
    start.set(qn("w:id"), str(identifier))
    start.set(qn("w:name"), name)
    end.set(qn("w:id"), str(identifier))
    field = _field(paragraph, f" SEQ {sequence} \\* ARABIC ", cached_text)
    field.addprevious(start)
    field.addnext(end)
    return name


def add_ref_field(paragraph, bookmark, *, cached_text=None, allow_missing=False):
    """Append a dirty REF hyperlink. Missing targets need explicit forward intent."""
    _name(bookmark)
    _, names = _registry(paragraph)
    target = names.get(bookmark.casefold())
    if target is None and not allow_missing:
        raise ValueError(f"REF target bookmark does not exist: {bookmark}")
    return _field(paragraph, f" REF {target or bookmark} \\h ", cached_text)


def add_caption(document, sequence, text, *, bookmark=None, label=None):
    """Append a native Caption paragraph with Chinese label + independent SEQ."""
    _plan(document, sequence, bookmark)
    if not isinstance(text, str) or label is not None and not isinstance(label, str):
        raise ValueError("Caption text/label must be strings")
    paragraph = document.add_paragraph(style="Caption")
    paragraph.add_run((SEQUENCES[sequence] if label is None else label) + " ")
    name = add_seq_field(paragraph, sequence, bookmark)
    paragraph.add_run("  " + text)
    return {"paragraph": paragraph, "bookmark": name, "layout": apply_caption_layout(document)}


def _paragraph_flag(paragraph, name, value):
    props = paragraph.get_or_add_pPr()
    item = getattr(props, "get_or_add_" + name)()
    item.set(W + "val", "1" if value else "0")


def _caption_sequences(paragraph):
    instructions, errors = _field_instructions(None, roots=[paragraph])
    sequences = []
    for instruction in instructions:
        match = re.match(r'\s*SEQ\s+(?:"(Figure|Table)"|(Figure|Table))(?=\s|$)', instruction, re.I)
        if match:
            sequences.append((match[1] or match[2]).title())
    return sequences, errors


def _explicit_boundary(paragraph, *, before=False):
    if paragraph.find(W + "pPr/" + W + "sectPr") is not None:
        return True
    if any(item.get(W + "type") in {"page", "column"} for item in paragraph.iter(W + "br")):
        return True
    flag = paragraph.find(W + "pPr/" + W + "pageBreakBefore")
    return before and flag is not None and flag.get(W + "val", "true").lower() not in {"0", "false", "off"}


def _declared_body_height(body, block_index):
    # A section's sectPr closes its preceding blocks. This is only a declared
    # height bound, not a pagination estimate (headers/footnotes can reduce fit).
    for index, block in enumerate(body):
        if index < block_index:
            continue
        section = block if block.tag == W + "sectPr" else block.find(W + "pPr/" + W + "sectPr")
        if section is None:
            continue
        size, margins = section.find(W + "pgSz"), section.find(W + "pgMar")
        if size is not None and margins is not None:
            try:
                return int(size.get(W + "h")) - int(margins.get(W + "top")) - int(margins.get(W + "bottom"))
            except (TypeError, ValueError):
                return None
    return None


def apply_caption_layout(document, *, allow_multipage_tables=False):
    """Bind real adjacent SEQ captions without moving/replacing document objects.

    Figure: inline object paragraph -> caption below. Table: caption above ->
    whole adjacent business table. Equation layout tables are excluded. Native
    keep properties are constraints, not proof that an oversized group fits.
    """
    if not isinstance(allow_multipage_tables, bool):
        raise ValueError("allow_multipage_tables must be boolean")
    report = {"status": "caption_layout_applied", "quality_status": "pending", "pages_verified": False,
              "allow_multipage_tables": allow_multipage_tables, "bindings": [], "pending": [],
              "note": "Properties only: review actual pages for every pair. Oversized groups remain pending; no cropping, shrinking or automatic multipage fallback."}
    body = document.element.body
    blocks = list(body)
    positions = {id(item): index for index, item in enumerate(blocks)}
    inline_ns = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
    for root in _roots(document):
        for caption in root.iter(W + "p"):
            sequences, errors = _caption_sequences(caption)
            if not sequences:
                continue
            sequence = sequences[0]
            position = positions.get(id(caption))
            record = {"sequence": sequence, "caption_block": position, "page_fit": "unverified"}
            if len(sequences) != 1 or errors:
                report["pending"].append({**record, "reason": "ambiguous_or_malformed_caption_fields"})
                continue
            if caption.getparent() is not body or position is None:
                report["pending"].append({**record, "reason": "caption_outside_direct_main_body"})
                continue
            neighbour_index = position - 1 if sequence == "Figure" else position + 1
            neighbour = blocks[neighbour_index] if 0 <= neighbour_index < len(blocks) else None
            if sequence == "Figure":
                if neighbour is None or neighbour.tag != W + "p":
                    report["pending"].append({**record, "reason": "figure_not_immediately_before_caption"})
                    continue
                if list(neighbour.iter(inline_ns + "anchor")) or list(neighbour.iter(W + "pict")):
                    report["pending"].append({**record, "reason": "floating_or_legacy_figure_needs_template_review"})
                    continue
                if not list(neighbour.iter(inline_ns + "inline")) or any((item.text or "").strip() for item in neighbour.iter(W + "t")):
                    report["pending"].append({**record, "reason": "adjacent_paragraph_is_not_an_inline_figure_only"})
                    continue
                if _explicit_boundary(neighbour) or _explicit_boundary(caption, before=True):
                    report["pending"].append({**record, "reason": "explicit_page_column_or_section_boundary"})
                    continue
                _paragraph_flag(neighbour, "keepNext", True)
                _paragraph_flag(neighbour, "keepLines", True)
                _paragraph_flag(caption, "keepLines", True)
                _paragraph_flag(caption, "keepNext", False)
                record.update(object_block=neighbour_index, object_kind="inline_drawing", placement="caption_below")
                height = _declared_body_height(body, position)
                extents = [int(item.get("cy", "0")) for item in neighbour.iter(inline_ns + "extent")]
                if height is not None and extents and max(extents) > height * 635:
                    report["pending"].append({**record, "reason": "figure_exceeds_declared_page_body"})
            else:
                if neighbour is None or neighbour.tag != W + "tbl":
                    report["pending"].append({**record, "reason": "table_not_immediately_after_caption"})
                    continue
                props = neighbour.find(W + "tblPr")
                marker = props.find(W + "tblCaption") if props is not None else None
                if marker is not None and marker.get(W + "val") == "OfficeEquationLayout":
                    report["pending"].append({**record, "reason": "equation_layout_is_not_a_business_table"})
                    continue
                if _explicit_boundary(caption) or props is not None and props.find(W + "tblpPr") is not None:
                    report["pending"].append({**record, "reason": "floating_table_or_section_boundary_needs_template_review"})
                    continue
                rows = neighbour.findall(W + "tr")
                if not rows or len(list(neighbour.iter(W + "tbl"))) != 1:
                    report["pending"].append({**record, "reason": "empty_or_nested_table_needs_template_review"})
                    continue
                if any(_explicit_boundary(p, before=True) for p in neighbour.iter(W + "p")):
                    report["pending"].append({**record, "reason": "explicit_page_column_or_section_boundary"})
                    continue
                _paragraph_flag(caption, "keepNext", True)
                _paragraph_flag(caption, "keepLines", True)
                for index, row in enumerate(rows):
                    row_props = row.find(W + "trPr")
                    if row_props is None:
                        row_props = OxmlElement("w:trPr")
                        row.insert(0, row_props)
                    stop = row_props.find(W + "cantSplit")
                    if stop is None:
                        stop = OxmlElement("w:cantSplit")
                        row_props.append(stop)
                    stop.set(W + "val", "1")
                    for paragraph in row.iter(W + "p"):
                        _paragraph_flag(paragraph, "keepNext", not allow_multipage_tables and index < len(rows) - 1)
                record.update(object_block=neighbour_index, object_kind="native_table", placement="caption_above",
                              whole_table_kept=not allow_multipage_tables, rows=len(rows))
                height = _declared_body_height(body, position)
                minimum = sum(int(item.get(W + "val", "0")) for row in rows
                              for item in row.findall(W + "trPr/" + W + "trHeight"))
                if not allow_multipage_tables and height is not None and minimum > height:
                    report["pending"].append({**record, "reason": "minimum_table_height_exceeds_declared_page_body"})
            report["bindings"].append(record)
    if report["pending"]:
        report["status"] = "pending"
    return report


def add_numbered_equation(document, latex, *, bookmark=None, pandoc=None, timeout=30):
    """Append centered OMML and a right-aligned (SEQ Equation) layout skeleton.

    The borderless three-column table is equation layout, not business data. It
    introduces no new workbook, data model or standalone spreadsheet workflow.
    """
    _plan(document, "Equation", bookmark)
    equation = latex_to_omml(latex, True, pandoc=pandoc, timeout=timeout)
    blocks = [item for item in document.element.body if item.tag != W + "sectPr"]
    if blocks and blocks[-1].tag == W + "tbl":
        # A real paragraph boundary prevents Writer/Word from merging adjacent
        # identical layout tables into a single business-looking table.
        separator = document.add_paragraph()
        separator.paragraph_format.space_before = Pt(0)
        separator.paragraph_format.space_after = Pt(0)
        separator.paragraph_format.line_spacing = Pt(1)
        separator.paragraph_format.keep_with_next = True
        separator.add_run().font.size = Pt(1)
    table = document.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    section = document.sections[-1]
    usable = int(section.page_width - section.left_margin - section.right_margin)
    widths = [usable // 8, usable - 2 * (usable // 8), usable // 8]
    for column, cell, width in zip(table.columns, table.rows[0].cells, widths):
        column.width = width
        cell.width = width
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    props = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = OxmlElement("w:" + edge)
        node.set(qn("w:val"), "nil")
        borders.append(node)
    props.append(borders)
    for tag, value in (("tblCaption", "OfficeEquationLayout"),
                       ("tblDescription", "Equation layout skeleton; not a business-data table")):
        item = OxmlElement("w:" + tag)
        item.set(qn("w:val"), value)
        props.append(item)
    row_props = table.rows[0]._tr.get_or_add_trPr()
    row_props.append(OxmlElement("w:cantSplit"))
    middle = table.cell(0, 1).paragraphs[0]
    middle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    middle._p.append(equation)
    right = table.cell(0, 2).paragraphs[0]
    right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    right.add_run("(")
    name = add_seq_field(right, "Equation", bookmark)
    right.add_run(")")
    return {"table": table, "bookmark": name, "latex": latex, "quality_status": "pending"}


def validate_references(document):
    """Check target existence and package structure; never certify cached numbers."""
    report = {"status": "failed", "quality_status": "pending", "errors": [],
              "bookmark_names": [], "sequences": {}, "references": [], "native_equation_count": 0,
              "field_results": "unverified; native refresh and rendered review are required"}
    try:
        _, names = _registry(document)
        report["bookmark_names"] = sorted(names.values())
        sequences = Counter()
        instructions, field_errors = _field_instructions(document)
        report["errors"].extend(field_errors)
        for root in _roots(document):
            report["native_equation_count"] += sum(1 for _ in root.iter(M + "oMath"))
        update = document.settings.element.find(W + "updateFields")
        report["update_fields_on_open"] = update.get(W + "val", "true") if update is not None else None
        for value in instructions:
            match = re.match(r"\s*(SEQ|REF|PAGEREF)\b", value, re.I)
            if not match:
                continue
            command = match[1].upper()
            tail = value[match.end():].strip()
            if not tail or tail.startswith("\\"):
                report["errors"].append(f"Incomplete {command} field instruction")
                continue
            if tail.startswith('"'):
                closing = tail.find('"', 1)
                if closing < 1:
                    report["errors"].append(f"Unclosed quoted {command} target")
                    continue
                target = tail[1:closing]
            else:
                target = tail.split()[0]
            if command == "SEQ":
                sequences[target] += 1
            else:
                report["references"].append({"command": command, "bookmark": target})
                if target.casefold() not in names:
                    report["errors"].append(f"Missing {command} bookmark target: {target}")
        report["sequences"] = dict(sequences)
        if not report["errors"]:
            report["status"] = "references_valid"
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
    return report
