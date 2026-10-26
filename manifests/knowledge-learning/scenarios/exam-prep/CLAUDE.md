# CLAUDE.md — Exam Preparation Scenario

## Focus

备考模式：以考试大纲为导向，强调密集复习、错题分析和模拟测试。

## Commands

| Command | Description |
|---------|-------------|
| `/learn <topic>` | 按考试大纲结构化学习 |
| `/flashcard <topic>` | 密集生成考试相关闪卡（默认 count=30） |
| `/review <topic>` | 高频复习 + 错题重做 |
| `/track progress` | 监控备考进度和薄弱环节 |

## 教材上传与章节规划

上传教材先轻量索引并展示 `projects/<教材或主题>/MATERIAL_INDEX.md`，再按 `/learn [topic] --plan [--material <path>]` 与 `references/learning-path-design.md` 生成同项目 `LEARNING_PATH.md`。复用已知目标、基础、已学范围，只补问缺失项；未指定范围覆盖所选教材。基础未知不视为掌握，缺章节/页码/习题信息标待补。

本场景的学习、复习和进度规则仅在相应学习活动中使用，不覆盖 `--plan`：规划阶段不全书提取笔记/闪卡、不排日/周课表、不要求时长或截止日期、不自动启动学习或持续任务。

## Scenario Rules

- 以考试大纲为知识组织骨架
- `/flashcard` 强度加倍（默认 count=30）
- 重点：错题分析与针对性补强
- 模拟测试后自动生成薄弱知识点报告
- 复习采用 spaced repetition + 交错练习
