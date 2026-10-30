---
name: exam-generator
description: 自适应逐题测验和独立试卷生成，保留难度题型配置，严格区分自拟题与教材原题。
dependencies:
  - skills/note-architect/SKILL.md
  - skills/spaced-repetition/SKILL.md
---

# 测验与试卷

共用 `commands/exam/COMMAND.md` 的语义与 `references/tutor-interaction.md`。默认逐题，作答前不展示答案/正确标记；只有 `--paper` 或明确试卷请求才批量输出独立题面和答案。`--count` 只控制数量，不改变模式。

- 题型：choice（一个正确项和三个合理干扰项）、fill、short、essay、mixed。
- 难度：easy 识记/理解，medium 应用/分析，hard 综合/评价，mixed 可参考 3:4:3，实际范围和题量优先。
- 来源：教材原题必须核验题号，教材自拟题标“助手自拟，依据…”，无教材题标“通用知识，助手自拟”。不虚构页码、干扰项出处或全范围覆盖率。
- 用户请求提示时分步给提示，直接要求答案时给解答但不记用户已作答；反馈对准实际回答，不用助手答案冒充用户回答。
- 原题、必要选项、当前序号和待答状态保存至 `LEARNING_RECORD.md`；新会话恢复未答题，不自答推进。未作答/未评估不填成绩，只记录实际尝试、反馈及其证据范围。
- 已知知识点分母时可核验覆盖率；未知范围写覆盖未评估，不默认 ≥80%。批量出题也不预填练习成绩。
- 答案与解析保留真实教材依据或自拟标签，题面与答案分离；纸面试卷生成不等于用户已练习。
