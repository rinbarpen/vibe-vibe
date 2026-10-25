#!/usr/bin/env python3
"""Render the canonical Unity skill catalog as a deterministic, standalone SVG.

No third-party packages or Unity installation are needed. This diagram describes
workflow rules; it is deliberately not a visualization of actual execution status.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import unicodedata
from xml.sax.saxutils import escape

STAGE_IDS = (
    "discovery", "design", "prototype", "vertical-slice", "production",
    "alpha", "beta", "release-ready", "live",
)
APPROVALS = {"design": "direction", "vertical-slice": "vertical-slice", "release-ready": "release"}
APPROVAL_LABELS = {"direction": "方向确认", "vertical-slice": "制作基线确认", "release": "发布确认"}
WIDTH = 1680
ROW_HEIGHT = 224
FIRST_ROW = 286


def nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    if any(ord(char) < 32 for char in value):
        raise ValueError(f"{label} contains a control character")
    return value


def validate_subskills(items: object, label: str) -> None:
    if not isinstance(items, list):
        raise ValueError(f"{label} must be an array")
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"{label} entries must be objects")
        for key in ("name", "label", "path"):
            nonempty(item.get(key), f"{label}.{key}")
        if "subskills" in item:
            validate_subskills(item["subskills"], f"{label}.{item['name']}.subskills")
        if "software_routes" in item:
            routes = item["software_routes"]
            if not isinstance(routes, list):
                raise ValueError("software_routes must be an array")
            for route in routes:
                nonempty(route, "software_route")


def modeling_branch(catalog: dict) -> dict | None:
    production = next(stage for stage in catalog["stages"] if stage["id"] == "production")
    return next((item for item in production["subskills"]
                 if item["name"] == "unity-game-modeling" and item.get("subskills")), None)


def testing_branch(catalog: dict) -> dict | None:
    alpha = next(stage for stage in catalog["stages"] if stage["id"] == "alpha")
    return next((item for item in alpha["subskills"]
                 if item["name"] == "unity-game-testing" and item.get("subskills")), None)


def load_catalog(path: Path) -> dict:
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read catalog {path}: {exc}") from exc
    if not isinstance(catalog, dict):
        raise ValueError("catalog must be a JSON object")
    nonempty(catalog.get("root_skill"), "root_skill")
    stages = catalog.get("stages")
    if not isinstance(stages, list) or len(stages) != len(STAGE_IDS):
        raise ValueError("catalog must contain exactly 9 ordered stages")
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict) or stage.get("id") != STAGE_IDS[index]:
            raise ValueError(f"stage {index + 1} must have id {STAGE_IDS[index]}")
        nonempty(stage.get("label"), f"stage {index + 1}.label")
        nonempty(stage.get("skill"), f"stage {index + 1}.skill")
        execution = stage.get("execution")
        review = stage.get("review")
        if not isinstance(execution, dict):
            raise ValueError(f"stage {stage['id']}.execution must be an object")
        if not isinstance(review, dict):
            raise ValueError(f"stage {stage['id']}.review must be an object")
        for key in ("skill", "path"):
            nonempty(execution.get(key), f"stage {stage['id']}.execution.{key}")
            nonempty(review.get(key), f"stage {stage['id']}.review.{key}")
        nonempty(review.get("profile"), f"stage {stage['id']}.review.profile")
        if review["profile"] != stage["id"]:
            raise ValueError(f"stage {stage['id']}.review.profile must match stage id")
        if stage.get("approval") != APPROVALS.get(stage["id"]):
            raise ValueError(f"stage {stage['id']}.approval must be {APPROVALS.get(stage['id'])!r}")
        validate_subskills(stage.get("subskills"), f"stage {stage['id']}.subskills")
        if not isinstance(review.get("specialties", []), list):
            raise ValueError("review.specialties must be an array")
        for specialty in review.get("specialties", []):
            nonempty(specialty.get("name") if isinstance(specialty, dict) else specialty, "review.specialty")
    return catalog


def text_width(value: str) -> int:
    """Conservative em units, including CJK glyphs, for deterministic wrapping."""
    return sum(2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in value)


def wrap_labels(labels: list[str], limit: int = 57) -> list[str]:
    lines: list[str] = []
    line = ""
    for label in labels:
        candidate = f"{line} · {label}" if line else label
        if line and text_width(candidate) > limit:
            lines.append(line)
            line = label
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def render(catalog: dict) -> str:
    stages = catalog["stages"]
    bottom = FIRST_ROW + ROW_HEIGHT * len(stages)
    modeling = modeling_branch(catalog)
    model_rows = math.ceil(len(modeling["subskills"]) / 5) if modeling else 0
    model_height = 220 + 120 * model_rows if modeling else 0
    testing = testing_branch(catalog)
    test_rows = math.ceil(len(testing["subskills"]) / 5) if testing else 0
    test_height = 220 + 120 * test_rows if testing else 0
    test_y = bottom + 72 + (model_height + 24 if modeling else 0)
    legend_y = test_y + (test_height + 24 if testing else 0)
    height = legend_y + 158
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="workflow-title workflow-desc">',
        '<title id="workflow-title">Unity 游戏全流程：执行 Skill、独立 Reviewer 与用户确认门（流程规范）</title>',
        '<desc id="workflow-desc">九个阶段分别由专属执行 Skill 调度专项子技能，独立 game-reviewer 使用 unity-game-review 及阶段 profile 评审冻结产物。changes_requested 返回原执行者产生新版本；blocked 等待证据或依赖；passed 才可推进。策划、垂直切片和发布准备经过用户明确确认。运营反馈形成下一轮迭代。这是工作流规范，不表示任何阶段实际已执行或通过。</desc>',
        '<defs>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="#527c72"/></marker>',
        '<marker id="return" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="#b77842"/></marker>',
        '<marker id="iteration" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="#7773a5"/></marker>',
        '<style>',
        'text { font-family: "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", sans-serif; fill: #233d43; }',
        '.mono { font-family: "DejaVu Sans Mono", "SFMono-Regular", Consolas, monospace; }',
        '.muted { fill: #62777b; } .flow { fill: none; stroke: #527c72; stroke-width: 2; marker-end: url(#arrow); }',
        '.return { fill: none; stroke: #b77842; stroke-width: 1.6; stroke-dasharray: 6 4; marker-end: url(#return); }',
        '.iterate { fill: none; stroke: #7773a5; stroke-width: 2; stroke-dasharray: 8 5; marker-end: url(#iteration); }',
        '</style>',
        '</defs>',
        f'<rect width="{WIDTH}" height="{height}" fill="#f7faf8"/>',
    ]

    def txt(x: int, y: int, value: str, size: int = 16, klass: str = "", **attrs: str) -> None:
        attr_text = "".join(f' {key.replace("_", "-")}="{escape(str(val))}"' for key, val in attrs.items())
        out.append(f'<text x="{x}" y="{y}" font-size="{size}" class="{klass}"{attr_text}>{escape(value)}</text>')

    def rect(x: int, y: int, w: int, h: int, fill: str, stroke: str, radius: int = 13) -> None:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')

    def path(d: str, klass: str = "flow") -> None:
        out.append(f'<path d="{d}" class="{klass}"/>')

    txt(56, 53, "UNITY / END-TO-END GAME DEVELOPMENT", 14, "muted", letter_spacing="2")
    txt(56, 103, "每一阶段都有执行 Skill，也都有独立 Reviewer", 34, font_weight="700")
    txt(56, 138, "工作流规范 · 不代表实际执行状态 · 技能名与阶段来自 skill-map.json", 17, "muted")
    rect(56, 162, 1568, 66, "#edf4f0", "#dce8e0")
    txt(78, 188, "主代理 / game-producer", 16, font_weight="700")
    txt(350, 188, f"总入口：{catalog['root_skill']}", 15, "mono")
    txt(78, 211, "冻结输入与产物 revision → 明确路径所有权 → 并行专项 → 集成证据 → 独立评审；共享状态单写，Unity Editor 串行。", 15, "muted")
    txt(75, 264, "阶段 / STAGE", 13, "muted", letter_spacing="1")
    txt(262, 264, "01  执行 Skill → 专项 Subskills", 16, font_weight="700")
    txt(838, 264, "02  独立 Reviewer → 阶段审查", 16, font_weight="700")
    txt(1373, 264, "03  准入 / 用户确认", 16, font_weight="700")

    specialties_lookup = {}
    for specialty in catalog.get("review_skills", catalog.get("specialties", [])):
        if isinstance(specialty, dict) and isinstance(specialty.get("name"), str):
            specialties_lookup[specialty["name"]] = specialty.get("label", specialty["name"].removeprefix("unity-game-"))

    for index, stage in enumerate(stages):
        y = FIRST_ROW + index * ROW_HEIGHT
        out.append(f'<g id="stage-{escape(stage["id"])}">')
        rect(66, y + 7, 1558, 207, "#ffffff" if index % 2 == 0 else "#f1f6f3", "#e0e9e4", 16)
        txt(86, y + 49, f"{index + 1:02d}", 26, "muted")
        txt(86, y + 83, stage["label"], 19, font_weight="700")
        txt(86, y + 106, stage["id"], 11, "mono muted")
        rect(246, y + 31, 520, 133, "#edf7f3", "#a8c8ba")
        txt(264, y + 58, "执行 / implementation owner", 14, "muted")
        execution_skill = stage["execution"]["skill"]
        txt(264, y + 85, execution_skill, 16 if len(execution_skill) <= 40 else 13, "mono", font_weight="700")
        labels = [item["label"] for item in stage["subskills"]]
        lines = wrap_labels(labels, 63)
        if len(lines) > 3:
            raise ValueError(f"stage {stage['id']}: specialist labels exceed SVG card capacity")
        for number, line in enumerate(lines):
            txt(264, y + 108 + number * 19, line, 13, "muted")
        path(f'M 766 {y + 94} H 819')
        txt(773, y + 81, "提交", 11, "muted")
        rect(825, y + 31, 481, 133, "#eef2f9", "#b3c2d7")
        txt(844, y + 58, "game-reviewer · 独立上下文 / 只读产物", 14, "muted")
        txt(844, y + 85, stage["review"]["skill"], 16, "mono", font_weight="700")
        txt(844, y + 109, f"profile: {stage['review']['profile']}", 13, "mono muted")
        names = stage["review"].get("specialties", [])
        review_labels = []
        for name in names:
            if isinstance(name, dict):
                review_labels.append(str(name.get("label", name["name"].removeprefix("unity-game-"))))
            else:
                review_labels.append(str(specialties_lookup.get(name, name.removeprefix("unity-game-"))))
        lines = wrap_labels(review_labels, 58)
        if len(lines) > 2:
            raise ValueError(f"stage {stage['id']}: reviewer specialties exceed SVG card capacity")
        for number, line in enumerate(lines):
            txt(844, y + 130 + number * 17, line, 12, "muted")
        path(f'M 1306 {y + 94} H 1350')
        txt(1312, y + 78, "passed", 10, "mono muted")
        approval = stage["approval"]
        rect(1356, y + 31, 245, 133, "#fff7e8" if approval else "#f3f7f4", "#d8b675" if approval else "#ccdcd2")
        if approval:
            txt(1375, y + 61, "用户明确确认", 17, font_weight="700")
            txt(1375, y + 89, APPROVAL_LABELS[approval], 17)
            txt(1375, y + 113, approval, 14, "mono muted")
            txt(1375, y + 143, "等待确认；拒绝则回修", 13, "muted")
            path(f'M 1478 {y + 164} V {y + 181} H 1067', "return")
        else:
            txt(1375, y + 66, "阶段准入", 17, font_weight="700")
            txt(1375, y + 96, "证据与版本一致", 15)
            txt(1375, y + 127, "复核依赖后推进", 14, "muted")
        path(f'M 1067 {y + 164} V {y + 181} H 510 V {y + 164}', "return")
        if approval:
            txt(1375, y + 203, "仅确认后推进", 12, "muted")
        txt(558, y + 177, "changes_requested → 原责任执行者修复 / 新 revision → 重审", 12, fill="#996333")
        txt(844, y + 203, "blocked → 等待依赖或证据，保持本阶段", 12, "muted")
        if index < len(stages) - 1:
            path(f'M 1601 {y + 94} H 1612 V {y + 219} H 500 V {y + ROW_HEIGHT + 31}')
        out.append('</g>')

    # Operational feedback loops back to production; changes to an approved
    # baseline need the relevant earlier approval again, never silent reuse.
    live_y = FIRST_ROW + (len(stages) - 1) * ROW_HEIGHT
    production_y = FIRST_ROW + STAGE_IDS.index("production") * ROW_HEIGHT
    path(f'M 1478 {live_y + 164} V {bottom + 21} H 35 V {production_y + 94} H 66', "iterate")
    txt(88, bottom + 47, "运营反馈 → 新迭代任务 → 正式制作（或回到受影响的上游阶段）；已批准基线变化需重新确认对应门。", 16, fill="#625e8d")
    if modeling:
        model_y = bottom + 72
        out.append('<g id="modeling-subpipeline">')
        rect(66, model_y, 1558, model_height, "#f0f4fa", "#b3c2d7", 16)
        txt(88, model_y + 35, f"模型子流程 / {modeling['label']}", 22, font_weight="700")
        txt(880, model_y + 35, modeling["name"], 16, "mono")
        route_labels = {"mcp": "MCP（发现真实工具）", "external-skill": "外部 Skill（实际可用）",
                        "blender-cli": "Blender CLI", "gui": "GUI（可用时）"}
        routes = " / ".join(route_labels.get(route, route) for route in modeling.get("software_routes", []))
        txt(88, model_y + 66, f"执行路由：{routes or '由任务包明确执行软件'}", 16)
        txt(88, model_y + 94, "路由需先检查可用性；本图不表示已经安装、连接或执行。无软件 / 无连接 → not_run，保留待验收状态。", 14, "muted")
        items = modeling["subskills"]
        columns = min(5, len(items))
        card_width = (1518 - (columns - 1) * 20) // columns
        for index, item in enumerate(items):
            row, column = divmod(index, 5)
            x, y = 86 + column * (card_width + 20), model_y + 119 + row * 120
            rect(x, y, card_width, 95, "#ffffff", "#b3c2d7")
            txt(x + 14, y + 27, f"{index + 1:02d}  {item['label']}", 16, font_weight="700")
            txt(x + 14, y + 53, item["name"], 12, "mono")
            roles = " / ".join(item.get("roles", []))
            role_lines = wrap_labels(roles.split(" / ") if roles else [], max(25, card_width // 7))
            for line_index, line in enumerate(role_lines[:2]):
                txt(x + 14, y + 73 + line_index * 15, line, 11, "mono muted")
            if index < len(items) - 1:
                if column < columns - 1 and column < 4:
                    path(f'M {x + card_width} {y + 47} H {x + card_width + 17}')
                else:
                    path(f'M {x + card_width // 2} {y + 95} V {y + 106} H 75 V {y + 167} H 83')
        footer_y = model_y + 119 + 120 * model_rows
        txt(88, footer_y + 12, "文件所有权：model-artist（可编辑源模型） → technical-artist（Unity 导入） → game-reviewer（独立审查）。", 15)
        txt(88, footer_y + 41, "原始源文件保留；导出文件 + 哈希 + 软件执行证据 + Unity 验证 → 独立评审；changes_requested → 原 Skill / owner 新版本重审。", 14, "muted")
        txt(88, footer_y + 69, "模型审查通过后回到正式制作集成，再走 production 阶段总审；模型文件存在不等同艺术质量或设备性能通过。", 14, "muted")
        out.append('</g>')
    if testing:
        out.append('<g id="testing-subpipeline">')
        rect(66, test_y, 1558, test_height, "#f4f0fa", "#c9bddb", 17)
        txt(88, test_y + 36, "游戏测试子流程 / 启动并操作真实游戏，再复现与回归", 22, font_weight="700")
        txt(1100, test_y + 36, testing["name"], 16, "mono")
        txt(88, test_y + 67, "跨原型 / 切片 / 制作 / Alpha / Beta / 候选包 / 热修复；QA 执行，独立 game-reviewer 审查。", 16)
        txt(88, test_y + 96, "路由：项目 harness · 已连接 MCP · 桌面 / 浏览器 skill · 设备工具；缺真实输入或构建 → not_run。", 14, "muted")
        items = testing["subskills"]
        columns = min(5, len(items))
        card_width = (1518 - (columns - 1) * 20) // columns
        for index, item in enumerate(items):
            row, column = divmod(index, 5)
            x, y = 86 + column * (card_width + 20), test_y + 119 + row * 120
            rect(x, y, card_width, 95, "#ffffff", "#c9bddb")
            txt(x + 14, y + 27, f"{index + 1:02d}  {item['label']}", 16, font_weight="700")
            txt(x + 14, y + 53, item["name"], 12, "mono")
            role_lines = wrap_labels(item.get("roles", []), max(25, card_width // 7))
            for line_index, line in enumerate(role_lines[:2]):
                txt(x + 14, y + 73 + line_index * 15, line, 11, "mono muted")
            if index < len(items) - 1:
                if column < columns - 1 and column < 4:
                    path(f'M {x + card_width} {y + 47} H {x + card_width + 17}')
                else:
                    path(f'M {x + card_width // 2} {y + 95} V {y + 106} H 75 V {y + 167} H 83')
        footer_y = test_y + 119 + 120 * test_rows
        txt(88, footer_y + 12, "缺陷 → 原实现 owner / 原执行 skill 修复 → 新 revision 的原用例 + 相邻回归 → 独立测试审查。", 15)
        txt(88, footer_y + 41, "记录普通输入、预期/实际、截图/视频/日志、构建与证据哈希；输入或构建改变须复测、复审。", 14, "muted")
        txt(88, footer_y + 69, "证据校验器不是游戏控制器；AI 游玩不等于真人体验，截图不代替音频/性能实测，用户确认门仍单独保留。", 14, "muted")
        out.append('</g>')
    rect(66, legend_y, 1558, 132, "#edf2f0", "#dbe4df")
    path(f'M 88 {legend_y + 28} H 126')
    txt(138, legend_y + 34, "passed + 依赖满足：下一阶段", 14)
    path(f'M 520 {legend_y + 28} H 558', "return")
    txt(570, legend_y + 34, "changes_requested / 用户要求回修：原执行者新版本", 14)
    path(f'M 1180 {legend_y + 28} H 1218', "iterate")
    txt(1230, legend_y + 34, "运营反馈：下一轮迭代", 14)
    txt(88, legend_y + 67, "评审结论：passed / changes_requested / blocked。缺少试玩、Editor、设备或构建证据不得等同 passed；审核通过也不等同发布完成。", 14, "muted")
    txt(88, legend_y + 101, "Reviewer 缺席：review_status=not_run，不推进；已审/已批准 revision 变化须重审，涉及确认基线则重走用户确认门。", 14, "muted")
    out.append('</svg>')
    return "\n".join(out) + "\n"


def default_catalog() -> Path:
    script = Path(__file__).resolve()
    bundle = script.parent.parent
    if bundle.name == ".unity-game":
        # An installed renderer belongs only to its own target project. In
        # particular, a target nested within this repository must not silently
        # consume the repository catalog when its installed skills are absent.
        root = bundle.parent
        candidates = [root / prefix / "unity-game-development/references/skill-map.json"
                      for prefix in (".agents/skills", ".claude/skills", ".codex/skills")]
    elif bundle.name == "unity-game" and bundle.parent.name == "manifests":
        candidates = [bundle.parent.parent / "mine/unity-game-development/references/skill-map.json"]
    else:
        candidates = [Path.cwd() / prefix / "unity-game-development/references/skill-map.json"
                      for prefix in (".agents/skills", ".claude/skills", ".codex/skills")]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ValueError("skill-map.json not found for this source/installed bundle; supply --catalog PATH")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, help="canonical skill-map.json; source or installed catalog detected by default")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent.parent / "references/workflow.svg")
    parser.add_argument("--check", action="store_true", help="compare existing SVG to canonical rendering without writing")
    args = parser.parse_args(argv)
    try:
        rendered = render(load_catalog(args.catalog if args.catalog is not None else default_catalog()))
        if args.check:
            if not args.output.is_file() or args.output.read_bytes() != rendered.encode("utf-8"):
                print(f"workflow SVG differs or is missing: {args.output}", file=sys.stderr)
                return 1
            print(f"workflow SVG is current: {args.output}")
        else:
            atomic_write(args.output, rendered)
            print(f"rendered workflow SVG: {args.output}")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"workflow render error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
