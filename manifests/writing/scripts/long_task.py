#!/usr/bin/env python3
"""Persistent chapter queue and supplement reports; not a background AI runner."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys

# Read-only queries should not create sibling bytecode files on first use.
sys.dont_write_bytecode = True

from check_bid import (array, choice, digest, fields, identifier, local_path,
                       SHA, string, unique_object, validate_schema, check as check_matrix)


def load(path):
    if path.is_symlink():
        raise ValueError("state file must not be a symlink")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def integer(value, where, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{where}: expected integer >= {minimum}")


def strings(value, where):
    array(value, where)
    if any(not isinstance(v, str) or not v for v in value) or len(value) != len(set(value)):
        raise ValueError(where + ": expected unique nonempty strings")


def sha_field(value):
    string(value, "sha256")
    if value and not SHA.fullmatch(value):
        raise ValueError("sha256: expected empty or 64 hex characters")


def file_ok(root, path, sha):
    p = local_path(root, path)
    return bool(p and p.is_file() and sha and digest(p) == sha.lower())


def file_stamp(root, path):
    p = local_path(root, path)
    return digest(p) if p and p.is_file() else "MISSING"


def validate(plan, bid, root):
    sources = validate_schema(bid, root)
    fields(plan, ("schema_version", "page_goal", "context_paths", "chapters", "supplements", "assets", "rendered"), "plan")
    if type(plan["schema_version"]) is not int or plan["schema_version"] != 1:
        raise ValueError("plan.schema_version: expected integer 1")
    goal = plan["page_goal"]
    fields(goal, ("minimum", "target", "maximum", "count_scope", "layout_basis"), "page_goal")
    for key in ("minimum", "target", "maximum"):
        integer(goal[key], "page_goal." + key)
    if not 0 < goal["minimum"] <= goal["target"] or (goal["maximum"] and goal["target"] > goal["maximum"]):
        raise ValueError("page_goal: require 0 < minimum <= target <= maximum (0 means no maximum)")
    for key in ("count_scope", "layout_basis"):
        string(goal[key], "page_goal." + key)
    strings(plan["context_paths"], "context_paths")
    for path in plan["context_paths"]:
        local_path(root, path)
    reqs = {r["id"]: r for r in bid["requirements"]}
    chapters, assets, supplements = {}, {}, {}
    for key, target in (("chapters", chapters), ("assets", assets), ("supplements", supplements)):
        array(plan[key], key)
        for item in plan[key]:
            if not isinstance(item, dict):
                raise ValueError(key + ": expected object entries")
            iid = identifier(item.get("id"), key + ".id")
            if iid in target:
                raise ValueError("duplicate " + key + " ID: " + iid)
            target[iid] = item
    paths, mapped = set(), set()
    for cid, chapter in chapters.items():
        fields(chapter, ("id", "title", "path", "budget_pages", "depends_on", "requirement_ids", "asset_ids", "status", "checkpoint"), cid)
        string(chapter["title"], cid + ".title")
        path = local_path(root, chapter["path"])
        if path is None or path in paths:
            raise ValueError(cid + ": chapter path must be nonempty and unique")
        paths.add(path)
        integer(chapter["budget_pages"], cid + ".budget_pages", 1)
        choice(chapter["status"], {"pending", "writing", "review", "accepted", "revision"}, cid + ".status")
        for key, allowed in (("depends_on", chapters), ("requirement_ids", reqs), ("asset_ids", assets)):
            strings(chapter[key], cid + "." + key)
            if set(chapter[key]) - set(allowed):
                raise ValueError(cid + ": unknown " + key)
        for rid in chapter["requirement_ids"]:
            if rid in mapped:
                raise ValueError(rid + ": assign one primary chapter; use depends_on for cross-chapter discussion")
            mapped.add(rid)
            if reqs[rid]["response_path"] != chapter["path"]:
                raise ValueError(rid + ": response_path differs from primary chapter path")
        cp = chapter["checkpoint"]
        if cp is not None:
            fields(cp, ("draft_sha256", "review_path", "review_sha256", "inputs_sha256"), cid + ".checkpoint")
            for key in ("draft_sha256", "review_sha256", "inputs_sha256"):
                sha_field(cp[key])
            local_path(root, cp["review_path"])
    # Topological order without recursion, including hundreds of chapters.
    ordered, remaining = [], set(chapters)
    while remaining:
        ready = [cid for cid in chapters if cid in remaining and set(chapters[cid]["depends_on"]) <= set(ordered)]
        if not ready:
            raise ValueError("chapter dependency cycle")
        ordered.extend(ready)
        remaining.difference_update(ready)
    for sid, item in supplements.items():
        fields(item, ("id", "kind", "title", "chapter_ids", "requirement_ids", "priority", "status", "request", "owner", "needed_by", "evidence"), sid)
        choice(item["kind"], {"material", "content", "visual", "decision"}, sid + ".kind")
        choice(item["priority"], {"blocking", "important", "optional"}, sid + ".priority")
        choice(item["status"], {"open", "provided", "verified"}, sid + ".status")
        for key in ("title", "request", "owner", "needed_by"):
            string(item[key], sid + "." + key)
        for key, allowed in (("chapter_ids", chapters), ("requirement_ids", reqs)):
            strings(item[key], sid + "." + key)
            if set(item[key]) - set(allowed):
                raise ValueError(sid + ": unknown " + key)
        array(item["evidence"], sid + ".evidence")
        for e in item["evidence"]:
            fields(e, ("path", "sha256"), sid + ".evidence[]")
            local_path(root, e["path"])
            sha_field(e["sha256"])
    for aid, asset in assets.items():
        fields(asset, ("id", "kind", "title", "chapter_ids", "source_ids", "purpose", "status", "path", "sha256", "editable_path", "editable_sha256", "preview_path", "preview_sha256", "caption", "alt_text", "note"), aid)
        choice(asset["kind"], {"diagram", "photo", "table", "chart", "attachment"}, aid + ".kind")
        choice(asset["status"], {"planned", "waiting_input", "draft", "verified"}, aid + ".status")
        for key in ("title", "purpose", "caption", "alt_text", "note"):
            string(asset[key], aid + "." + key)
        for key in ("path", "editable_path", "preview_path"):
            local_path(root, asset[key])
        for key in ("sha256", "editable_sha256", "preview_sha256"):
            sha_field(asset[key])
        for key, allowed in (("chapter_ids", chapters), ("source_ids", sources)):
            strings(asset[key], aid + "." + key)
            if set(asset[key]) - set(allowed):
                raise ValueError(aid + ": unknown " + key)
        owners = {cid for cid, chapter in chapters.items() if aid in chapter["asset_ids"]}
        if not owners or owners != set(asset["chapter_ids"]):
            raise ValueError(aid + ": chapter_ids must match the chapters referencing this asset")
    rendered = plan["rendered"]
    fields(rendered, ("path", "sha256", "pages", "count_scope", "qa_path", "qa_sha256"), "rendered")
    integer(rendered["pages"], "rendered.pages")
    for key in ("path", "qa_path"):
        local_path(root, rendered[key])
    for key in ("sha256", "qa_sha256"):
        sha_field(rendered[key])
    string(rendered["count_scope"], "rendered.count_scope")
    return sources, reqs, chapters, assets, supplements, ordered


def analyze(plan, bid, root):
    sources, reqs, chapters, assets, supplements, ordered = validate(plan, bid, root)
    reference_state = None
    reference_path = local_path(root, "references.json")
    inline_citations = any("[^C-" in local_path(root, c["path"]).read_text(encoding="utf-8")
                           for c in chapters.values() if local_path(root, c["path"]).is_file())
    if reference_path.is_file() or inline_citations:
        from reference_tools import audit, load, empty
        reference_state = audit(load(reference_path) if reference_path.is_file() else empty(), bid, plan, root)
    source_bad = {sid for sid, s in sources.items() if not file_ok(root, s["path"], s["sha256"])}
    supplement_open = {sid for sid, s in supplements.items() if s["status"] != "verified"
                       or not s["evidence"] or any(not file_ok(root, e["path"], e["sha256"]) for e in s["evidence"])}
    asset_bad = {}
    for aid, a in assets.items():
        problems = []
        if a["status"] != "verified":
            problems.append("未验收")
        if not file_ok(root, a["path"], a["sha256"]) or not file_ok(root, a["preview_path"], a["preview_sha256"]):
            problems.append("缺成品/预览或哈希变化")
        if a["kind"] in {"diagram", "table", "chart"} and not file_ok(root, a["editable_path"], a["editable_sha256"]):
            problems.append("缺可编辑图源/表源")
        if not a["caption"].strip() or not a["alt_text"].strip() or not a["source_ids"] or set(a["source_ids"]) & source_bad:
            problems.append("缺题注/说明/有效来源")
        if problems:
            asset_bad[aid] = problems
    missing_context = [p for p in plan["context_paths"] if file_stamp(root, p) == "MISSING"]
    current, blockers, completion, stamps = {}, {}, {}, {}
    for cid in ordered:
        c = chapters[cid]
        block = ["上下文缺失: " + p for p in missing_context]
        block += ["前置章节未验收或失效: " + dep for dep in c["depends_on"] if not current[dep]]
        block += ["补充项: " + sid for sid in sorted(supplement_open) if supplements[sid]["priority"] == "blocking"
                  and (not supplements[sid]["chapter_ids"] and not supplements[sid]["requirement_ids"] or cid in supplements[sid]["chapter_ids"]
                       or set(c["requirement_ids"]) & set(supplements[sid]["requirement_ids"]))]
        needed_sources = set()
        for rid in c["requirement_ids"]:
            r = reqs[rid]
            needed_sources.add(r["source_id"])
            needed_sources.update(e["source_id"] for e in r["evidence"])
            if r["status"] == "gap":
                block.append("条款缺口: " + rid)
        for aid in c["asset_ids"]:
            needed_sources.update(assets[aid]["source_ids"])
        if reference_state:
            needed_sources.update(reference_state["pins"][cid]["source_ids"])
        block += ["来源缺失/变化: " + sid for sid in sorted(needed_sources & source_bad)]
        done_problems = list(block)
        if reference_state:
            done_problems += ["引用待核对: " + issue for issue in reference_state["issues"][cid]]
        for rid in c["requirement_ids"]:
            r = reqs[rid]
            if r["status"] != "covered" or not r["locator"].strip() or not r["text"].strip():
                done_problems.append("条款未完成: " + rid)
            response = local_path(root, c["path"])
            if response is None or not response.is_file() or f"<!-- REQ:{rid} -->" not in response.read_text(encoding="utf-8"):
                done_problems.append("条款标记缺失: " + rid)
            if r["requires_evidence"] and not r["evidence"] or any(not e["locator"].strip() for e in r["evidence"]):
                done_problems.append("证明材料/定位缺失: " + rid)
        done_problems += ["图表未就绪: " + aid for aid in c["asset_ids"] if aid in asset_bad]
        if file_stamp(root, c["path"]) == "MISSING":
            done_problems.append("章节文件缺失")
        inputs = {"requirements": [reqs[rid] for rid in c["requirement_ids"]],
                  "sources": {sid: {**sources[sid], "actual": file_stamp(root, sources[sid]["path"])} for sid in sorted(needed_sources)},
                  "context": {p: file_stamp(root, p) for p in plan["context_paths"]},
                  "dependencies": {dep: {"current": current[dep], "actual": file_stamp(root, chapters[dep]["path"])} for dep in c["depends_on"]},
                  "assets": {aid: {**assets[aid], "actual": {k: file_stamp(root, assets[aid][k]) for k in ("path", "editable_path", "preview_path")}} for aid in c["asset_ids"]}}
        if reference_state and (reference_state["pins"][cid]["citations"] or reference_state["pins"][cid]["notes"] or reference_state["issues"][cid]):
            inputs["references"] = reference_state["pins"][cid]
        stamp = hashlib.sha256(json.dumps(inputs, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        cp = c["checkpoint"]
        current[cid] = bool(c["status"] == "accepted" and cp and not done_problems
                            and file_ok(root, c["path"], cp["draft_sha256"])
                            and file_ok(root, cp["review_path"], cp["review_sha256"])
                            and cp["inputs_sha256"] == stamp)
        blockers[cid], completion[cid], stamps[cid] = block, done_problems, stamp
    return dict(sources=sources, reqs=reqs, chapters=chapters, assets=assets, supplements=supplements,
                current=current, blockers=blockers, completion=completion, stamps=stamps,
                source_bad=source_bad, supplement_open=supplement_open, asset_bad=asset_bad,
                reference_state=reference_state)


def next_task(state):
    for cid, c in state["chapters"].items():
        if not state["current"][cid] and not state["blockers"][cid]:
            return {"kind": "chapter", "id": cid, "title": c["title"], "path": c["path"],
                    "action": "复核当前章节并续写" if c["checkpoint"] or c["status"] != "pending" else "读取章节任务包后起草",
                    "asset_ids": c["asset_ids"], "remaining_before_checkpoint": state["completion"][cid]}
    if state["chapters"] and all(state["current"].values()):
        return {"kind": "assembly", "action": "统一总稿、跨章审查、排版与实际页数验收"}
    blocked = {cid: why for cid, why in state["blockers"].items() if why}
    return {"kind": "waiting", "action": "汇总阻塞项并请求补充；保留已完成章节，不重启全文",
            "blocked_chapters": len(blocked), "blockers": dict(list(blocked.items())[:5]),
            "more_in_report": len(blocked) > 5}


def assembly_stamp(state, root):
    inputs = {cid: {"path": c["path"], "draft": file_stamp(root, c["path"]),
                    "inputs": state["stamps"][cid], "current": state["current"][cid]}
              for cid, c in state["chapters"].items()}
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()


def report_text(plan, state):
    lines = ["# 长标书进度与补充提醒", "", "本报告按当前文件生成；不是后台通知或真实审批记录。", "",
             f"章节：{sum(state['current'].values())}/{len(state['chapters'])} 个检查点当前有效。",
             f"篇幅：规划至少 {plan['page_goal']['minimum']} 页，目标 {plan['page_goal']['target']} 页；章节预算合计 {sum(c['budget_pages'] for c in state['chapters'].values())} 页。", "",
             "## 下一步", "", json.dumps(next_task(state), ensure_ascii=False, indent=2), "", "## 需要补充的材料、内容与决定", ""]
    for sid in sorted(state["supplement_open"]):
        s = state["supplements"][sid]
        lines += [f"### {sid} · {s['title']} [{s['priority']}]", f"- 请补充：{s['request']}",
                  f"- 类型：{s['kind']}；提供者：{s['owner']}；需要时间：{s['needed_by'] or '进入依赖章节前'}",
                  f"- 影响章节：{', '.join(s['chapter_ids']) or '相关章节/全局'}；条款：{', '.join(s['requirement_ids']) or '待映射'}",
                  f"- 当前：{s['status']}；提交材料后核对文件、版本与哈希再标 verified。", ""]
    linked = {rid for sid in state["supplement_open"] for rid in state["supplements"][sid]["requirement_ids"]}
    for rid, r in state["reqs"].items():
        if rid not in linked and (r["status"] == "gap" or r["requires_evidence"] and not r["evidence"]):
            lines += [f"- 条款 {rid}：{r['text']}；依据 {r['source_id']} {r['locator']}；需要补充：{r['note'] or '满足该要求的实际证明材料或业务处理决定'}。"]
    if state["source_bad"]:
        lines += ["", "来源待核对：" + ", ".join(sorted(state["source_bad"]))]
    lines += ["", "## 图、表、照片与附件", ""]
    for aid, a in state["assets"].items():
        lines += [f"### {aid} · {a['title']} [{a['status']}]", f"- 用途：{a['purpose']}；章节：{', '.join(a['chapter_ids'])}",
                  f"- 需要：{'; '.join(state['asset_bad'].get(aid, ['文件/图源/预览与登记哈希一致']))}",
                  f"- 补充说明：{a['note'] or '核对来源、题注、正文引用及实际嵌入尺寸。'}", ""]
    lines += ["## 当前阻塞及失效检查点", ""]
    for cid, c in state["chapters"].items():
        if state["blockers"][cid]:
            lines.append(f"- {cid}：" + "；".join(state["blockers"][cid]))
        elif c["status"] == "accepted" and not state["current"][cid]:
            lines.append(f"- {cid}：检查点失效；复核变化的正文、来源、依赖、图表或审查记录。")
    if state["reference_state"]:
        lines += ["", "## 引用与新资料核对", ""]
        for cid, issues in state["reference_state"]["issues"].items():
            lines += [f"- {cid}：{issue}" for issue in issues]
    lines += ["", "页数以当前排版成品的计数证据为准；预算、字数或手填页数字段不证明实际页数。", ""]
    return "\n".join(lines)


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".writing-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def snapshot(root, path):
    if path.exists():
        original = path.read_bytes()
        backup = local_path(root, "archives/writing-state/" + path.name + "." + hashlib.sha256(original).hexdigest() + ".bak")
        backup.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists() and backup.read_bytes() != original:
            raise ValueError("checkpoint backup differs from expected content")
        if not backup.exists():
            backup.write_bytes(original)
        return backup


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "next", "report", "checkpoint"))
    parser.add_argument("plan", type=Path)
    parser.add_argument("--bid", default="bid.json")
    parser.add_argument("--output", help="Write a supplement report; otherwise stdout only")
    parser.add_argument("--chapter")
    parser.add_argument("--review")
    parser.add_argument("--release", action="store_true", help="Check long-task readiness, not release approval")
    args = parser.parse_args(argv)
    try:
        if args.plan.is_symlink():
            raise ValueError("plan must not be a symlink")
        root = args.plan.resolve().parent
        plan_path = local_path(root, args.plan.name)
        bid_path = local_path(root, args.bid)
        if plan_path is None or bid_path is None or plan_path == bid_path or bid_path.parent != root:
            raise ValueError("plan and bid must be distinct files in the same project")
        before = digest(plan_path)
        plan, bid = load(plan_path), load(bid_path)
        state = analyze(plan, bid, root)
        if args.command == "next":
            print(json.dumps(next_task(state), ensure_ascii=False, indent=2))
        elif args.command == "report":
            text = report_text(plan, state)
            if args.output:
                path = local_path(root, args.output)
                if path and path.relative_to(root).parts[0] in {"scripts", "templates", "references", "rules", ".agents", ".claude", ".vibe-tool", "archives"}:
                    raise ValueError("report output overlaps configuration or archive resources")
                protected = {plan_path, bid_path}
                protected.add(local_path(root, "references.json"))
                if state["reference_state"]:
                    protected.update(local_path(root, n[k]) for n in state["reference_state"]["notes"].values() for k in ("extract_path", "review_path"))
                protected.update(local_path(root, p) for p in plan["context_paths"])
                protected.update(local_path(root, s["path"]) for s in state["sources"].values())
                protected.update(local_path(root, c["path"]) for c in state["chapters"].values())
                protected.update(local_path(root, c["checkpoint"]["review_path"]) for c in state["chapters"].values() if c["checkpoint"])
                protected.update(local_path(root, a[k]) for a in state["assets"].values() for k in ("path", "editable_path", "preview_path"))
                protected.update(local_path(root, e["path"]) for s in state["supplements"].values() for e in s["evidence"])
                protected.update(local_path(root, plan["rendered"][k]) for k in ("path", "qa_path"))
                if path is None or path in protected:
                    raise ValueError("report output overlaps a project input or artifact")
                backup = snapshot(root, path)
                atomic_write(path, text)
                print("REPORT " + str(path))
                if backup:
                    print("PREVIOUS REPORT " + str(backup))
            else:
                print(text)
        elif args.command == "checkpoint":
            cid = args.chapter
            if cid not in state["chapters"] or not args.review:
                raise ValueError("checkpoint requires --chapter ID and --review path")
            c = state["chapters"][cid]
            if c["status"] != "review":
                raise ValueError("set the reviewed candidate status to review before checkpointing")
            review = local_path(root, args.review)
            if state["completion"][cid]:
                raise ValueError("chapter is not ready: " + "; ".join(state["completion"][cid]))
            draft_sha = file_stamp(root, c["path"])
            protected = {plan_path, bid_path}
            protected.add(local_path(root, "references.json"))
            protected.update(local_path(root, p) for p in plan["context_paths"])
            protected.update(local_path(root, item["path"]) for item in state["sources"].values())
            protected.update(local_path(root, item["path"]) for item in state["chapters"].values())
            protected.update(local_path(root, a[k]) for a in state["assets"].values() for k in ("path", "editable_path", "preview_path"))
            if not review or not review.is_file() or review in protected or draft_sha not in review.read_text(encoding="utf-8"):
                raise ValueError("review must be a distinct file containing the current draft SHA-256")
            if digest(plan_path) != before:
                raise ValueError("plan changed during checkpoint; reload first")
            backup = snapshot(root, plan_path)
            c["status"] = "accepted"
            c["checkpoint"] = dict(draft_sha256=draft_sha, review_path=args.review,
                                   review_sha256=digest(review), inputs_sha256=state["stamps"][cid])
            atomic_write(plan_path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
            print(f"CHECKPOINT {cid} {draft_sha}\nPREVIOUS PLAN {backup}")
        else:
            stale = [cid for cid, c in state["chapters"].items() if c["status"] == "accepted" and not state["current"][cid]]
            print(f"LONG TASK chapters={len(state['chapters'])} current={sum(state['current'].values())} stale={len(stale)} open_supplements={len(state['supplement_open'])} pending_assets={len(state['asset_bad'])}")
            print("ASSEMBLY_INPUTS_SHA256 " + assembly_stamp(state, root))
            print("NEXT " + json.dumps(next_task(state), ensure_ascii=False))
            if args.release:
                issues = []
                if check_matrix(bid, root, "release"):
                    issues.append("bid matrix is not ready")
                if not state["chapters"] or not all(state["current"].values()):
                    issues.append("chapters have missing/stale checkpoints")
                if sum(c["budget_pages"] for c in state["chapters"].values()) < plan["page_goal"]["minimum"]:
                    issues.append("chapter page budget is below the minimum")
                if set(state["reqs"]) - {rid for c in state["chapters"].values() for rid in c["requirement_ids"]}:
                    issues.append("requirements lack a primary chapter")
                if any(state["supplements"][sid]["priority"] != "optional" for sid in state["supplement_open"]):
                    issues.append("required supplements remain open")
                if state["asset_bad"] or state["source_bad"]:
                    issues.append("assets or sources are missing/stale")
                if state["reference_state"] and state["reference_state"]["global_issues"]:
                    issues.append("citation registry contains unbound entries")
                r, g = plan["rendered"], plan["page_goal"]
                if not file_ok(root, r["path"], r["sha256"]) or not file_ok(root, r["qa_path"], r["qa_sha256"]):
                    issues.append("current rendered document and page-count/QA record are missing/stale")
                elif r["sha256"] not in local_path(root, r["qa_path"]).read_text(encoding="utf-8"):
                    issues.append("page-count/QA record does not bind the current document hash")
                elif assembly_stamp(state, root) not in local_path(root, r["qa_path"]).read_text(encoding="utf-8"):
                    issues.append("page-count/QA record is stale against the current chapter assembly")
                if r["pages"] < g["minimum"] or g["maximum"] and r["pages"] > g["maximum"] or r["count_scope"] != g["count_scope"]:
                    issues.append("recorded pages/counting scope do not meet the page goal")
                for issue in issues:
                    print("PENDING " + issue)
                print("Recorded page counts still require actual counting evidence and full-page QA; no release or submission is performed.")
                return 1 if issues else 0
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print("LONG TASK ERROR " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
