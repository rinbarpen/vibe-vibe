---
description: 有卡片使用 SM-2，无卡片根据笔记、问题和实际作答记录进行对话复习
globs: ["flashcards/**/*", "projects/**/*", "notes/**/*"]
---

# /review

```text
/review [topic] [--limit 20] [--mode recall|cloze|qa]
```

遵循 `references/tutor-interaction.md`，先读当前项目 `LEARNING_RECORD.md` 和相关笔记，范围不明才问。用户要概览回顾则先总结，不强制测验。

## 有卡片

使用已有 SM-2 数据，按到期时间优先、同日可交错主题，默认最多 `REVIEW_LIMIT=20` 张。逐张展示题面，等真实回答或自评再给反馈，不先展示答案。保留 0–5 质量评分与 EF/间隔更新，具体算法见 `skills/spaced-repetition/SKILL.md`；没有评分不伪造评分或更改调度。材料卡片可回溯实际来源，通用知识卡片按 provenance 标识，不造页码。

## 没有卡片或当前主题无到期卡

明确当前无卡片/到期卡，直接根据已有笔记、遗留问题和真实错误组织简短回顾或逐题检索练习，不要求先生成闪卡。没有历史也可按用户指定主题做基础回顾，说明这是通用复习而非“上次学过”。

## 记录

题目、待答状态、实际回答与反馈按 `references/learning-records.md` 保存，未作答/未测保留未作答/未评估；非卡片练习不伪造 SM-2 调度数据。新解释形成知识增量时自动更新图文 Markdown，不重复归档原内容。默认低打扰保存；查看复习数据而非开始复习时只读。
