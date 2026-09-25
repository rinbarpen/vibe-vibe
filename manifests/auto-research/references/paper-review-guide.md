# Automated Paper Review Guide

投稿前默认采用三路并行独立评审（`paper-review`、`academic-paper-reviewer`、gptweb ICLR prompt）；评审派发、gptweb API 调用和综合规则见 [`multi-review.md`](multi-review.md)，可直接使用的 gptweb prompt 见 [`iclr-review-prompt.md`](iclr-review-prompt.md)。下文描述的 ARIS `auto-review-loop` 是另外的循环评审流程，不取代三路独立评审。

## 概述

自动论文评审能力由 aris 中的三个技能提供：

| 技能 | 用途 | 评审轮数 |
|------|------|----------|
| auto-review-loop | 通用研究评审循环 | 最多 4 轮 |
| auto-paper-improvement-loop | 论文改进循环（GPT-5.4 xhigh） | 2 轮 |
| rebuttal | 审稿回复生成 | 1 轮 |

附加校验技能：
- `paper-claim-audit` — 论文中数值声明与原始结果文件的一致性校验
- `citation-audit` — 参考文献的 DBLP/arXiv 交叉验证

## auto-review-loop 工作原理

### 输入
- 论文草稿（LaTeX / Markdown / PDF）
- 可选：评审重点（method / experiment / writing 等）

### 评审流程

```
Round 1: 初始评审
    ↓ 生成评审报告（分数、优缺点、建议）
    ↓
Round 2: 改进后评审
    ↓ 基于修改后的论文再次评审
    ↓
Round 3: 深度评审
    ↓ 更严格的评估标准
    ↓
Round 4: 终审
    ↓ 决策：accept / minor revision / major revision / reject
```

### 输出
- 结构化评审报告：
  - Overall score（1-10）
  - Strengths（3-5 条）
  - Weaknesses（3-5 条）
  - Specific suggestions（逐条）
  - Decision recommendation

### 难度级别

| 级别 | 评判标准 | 适用场景 |
|------|----------|----------|
| medium | 一般会议标准 | 标准论文 |
| hard | 顶会标准 | 重要投稿 |
| nightmare | 最严格标准 | 关键验收 |

## auto-paper-improvement-loop

### 特点
- 使用 GPT-5.4 xhigh 模式的深度评审
- 2 轮改进循环
- 评审者独立性协议：每轮 fresh review thread

### 流程
```
论文草稿 → GPT-5.4 评审 → 根据意见修改 → 再次评审 → 终稿
```

## rebuttal（审稿回复）

### 输入
- 评审意见（来自 auto-review-loop 或外部评审）
- 当前论文版本

### 输出
- 结构化回复表：每行 = 评审意见 → 回复 → 对应修改
- 修改摘要：列出所有修改点
- 字符数约束（按会议要求）

## 评审者独立性协议

核心约束（来自 ARIS shared-references）：

```
评审者必须从原始工件直接形成自己的评估。
执行者不得在评审前预先消化或总结论文内容给评审者。
```

具体规则：
1. 评审者独立访问原始论文文件，不经过执行者过滤
2. 执行者不生成"供评审者阅读的摘要"
3. 每轮评审使用独立会话（不缓存上下文）
4. 评审者之间不共享上下文

## 数值声明校验 (paper-claim-audit)

自动提取论文中的所有数值声明并与原始结果文件逐条比对：

| 论文声明 | 结果文件值 | 一致? |
|----------|-----------|-------|
| "accuracy 92.3%" | 92.31% | ✅ |
| "improvement 5.2%" | 5.1% | ⚠️ 偏差 0.1% |

## 引用校验 (citation-audit)

自动检查：
- BibTeX 条目完整性（author, title, year, venue, DOI）
- 引用是否存在（DBLP/arXiv 交叉验证）
- 格式是否符合目标会议标准
