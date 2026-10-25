"""Read-only OOXML feature evidence and explicit new-chart decisions.

This importable helper neither opens Excel nor executes/extracts VBA source. A
successful preservation comparison covers the listed package features only, not
all workbook semantics, signature validity, calculation or visual fidelity.
"""
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
import posixpath
import xml.etree.ElementTree as ET
import zipfile


S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
C = "http://schemas.openxmlformats.org/package/2006/content-types"
MAIN_TYPES = {
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
    ".xlsm": "application/vnd.ms-excel.sheet.macroEnabled.main+xml",
    ".xltx": "application/vnd.openxmlformats-officedocument.spreadsheetml.template.main+xml",
    ".xltm": "application/vnd.ms-excel.template.macroEnabled.main+xml",
}


class ChartConfirmationRequired(ValueError):
    """The new-chart branch is still pending an actual user decision."""


class MacroConfirmationRequired(ValueError):
    """This particular macro operation has not been approved."""


def chart_decision(answer=None, *, source=None, scope="new_charts") -> dict:
    """Record, not manufacture, a user answer: yes / no / pending.

    ``source`` identifies the actual conversation/request evidence, not a claim
    that this helper authenticated it. Tests may explicitly label it simulated.
    A prior explicit user request to create charts can be reused for that scope.
    """
    answer = "pending" if answer is None else answer
    if not isinstance(answer, str) or answer not in ("yes", "no", "pending"):
        raise ValueError("Chart decision must be yes, no or pending")
    if not isinstance(scope, str) or not scope.strip() or len(scope) > 1000:
        raise ValueError("Chart decision requires a nonempty bounded scope")
    if source is not None and (not isinstance(source, str) or not source.strip()):
        raise ValueError("Chart source must identify conversation/request evidence")
    if answer != "pending" and not source:
        raise ValueError("An explicit yes/no needs its actual user-decision source")
    return {"kind": "chart", "decision": answer, "source": source, "scope": scope,
            "evidence_authenticated": False}


def require_chart_confirmation(decision=None, *, creating_new_charts=True,
                               scope="new_charts") -> bool:
    """Before mutation: True permits new charts, False means skip them.

    Pending raises so callers can ask the user while continuing unrelated work.
    Existing-chart preservation/unrelated edits do not require a fresh answer.
    This contract cannot turn an invented JSON record into a real user reply.
    """
    if not isinstance(creating_new_charts, bool):
        raise ValueError("creating_new_charts must be a boolean")
    if not creating_new_charts:
        return True
    if decision is None:
        raise ChartConfirmationRequired("New charts pending user confirmation")
    if not isinstance(decision, dict):
        raise ValueError("Use chart_decision to record the user answer")
    if decision.get("kind") != "chart":
        raise ChartConfirmationRequired("A separate chart decision is required")
    checked = chart_decision(decision.get("decision"), source=decision.get("source"),
                             scope=decision.get("scope", ""))
    if checked["scope"] != scope:
        raise ChartConfirmationRequired("Chart decision belongs to another scope")
    if checked["decision"] == "pending":
        raise ChartConfirmationRequired("New charts pending user confirmation")
    return checked["decision"] == "yes"


def macro_decision(answer=None, *, source=None, scope="macro_work",
                   requested_modes=("preserve",)) -> dict:
    """Record separate macro approval, restricted to selected modes and scope.

    Merely preserving/inventorying opaque bytes does not approve macro execution.
    ``invoke`` means a selected, reviewed procedure, never arbitrary macros.
    """
    record = chart_decision(answer, source=source, scope=scope)
    record["kind"] = "macro"
    if isinstance(requested_modes, str) or not isinstance(requested_modes, (list, tuple)):
        raise ValueError("requested_modes must list preserve/create/modify/invoke")
    if not requested_modes or any(mode not in ("preserve", "create", "modify", "invoke")
                                  for mode in requested_modes):
        raise ValueError("Unknown/empty macro operation modes")
    record["requested_modes"] = sorted(set(requested_modes))
    return record


def require_macro_confirmation(decision=None, *, mode, scope="macro_work") -> bool:
    """Gate a macro operation without opening an app or executing any code."""
    if mode not in ("preserve", "create", "modify", "invoke"):
        raise ValueError("Unknown macro operation mode")
    if mode == "preserve":
        return True
    if decision is None:
        raise MacroConfirmationRequired("Selected macro operation pending user approval")
    if not isinstance(decision, dict):
        raise ValueError("Use macro_decision to record selected user approval")
    if decision.get("kind") != "macro":
        raise MacroConfirmationRequired("A separate macro decision is required")
    checked = macro_decision(decision.get("decision"), source=decision.get("source"),
                             scope=decision.get("scope", ""),
                             requested_modes=decision.get("requested_modes", ()))
    if checked["scope"] != scope or mode not in checked["requested_modes"]:
        raise MacroConfirmationRequired("Macro approval does not cover this scope/mode")
    if checked["decision"] == "pending":
        raise MacroConfirmationRequired("Selected macro operation pending user approval")
    return checked["decision"] == "yes"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _xml(data: bytes, name: str):
    if len(data) > 20 * 1024 * 1024:
        raise ValueError(f"Workbook XML budget exceeded: {name}")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError(f"DTD/entity input needs a separate reviewed route: {name}")
    return ET.fromstring(data)


def _rel_source(name: str) -> str:
    if name == "_rels/.rels":
        return ""
    path = PurePosixPath(name)
    return str(path.parent.parent / path.name[:-5])


def _resolve(source: str, target: str) -> str:
    # OPC targets are URI paths; reject ambiguous filesystem-like spellings.
    from urllib.parse import unquote, urlsplit
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or "\\" in target:
        raise ValueError(f"Invalid internal relationship target: {target}")
    decoded = unquote(parsed.path)
    result = posixpath.normpath(posixpath.join(posixpath.dirname(source), decoded)
                               if not decoded.startswith("/") else decoded[1:])
    if result in ("", ".", "..") or result.startswith("../") or "\\" in result:
        raise ValueError(f"Relationship leaves the package: {target}")
    return result


def _protected(name: str) -> bool:
    lower = name.lower()
    return (lower.startswith(("xl/vba", "xl/activex/", "xl/ctrlprops/", "customui/",
                              "xl/macrosheets/", "xl/dialogsheets/", "_xmlsignatures/",
                              "xl/embeddings/")) or lower.endswith(".vml"))


def _protected_type(value: str) -> bool:
    lower = value.lower()
    return any(token in lower for token in ("vbaproject", "activex", "controlproperties",
                                             "ctrlprop", "vmldrawing", "macrosheet",
                                             "dialogsheet", "oleobject", "digital-signature",
                                             "/ui/extensibility"))


def _canonical(node, rels: dict) -> list:
    attrs = dict(node.attrib)
    for key, value in list(attrs.items()):
        if key.startswith("{" + R + "}"):
            attrs[key] = rels.get(value, "unresolved:" + value)
    return [node.tag, sorted(attrs.items()), (node.text or "").strip(),
            [_canonical(child, rels) for child in node]]


def inspect_workbook(path) -> dict:
    """Inventory a bounded xlsx/xlsm/xltx/xltm package without loading it.

    VBA binaries stay opaque; no macros, links, formulas or XLM code are run.
    Unsupported/mismatched package semantics are errors, not an execution pass.
    """
    path = Path(path).resolve(strict=True)
    if path.suffix.lower() not in MAIN_TYPES:
        raise ValueError("Expected .xlsx, .xlsm, .xltx or .xltm")
    before = _file_sha(path)
    errors, relationships, roots, types = [], [], {}, {}
    with zipfile.ZipFile(path) as package:
        members = package.infolist()
        names = [info.filename for info in members]
        if (len(members) > 20000 or sum(info.file_size for info in members) > 500 * 1024 * 1024
                or any(info.file_size > 100 * 1024 * 1024 for info in members)):
            raise ValueError("Workbook package inspection budget exceeded")
        if len(set(names)) != len(names):
            raise ValueError("Duplicate workbook package members")
        if any(name.startswith("/") or "\\" in name or
               posixpath.normpath(name).startswith("../") or
               posixpath.normpath(name) != name.rstrip("/") for name in names):
            raise ValueError("Ambiguous workbook package member path")
        if "[Content_Types].xml" not in names or "xl/workbook.xml" not in names:
            raise ValueError("Missing workbook package core parts")
        hashes = {}
        for info in members:
            if info.is_dir():
                continue
            data = package.read(info)
            hashes[info.filename] = _sha(data)
            if info.filename.endswith((".xml", ".rels")):
                roots[info.filename] = _xml(data, info.filename)
        defaults, overrides = {}, {}
        for item in roots["[Content_Types].xml"]:
            if item.tag == "{" + C + "}Default":
                key = item.get("Extension", "").lower()
                if key in defaults:
                    errors.append("Duplicate content-type default: " + key)
                defaults[key] = item.get("ContentType", "")
            elif item.tag == "{" + C + "}Override":
                key = item.get("PartName", "").lstrip("/")
                if key in overrides:
                    errors.append("Duplicate content-type override: " + key)
                overrides[key] = item.get("ContentType", "")
        errors.extend("Content-type target missing: " + name for name in overrides if name not in hashes)
        for name in hashes:
            types[name] = overrides.get(name, defaults.get(name.rsplit(".", 1)[-1].lower(), ""))
        main_type = types["xl/workbook.xml"]
        if main_type != MAIN_TYPES[path.suffix.lower()]:
            errors.append("Extension/workbook content type mismatch")
        by_source = {}
        for name, root in roots.items():
            if not name.endswith(".rels"):
                continue
            source = _rel_source(name)
            if source and source not in hashes:
                errors.append("Relationship source missing: " + source)
            ids = set()
            for item in root.findall("{" + P + "}Relationship"):
                rid, kind, target = item.get("Id", ""), item.get("Type", ""), item.get("Target", "")
                mode = item.get("TargetMode", "Internal")
                if not rid or rid in ids or not kind or not target:
                    errors.append("Invalid/duplicate relationship: " + name)
                ids.add(rid)
                resolved = target if mode == "External" else _resolve(source, target)
                if mode not in ("Internal", "External"):
                    errors.append("Unknown relationship mode: " + name)
                if mode != "External" and resolved not in hashes:
                    errors.append("Missing relationship target: " + resolved)
                record = {"source": source, "type": kind, "target": resolved, "mode": mode}
                relationships.append(record)
                by_source.setdefault(source, {})[rid] = resolved
        # OPC part names are not fixed. Seed by content/relationship semantics
        # as well as conventional paths (e.g. a VBA project may be macros.bin).
        protected = {name for name in hashes if _protected(name) or _protected_type(types[name])}
        protected |= {r["target"] for r in relationships
                      if _protected_type(r["type"]) and r["mode"] == "Internal"
                      and r["target"] in hashes}
        # Preserve supporting images/binaries and all outbound relationship
        # dependencies of VBA/control/customUI/XLM parts, not just the VBA bin.
        while True:
            expanded = protected | {r["target"] for r in relationships
                                    if r["source"] in protected and r["mode"] == "Internal"
                                    and r["target"] in hashes}
            expanded |= {name for name in roots if name.endswith(".rels")
                         and _rel_source(name) in expanded}
            if expanded == protected:
                break
            protected = expanded
        protected_rels = sorted((r for r in relationships
                                 if r["source"] in protected or r["target"] in protected),
                                key=lambda r: (r["source"], r["type"], r["target"], r["mode"]))
        # Relationship ID renumbering is harmless; compare resolved bindings.
        code_names, bindings, macro_bindings = {}, {}, {}
        binding_tags = {"{" + S + "}" + tag for tag in
                        ("controls", "legacyDrawing", "legacyDrawingHF", "oleObjects")}
        for name, root in roots.items():
            if name == "xl/workbook.xml" or name.startswith("xl/worksheets/") and name.endswith(".xml"):
                code_names[name] = [node.get("codeName") for node in root
                                    if node.tag in ("{" + S + "}workbookPr", "{" + S + "}sheetPr")
                                    and "codeName" in node.attrib]
                selected = [_canonical(node, by_source.get(name, {})) for node in root
                            if node.tag in binding_tags]
                if selected:
                    bindings[name] = selected
            selected_macros = []
            if name == "xl/workbook.xml":
                for node in root.iter("{" + S + "}definedName"):
                    label = node.get("name", "").lower().removeprefix("_xlnm.")
                    flags = {key.rsplit("}", 1)[-1].lower(): value for key, value in node.attrib.items()}
                    if (label in ("auto_open", "auto_close", "auto_activate", "auto_deactivate") or
                            any(flags.get(key, "0").lower() not in ("0", "false", "off")
                                for key in ("macro", "vbprocedure", "xlm"))):
                        selected_macros.append(["definedName", sorted(node.attrib.items()),
                                                "".join(node.itertext()).strip()])
            if name.startswith("xl/drawings/") or "drawing" in types.get(name, "").lower():
                for node in root.iter():
                    macros = sorted((key, value) for key, value in node.attrib.items()
                                    if key.rsplit("}", 1)[-1].lower() == "macro")
                    if macros:
                        identity = next((child for child in node.iter()
                                         if child.tag.rsplit("}", 1)[-1] == "cNvPr"), None)
                        selected_macros.append(["drawing", node.tag,
                                                identity.get("id") if identity is not None else None,
                                                identity.get("name") if identity is not None else None,
                                                macros])
            if selected_macros:
                macro_bindings[name] = selected_macros
        vba = sorted({name for name in hashes if
                      ("vbaproject" in types[name].lower() and "signature" not in types[name].lower())
                      or name.lower().endswith("vbaproject.bin")} |
                     {r["target"] for r in relationships if r["type"].lower().endswith("/vbaproject")
                      and r["mode"] == "Internal" and r["target"] in hashes})
        xlm = sorted(name for name in protected if "macrosheet" in types.get(name, "").lower()
                     or name.lower().startswith("xl/macrosheets/"))
        if (vba or xlm) and path.suffix.lower() not in (".xlsm", ".xltm"):
            errors.append("VBA/XLM macro content in a non-macro workbook type")
        for part in vba:
            if not any(r["target"] == part and r["type"].lower().endswith("/vbaproject")
                       for r in relationships):
                errors.append("VBA project lacks its package relationship: " + part)
            if "vbaproject" not in types[part].lower():
                errors.append("VBA project content type missing: " + part)
        chart_namespaces = ("http://schemas.openxmlformats.org/drawingml/2006/chart",
                            "http://schemas.microsoft.com/office/drawing/2014/chartex")
        charts = sorted(name for name, root in roots.items() if root.tag in
                        {"{" + namespace + "}chartSpace" for namespace in chart_namespaces})
        chart_auxiliary = sorted(name for name in hashes if name.startswith("xl/charts/")
                                 and name not in charts and "/_rels/" not in name)
        result = {"status": "inspected" if not errors else "failed", "quality_status": "pending",
                  "path": str(path), "extension": path.suffix.lower(), "source_sha256": before,
                  "workbook_content_type": main_type, "errors": errors,
                  "native_charts": [{"part": name, "sha256": hashes[name], "content_type": types[name]}
                                    for name in charts], "native_chart_count": len(charts),
                  "chart_auxiliary_parts": {name: hashes[name] for name in chart_auxiliary},
                  "vba_projects": vba, "xlm_macro_parts": xlm,
                  "macro_related_parts": {name: hashes[name] for name in sorted(protected)},
                  "macro_relationships": protected_rels,
                  "macro_content_types": {name: types[name] for name in sorted(protected) if name in types},
                  "code_names": code_names, "control_bindings": bindings, "macro_bindings": macro_bindings,
                  "external_relationships": [r for r in relationships if r["mode"] == "External"],
                  "macro_execution_status": "not_run", "vba_source_review_status": "opaque_binary_not_extracted",
                  "limits": ["Package inventory is not Excel execution or visual/calculation QA",
                             "VBA/signature bytes do not prove source review, signature validity or trust",
                             "Charts/cells/shapes outside the listed protected graph need separate verification"]}
    after = _file_sha(path)
    if after != before:
        raise ValueError("Input workbook changed during read-only inspection")
    result["source_unchanged"] = True
    return result


def verify_macro_preservation(source, output) -> dict:
    """Compare macro-related parts/relationships/types/bindings, read-only.

    Exact opaque part bytes are intentional. A changed signed project must be
    reviewed/re-signed in native Excel, not passed off as unchanged preservation.
    """
    if Path(source).resolve() == Path(output).resolve():
        raise ValueError("Preservation needs a distinct source and working-copy output")
    baseline, modified = inspect_workbook(source), inspect_workbook(output)
    if (_file_sha(Path(source)) != baseline["source_sha256"] or
            _file_sha(Path(output)) != modified["source_sha256"]):
        raise ValueError("A workbook changed during preservation comparison")
    errors = ["source: " + item for item in baseline["errors"]]
    errors += ["output: " + item for item in modified["errors"]]
    if baseline["extension"] != modified["extension"]:
        errors.append("Workbook extension changed; explicit native conversion verification required")
    for key in ("workbook_content_type", "macro_related_parts", "macro_relationships",
                "macro_content_types", "code_names", "control_bindings", "macro_bindings"):
        if baseline[key] != modified[key]:
            errors.append("Protected feature changed: " + key)
    return {"status": "preserved" if not errors else "failed", "preservation_passed": not errors,
            "quality_status": "pending", "macro_execution_status": "not_run",
            "source_sha256": baseline["source_sha256"], "output_sha256": modified["source_sha256"],
            "source_unchanged": baseline["source_unchanged"], "errors": errors,
            "scope": ["exact macro/control/XLM/signature graph part bytes", "resolved macro relationships",
                      "macro content types", "workbook/worksheet codeNames", "worksheet control bindings",
                      "explicit drawing macro attributes and macro/XLM defined-name bindings"],
            "baseline": baseline, "output": modified,
            "limits": baseline["limits"] + ["No Excel recalculation, execution, macro compilation or page QA was performed"]}
