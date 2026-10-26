# CLAUDE.md — Self-Study Scenario

## Focus

自主学习模式：无外部约束，以兴趣驱动、探索为导向的深度学习。

## Commands

| Command | Description |
|---------|-------------|
| `/learn <topic>` | 自定节奏学习会话 |
| `/study <material>` | 深入钻研特定材料 |

## 教材上传与章节规划

上传教材先轻量索引并展示 `projects/<教材或主题>/MATERIAL_INDEX.md`，再按 `/learn [topic] --plan [--material <path>]` 与 `references/learning-path-design.md` 生成同项目 `LEARNING_PATH.md`。复用已知目标、基础、已学范围，只补问缺失项；未指定范围覆盖所选教材。基础未知不视为掌握，缺章节/页码/习题信息标待补。

本场景的学习、复习和进度规则仅在相应学习活动中使用，不覆盖 `--plan`：规划阶段不全书提取笔记/闪卡、不排日/周课表、不要求时长或截止日期、不自动启动学习或持续任务。

## Scenario Rules

- 学习节奏由用户自定，无硬性截止日期
- 重点在于兴趣导向的深度理解和知识连接
- 推荐使用费曼技巧检验理解深度
- 鼓励跨材料探索和 `[[wiki-link]]` 扩展阅读
- 在已有学习会话中每隔 3-5 天提醒可使用 `/review`；不由教材规划创建后台复习或持续陪学任务
