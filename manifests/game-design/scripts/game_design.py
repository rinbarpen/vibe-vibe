#!/usr/bin/env python3
"""Read-only engine discovery and design-contract checks. Python 3.10+, stdlib only."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

HOME = Path(__file__).resolve().parents[1]
FIELDS = ("id", "name", "category", "fit", "version", "scene", "code", "assets",
          "space", "input", "save_network", "tests", "build", "pitfalls")
LABELS = ("版本与工具链", "场景与实体", "脚本与数值", "资产管线", "坐标与尺度",
          "输入与 UI", "存档与联网", "测试与证据", "构建与导出", "约束与风险")
ADAPT = ("version", "scene", "code", "assets", "space", "input", "save_network",
         "tests", "build", "pitfalls")


def load_catalog():
    catalog = json.loads((HOME / "references/engines.json").read_text(encoding="utf-8"))
    if type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1:
        raise ValueError("catalog schema_version must be 1")
    if not isinstance(catalog.get("engines"), list) or not catalog["engines"]:
        raise ValueError("catalog engines must be a non-empty list")
    seen = set()
    for engine in catalog["engines"]:
        if not isinstance(engine, dict):
            raise ValueError("engine must be an object")
        for key in FIELDS:
            if not isinstance(engine.get(key), str) or not engine[key].strip():
                raise ValueError(f"engine missing {key}")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", engine["id"]) or engine["id"] in seen:
            raise ValueError("invalid or duplicate engine id")
        seen.add(engine["id"])
        if engine.get("support") != "design-adapter" or engine.get("runtime_validation") != "not_run":
            raise ValueError("catalog describes adapters, not runtime pass claims")
        if not isinstance(engine.get("sources"), list) or not engine["sources"] or any(
                not isinstance(url, str) or not url.startswith("https://") for url in engine["sources"]):
            raise ValueError("official source links required")
        detect = engine.get("detection")
        if not isinstance(detect, dict) or not detect or detect.keys() - {
                "all", "files", "text", "json_keys", "dependencies"}:
            raise ValueError("invalid detection rules")
        for kind, values in detect.items():
            if not isinstance(values, list) or not values:
                raise ValueError("detection values must be non-empty lists")
            for value in values:
                if kind in ("text", "json_keys"):
                    if not isinstance(value, list) or len(value) != 2:
                        raise ValueError("invalid structured detection rule")
                    pattern, criterion = value
                    if kind == "text" and (not isinstance(criterion, str) or not criterion):
                        raise ValueError("text criterion required")
                    if kind == "json_keys" and (not isinstance(criterion, list) or not criterion
                            or any(not isinstance(k, str) or not k for k in criterion)):
                        raise ValueError("JSON keys required")
                else:
                    pattern = value
                if (not isinstance(pattern, str) or not pattern or ".." in Path(pattern).parts
                        or Path(pattern).is_absolute() or "**" in pattern or "\\" in pattern
                        or len(Path(pattern).parts) > 3):
                    raise ValueError("detection must stay in bounded project paths")
    return catalog


def safe_matches(project, pattern):
    # Never inspect symlinks or recursively scan large asset/dependency trees.
    matches = []
    for path in project.glob(pattern):
        if path.is_symlink():
            continue
        if any((project / parent).is_symlink() for parent in path.relative_to(project).parents):
            continue
        matches.append(path)
    return sorted(matches)


def read_small(path):
    if not path.is_file() or path.stat().st_size > 2_000_000:
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def detect(project, catalog):
    if not project.is_dir():
        raise ValueError(f"project directory missing: {project}")
    hits, warnings = [], []
    package = {}
    package_path = project / "package.json"
    if package_path in safe_matches(project, "package.json"):
        try:
            package = json.loads(read_small(package_path))
            if not isinstance(package, dict):
                raise ValueError("expected JSON object")
        except (ValueError, OSError) as exc:
            warnings.append(f"package.json: {exc}")
    deps = set()
    for group in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        if isinstance(package.get(group), dict):
            deps.update(package[group])
    for engine in catalog["engines"]:
        rules, evidence = engine["detection"], []
        if "all" in rules and all(safe_matches(project, p) for p in rules["all"]):
            evidence.extend(rules["all"])
        for pattern in rules.get("files", []):
            evidence.extend(str(p.relative_to(project)) for p in safe_matches(project, pattern) if p.is_file())
        for dep in rules.get("dependencies", []):
            if dep in deps:
                evidence.append(f"package.json dependency: {dep}")
        for pattern, text in rules.get("text", []):
            for path in safe_matches(project, pattern):
                source = read_small(path)
                matched = text in source
                if text == "BEVY_DEPENDENCY":
                    matched = bool(re.search(r"(?m)^\s*(?:bevy\s*=|\[(?:workspace\.)?dependencies\.bevy\])", source))
                if matched:
                    evidence.append(str(path.relative_to(project)))
        for pattern, keys in rules.get("json_keys", []):
            for path in safe_matches(project, pattern):
                try:
                    obj = json.loads(read_small(path))
                    if isinstance(obj, dict) and all(k in obj for k in keys):
                        evidence.append(str(path.relative_to(project)))
                except (ValueError, OSError):
                    continue  # Most root JSON files are not engine project files.
        if evidence:
            hits.append({"engine": engine["id"], "evidence": sorted(set(evidence))})
    status = "detected" if len(hits) == 1 else "ambiguous" if hits else "unrecognized"
    return {"status": status, "candidates": hits, "warnings": warnings,
            "runtime_validation": "not_run", "note": "Root-only hints; confirm engine/version, or inspect an explicit subproject."}


def adapter_markdown(engine):
    lines = [f"# {engine['name']} 适配器", "", "> 由 engines.json 生成；修改数据后运行 render-adapters。", "",
             engine["fit"], "", "状态：设计/工程映射已登记；运行时验证 **not_run**。", "",
             "识别规则（仅线索，不选择/升级引擎）：", "", "```json",
             json.dumps(engine["detection"], ensure_ascii=False, indent=2), "```", ""]
    for key, label in zip(ADAPT, LABELS):
        lines += [f"## {label}", "", engine[key], ""]
    lines += ["## 官方资料", ""] + [f"- [官方文档]({u})" for u in engine["sources"]]
    return "\n".join(lines) + "\n"


def render_adapters(catalog, check=False):
    expected = {}
    rows = ["# 引擎覆盖矩阵", "", "> 自动生成，事实源为 [engines.json](engines.json)。覆盖表示设计适配，不表示构建通过。", "",
            "| ID | 引擎/框架 | 类别 | 适用与边界 |", "|---|---|---|---|"]
    for engine in catalog["engines"]:
        expected[HOME / f"references/adapters/{engine['id']}.md"] = adapter_markdown(engine)
        rows.append(f"| `{engine['id']}` | [{engine['name']}](adapters/{engine['id']}.md) | {engine['category']} | {engine['fit']} |")
    expected[HOME / "references/engine-matrix.md"] = "\n".join(rows) + "\n"
    drift = []
    for path, content in expected.items():
        if not path.is_file() or path.read_bytes() != content.encode():
            drift.append(str(path.relative_to(HOME)))
            if not check:
                atomic_write(path, content.encode())
    extras = set((HOME / "references/adapters").glob("*.md")) - set(expected)
    if extras:
        raise ValueError("stale adapter files; review/remove explicitly: " + ", ".join(str(p) for p in sorted(extras)))
    return {"status": "drift" if check and drift else "ok", "engines": len(catalog["engines"]), "changed": drift}


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(data)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def check_project(project, catalog):
    state = json.loads((project / ".game-design/state/project.json").read_text(encoding="utf-8"))
    if not isinstance(state, dict) or type(state.get("schema_version")) is not int or state["schema_version"] != 1:
        raise ValueError("project state schema_version must be 1")
    ids = {e["id"] for e in catalog["engines"]}
    if state.get("engine") is not None and state["engine"] not in ids:
        raise ValueError("unknown engine; add a complete adapter before selecting it")
    if state.get("mode") not in ("design-only", "implementation"):
        raise ValueError("mode must be design-only or implementation")
    if not isinstance(state.get("engine_version"), str):
        raise ValueError("engine_version must be a string")
    if not isinstance(state.get("targets"), list) or any(not isinstance(x, str) or not x.strip() for x in state["targets"]):
        raise ValueError("targets must be a list of non-empty platform strings")
    if "genres" in state:
        from production_tools import load_data
        genres, _, _ = load_data()
        known = {g['id'] for g in genres['genres']}
        chosen = state['genres']
        if (not isinstance(chosen, list) or any(not isinstance(x, str) or x not in known for x in chosen)
                or len(set(chosen)) != len(chosen)):
            raise ValueError('genres must be a unique list of registered genre IDs')
    for field, allowed in (
            ('dimension', ('2d', '2.5d', '3d', 'mixed')),
            ('multiplayer', ('offline', 'local', 'online', 'hybrid'))):
        if field in state and state[field] is not None and state[field] not in allowed:
            raise ValueError('invalid '+field)
    if 'content_pipeline' in state and (not isinstance(state['content_pipeline'], list)
            or any(x not in ('2d-art','3d-dcc','procedural','asset-library') for x in state['content_pipeline'])):
        raise ValueError('invalid content_pipeline')
    if not isinstance(state.get("budgets"), dict):
        raise ValueError("budgets must be an object")
    for key in ("frame_time_ms", "memory_mb", "download_mb"):
        value = state.get("budgets", {}).get(key)
        if value is not None and (type(value) not in (float, int) or not 0 < value < float("inf")):
            raise ValueError(f"budget {key} must be positive or null")
    result = detect(project, catalog)
    pending = []
    if not state["engine"]:
        pending.append("engine decision")
    if not state["engine_version"].strip():
        pending.append("engine version")
    if not state["targets"]:
        pending.append("target platforms")
    for field in ('genres', 'dimension', 'multiplayer', 'content_pipeline'):
        if field in state and not state[field]:
            pending.append('project profile: '+field)
    for key in ("frame_time_ms", "memory_mb", "download_mb"):
        if state["budgets"].get(key) is None:
            pending.append(f"budget: {key}")
    if result["candidates"] and state["engine"] not in (None, *(x["engine"] for x in result["candidates"])):
        raise ValueError("selected engine conflicts with detected project; record migration decision first")
    if result["status"] == "ambiguous":
        pending.append("multiple runtimes: choose an explicit subproject and record primary engine")
    return {"status": "pending" if pending else "configured", "pending": pending,
            "detection": result, "runtime_validation": "not_run",
            "note": "Configuration check only; does not approve design, playability, build, or release."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("check-catalog")
    p = sub.add_parser("adapter")
    p.add_argument("--engine", required=True)
    for name in ("detect", "check-project"):
        p = sub.add_parser(name)
        p.add_argument("--project", default=".")
    p = sub.add_parser("render-adapters")
    p.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        catalog = load_catalog()
        rc = 0
        if args.command == "list":
            result = [{k: e[k] for k in ("id", "name", "category", "support")} for e in catalog["engines"]]
        elif args.command == "adapter":
            result = next((e for e in catalog["engines"] if e["id"] == args.engine), None)
            if result is None:
                raise ValueError(f"unknown engine: {args.engine}")
        elif args.command == "check-catalog":
            result = {"status": "ok", "engines": len(catalog["engines"])}
        elif args.command == "render-adapters":
            result = render_adapters(catalog, args.check)
            rc = int(result["status"] == "drift")
        elif args.command == "detect":
            result = detect(Path(args.project).resolve(), catalog)
            rc = int(result["status"] != "detected")
        else:
            result = check_project(Path(args.project).resolve(), catalog)
            rc = int(result["status"] == "pending")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return rc
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
