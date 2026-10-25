---
name: omnidraw
description: Unified drawing and diagram command center with sub-skills for Draw.io, Mermaid, Visio, GPT-Image-2, Nano Banana Pro v1/v2, PlantUML, Excalidraw, matplotlib, canvas-design, scientific-schematics, and CCFA Visual Composer. Routes user requests to the best tool based on intent and scenario (patent, paper, architecture, presentation, UML, creative, etc.).
---

# Omnidraw

Routes drawing requests to the right sub-skill based on **what you need** and **what scenario you're in**.

![Omnidraw 工作流：按图意路由、保留图源、审阅并迭代](assets/workflow.svg)

[可编辑 Mermaid 图源](assets/workflow.mmd)。流程图展示本技能的路由与审阅闭环。

## 安装后的路由与办公配图

- 先读本技能内所选子目录的 `SKILL.md`；例如 `mermaid/` 的语法与模板可独立使用。仅检查本次路线需要的工具，不要求初始化全部上游子模块。
- 文中 `../../skills/...` 链接是**源码仓库内的可选上游参考**。安装到项目后，先按技能名发现当前可用的已安装 skill（如 `ccf-visual-composer`），再读取其真实路径；不沿用失效的仓库相对路径，不把缺少可选上游当成全部绘图路线不可用。
- 办公配图统一从 Omnidraw 分流：流程/逻辑说明优先本地 Mermaid，精确布局选 Draw.io；插画/照片选可用图像工具；真实数据图选 matplotlib。文字、单位、来源、图意和视觉一致性均需审阅，问题回到制作路线修复。
- 保留可编辑图源、预览、题注/替代文本和来源；文档角色负责嵌入原生办公文件。表格内容、合计与单位交给当前可用的 `omnisheet` 技能，避免把可编辑表格当成配图截图。

## Sub-Skills

| Sub-Skill | Best For | Deps |
|-----------|----------|------|
| [drawio](drawio/SKILL.md) | Flowcharts, architecture, network, cloud, patent/academic | drawio MCP + drawio-skills submodule |
| [mermaid](mermaid/SKILL.md) | Sequence, ERD, Gantt, git, mindmap, state, quick markdown | 本地语法可直接使用；渲染器按环境选择，上游 Pretty-mermaid-skills 可选 |
| [visio](visio/SKILL.md) | VSDX format, BPMN, enterprise deliverables | Draw.io bridge |
| [gpt-image-2](gpt-image-2/SKILL.md) | Illustrations, concept art, logos, photos (OpenAI) | `OPENAI_API_KEY` |
| [nano-banana](nano-banana/SKILL.md) | Photos, concept art, fast iteration (fal-ai v1/v2) | fal-ai MCP |
| [plantuml](plantuml/SKILL.md) | UML (class, use case, activity, component, deployment) | None |
| [excalidraw](excalidraw/SKILL.md) | Hand-drawn sketches, whiteboard, wireframes | None |
| [matplotlib](matplotlib/SKILL.md) | Data charts, publication figures, statistical plots | Python |
| [canvas-design](canvas-design/SKILL.md) | Posters, design artifacts | canvas-design skill |
| [scientific-schematics](scientific-schematics/SKILL.md) | Publication schematics, mechanism diagrams | scientific MCP |
| [ccf-visual-composer](../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) | CCF-A paper figures, visual tables, method/architecture diagrams, and editable reconstruction | CCFA-Skills; GPT Image 2 by default, pure SVG on request |

## Scenario Dispatch

### 专利附图
→ [drawio](drawio/SKILL.md) (结构/流程/电路图, A–H format, 15px, B&W)
→ [matplotlib](matplotlib/SKILL.md) (数据图)

### 学术论文图 — English (IEEE/ACM/Elsevier/Springer)
→ [drawio](drawio/SKILL.md) (架构图, grayscale, EPS/PDF, LaTeX)
→ [mermaid](mermaid/SKILL.md) (序列图)
→ [matplotlib](matplotlib/SKILL.md) (数据图, 300 DPI, serif)
→ [scientific-schematics](scientific-schematics/SKILL.md) (机制图)
→ [ccf-visual-composer](../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) (方法架构、流程、图形摘要、视觉表格；可编辑 SVG/PDF/PPTX)

### 学术论文图 — 中文 (中国科学/计算机学报/软件学报)
→ [drawio](drawio/SKILL.md) (架构图/流程图, 宋体, 双语图注)
→ [matplotlib](matplotlib/SKILL.md) (数据图, 中文标签)
→ [ccf-visual-composer](../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) (中文/中英方法图、科研示意图与图形摘要)

### 技术架构图
→ [drawio](drawio/SKILL.md) (系统/云/网络架构)
→ [mermaid](mermaid/SKILL.md) (C4, 快速上下文图)

### 流程/逻辑图
→ [mermaid](mermaid/SKILL.md) (快速内联)
→ [drawio](drawio/SKILL.md) (精确布局)

### 数据图表
→ [matplotlib](matplotlib/SKILL.md) (编程生成, 发表级)
→ [mermaid](mermaid/SKILL.md) (快速饼图/柱状图)

### 演示文稿 / Pitch Deck
→ [nano-banana](nano-banana/SKILL.md) (v2, 16:9 hero images)
→ [gpt-image-2](gpt-image-2/SKILL.md) (概念插图)
→ [drawio](drawio/SKILL.md) (架构 slides)
→ [matplotlib](matplotlib/SKILL.md) (数据 chart slides)

### 照片 / 真实感图像
→ [nano-banana](nano-banana/SKILL.md) (v2, best quality)
→ [gpt-image-2](gpt-image-2/SKILL.md) (detailed prompt following)

### 概念艺术 / 插画
→ [gpt-image-2](gpt-image-2/SKILL.md) (详细提示词跟随)
→ [nano-banana](nano-banana/SKILL.md) (v2, 快速视觉探索)

### UML 建模
→ [plantuml](plantuml/SKILL.md) (类图/用例/组件/部署)
→ [mermaid](mermaid/SKILL.md) (序列/状态)

### Visio 格式交付
→ [visio](visio/SKILL.md) (Draw.io→VSDX bridge)
→ [drawio](drawio/SKILL.md) (creation, export to VSDX)

### 手绘 / 白板风格
→ [excalidraw](excalidraw/SKILL.md) (rough.js aesthetic)

### 海报 / 设计产物
→ [canvas-design](canvas-design/SKILL.md) (design-focused)
→ [gpt-image-2](gpt-image-2/SKILL.md) (视觉概念生成)

### 科研示意图
→ [scientific-schematics](scientific-schematics/SKILL.md) (发表级)
→ [drawio](drawio/SKILL.md) (fallback)
→ [ccf-visual-composer](../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) (视觉契约、审美稿、渲染质检与可编辑重建)

### 快速内联 (Markdown)
→ [mermaid](mermaid/SKILL.md) (零设置, GitHub/Notion/Obsidian 原生渲染)

## Routing Matrix

### Diagrams

| Intent | Primary | Fallback |
|--------|---------|----------|
| Flowchart / process | [drawio](drawio/SKILL.md) | [mermaid](mermaid/SKILL.md) |
| System architecture | [drawio](drawio/SKILL.md) | [mermaid](mermaid/SKILL.md) (C4) |
| Network topology | [drawio](drawio/SKILL.md) | — |
| Cloud (AWS/GCP/Azure) | [drawio](drawio/SKILL.md) | — |
| Sequence diagram | [mermaid](mermaid/SKILL.md) | [drawio](drawio/SKILL.md) |
| UML class / use case | [plantuml](plantuml/SKILL.md) | [drawio](drawio/SKILL.md) |
| UML activity / component / deployment | [plantuml](plantuml/SKILL.md) | [drawio](drawio/SKILL.md) |
| State machine | [mermaid](mermaid/SKILL.md) | [plantuml](plantuml/SKILL.md) |
| ER diagram | [mermaid](mermaid/SKILL.md) (ERD) | [drawio](drawio/SKILL.md) |
| Gantt / timeline | [mermaid](mermaid/SKILL.md) | [drawio](drawio/SKILL.md) |
| Pie / simple chart | [mermaid](mermaid/SKILL.md) | [matplotlib](matplotlib/SKILL.md) |
| Bar / line / scatter / heatmap | [matplotlib](matplotlib/SKILL.md) | [mermaid](mermaid/SKILL.md) |
| Git branch graph | [mermaid](mermaid/SKILL.md) (git) | — |
| Mind map | [mermaid](mermaid/SKILL.md) (mindmap) | [drawio](drawio/SKILL.md) |
| BPMN | [visio](visio/SKILL.md) | [drawio](drawio/SKILL.md) |
| Org chart | [drawio](drawio/SKILL.md) | [visio](visio/SKILL.md) |
| Wireframe / sketch | [excalidraw](excalidraw/SKILL.md) | [drawio](drawio/SKILL.md) |
| Infographic | [drawio](drawio/SKILL.md) | [canvas-design](canvas-design/SKILL.md) |

### Images

| Intent | Primary | Fallback |
|--------|---------|----------|
| Photo-realistic | [nano-banana](nano-banana/SKILL.md) (v2) | [gpt-image-2](gpt-image-2/SKILL.md) |
| Quick concept iteration | [nano-banana](nano-banana/SKILL.md) (v1) | [nano-banana](nano-banana/SKILL.md) (v2) |
| Illustration / concept art | [gpt-image-2](gpt-image-2/SKILL.md) | [nano-banana](nano-banana/SKILL.md) (v2) |
| Logo / icon | [gpt-image-2](gpt-image-2/SKILL.md) | [nano-banana](nano-banana/SKILL.md) (v2) |
| Poster / design | [canvas-design](canvas-design/SKILL.md) | [gpt-image-2](gpt-image-2/SKILL.md) |
| Scientific schematic | [scientific-schematics](scientific-schematics/SKILL.md) | [drawio](drawio/SKILL.md) |
| Research illustration / graphical abstract | [ccf-visual-composer](../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) | [scientific-schematics](scientific-schematics/SKILL.md) |

> Full matrix with capability comparisons: [references/routing-matrix.md](references/routing-matrix.md)

## Multi-Tool Workflows

### Architecture → Visio Deliverable
1. [drawio](drawio/SKILL.md) → create diagram with MCP
2. [drawio](drawio/SKILL.md) → export as `.drawio`
3. [visio](visio/SKILL.md) → convert to VSDX via draw.io desktop
4. [visio](visio/SKILL.md) → polish in Microsoft Visio

### Paper Figure Pipeline
1. [drawio](drawio/SKILL.md) → architecture/pipeline diagram (grayscale, LaTeX)
2. [matplotlib](matplotlib/SKILL.md) → results/data chart (300 DPI, serif)
3. Combine, export EPS/PDF for submission

### CCFA Publication Visual Pipeline
1. [ccf-visual-composer](../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) → define the visual contract and content-fit topology
2. Generate and inspect the raster aesthetic draft with GPT Image 2 by default, or use the explicit pure-SVG route when requested
3. Verify labels, representations, operators, branches, merges, outputs, evidence boundaries, and paper-versus-presentation grammar
4. After the composition is accepted, reconstruct semantic SVG/vector PDF/editable PPTX and run render QA

### Presentation Deck
1. [nano-banana](nano-banana/SKILL.md) → hero image (v2, 16:9)
2. [drawio](drawio/SKILL.md) → simplified architecture slide
3. [matplotlib](matplotlib/SKILL.md) → data chart slide
4. [gpt-image-2](gpt-image-2/SKILL.md) → concept illustration

### Image Iteration
1. [nano-banana](nano-banana/SKILL.md) → v1 quick iterations (3 directions)
2. [nano-banana](nano-banana/SKILL.md) → v2 refine best direction
3. [gpt-image-2](gpt-image-2/SKILL.md) → alternative style variant

## Best Practices

1. **Scenario first** — patent? paper? presentation? The scenario drives tool choice.
2. **Prefer zero-dependency** when quality equivalent (Mermaid > Draw.io for quick flows)
3. **v1 for explore, v2 for final** (Nano Banana) — save time and cost
4. **Draw.io for precise layout** — Mermaid auto-layout can't be pixel-tuned
5. **Don't fight the tool** — UML → PlantUML, photos → Nano Banana, data → matplotlib
6. **Be specific** — name output format, resolution, color/B&W, target venue
7. **Iterate** — generate draft, review, refine (especially for images)

## Template Reference

- [references/routing-matrix.md](references/routing-matrix.md) — Full 50+ row decision table with tool capability comparison
- [templates/scenario-prompts.md](templates/scenario-prompts.md) — Copy-paste dispatch prompts for 15+ scenarios
- Each sub-skill's `SKILL.md` for per-tool quick starts and templates
