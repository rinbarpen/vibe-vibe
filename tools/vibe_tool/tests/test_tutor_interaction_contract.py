"""Static Tutor contracts only: not a conversational/model quality test."""

from pathlib import Path
import re
import unittest


MANIFEST = Path(__file__).resolve().parents[3] / "manifests/tutor"


class TutorInteractionContractTests(unittest.TestCase):
    def read(self, rel):
        return (MANIFEST / rel).read_text(encoding="utf-8")

    def test_canonical_router_is_discoverable_across_entrypoints_and_scenarios(self):
        documents = ["CLAUDE.md", "AGENTS.md", ".cursorrules", "skills/SKILL.md",
                     "commands/COMMANDS.md", "commands/import/COMMAND.md",
                     "commands/learn/COMMAND.md", "commands/study/COMMAND.md",
                     "commands/review/COMMAND.md", "commands/exam/COMMAND.md",
                     "rules/tutor-core.mdc"]
        documents += [str(p.relative_to(MANIFEST)) for p in (MANIFEST / "scenarios").rglob("*.md*")]
        for rel in documents:
            with self.subTest(document=rel):
                self.assertIn("references/tutor-interaction.md", self.read(rel))
        text = self.read("references/tutor-interaction.md")
        for phrase in ("具体概念", "只上传", "上传并指定", "仅导入", "系统学", "只读",
                       "待答", "直接告诉答案", "换个话题", "无教材", "保存失败"):
            self.assertIn(phrase, text)

    def test_visible_tutoring_state_and_old_record_compatibility_are_defined(self):
        for rel in ("templates/LEARNING_RECORD.md.example", "references/learning-records.md"):
            with self.subTest(document=rel):
                text = self.read(rel)
                for phrase in ("当前辅导状态", "当前任务", "待答", "实际作答", "反馈",
                               "下一步", "暂停任务", "内部推理", "旧", "未作答"):
                    self.assertIn(phrase, text)
        self.assertIn("不自答推进", self.read("commands/study/COMMAND.md"))
        self.assertIn("不写入本区", self.read("templates/LEARNING_RECORD.md.example"))

    def test_general_knowledge_does_not_require_fabricated_material_sources(self):
        source = self.read("references/source-grounding.md")
        for phrase in ("通用知识讲解", "助手自拟", "真正待核实", "source: []", "provenance",
                       "PDF 页序", "印刷页码", "正文待核", "用户信息", "规划建议"):
            self.assertIn(phrase, source)
        self.assertIn("无材料时按主题单元规划", self.read("commands/learn/COMMAND.md"))
        self.assertIn("source: []", self.read("templates/CHAPTER_NOTE.md.example"))
        self.assertIn("主题规划，非教材目录", self.read("templates/LEARNING_PATH.md.example"))

    def test_exam_is_interactive_by_default_with_explicit_paper_mode(self):
        for rel in ("commands/exam/COMMAND.md", "skills/exam-generator/SKILL.md"):
            with self.subTest(document=rel):
                text = self.read(rel)
                for phrase in ("默认", "逐题", "--paper", "--count", "作答前", "题面", "未作答"):
                    self.assertIn(phrase, text)
                self.assertNotIn("✓", text)
        self.assertIn("没有卡片", self.read("commands/review/COMMAND.md"))
        self.assertIn("不伪造 SM-2", self.read("commands/review/COMMAND.md"))

    def test_no_fixed_timed_checks_or_every_turn_path_spam(self):
        for rel in ("AGENTS.md", "commands/learn/COMMAND.md", "skills/active-learning/SKILL.md",
                    "rules/tutor-review-discipline.mdc", "references/learning-methodologies.md"):
            with self.subTest(document=rel):
                self.assertNotRegex(self.read(rel), r"每(?:隔|约)?\s*20(?:[-–]\s*30)?\s*分钟")
        text = self.read("references/tutor-interaction.md")
        for phrase in ("首次建档", "阶段总结", "明确要求", "导出", "不反复列", "本轮回复结束前"):
            self.assertIn(phrase, text)

    def test_evaluations_distinguish_acceptance_prompts_from_executed_model_evidence(self):
        text = self.read("evaluations/README.md")
        cases = [int(number) for number in re.findall(r"^### (\d+)\.", text, re.MULTILINE)]
        self.assertEqual(cases, list(range(1, 19)))
        self.assertIn("不等于已执行结果", text)
        self.assertIn("不得冒充独立会话通过", text)


if __name__ == "__main__":
    unittest.main()
