---
description: 从学习材料/笔记生成 SM-2 兼容的间隔重复闪卡，支持 QA/Cloze/Enumeration 格式
globs: ["flashcards/decks/**/*"]
---

# /flashcard

## Purpose

将知识笔记转化为 SM-2 间隔重复闪卡，支持多种卡片格式。遵循最小信息原则，每张卡片只测试一个知识点。

## Usage

```
/flashcard <topic>                   # 从主题笔记生成闪卡
/flashcard <topic> --count 20        # 生成 20 张卡片
/flashcard <topic> --format cloze    # 填空格式
/flashcard --all                     # 从所有笔记生成
```

Examples:
```
/flashcard 决策树
/flashcard 微积分 --count 30
/flashcard Python基础 --format cloze
/flashcard --all
```

## Execution Logic

1. 读取 topic 对应的笔记 (notes/atoms/ 和 notes/summaries/)
2. 提取可测试的原子知识点
3. 生成多种类型卡片:
   - Q&A: 正面问题 + 背面答案
   - Cloze: 填空，关键概念被遮挡
   - Enumeration: 列举类问题（触发最小信息检查）
4. 教材卡片标注真实 `[Source: 材料名, 已核验位置]`，通用卡片标 provenance: general 与通用知识/自拟说明
5. 输出到 `flashcards/decks/<topic>.md`

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `topic` | — | 卡片主题 |
| `--count` | 10 | 卡片数量 |
| `--format` | qa | 格式: qa/cloze/enum |

## Strict Mode Behavior

- 教材卡片必须标真实来源，通用知识卡片不编造教材出处
- 教材卡片答案基于已核验材料；通用卡片按 `references/source-grounding.md` 区分讲解/自拟与真正待核实内容
- AI 推理性扩展标注 `[inference]`
