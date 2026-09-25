"""Contract checks for the first-party AI visual workflow skill pack."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "ai-visual-content": "visual-content",
    "ai-image-workflow": "image",
    "ai-comic-workflow": "comic",
    "ai-manhua-workflow": "manhua",
    "ai-video-workflow": "video",
    "ai-ecommerce-visual": "ecommerce",
}


def _skill_text(name: str) -> str:
    return (ROOT / "mine" / name / "SKILL.md").read_text(encoding="utf-8")


def _frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    assert match, "SKILL.md must start with YAML frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def _continuity_errors(sequence: list[dict]) -> list[str]:
    errors = []
    previous = None
    previous_order = 0
    for item in sequence:
        if item["order"] <= previous_order:
            errors.append(f"non-increasing order at {item['sequence_id']}")
        if previous is not None:
            for entity_id, prior_state in previous.items():
                if entity_id in item["state_before"] and item["state_before"][entity_id] != prior_state:
                    errors.append(f"state discontinuity for {entity_id} at {item['sequence_id']}")
        previous = item["state_after"]
        previous_order = item["order"]
    return errors


def test_skill_pack_has_discriminating_frontmatter_and_modes():
    for name in SKILLS:
        text = _skill_text(name)
        metadata = _frontmatter(text)
        assert metadata["name"] == name
        assert metadata["description"]
        assert "快版" in text and "质量版" in text
        assert "## 稳定性与验收门槛" in text
        assert (ROOT / "mine" / name / "agents" / "openai.yaml").is_file()


def test_scenario_skills_support_references_and_quality_gates():
    for name in list(SKILLS)[1:]:
        text = _skill_text(name)
        assert "参考视频" in text
        assert "参考图" in text or "参考图片" in text
        assert "generation" in text
        assert "阻断/重大" in text
        assert "state_before" in text and "state_after" in text
        for relative in re.findall(r"\]\((references/[^)]+)\)", text):
            assert (ROOT / "mine" / name / relative).is_file(), relative


def test_serialized_templates_preserve_state_and_reproducibility_fields():
    required = {"schema_version", "project_id", "scenario", "mode", "references", "entities", "sequence", "outputs", "qa_issues"}
    for name, scenario in SKILLS.items():
        data = json.loads((ROOT / "mine" / name / "references" / "project-state-template.json").read_text(encoding="utf-8"))
        assert required <= data.keys()
        assert data["scenario"] == scenario
        assert data["mode"] in {"fast", "quality"}
        ref_ids = {ref["reference_id"] for ref in data["references"]}
        entity_ids = {entity["entity_id"] for entity in data["entities"]}
        sequence_ids = {item["sequence_id"] for item in data["sequence"]}
        assert len(ref_ids) == len(data["references"])
        assert len(entity_ids) == len(data["entities"])
        assert len(sequence_ids) == len(data["sequence"])
        for item in data["sequence"]:
            assert set(item["reference_ids"]) <= ref_ids
            assert set(item["state_before"]) <= entity_ids
            assert set(item["state_after"]) <= entity_ids
            assert {"tool", "workflow_id", "model", "model_version", "seed", "settings", "run_id"} <= item["generation"].keys()
            assert {"identity_or_product_facts", "action_and_relationship", "state_continuity", "reference_alignment", "detail_and_delivery"} <= item["quality_checks"].keys()
        assert (ROOT / "mine" / name / "references" / "continuity-template.md").is_file()


def test_sequential_state_contract_detects_a_broken_handoff():
    valid = [
        {"sequence_id": "P1", "order": 1, "state_before": {"CHAR-1": {"pose": "standing"}}, "state_after": {"CHAR-1": {"pose": "holding cup"}}},
        {"sequence_id": "P2", "order": 2, "state_before": {"CHAR-1": {"pose": "holding cup"}}, "state_after": {"CHAR-1": {"pose": "cup on table"}}},
        {"sequence_id": "P3", "order": 3, "state_before": {"CHAR-1": {"pose": "cup on table"}}, "state_after": {"CHAR-1": {"pose": "walking away"}}},
    ]
    assert _continuity_errors(valid) == []
    broken = [*valid[:2], {**valid[2], "state_before": {"CHAR-1": {"pose": "holding cup"}}}]
    assert any("state discontinuity" in error for error in _continuity_errors(broken))


def test_workflow_map_covers_all_five_scenarios_and_case_checks():
    matrix = (ROOT / "mine" / "ai-visual-content" / "references" / "workflow-map.md").read_text(encoding="utf-8")
    for label in ("AI 绘画/修图", "静态 AI 漫画", "AI 漫剧", "通用 AI 视频", "电商视觉"):
        assert label in matrix
    assert "代表性回归用例" in matrix
    assert "未关闭的阻断/重大问题不能标为通过" in matrix
