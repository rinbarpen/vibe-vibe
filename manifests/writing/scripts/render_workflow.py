#!/usr/bin/env python3
"""Render a validated manifest workflow JSON as a deterministic, standalone SVG.

Copy this file to a manifest's scripts/render_workflow.py without dependencies.
Usage: python3 render_workflow.py --source workflow.json --output workflow.svg [--check]
"""
from __future__ import annotations

import argparse
from collections import deque
import html
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata

LANES = {"ai": 0, "check": 1, "terminal": 1, "human": 2}
COLORS = {
    "ai": ("#eff6ff", "#2563eb", "AI 执行"),
    "check": ("#ecfdf5", "#047857", "AI 判定 / 校验"),
    "human": ("#fff7ed", "#c2410c", "人工决策"),
    "terminal": ("#f1f5f9", "#475569", "起点 / 交付"),
}
ID = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*\Z")


def _text(value, where, limit):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: expected a non-empty string")
    if len(value) > limit:
        raise ValueError(f"{where}: exceeds {limit} characters")
    if any(not (ord(c) in (9, 10, 13) or 0x20 <= ord(c) <= 0xD7FF
                or 0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF)
           for c in value):
        raise ValueError(f"{where}: contains an invalid XML character")
    return value


def _keys(value, required, where, optional=()):
    if not isinstance(value, dict):
        raise ValueError(f"{where}: expected an object")
    missing, extra = set(required) - value.keys(), value.keys() - set(required) - set(optional)
    if missing or extra:
        raise ValueError(f"{where}: missing keys {sorted(missing)}; unknown keys {sorted(extra)}")


def _reachable(start, adjacency):
    seen, pending = {start}, deque([start])
    while pending:
        for target in adjacency[pending.popleft()]:
            if target not in seen:
                seen.add(target)
                pending.append(target)
    return seen


def _validate(workflow):
    _keys(workflow, ("schema_version", "title", "description", "nodes", "edges"), "workflow")
    if type(workflow["schema_version"]) is not int or workflow["schema_version"] != 1:
        raise ValueError("schema_version: expected integer 1")
    _text(workflow["title"], "title", 120)
    _text(workflow["description"], "description", 500)
    nodes, edges = workflow["nodes"], workflow["edges"]
    if not isinstance(nodes, list) or not 2 <= len(nodes) <= 80:
        raise ValueError("nodes: expected 2 to 80 nodes")
    if not isinstance(edges, list) or not 1 <= len(edges) <= 160:
        raise ValueError("edges: expected 1 to 160 edges")
    by_id, occupied = {}, set()
    for i, node in enumerate(nodes):
        where = f"nodes[{i}]"
        _keys(node, ("id", "label", "kind", "row", "detail"), where, ("trigger", "resume"))
        identifier = _text(node["id"], f"{where}.id", 80)
        if not ID.fullmatch(identifier):
            raise ValueError(f"{where}.id: expected an ASCII identifier")
        if identifier in by_id:
            raise ValueError(f"{where}.id: duplicate node {identifier}")
        if not isinstance(node["kind"], str) or node["kind"] not in LANES:
            raise ValueError(f"{where}.kind: expected ai, check, human, or terminal")
        if type(node["row"]) is not int or node["row"] < 0:
            raise ValueError(f"{where}.row: expected a non-negative integer")
        cell = (LANES[node["kind"]], node["row"])
        if cell in occupied:
            raise ValueError(f"{where}: overlapping lane/row {cell}")
        occupied.add(cell)
        _text(node["label"], f"{where}.label", 120)
        _text(node["detail"], f"{where}.detail", 500)
        if node["kind"] == "human":
            for field in ("trigger", "resume"):
                _text(node.get(field), f"{where}.{field}", 250)
        elif "trigger" in node or "resume" in node:
            raise ValueError(f"{where}: trigger/resume apply only to human nodes")
        by_id[identifier] = node
    forward = {identifier: [] for identifier in by_id}
    reverse = {identifier: [] for identifier in by_id}
    seen_edges = set()
    for i, edge in enumerate(edges):
        where = f"edges[{i}]"
        _keys(edge, ("from", "to", "label", "kind"), where)
        for field in ("from", "to"):
            _text(edge[field], f"{where}.{field}", 80)
            if edge[field] not in by_id:
                raise ValueError(f"{where}.{field}: unknown node {edge[field]}")
        _text(edge["label"], f"{where}.label", 80)
        if not isinstance(edge["kind"], str) or edge["kind"] not in ("normal", "rework"):
            raise ValueError(f"{where}.kind: expected normal or rework")
        identity = (edge["from"], edge["to"], edge["kind"], edge["label"])
        if identity in seen_edges:
            raise ValueError(f"{where}: duplicate edge")
        seen_edges.add(identity)
        forward[edge["from"]].append(edge["to"])
        reverse[edge["to"]].append(edge["from"])
    starts = [identifier for identifier in by_id if not reverse[identifier]]
    ends = [identifier for identifier in by_id if not forward[identifier]]
    if len(starts) != 1 or len(ends) != 1 or starts == ends:
        raise ValueError("workflow: expected one distinct start (no incoming edges) and end (no outgoing edges)")
    if any(by_id[identifier]["kind"] != "terminal" for identifier in starts + ends):
        raise ValueError("workflow: start and end must have kind terminal")
    if set(by_id) != _reachable(starts[0], forward):
        raise ValueError("workflow: every node must be reachable from the start")
    if set(by_id) != _reachable(ends[0], reverse):
        raise ValueError("workflow: every node must be able to reach the end")
    return by_id


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON: duplicate object key {key}")
        result[key] = value
    return result


def load_workflow(path):
    """Load UTF-8 JSON and validate its schema, layout, and graph."""
    with Path(path).open(encoding="utf-8") as source:
        workflow = json.load(source, object_pairs_hook=_unique_object)
    _validate(workflow)
    return workflow


def _width(text):
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


def _wrap(text, width):
    # Character-level wrapping handles CJK and long unbroken identifiers alike.
    lines, line, used = [], "", 0
    for char in " ".join(text.split()):
        size = _width(char)
        if used + size > width and line:
            lines.append(line.rstrip())
            line, used = "", 0
        if char != " " or line:
            line += char
            used += size
    if line:
        lines.append(line.rstrip())
    return lines


def render(workflow):
    """Return deterministic accessible SVG text; no filesystem writes."""
    by_id = _validate(workflow)
    nodes = sorted(by_id.values(), key=lambda node: (node["row"], LANES[node["kind"]], node["id"]))
    edges = sorted(workflow["edges"], key=lambda edge: (edge["kind"], edge["from"], edge["to"], edge["label"]))
    esc = html.escape
    parts = []
    add = parts.append
    font = "system-ui, -apple-system, 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif"
    card_width, lane_pitch, left, gap = 360, 410, 40, 86
    title_lines = _wrap(workflow["title"], 76)
    desc_lines = _wrap(workflow["description"], 138)
    header_bottom = 36 + len(title_lines) * 32 + len(desc_lines) * 20 + 40
    content_top = header_bottom + 50
    row_heights, text_lines = {}, {}
    for node in nodes:
        label = _wrap(node["label"], 33)
        detail = _wrap(node["detail"], 43)
        extra = []
        if node["kind"] == "human":
            extra = _wrap("介入条件：" + node["trigger"], 43) + _wrap("恢复执行：" + node["resume"], 43)
        height = 50 + len(label) * 24 + (len(detail) + len(extra)) * 20 + (14 if extra else 0)
        text_lines[node["id"]] = (label, detail, extra)
        row_heights[node["row"]] = max(row_heights.get(node["row"], 0), height)
    row_y, cursor = {}, content_top
    # Empty row numbers are ordering slots rather than blank, unbounded space.
    for row in sorted(row_heights):
        row_y[row] = cursor
        cursor += row_heights[row] + gap
    positions = {node["id"]: (left + LANES[node["kind"]] * lane_pitch,
                               row_y[node["row"]], card_width, row_heights[node["row"]]) for node in nodes}
    reworks = [edge for edge in edges if edge["kind"] == "rework"]
    width = max(1260, 1310 + 26 * len(reworks) + (210 if reworks else 0))
    height = cursor + 36
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="workflow-title workflow-description">')
    add(f'  <title id="workflow-title">{esc(workflow["title"])}</title>')
    add(f'  <desc id="workflow-description">{esc(workflow["description"])} 设计规范示意，不代表实时运行状态。左侧 AI 执行，中间 AI 判定与校验，右侧人工决策；橙色虚线表示返工。</desc>')
    add('  <defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,4 L0,8 Z" fill="#64748b"/></marker><marker id="rework-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,4 L0,8 Z" fill="#c2410c"/></marker></defs>')
    add(f'  <g font-family="{font}" fill="#0f172a">')
    add(f'    <rect width="{width}" height="{height}" fill="#ffffff"/>')
    y = 38
    for line in title_lines:
        add(f'    <text x="28" y="{y}" font-size="26" font-weight="700">{esc(line)}</text>')
        y += 32
    for line in desc_lines:
        add(f'    <text x="28" y="{y}" font-size="14" fill="#475569">{esc(line)}</text>')
        y += 20
    add(f'    <text x="28" y="{y + 4}" font-size="13" fill="#64748b">设计规范 · 静态流程示意，不代表执行状态 · 实线：正常流转；橙色虚线：返工</text>')
    for lane, label in enumerate(("AI 自主执行", "AI 判定 / 校验与起止", "人工决策门")):
        x = 20 + lane * lane_pitch
        add(f'    <rect x="{x}" y="{header_bottom}" width="400" height="{cursor - header_bottom - 30}" rx="14" fill="{("#f8faff", "#f6fbf9", "#fffbf5")[lane]}" stroke="#e2e8f0"/>')
        add(f'    <text x="{x + 200}" y="{header_bottom + 29}" text-anchor="middle" font-size="16" font-weight="700">{label}</text>')
    edge_labels = []
    rework_index = 0
    for edge in edges:
        sx, sy, sw, sh = positions[edge["from"]]
        tx, ty, tw, th = positions[edge["to"]]
        source, target = by_id[edge["from"]], by_id[edge["to"]]
        source_center, target_center = sx + sw / 2, tx + tw / 2
        color = "#c2410c" if edge["kind"] == "rework" else "#64748b"
        dash = ' stroke-dasharray="7 5"' if edge["kind"] == "rework" else ""
        marker = "rework-arrow" if edge["kind"] == "rework" else "arrow"
        if edge["kind"] == "rework":
            rail = 1270 + 26 * rework_index
            rework_index += 1
            # Route above the target card, so the final arrow never passes through another card.
            target_gap = ty - 23
            start_y = sy + sh / 2
            path = f"M {sx + sw},{start_y} H {rail} V {target_gap} H {target_center} V {ty}"
            edge_labels.append((rail + 10, (start_y + target_gap) / 2, edge["label"], color, "start"))
        elif ty > sy:
            mid_y = sy + sh + gap / 2
            intervening = any(node["id"] not in (source["id"], target["id"])
                              and LANES[node["kind"]] == LANES[target["kind"]]
                              and source["row"] < node["row"] < target["row"] for node in nodes)
            if intervening:
                rail = tx - 16
                end_gap = ty - 24
                path = f"M {source_center},{sy + sh} V {mid_y} H {rail} V {end_gap} H {target_center} V {ty}"
            else:
                path = f"M {source_center},{sy + sh} V {mid_y} H {target_center} V {ty}"
            anchor_x = (source_center + target_center) / 2
            edge_labels.append((anchor_x + (12 if source_center == target_center else 0), mid_y - 9, edge["label"], color, "start" if source_center == target_center else "middle"))
        else:
            # Same-row or upward normal edges remain supported via a gutter.
            rail = max(sx + sw, tx + tw) + 18
            start_y, end_y = sy + sh / 2, ty + th / 2
            path = f"M {sx + sw},{start_y} H {rail} V {end_y} H {tx + tw}"
            edge_labels.append((rail + 6, (start_y + end_y) / 2 - 7, edge["label"], color, "start"))
        add(f'    <path data-from="{esc(edge["from"])}" data-to="{esc(edge["to"])}" d="{path}" fill="none" stroke="{color}" stroke-width="2"{dash} marker-end="url(#{marker})"/>')
    for node in nodes:
        x, y, w, h = positions[node["id"]]
        fill, border, badge = COLORS[node["kind"]]
        label, detail, extra = text_lines[node["id"]]
        add(f'    <g id="node-{esc(node["id"])}" data-kind="{node["kind"]}" data-row="{node["row"]}">')
        add(f'      <title>{esc(node["label"] + " — " + node["detail"])}</title>')
        add(f'      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{26 if node["kind"] == "terminal" else 10}" fill="{fill}" stroke="{border}" stroke-width="1.8"/>')
        add(f'      <text x="{x + 16}" y="{y + 24}" font-size="12" fill="{border}" font-weight="700">{badge}</text>')
        line_y = y + 50
        for line in label:
            add(f'      <text x="{x + 16}" y="{line_y}" font-size="18" font-weight="700">{esc(line)}</text>')
            line_y += 24
        for line in detail:
            add(f'      <text x="{x + 16}" y="{line_y}" font-size="14" fill="#334155">{esc(line)}</text>')
            line_y += 20
        if extra:
            line_y += 12
            for line in extra:
                add(f'      <text x="{x + 16}" y="{line_y}" font-size="14" fill="#9a3412">{esc(line)}</text>')
                line_y += 20
        add('    </g>')
    for x, y, label, color, anchor in edge_labels:
        for i, line in enumerate(_wrap(label, 23)):
            add(f'    <text x="{x}" y="{y + i * 17}" text-anchor="{anchor}" font-size="12" fill="{color}" stroke="#ffffff" stroke-width="4" paint-order="stroke">{esc(line)}</text>')
    add(f'    <text x="28" y="{height - 26}" font-size="12" fill="#64748b">schema_version: 1 · 人工节点必须定义介入条件与恢复位置 · 修改 JSON 后重新生成并执行 --check</text>')
    add('  </g>\n</svg>')
    return "\n".join(parts) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="UTF-8 workflow JSON")
    parser.add_argument("--output", required=True, type=Path, help="generated SVG")
    parser.add_argument("--check", action="store_true", help="compare only; never write files")
    args = parser.parse_args(argv)
    try:
        same = args.source.resolve() == args.output.resolve()
        if args.source.exists() and args.output.exists():
            same = same or os.path.samefile(args.source, args.output)
        if same:
            raise ValueError("source and output must be different files")
        svg = render(load_workflow(args.source))
        if args.check:
            if not args.output.is_file():
                print(f"MISSING: {args.output}", file=sys.stderr)
                return 1
            if args.output.read_bytes() != svg.encode("utf-8"):
                print(f"DRIFT: {args.output}; regenerate from {args.source}", file=sys.stderr)
                return 1
            print(f"OK: {args.output} is up to date.")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=args.output.parent, prefix=f".{args.output.name}.",
                                             suffix=".tmp", delete=False) as target:
                temporary = target.name
                target.write(svg)
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary, args.output)
        finally:
            if temporary is not None and os.path.exists(temporary):
                os.unlink(temporary)
        print(f"Wrote SVG: {args.output}")
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
