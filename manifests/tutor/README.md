# Tutor — 你的对话式学习导师

直接说想学什么、哪里没懂或希望怎样讲。有教材结合真实章节，无教材也能辅导；自动保存图文 Markdown 和学习记录，PDF 按需导出。

## 安装与旧项目升级

```bash
vibe init tutor "my learning project"
vibe init tutor "my course" --scenario course-learning
vibe add manifest tutor "/path/to/existing project" --force
vibe add manifest tutor "/path/to/existing project" --force --dry-run
```

旧名称 `knowledge-learning` 已停用，只提示新入口，不作为别名执行。已识别的旧项目不带 `--force` 时保持原样；显式升级先备份将覆盖的模板及将停用的旧规则，再安装 Tutor。教材、笔记、图源、PDF、`LEARNING_RECORD.md` 和自定义文件留在原位。备份在 `.vibe-tool/backups/tutor/<唯一ID>/`，安装输出可直接运行的 `python -B <备份目录>/restore.py`；恢复前核验备份和变更，升级后自行修改过的模板默认保留并提示，不静默覆盖。

重复安装默认保留文件；`--force` 仅替换对应模板并停用已知旧规则，不扫描删除自定义资料。未指定场景时沿用可识别旧场景；多场景遗留冲突在写入前提示使用 `--scenario`。可选场景为 `self-study`、`course-learning`、`exam-prep`、`research-reading`，只提供默认偏好，实际对话需求优先。

## 怎么交互

| 你说 | Tutor 做什么 |
|------|-------------|
| 我想学线性代数，刚接触 | 简短确认起点，给方向后开始一个单元 |
| 为什么这里不能求平均？ | 直接回答，不要求先上传教材 |
| 上传教材：帮我理解第二章 | 定位第二章并辅导，不强制全书规划 |
| 根据这本书规划学习 | 索引真实章节并保存路线，交付后停止 |
| 不会，提示一下 / 直接讲答案 | 按要求提示或完整解释，不强制固定教学法 |
| 考我一下 / 复习一下 | 逐题测验或按学习记录复习，没有卡片也可用 |
| 从上次继续 | 先恢复待答任务，再处理已确认位置，不猜上一章已完成 |
| 记一下，这是我的原话…… | 原文与助手整理分开保存 |
| 导出 PDF | 转换选定笔记，保留原件，不附带个人日志 |

入口详见 `CLAUDE.md`。九个可选指令见安装后的 `.cursor/commands/COMMANDS.md`；普通对话无需记命令。`/learn --plan`、`/exam --paper`、`--export pdf` 是助手参数，不是 vibe CLI 参数。

## 自动记录与图文笔记

- `projects/<教材或主题>/LEARNING_RECORD.md`：个人条件、原文、真实进度、实际作答及当前辅导状态，规则见 `references/learning-records.md`。
- `MATERIAL_INDEX.md`：仅有教材时建立，分开保存 PDF 页序/印刷页码及解析缺口；`LEARNING_PATH.md`：需要规划时保存，主题学习不造教材章节。
- `notes/summaries/<主题>/` 自动保存本轮学习增量为 MD；短内容文字表达，复杂关系用真实 SVG/PNG，图像与可编辑源放 `notes/assets/<主题>/`。见 `references/illustrated-notes.md`。
- 先读再更新，保留用户原文和手改；未作答不填成绩，讲过或生成笔记不等于掌握。普通教学不重复列保存路径，首次建档/阶段总结/明确记录/导出时提示，保存失败立即说明。
- PDF 按需调用 `scripts/export-notes.py`，需要本地 Pandoc 和 Chrome/Chromium；Mermaid 代码需本地渲染器或先绘制 SVG，不下载运行依赖。MD、图源和既有 PDF 默认保留。

内置技能在项目根 `skills/`，从 `skills/SKILL.md` 按需读取；角色说明在 `agents/tutor-agents.md`，不代表注册了原生子 Agent。通用辅导与教材引用边界见 `references/source-grounding.md`。自动指当前回合落盘，不是后台监听或定时任务；默认不排每日课表。

## 验证

安装与资源契约测试在仓库 `tools/vibe_tool/tests/`；真实会话验收案例在本 manifest 的 `evaluations/README.md`。静态检查不等于教学效果通过，PDF 成品需检查文字、图片与实际页面。
