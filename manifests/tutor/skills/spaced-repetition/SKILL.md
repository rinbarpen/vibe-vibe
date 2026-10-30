---
name: spaced-repetition
description: SM-2 间隔重复调度技能。基于 SuperMemo SM-2 算法实现闪卡创建、调度、复习、难度调整、统计分析。
dependencies: []
---

# 间隔重复调度 (Spaced Repetition)

## 概述

基于 SuperMemo SM-2 算法，管理闪卡从创建到稳定的全生命周期。

## SM-2 算法参数

### 质量评分

| 评分 | 含义 | 操作 |
|------|------|------|
| 5 | 完美回忆 | interval × EF |
| 4 | 稍有迟疑 | interval × EF |
| 3 | 较困难但正确 | interval × EF |
| 2 | 错误但答案熟悉 | 重置为 1 天 |
| 1 | 完全错误 | 重置为 1 天 |
| 0 | 完全忘记 | 重置为 1 天 |

### 间隔计算

```
第一次复习:   1 天
第二次复习:   6 天
第 n 次复习:  interval(n) = interval(n-1) × EF
评分 < 3:     interval 重置为 1 天
```

### 易度因子 (EF)

```
EF' = EF + (0.1 - (5-q) × (0.08 + (5-q) × 0.02))
EF 最小值: 1.3
初始 EF:  2.5
```

## 核心准则

### 最小信息原则
- 每张卡片只测试一个知识点
- 每个问题必须有唯一确定的答案

### 卡片格式

```markdown
## Q: [问题]
A: [答案]
Source: [材料名, 页码]
Deck: [主题]
Created: [日期]
Interval: [天数]
EF: [易度因子]
```

## 使用场景

- 语言学习的词汇记忆
- 学科概念的精确回忆
- 考试备考的系统复习

## Tutor 集成

本技能用于已有卡片的真实调度，不是普通学习/复习的前置。无卡片按 `commands/review/COMMAND.md` 使用笔记和实际问题；没有用户评分不虚构质量值或改调度。通用卡片可 provenance: general，不伪造教材出处；作答前不展示答案。
