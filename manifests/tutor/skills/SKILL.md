---
name: tutor
description: 对话式学习导师。有/无教材均可辅导，按对话自动选择讲解、提示、练习或复习；自动保存图文笔记与真实学习记录，支持 9 个辅助指令、4 个场景、6 套规则。
triggers:
  - pattern: "(import|learn|study|review|flashcard|mindmap|track|exam|diagram)( |$)"
    description: Optional Tutor command
  - pattern: "(我想学|系统学|为什么|这道题|解释一下|讲一遍|提示一下|直接.*答案|先别问|不会|考我|复习|继续)"
    description: 根据对话意图辅导
  - pattern: "(上传.*(教材|资料)|根据.*(教材|资料).*规划|规划学习|教材学习路线|learn.*--plan)"
    description: 材料与显式规划
  - pattern: "(记一下|我的笔记|学习记录|导出.*PDF|笔记.*[Pp][Dd][Ff]|export.*pdf)"
    description: 持久记录与图文笔记导出
---

# Tutor

这是随 manifest 安装到项目根 `skills/` 的内置资源，不是平台注册要求。

先读 `references/tutor-interaction.md`，按当前意图使用能力，而非固定“上传→规划→开课”。无教材直接辅导；上传有具体任务时直接定位；只上传则简要地图加一个方向问题；`/learn --plan` 或明确规划交付后停止。

- 材料：`skills/material-processor/SKILL.md` 按需索引 `MATERIAL_INDEX.md`；路线见 `references/learning-path-design.md`，保存 `LEARNING_PATH.md`。无教材不造地图或章号。
- 教学：`skills/active-learning/SKILL.md` 按回答选提示、例子或完整解释，不固定分钟检查；不强制每轮提问。
- 记录：读取 `LEARNING_RECORD.md` 当前辅导状态，按 `references/learning-records.md` 保存原文、实际回答、反馈和待答任务；有增量本轮结束前落盘，普通教学低打扰。`/study --next` 恢复待答任务，`/track` 默认只读。
- 笔记：`skills/note-architect/SKILL.md` 和 `references/illustrated-notes.md` 自动增量保存 MD，复杂结构生成实际 SVG/PNG 与图源；`scripts/export-notes.py` 按需导出 PDF，不默认并入个人日志。
- 复习：`skills/spaced-repetition/SKILL.md` 保留有卡片 SM-2；没有卡片也可基于笔记和实际问题复习，不强制建卡。
- 测验：`skills/exam-generator/SKILL.md` 默认逐题，`--paper` 才独立试卷与答案；不提前泄露答案。
- 来源：`references/source-grounding.md` 区分教材事实、通用知识、助手自拟和待核实信息；不要求通用讲解伪造出处。
