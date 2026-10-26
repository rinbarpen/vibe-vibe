---
name: note-architect
description: 笔记架构技能。结构化原子笔记、渐进式提炼、[[wiki-link]] 知识网络构建、跨材料概念连接。
dependencies: []
---

# 笔记架构师 (Note Architect)

## 概述

将源材料提取的零散知识组织为结构化的笔记网络，支持渐进式提炼和跨材料连接。

教材导入与 `/learn --plan` 只建立材料地图/路线，不调用本技能批量生成全书笔记。以下生命周期用于用户开始具体单元学习或明确要求笔记提炼时；规划文件保留自己的结构，不套用原子笔记 frontmatter。

## 笔记生命周期

### Layer 1: 原文提取
- 直接来自材料的内容
- 保留原始表述
- 标注精确来源 `[Source: ...]`

### Layer 2: 用自己话重述
- 在原文基础上用自己的语言表述
- 保持概念准确性
- 加入个人理解

### Layer 3: 跨概念连接
- 建立 `[[wiki-link]]` 连接
- 识别不同材料中的同一概念
- 标注概念之间的关系类型

### Layer 4: 综合与提炼
- 跨材料的概念综合
- 识别模式与关系
- 输出到 notes/summaries/

## 笔记结构标准

```markdown
---
title: 概念名称
source: [材料名, 位置]
tags: [domain/xxx, topic/xxx, status/seedling]
type: concept|fact|question|exercise
confidence: high|medium|low
created: YYYY-MM-DD
---

# 概念名称

**定义**: 概念的精确定义（L1: 来自材料）

用自己的话重述（L2）

**示例**: 实际例子

**相关概念**: [[概念A]], [[概念B]]

**待解问题**:
- 未理解的部分
```
