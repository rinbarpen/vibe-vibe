# CLAUDE.md — Research Reading Scenario

## Focus

研究阅读模式：以问题为导向的深度文献阅读与综合。适用于论文阅读、技术调研、前沿追踪。

## Commands

| Command | Description |
|---------|-------------|
| `/import <path/url>` | 导入论文/技术报告 |
| `/study <material>` | 精读特定文献 |
| `/learn <topic>` | 基于文献学习 |

## 教材上传与章节规划

上传教材先轻量索引并展示 `projects/<教材或主题>/MATERIAL_INDEX.md`，再按 `/learn [topic] --plan [--material <path>]` 与 `references/learning-path-design.md` 生成同项目 `LEARNING_PATH.md`。复用已知目标、基础、已学范围，只补问缺失项；未指定范围覆盖所选教材。基础未知不视为掌握，缺章节/页码/习题信息标待补。

本场景的学习、复习和进度规则仅在相应学习活动中使用，不覆盖 `--plan`：规划阶段不全书提取笔记/闪卡、不排日/周课表、不要求时长或截止日期、不自动启动学习或持续任务。

## Scenario Rules

- 以研究问题为起点，而非预定课程大纲
- 重视文献追踪和前沿洞察
- 精读单篇文献时提取：问题 → 方法 → 结果 → 结论，导入时仅索引
- 有对应内容依据的文献间建立对比连接
- 用户请求综合阅读时产出文献综述 + 跨文献连接图，不在上传后默认生成
