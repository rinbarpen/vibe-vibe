#!/usr/bin/env python3
"""Check an Omnippt v1 design contract, not a rendered presentation.

No PowerPoint engine or source fetching. JSON decisions record an actual user
reply (or an explicitly simulated fixture); this checker cannot authenticate it.
Pending chart/macro branches do not prevent structurally valid non-chart work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
HEX = re.compile(r"#[0-9A-Fa-f]{6}\Z")
SHA = re.compile(r"[0-9a-fA-F]{64}\Z")
KINDS = {"text", "shape", "card", "table", "chart", "image", "group"}


def validate_deck(contract: dict, *, base_dir=None) -> dict:
    """Return structural errors, branch gates and explicitly pending final QA.

    ``base_dir`` resolves local source/template locations. Without it, those
    locations are pending checks, not silently reported as verified. IDs resolve
    source references; statements and geometry remain author declarations.
    """
    errors, warnings, blocked = [], [], []

    def error(path, message):
        errors.append({"path": path, "message": message})

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def number(value, *, positive=False):
        try:
            return (isinstance(value, (int, float)) and not isinstance(value, bool)
                    and math.isfinite(value) and (value > 0 if positive else True))
        except OverflowError:
            return False

    def objects(value, path, *, nonempty=False):
        if not isinstance(value, list) or len(value) > 10000 or nonempty and not value:
            error(path, "Expected a bounded" + (" nonempty" if nonempty else "") + " list")
            return []
        result = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                error(f"{path}[{index}]", "Expected an object")
            else:
                result.append(item)
        return result

    def index(items, path):
        found = {}
        for offset, item in enumerate(items):
            identity = item.get("id")
            if not isinstance(identity, str) or not ID.fullmatch(identity):
                error(f"{path}[{offset}].id", "Use a stable ASCII ID, 1–64 characters")
            elif identity in found:
                error(f"{path}[{offset}].id", "Duplicate stable ID: " + identity)
            else:
                found[identity] = item
        return found

    def refs(value, registry, path):
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            error(path, "Expected a list of source/fact IDs")
            return set()
        if len(set(value)) != len(value):
            error(path, "Duplicate reference IDs")
        for identity in value:
            if identity not in registry:
                error(path, "Unresolved reference: " + identity)
        return set(value)

    def location(item, path):
        target = item.get("location", item.get("path"))
        if not text(target):
            error(path, "Expected a nonempty source/template location")
            return
        expected = item.get("sha256")
        if expected is not None and (not isinstance(expected, str) or not SHA.fullmatch(expected)):
            error(path + ".sha256", "Expected a SHA-256 hex digest")
            return
        if base_dir is None:
            warnings.append({"path": path, "message": "Local source/template existence and hash pending: set base_dir"})
            return
        file = Path(base_dir) / target
        if not file.is_file():
            error(path, "Local source/template does not exist: " + target)
        elif expected and hashlib.sha256(file.read_bytes()).hexdigest().lower() != expected.lower():
            error(path, "Local source/template SHA-256 mismatch")

    if not isinstance(contract, dict):
        return {"status": "invalid", "quality_status": "pending", "structure_valid": False,
                "ready_for_nonchart_build": False, "ready_for_all_requested_build": False,
                "errors": [{"path": "$", "message": "Expected a contract object"}],
                "warnings": [], "blocked_operations": []}
    if contract.get("schema_version") != 1 or isinstance(contract.get("schema_version"), bool):
        error("schema_version", "Expected schema_version 1")
    identity = contract.get("id")
    if not isinstance(identity, str) or not ID.fullmatch(identity):
        error("id", "Expected a stable deck ID")
    revision = contract.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        error("revision", "Expected a positive integer revision")
    if contract.get("mode") not in ("create", "template", "edit"):
        error("mode", "Expected create, template or edit")
    brief = contract.get("brief", {})
    if not isinstance(brief, dict) or not all(text(brief.get(key)) for key in ("audience", "outcome")):
        error("brief", "Record audience and intended outcome before outlining")
    canvas = contract.get("canvas", {})
    if not isinstance(canvas, dict):
        canvas = {}
    width, height = canvas.get("width"), canvas.get("height")
    valid_canvas = number(width, positive=True) and number(height, positive=True)
    if not valid_canvas or canvas.get("unit") not in ("in", "pt", "px", "cm"):
        error("canvas", "Expected finite positive width/height and explicit in/pt/px/cm unit")
    tokens = contract.get("tokens", {})
    if not isinstance(tokens, dict):
        tokens = {}
    if not text(tokens.get("font")):
        error("tokens.font", "Declare a font; installed availability is separate QA")
    for key in ("background", "foreground", "accent"):
        if not isinstance(tokens.get(key), str) or not HEX.fullmatch(tokens[key]):
            error("tokens." + key, "Expected #RRGGBB")
    for key in ("body_pt", "title_pt"):
        if not number(tokens.get(key), positive=True):
            error("tokens." + key, "Expected a finite positive point size")
    stages = contract.get("stage_revisions", {})
    for stage in ("outline", "storyboard", "design"):
        if (not isinstance(stages, dict) or not isinstance(stages.get(stage), int)
                or isinstance(stages.get(stage), bool) or stages.get(stage) != revision):
            error("stage_revisions." + stage, "Missing/stale stage: re-review against the current revision")

    sources = index(objects(contract.get("sources"), "sources"), "sources")
    for sid, source in sources.items():
        path = "sources." + sid
        kind = source.get("kind")
        if kind == "url":
            value = source.get("location")
            try:
                parsed = urlsplit(value) if isinstance(value, str) else None
            except ValueError:
                parsed = None
            if parsed is None or parsed.scheme not in ("http", "https") or not parsed.netloc:
                error(path, "URL source needs an absolute HTTP(S) location")
        elif kind in ("file", "data"):
            location(source, path)
        elif kind == "user":
            if not text(source.get("location")):
                error(path, "Identify the supplied user material or statement")
        else:
            error(path + ".kind", "Expected url, file, data or user")
    facts = index(objects(contract.get("facts"), "facts"), "facts")
    for fid, fact in facts.items():
        if not text(fact.get("text")):
            error("facts." + fid + ".text", "Expected a factual statement")
        used = refs(fact.get("source_ids"), sources, "facts." + fid + ".source_ids")
        if not used:
            error("facts." + fid + ".source_ids", "A factual claim needs its source")
    outline = index(objects(contract.get("outline"), "outline", nonempty=True), "outline")
    boards = index(objects(contract.get("storyboard"), "storyboard", nonempty=True), "storyboard")
    if set(outline) != set(boards):
        error("storyboard", "Outline/storyboard slide coverage must match exactly")
    if list(outline) != list(boards):
        error("storyboard", "Outline/storyboard order differs; update both after reordering")
    if contract.get("mode") == "edit":
        scope = contract.get("edit_scope", {})
        chosen = refs(scope.get("slide_ids") if isinstance(scope, dict) else None,
                      outline, "edit_scope.slide_ids")
        if chosen != set(outline) or not isinstance(scope, dict) or not text(scope.get("notes")):
            error("edit_scope", "Describe the requested edit; contract IDs must exactly cover selected slides")
    if contract.get("mode") == "template":
        template = contract.get("template")
        if not isinstance(template, dict):
            error("template", "Declare the native template path and SHA-256")
        else:
            if not template.get("sha256"):
                error("template.sha256", "Record the template hash before editing a copy")
            location(template, "template")

    def decision(kind):
        all_decisions = contract.get("decisions", {})
        value = all_decisions.get(kind) if isinstance(all_decisions, dict) else None
        path = "decisions." + kind
        if not isinstance(value, dict):
            error(path, "Record a separate yes/no/pending decision")
            return {"decision": "pending"}
        answer = value.get("decision")
        if answer not in ("yes", "no", "pending"):
            error(path, "Expected yes, no or pending")
        if value.get("scope") != identity:
            error(path + ".scope", "Decision scope must match this deck ID")
        if answer in ("yes", "no"):
            if not text(value.get("source")) or value.get("evidence_type") not in ("user", "simulated"):
                error(path, "A yes/no needs user-decision evidence or an explicitly simulated fixture")
            elif value["evidence_type"] == "simulated":
                warnings.append({"path": path, "message": "Simulated decision is test evidence, not a live user reply"})
        return value

    chart, macro = decision("chart"), decision("macro")
    modes = macro.get("requested_modes")
    if not isinstance(modes, list) or any(mode not in ("preserve", "create", "modify", "invoke") for mode in modes):
        error("decisions.macro.requested_modes", "List selected preserve/create/modify/invoke operations (possibly empty)")
    else:
        for mode in sorted(set(modes) - {"preserve"}):
            if macro.get("decision") != "yes":
                blocked.append({"kind": "macro", "mode": mode, "reason": macro.get("decision", "pending")})
            details = macro.get("operation_details", {})
            selected = details.get(mode) if isinstance(details, dict) else None
            required = ("target", "intent", "effects") + (("entry",) if mode in ("invoke", "modify") else ())
            if not isinstance(selected, dict) or not all(text(selected.get(key)) for key in required):
                blocked.append({"kind": "macro", "mode": mode, "reason": "pending_operation_details",
                                "required": list(required)})
    all_element_ids = set()
    for sid, slide in outline.items():
        if not text(slide.get("conclusion")):
            error("outline." + sid, "Each slide needs its conclusion, not only a topic")
        slide_facts = refs(slide.get("fact_ids"), facts, "outline." + sid + ".fact_ids")
        board = boards.get(sid, {})
        if not text(board.get("layout")):
            error("storyboard." + sid + ".layout", "Declare the plain storyboard layout intent")
        elements = index(objects(board.get("elements"), "storyboard." + sid + ".elements", nonempty=True),
                         "storyboard." + sid + ".elements")
        boxes = {}
        for eid, element in elements.items():
            path = "storyboard." + sid + ".elements." + eid
            if eid in all_element_ids:
                error(path, "Element stable IDs must be unique across the deck")
            all_element_ids.add(eid)
            kind = element.get("kind")
            if not isinstance(kind, str) or kind not in KINDS:
                error(path + ".kind", "Unknown storyboard element kind")
            if not isinstance(element.get("native"), bool) or kind != "image" and element.get("native") is not True:
                error(path + ".native", "Text/shapes/tables/charts remain native editable objects; images declare false")
            if kind == "image" and element.get("native") is not False:
                error(path + ".native", "Image fallback is not an editable native chart/table/text object")
            if kind == "text" and not text(element.get("text")):
                error(path + ".text", "Declare the intended native text")
            used = refs(element.get("fact_ids", []), facts, path + ".fact_ids")
            if not used <= slide_facts:
                error(path + ".fact_ids", "Element facts must belong to this slide outline")
            operation = element.get("operation", "create")
            if operation not in ("create", "preserve", "modify"):
                error(path + ".operation", "Expected create, preserve or modify")
            if "chart" in element and not isinstance(element["chart"], bool):
                error(path + ".chart", "Use a boolean chart-content declaration, including image charts")
            is_chart = kind == "chart" or element.get("chart") is True
            if is_chart and contract.get("mode") == "create" and operation != "create":
                error(path + ".operation", "A new deck has no existing chart to preserve/modify; declare creation or a real edit/template scope")
            if is_chart and operation == "create" and chart.get("decision") != "yes":
                blocked.append({"kind": "chart", "slide_id": sid, "element_id": eid,
                                "reason": chart.get("decision", "pending")})
            box = element.get("box")
            if (not isinstance(box, list) or len(box) != 4 or not all(number(value) for value in box)
                    or box[2] <= 0 or box[3] <= 0):
                error(path + ".box", "Expected finite [x,y,width,height] with positive size, in canvas units")
            else:
                boxes[eid] = box
                if valid_canvas and (box[0] < 0 or box[1] < 0 or box[0] + box[2] > width + 1e-8 or box[1] + box[3] > height + 1e-8):
                    error(path + ".box", "Element overflows the declared canvas")
        for eid, element in elements.items():
            parent = element.get("parent")
            if parent is not None:
                path = "storyboard." + sid + ".elements." + eid + ".parent"
                if not isinstance(parent, str):
                    error(path, "Parent must be an element ID string")
                    continue
                if parent == eid or parent not in elements or elements[parent].get("kind") not in ("card", "group"):
                    error(path, "Parent must name another explicit card/group on the same slide")
                elif eid in boxes and parent in boxes:
                    child, outer = boxes[eid], boxes[parent]
                    if (child[0] < outer[0] - 1e-8 or child[1] < outer[1] - 1e-8 or
                            child[0] + child[2] > outer[0] + outer[2] + 1e-8 or
                            child[1] + child[3] > outer[1] + outer[3] + 1e-8):
                        error(path, "Child must fit inside its explicitly declared parent")
                seen, cursor = {eid}, parent
                while isinstance(cursor, str) and cursor in elements:
                    if cursor in seen:
                        error(path, "Parent relationship cycle")
                        break
                    seen.add(cursor)
                    cursor = elements[cursor].get("parent")
            if element.get("kind") != "card" or eid not in boxes:
                continue
            for other, peer in elements.items():
                if (other <= eid or peer.get("kind") != "card" or other not in boxes or
                        peer.get("parent") != parent):
                    continue
                first, second = boxes[eid], boxes[other]
                if (min(first[0] + first[2], second[0] + second[2]) - max(first[0], second[0]) > 1e-8 and
                        min(first[1] + first[3], second[1] + second[3]) - max(first[1], second[1]) > 1e-8):
                    error("storyboard." + sid, f"Peer cards overlap: {eid}, {other}")
    return {"status": "invalid" if errors else "draft", "quality_status": "pending",
            "schema_version": 1, "deck_id": identity, "revision": revision,
            "structure_valid": not errors, "ready_for_nonchart_build": not errors,
            "ready_for_all_requested_build": not errors and not blocked,
            "errors": errors, "warnings": warnings, "blocked_operations": blocked,
            "slide_count": len(outline), "evidence_authenticated": False,
            "not_verified": ["User confirmation authenticity and factual truth", "Actual PPTX native object inventory",
                             "Font availability, text overflow, rendering and target PowerPoint behavior",
                             "Independent visual/content QA and native macro execution",
                             "Revision history: callers must advance revision after substantive changes"]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--report", type=Path, help="Fresh JSON evidence file; never overwrite input or an existing report")
    args = parser.parse_args(argv)
    try:
        source = args.contract.resolve(strict=True)
        if args.report and (args.report.resolve() == source or args.report.exists()):
            raise ValueError("Choose a fresh report path distinct from the contract")
        data = source.read_bytes()
        if len(data) > 4 * 1024 * 1024:
            raise ValueError("Deck contract exceeds the 4 MiB inspection budget")
        contract = json.loads(data, parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Non-finite JSON value: " + value)))
        result = validate_deck(contract, base_dir=source.parent)
        result["source_sha256"] = hashlib.sha256(data).hexdigest()
        result["source_unchanged"] = source.read_bytes() == data
        if not result["source_unchanged"]:
            raise ValueError("Contract changed during validation")
        if args.report:
            with args.report.open("x", encoding="utf-8") as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["structure_valid"] else 1
    except (OSError, ValueError, RecursionError) as exc:
        print(json.dumps({"status": "invalid", "quality_status": "pending", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
