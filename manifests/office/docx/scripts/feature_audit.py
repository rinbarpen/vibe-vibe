#!/usr/bin/env python3
"""Inventory native Word features and compare explicitly supplied constraints.

This reads package metadata, not Word's UI. It never executes VBA, changes the
document, proves password strength, or declares final visual/content QA passed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from verify import package_inventory, sha256, write_json

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"


def flag(element) -> bool | None:
    if element is None:
        return None
    return element.get(W + "val", "true").lower() not in ("0", "false", "off")


def attribute(parent, tag: str, name: str = "val"):
    child = parent.find(W + tag) if parent is not None else None
    return child.get(W + name) if child is not None else None


def inventory(path: Path) -> dict:
    package_inventory(path, "word/document.xml")
    with zipfile.ZipFile(path) as package:
        document = ET.fromstring(package.read("word/document.xml"))
        styles = ET.fromstring(package.read("word/styles.xml")) if "word/styles.xml" in package.namelist() else ET.Element("styles")
        settings = ET.fromstring(package.read("word/settings.xml")) if "word/settings.xml" in package.namelist() else ET.Element("settings")
        raw_styles = {}
        for node in styles.findall(W + "style"):
            rpr, ppr = node.find(W + "rPr"), node.find(W + "pPr")
            fonts = rpr.find(W + "rFonts") if rpr is not None else None
            size = attribute(rpr, "sz")
            raw_styles[node.get(W + "styleId")] = {
                "name": attribute(node, "name"), "based_on": attribute(node, "basedOn"),
                "font": fonts.get(W + "ascii") if fonts is not None else None,
                "east_asia_font": fonts.get(W + "eastAsia") if fonts is not None else None,
                "size_pt": float(size) / 2 if size is not None else None,
                "keep_with_next": flag(ppr.find(W + "keepNext")) if ppr is not None else None,
            }
        default_rpr = styles.find(f"{W}docDefaults/{W}rPrDefault/{W}rPr")
        default_fonts = default_rpr.find(W + "rFonts") if default_rpr is not None else None
        default_size = attribute(default_rpr, "sz")
        defaults = {"font": default_fonts.get(W + "ascii") if default_fonts is not None else None,
                    "east_asia_font": default_fonts.get(W + "eastAsia") if default_fonts is not None else None,
                    "size_pt": float(default_size) / 2 if default_size is not None else None,
                    "keep_with_next": False}

        def effective(style_id, seen=None):
            seen = set() if seen is None else seen
            if style_id in seen:
                raise ValueError("Style inheritance cycle")
            seen.add(style_id)
            node = raw_styles.get(style_id, {})
            base = effective(node["based_on"], seen) if node.get("based_on") else dict(defaults)
            base.update({key: value for key, value in node.items() if value is not None})
            return base

        controls = []
        for node in document.iter(W + "sdt"):
            props = node.find(W + "sdtPr")
            controls.append({"tag": attribute(props, "tag"), "alias": attribute(props, "alias"),
                             "lock": attribute(props, "lock"),
                             "text": "".join(x.text or "" for x in node.iter(W + "t"))})
        tables = []
        for node in document.iter(W + "tbl"):
            rows = []
            for row in node.findall(W + "tr"):
                props = row.find(W + "trPr")
                rows.append({"repeat_header": bool(flag(props.find(W + "tblHeader"))) if props is not None else False,
                             "prevent_split": bool(flag(props.find(W + "cantSplit"))) if props is not None else False})
            tables.append({"rows": rows, "style": attribute(node.find(W + "tblPr"), "tblStyle")})
        fields = []
        # A field instruction can span multiple runs; collect through separator/end.
        for name in package.namelist():
            if not name.startswith("word/") or not name.endswith(".xml") or name in ("word/styles.xml", "word/settings.xml"):
                continue
            tree = ET.fromstring(package.read(name))
            stack = []
            for node in tree.iter():
                if node.tag == W + "fldSimple":
                    fields.append({"part": name, "instruction": node.get(W + "instr", "").strip()})
                elif node.tag == W + "fldChar":
                    kind = node.get(W + "fldCharType")
                    if kind == "begin":
                        stack.append([])
                    elif kind in ("separate", "end") and stack:
                        text = "".join(stack[-1]).strip()
                        if text:
                            fields.append({"part": name, "instruction": text})
                            stack[-1] = []
                        if kind == "end":
                            stack.pop()
                elif node.tag == W + "instrText" and stack:
                    stack[-1].append(node.text or "")
        protection = settings.find(W + "documentProtection")
        return {
            "styles": {name: effective(name) for name in raw_styles},
            "content_controls": controls, "tables": tables, "fields": fields,
            "figures": [{"id": n.get("id"), "name": n.get("name"), "alt_text": n.get("descr", ""),
                         "title": n.get("title", "")} for n in document.iter(WP + "docPr")],
            "bookmarks": [n.get(W + "name") for n in document.iter(W + "bookmarkStart")],
            "document_protection": {"enforced": protection.get(W + "enforcement", "false").lower() not in ("0", "false", "off") if protection is not None else False,
                                    "edit": protection.get(W + "edit") if protection is not None else None},
            "tracked_changes_enabled": bool(flag(settings.find(W + "trackRevisions"))),
            "macros_present": any(n.endswith("vbaProject.bin") for n in package.namelist()),
        }


def compare(actual: dict, expected: dict) -> list[str]:
    errors = []
    allowed = {"styles", "content_controls", "fields", "figures", "tables", "document_protection"}
    if not isinstance(expected, dict) or set(expected) - allowed:
        raise ValueError("Unknown constraint keys or non-object constraint document")

    def properties(want, allowed_keys):
        if not isinstance(want, dict) or set(want) - set(allowed_keys):
            raise ValueError("Unknown or malformed constraint properties")

    for name, want in expected.get("styles", {}).items():
        properties(want, ("font", "east_asia_font", "size_pt", "keep_with_next"))
        style = actual["styles"].get(name)
        if style is None:
            errors.append(f"Missing style {name}")
        else:
            for key, value in want.items():
                if style.get(key) != value:
                    errors.append(f"Style {name}.{key}: expected {value!r}, observed {style.get(key)!r}")
    for tag, want in expected.get("content_controls", {}).items():
        properties(want, ("lock", "alias"))
        matches = [n for n in actual["content_controls"] if n["tag"] == tag]
        if len(matches) != 1:
            errors.append(f"Expected one content control tagged {tag}, found {len(matches)}")
        else:
            for key, value in want.items():
                if matches[0].get(key) != value:
                    errors.append(f"Content control {tag}.{key} differs")
    fields = expected.get("fields", [])
    if not isinstance(fields, list) or not all(isinstance(x, str) and x for x in fields):
        raise ValueError("fields must be a list of field command names")
    commands = {x["instruction"].split()[0].upper() for x in actual["fields"] if x["instruction"].split()}
    for command in fields:
        if command.upper() not in commands:
            errors.append(f"Missing field command {command}")
    for kind in ("figures", "tables"):
        want = expected.get(kind, {})
        properties(want, ("min_count", "require_alt_text") if kind == "figures" else ("min_count", "repeat_header", "prevent_row_split"))
        minimum = want.get("min_count", 0)
        if type(minimum) is not int or minimum < 0:
            raise ValueError("min_count must be a nonnegative integer")
        if len(actual[kind]) < minimum:
            errors.append(f"Expected at least {minimum} {kind}, found {len(actual[kind])}")
        for key in set(want) - {"min_count"}:
            if type(want[key]) is not bool:
                raise ValueError(f"{key} must be boolean")
        if kind == "figures" and want.get("require_alt_text"):
            for n, item in enumerate(actual[kind], 1):
                if not item["alt_text"].strip():
                    errors.append(f"Figure {n} lacks alt text")
        if kind == "tables":
            for n, item in enumerate(actual[kind], 1):
                if "repeat_header" in want and (not item["rows"] or item["rows"][0]["repeat_header"] != want["repeat_header"]):
                    errors.append(f"Table {n} repeating-header constraint differs")
                if "prevent_row_split" in want and any(row["prevent_split"] != want["prevent_row_split"] for row in item["rows"]):
                    errors.append(f"Table {n} row-splitting constraint differs")
    protection = expected.get("document_protection", {})
    properties(protection, ("enforced", "edit"))
    for key, value in protection.items():
        if actual["document_protection"].get(key) != value:
            errors.append(f"Document protection {key} differs")
    return errors


def audit(path: Path, expected: dict | None = None) -> dict:
    report = {"file": str(path.resolve()), "status": "failed", "quality_status": "pending", "errors": [],
              "macro_execution": "not_run", "note": "Metadata evidence only; verify native UI behavior, field results and full rendered pages separately."}
    before = None
    try:
        if path.suffix.lower() not in (".docx", ".docm", ".dotx", ".dotm"):
            raise ValueError("Expected a Word OOXML document or template")
        before = sha256(path)
        report["sha256"] = before
        report["features"] = inventory(path)
        if expected is not None:
            report["expected"] = expected
            report["errors"] = compare(report["features"], expected)
        if not report["errors"]:
            report["status"] = "native_constraints_pass" if expected is not None else "native_features_recorded"
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
    if before is not None:
        report["input_unchanged"] = sha256(path) == before
        if not report["input_unchanged"]:
            report["status"] = "failed"
            report["errors"].append("Input changed during read-only audit")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--expect", type=Path, help="Explicit JSON constraints; never changes the document")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() in {args.file.resolve(), args.expect.resolve() if args.expect else None}:
        parser.error("Report path must differ from document and constraint paths")
    try:
        expected = json.loads(args.expect.read_text(encoding="utf-8")) if args.expect else None
        report = audit(args.file, expected)
    except Exception as exc:
        report = {"status": "failed", "quality_status": "pending", "errors": [str(exc)]}
    write_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if report["status"] == "failed" else 0)
