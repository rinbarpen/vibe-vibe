---
description: 基于学习材料生成知识图谱可视化，展示概念层级关系和跨材料连接
globs: ["notes/**/*"]
---

# /mindmap

## Purpose

生成主题的知识图谱，以 Mermaid 流程图或 Markdown 大纲形式展示概念层级、跨材料连接。

## Usage

```
/mindmap <topic>                     # 生成知识图谱
/mindmap <topic> --depth 3           # 展开到 3 层深度
/mindmap <topic> --format mermaid    # Mermaid 流程图格式
/mindmap <topic> --format outline    # Markdown 大纲格式
```

Examples:
```
/mindmap 机器学习
/mindmap 微积分 --depth 3
/mindmap Python --format mermaid
```

## Execution Logic

1. 加载 topic 相关笔记（含 `[[wiki-link]]` 连接）
2. 构建概念关联图
3. 按深度层级展开（默认 depth=2）
4. 标注跨材料连接（不同来源的概念用不同颜色标记）
5. 输出: Mermaid 流程图 + Markdown 大纲

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `topic` | — | 图谱中心主题 |
| `--depth` | 2 | 展开层数 (max: 4) |
| `--format` | both | 格式: mermaid/outline/both |

## Strict Mode Behavior

- 教材节点标真实来源，通用知识节点标讲解/建议结构，不虚构出处
- 节点颜色区分来源材料

通用主题也可绘图，不以已有材料/笔记为门槛。除非明确只要大纲/图源，Mermaid 图需渲染成真实 SVG/PNG 并保留源；图像/alt/图注/相对路径及 PDF 规则见 `references/illustrated-notes.md`。
