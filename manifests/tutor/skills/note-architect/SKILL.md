---
name: note-architect
description: 具体章节学习时自动整理图文 Markdown、真实图资源与原子知识链接；按需导出 PDF，保留用户原文和手改。
dependencies: []
---

# 笔记架构师 (Note Architect)

将当前实际学习范围组织为可持续更新的章节主笔记和按需生成的原子概念网络。具体章节讲解或讨论一旦产生真实知识增量，在**本轮回复结束前**自动保存 Markdown，不等用户额外说“做笔记”。教材导入与 `/learn --plan` 只建立材料地图/路线，不批量生成全书笔记；纯查看、纯导出和无学习增量的闲聊不创建空笔记。

## 主笔记、图资源与原子笔记

- 章节主笔记为 `notes/summaries/<教材或主题>/<单元ID>-<章节名>.md`，初次参考 `.cursor/templates/CHAPTER_NOTE.md.example`；有教材使用已核验材料/单元 ID 和来源；无教材使用稳定主题单元 ID、provenance: general、source: []，不要求上传或造章节。未讲内容不提前填满，练习只记实际出现的题目和作答。
- 独立可复用概念按需放在 `notes/atoms/<主题>/`，主笔记链接它们；跨概念/材料有依据才建立 `[[wiki-link]]`，不要为成网编造关系。
- 短定义、少量事实用文字，简短对比用表格；流程、分支、层级、多概念依赖与长且抽象关系优先实际图解，长线性内容分小节而不是塞入图框。图文决策、嵌图和 PDF 细则按 `references/illustrated-notes.md`，绘图执行可参照 `.cursor/commands/diagram/COMMAND.md`。
- 图像为 `notes/assets/<主题>/<稳定图ID>.svg` 或 `.png`，保留可编辑源，用相对 Markdown 图片链接嵌入。只有 Mermaid 代码不算可见图；实际验证渲染。每图有标题、alt、图注、来源或助手示意/推断标记及简短文字结论，不改变教材含义。

## 增量更新与作者边界

先读旧文件和资源，保留稳定文件名/图 ID。已有模板使用“助手整理（自动更新）”及 `<!-- AUTO-NOTES:START -->` / `<!-- AUTO-NOTES:END -->` 边界，只合并助手范围；用户手改即使在该范围也保留，另作补充或更正。无可靠边界时不重写旧文，追加本次增量小节。同一增量不重复落盘。

个人记录在 `projects/<教材或主题>/LEARNING_RECORD.md`，遵循 `references/learning-records.md`：

- 用户明确提供的原文笔记、问题、请记住的文本用引用块保存，与助手章节笔记/摘要分开。用户感受、目标、自评不强套教材 source；知识错误原文保留，核对反馈另列。
- 学习记录中的助手摘要只概述活动并链接章节主笔记，不转储聊天、整段讲解或内部推理。助手自动笔记只证明发生了整理，不证明用户已读、已练习或掌握。
- 重新索引/规划保留历史与原文；原文更正引用旧条目，用户明确删除则按指定范围删除，不再次复制应删内容。

## 按需 PDF 与保存反馈

Markdown 默认自动保存。自然语言“导出这份笔记为 PDF”或 `/learn`、`/study` 的 `--export pdf` 才执行项目内 `python scripts/export-notes.py INPUT.md --output OUTPUT.pdf`；纯转换已有笔记不重学、不记学习事件。先确认所选学习笔记和实际图链，不把 `LEARNING_RECORD.md` 的原文日志夹入；保留 MD/图源，已有 PDF 默认保留，明确同意后才加 `--force`，需要中文字体可加 `--font FONT_PATH`。

保存后核对文件、图链及本次覆盖范围；PDF 实际生成后检查中文、图像与版面，再反馈真实路径。渲染/导出未完成时说明具体待补项，不把未渲染代码当图片或 PDF 成品。

## 原子概念的渐进提炼

1. 提炼材料中的定义、事实和例子，保留真实 `[Source: 材料, 已核验位置]`；只摘取必要短句，不整段复制教材。
2. 用助手自己的语言重述并标明是解释，不冒充用户原话；独立补充按 `references/source-grounding.md` 标核验状态。
3. 连接相关概念，注明依赖/区别/例证等实际关系；不明关系标 `[inference]`。
4. 回到章节主笔记综合本次重点、图解与待解问题，不重复复制原子笔记全文。

原子笔记保留已有结构：

```markdown
---
title: 概念名称
source: [材料名, 已核验位置]
tags: [domain/pdf, topic/统计, status/seedling]
type: concept
confidence: high
created: YYYY-MM-DD
modified: YYYY-MM-DD
related: ["[[相关概念]]"]
---

# 概念名称

**定义**：材料中的核心定义。

**助手解释**：保持材料含义的重述。

**示例**：注明教材例子或助手生成。

**相关概念**：[[相关概念]]。

**待解问题**：只列实际存在的问题。
```

普通教学只在后台实际保存并核验，不重复列路径；首次建档、阶段总结、明确记录或导出时提示，失败立即说明。通用知识和教材事实的 provenance 遵循 `references/source-grounding.md`。
