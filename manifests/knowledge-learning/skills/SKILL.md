---
name: knowledge-learning
description: 个人知识管理与多载体学习技能集。上传教材后轻量索引并按真实章节规划学习路线，也支持具体单元提取、笔记、闪卡与复习。提供 9 个学习指令、4 个学习场景、6 套管理规则，采用严格源引用。
triggers:
  - pattern: "(import|learn|study|review|flashcard|mindmap|track|exam|diagram)( |$)"
    description: Knowledge-learning command trigger
  - pattern: "learn.*--plan"
    description: Textbook-grounded chapter planning
  - pattern: "(upload|add|load) (material|file|document|slide|pdf|video|article)"
    description: Material indexing trigger
  - pattern: "(上传.*(教材|资料)|根据.*(教材|资料).*规划|规划学习|教材学习路线)"
    description: 中文教材上传与章节规划
  - pattern: "(create|generate|make) (flashcard|study guide|summary|mindmap)"
    description: Learning material generation
  - pattern: "(review|recall|revise|reinforce|巩固|复习)"
    description: Review session trigger
  - pattern: "(track|monitor|check|progress|进度)"
    description: Progress tracking trigger
---

# Knowledge Learning

本目录是随 manifest 安装到项目根 `skills/` 的内置资源，不是额外的平台注册要求。

- 上传/导入：先用 `skills/material-processor/SKILL.md` 建立 `projects/<教材或主题>/MATERIAL_INDEX.md`，展示真实章节地图，不默认生成全书笔记和闪卡。
- `/learn [topic] --plan [--material <path>]` 或自然语言教材规划：读取 `references/learning-path-design.md`，复用已知目标、基础、已学范围，输出同项目的 `LEARNING_PATH.md`。只补问缺失信息，不排每日/每周课表；不依赖 NotebookLM 开关。
- 无 `--plan` 的 `/learn` 保持主动学习会话；具体单元才按需提取，其他复习、考试和图表指令继续按需使用。
- 教材事实、用户提供的信息、助手规划建议分开标识；每份材料分别索引，真实定位和未核验范围遵循 `references/source-grounding.md`。
