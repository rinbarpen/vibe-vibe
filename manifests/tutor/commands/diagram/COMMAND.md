---
description: 为学习概念生成真实本地图解和可编辑源；--attach 将图像嵌入已有 Markdown 笔记
globs: ["materials/images/**/*", "notes/**/*"]
---

# /diagram

## Purpose

为学习笔记生成可见的本地图表，保留可编辑图源。适用于流程、结构、层级、时间和多概念关系；短定义用文字，简短对比可以保留表格，不把内容机械转图。完整选择标准与 PDF 兼容要求见 `references/illustrated-notes.md`。

## Usage

```text
/diagram <concept>                         # 根据概念关系自动选类型
/diagram <concept> --type flowchart         # 流程图
/diagram <concept> --type timeline          # 时间线
/diagram <concept> --type comparison        # 简短对比表或复杂关系图
/diagram <note> --attach                    # 生成真实图像并嵌入现有笔记
/diagram <concept> --output both            # 图像文件与预览/源码说明
```

Examples:
```text
/diagram 决策树构建流程
/diagram 机器学习算法分类 --type mindmap
/diagram 线性回归vs逻辑回归 --type comparison
/diagram 微积分发展史 --type timeline
/diagram notes/summaries/决策树/U02-信息增益.md --attach
/diagram notes/atoms/决策树/信息增益.md --attach
```

## Diagram Types

| 类型 | 适用内容 | 默认产物 |
|------|----------|----------|
| `flowchart` | 步骤、算法、条件分支、反馈循环 | SVG/PNG + Mermaid 或 SVG 源 |
| `mindmap` | 概念层级、知识结构 | SVG/PNG + 可编辑源 |
| `architecture` | 组件、模型、系统结构 | SVG/PNG + SVG/drawio/Mermaid 源 |
| `timeline` | 有材料依据的发展顺序或事件 | SVG/PNG + 可编辑源 |
| `comparison` | 对齐少量维度用表格；复杂关系用对比图 | Markdown 表格或 SVG/PNG + 源 |
| `concept` | 多概念依赖和关系网络 | SVG/PNG + 可编辑源 |
| `auto` | 按信息结构选择，不按字数硬凑图 | 对应类型产物 |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `topic/note` | — | 概念名称或现有笔记路径 |
| `--type` | auto | flowchart/mindmap/architecture/timeline/comparison/concept/auto |
| `--attach` | false | 实际生成图像并以相对 Markdown 链接加入已有笔记；保留原文 |
| `--output` | inline | inline/file/both；控制回复展示，图像仍落地本地资源 |

`inline` 展示实际图像预览/Markdown 图片链接；`file` 只反馈已保存路径；`both` 提供二者。Mermaid/drawio 源可以链接或作为补充展示，但只有代码不算已交付图片。简短 `comparison` 表格保持 Markdown；用户明确要求附图或使用 `--attach` 时实际生成对比图而不是只追加表格。

## Execution Logic

1. **先读来源与旧笔记**：确定当前主题和源材料；`--attach` 读取目标笔记及图资源，保持用户原文、手改、已有文件名和图 ID。不凭主题相同就合并多份教材。
2. **选表达结构**：按 `references/illustrated-notes.md` 判断文字/表格/图。绘图时提取必要节点、边、层级和标签，不把整个段落塞进框内；未知关系标 `[inference]`，不补造教材因果或先修关系。
3. **生成真实资源**：保存 `notes/assets/<主题>/<稳定图ID>.svg` 或 `.png`，并保留 `.mmd`、`.drawio` 或标准 SVG 图源。可用现有 `mmdc -i SOURCE.mmd -o OUTPUT.svg`，或直接写可验证的标准 SVG；不用在线 CDN，也不只留下 Mermaid fence。已有 drawio 文件保留在原位置，另导出图像到上述资源目录。
4. **验证图像**：检查文件有效，实际渲染/打开检查中文、字号、箭头、重叠和裁切；复杂图拆成多图，每图聚焦一种关系。缺渲染器时尝试标准 SVG；仍未得到实际图就标“待渲染”，不称附图已完成。
5. **嵌入并解释**：`--attach` 在目标笔记助手整理范围加入相对于该 Markdown 的图片链接，配标题、alt、图注、来源或助手示意/推断标签和简短文字结论。同一图更新原 ID；没有可靠助手边界时保留原文并追加图解小节，不重写全篇。实际写入后再核对相对路径。
6. **反馈结果**：给出实际图像、图源和已更新笔记路径；`--output` 按对应方式展示。图像不是练习证据，不据此标记用户掌握；后续需要 PDF 时按笔记导出流程执行 `python scripts/export-notes.py INPUT.md --output OUTPUT.pdf`。

## 笔记嵌图形态

下面只说明结构，执行 `/diagram --attach` 时必须先实际生成并检查对应资源：

```markdown
### 图解：分裂与停止条件

![图 1：从候选分裂到检查停止条件的流程](../../assets/决策树/U02-分裂流程.svg)

*图 1 · [助手示意]；[Source: 教材.pdf, 决策树章节]。图源：[Mermaid](../../assets/决策树/U02-分裂流程.mmd)。*

结论：每次分裂后重新检查停止条件，满足条件时输出叶节点。
```

## Source Grounding

- 节点、关系和时间均基于实际源材料；图解引用精确到已核验的位置，PDF 页序与印刷页码分开。
- 绘图中的简化标 `[助手示意]`；没有材料直接支持的关系标 `[inference]` 并说明，不冒充教材原图。
- 对比维度和数字有来源；未核实的项写“待核”，不填一个看起来合理的值。

## 无教材与对话需求

也支持通用主题图解，不要求先上传；教材事实有真实引用，通用示意标“通用知识，助手示意”，不造出处。用户只要简短文字时不强制配图，当前任务按 `references/tutor-interaction.md`。
