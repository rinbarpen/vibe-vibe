# CLAUDE.md — Course Learning Scenario

## Focus

课程学习模式：跟随结构化课程（PPT + 课本 + 视频 + 习题），按教学进度推进。

## Commands

| Command | Description |
|---------|-------------|
| `/import <path>` | 导入课程材料到对应目录 |
| `/study <material>` | 按材料类型专项学习 |
| `/learn <topic>` | 基于课程材料学习 |
| `/learn [topic] --plan [--material <path>]` | 按教材真实章节规划路线 |
| `/flashcard <topic>` | 从课程内容生成闪卡 |

## 教材上传与章节规划

上传教材先轻量索引并展示 `projects/<教材或主题>/MATERIAL_INDEX.md`，再按 `/learn [topic] --plan [--material <path>]` 与 `references/learning-path-design.md` 生成同项目 `LEARNING_PATH.md`。复用已知目标、基础、已学范围，只补问缺失项；未指定范围覆盖所选教材。基础未知不视为掌握，缺章节/页码/习题信息标待补。

本场景的学习、复习和进度规则仅在相应学习活动中使用，不覆盖 `--plan`：规划阶段不全书提取笔记/闪卡、不排日/周课表、不要求时长或截止日期、不自动启动学习或持续任务。

## Scenario Rules

- 原件统一按载体保存到 `materials/<type>/`；课程-章节及配套资料关系写入项目材料索引，有依据才建立对应
- 用户已提供课程日历且要求按课学习时才同步进度；教材章节规划本身不生成或索要日历
- PPT + 课本 + 视频 + 习题按已核实的章节关系协同使用，不要求用户补齐全部载体
- 每次课程后有复习提醒
- 章节结束后进行综合测试
