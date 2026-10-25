# Omnidraw Routing Matrix

Full decision table mapping user intent to tool sub-skill. Includes capability comparison across all tools.

## How to Use

1. Identify the user's **intent** (what kind of diagram/image)
2. Check the **scenario** (patent, paper, presentation, etc.)
3. Dispatch to the **primary sub-skill**
4. Use **fallback** if primary is unavailable or unsuitable

办公文档的图统一先经过 Omnidraw；确定性流程说明优先本地 `mermaid`，精确图形布局再选 `drawio`，数据图以真实数据驱动 `matplotlib`。图源与预览一起交给格式制作人，图意/标签/数据复核不通过则回到制作路线迭代。表格语义与数值规格由已安装的 `omnisheet` 负责，而不是以图片代替原生表格。

**安装后解析**：本文件的 `../<sub-skill>/SKILL.md` 指向随 Omnidraw 一起安装的本地子技能；`../../../skills/...` 仅为源码仓库内可选上游参考。项目安装环境按 skill 名发现实际安装位置。只为所选路线检查依赖，本地 Mermaid 流程无需初始化全部子模块。

---

## Routing Matrix: Intent → Sub-Skill

### Diagrams (Structured Visual Logic)

| Intent | Primary | Fallback | Notes |
|--------|---------|----------|-------|
| Flowchart / process | [drawio](../drawio/SKILL.md) | [mermaid](../mermaid/SKILL.md) | Draw.io for publishable; Mermaid for quick |
| System architecture | [drawio](../drawio/SKILL.md) | [mermaid](../mermaid/SKILL.md) (C4) | Draw.io for precise icon placement |
| Network topology | [drawio](../drawio/SKILL.md) | — | Only Draw.io has network shapes |
| Cloud (AWS/GCP/Azure) | [drawio](../drawio/SKILL.md) | — | Only Draw.io has cloud icon sets |
| Sequence diagram | [mermaid](../mermaid/SKILL.md) | [drawio](../drawio/SKILL.md) | Mermaid faster; Draw.io for complex |
| Class diagram | [plantuml](../plantuml/SKILL.md) | [mermaid](../mermaid/SKILL.md) | PlantUML best UML class support |
| Use case diagram | [plantuml](../plantuml/SKILL.md) | [drawio](../drawio/SKILL.md) | Only PlantUML has native syntax |
| Activity diagram | [plantuml](../plantuml/SKILL.md) | [drawio](../drawio/SKILL.md) | PlantUML activity syntax best |
| Component diagram | [plantuml](../plantuml/SKILL.md) | [drawio](../drawio/SKILL.md) | — |
| Deployment diagram | [plantuml](../plantuml/SKILL.md) | [drawio](../drawio/SKILL.md) | — |
| Timing diagram | [plantuml](../plantuml/SKILL.md) | — | Only PlantUML has timing syntax |
| State machine | [mermaid](../mermaid/SKILL.md) | [plantuml](../plantuml/SKILL.md) | stateDiagram-v2 is clean |
| ER diagram / data model | [mermaid](../mermaid/SKILL.md) (ERD) | [plantuml](../plantuml/SKILL.md) | Mermaid for quick; PlantUML for detailed |
| DB schema (production) | [drawio](../drawio/SKILL.md) | [mermaid](../mermaid/SKILL.md) | Draw.io for production documentation |
| Gantt chart | [mermaid](../mermaid/SKILL.md) | [drawio](../drawio/SKILL.md) | — |
| Timeline | [mermaid](../mermaid/SKILL.md) | [drawio](../drawio/SKILL.md) | — |
| Pie / donut | [mermaid](../mermaid/SKILL.md) | [matplotlib](../matplotlib/SKILL.md) | Mermaid for markdown; matplotlib for pub |
| Bar chart | [matplotlib](../matplotlib/SKILL.md) | [mermaid](../mermaid/SKILL.md) | matplotlib for precise control |
| Line / scatter / heatmap | [matplotlib](../matplotlib/SKILL.md) | — | matplotlib is the only option |
| Error bars / stats | [matplotlib](../matplotlib/SKILL.md) | — | matplotlib only |
| Git branch graph | [mermaid](../mermaid/SKILL.md) (git) | — | Mermaid only |
| Mind map | [mermaid](../mermaid/SKILL.md) (mindmap) | [drawio](../drawio/SKILL.md) | — |
| BPMN | [visio](../visio/SKILL.md) | [drawio](../drawio/SKILL.md) | Visio has best BPMN stencils |
| Org chart | [drawio](../drawio/SKILL.md) | [visio](../visio/SKILL.md) | Draw.io faster; Visio for data-linked |
| Wireframe / UI mockup | [excalidraw](../excalidraw/SKILL.md) | [drawio](../drawio/SKILL.md) | Excalidraw hand-drawn fits wireframes |
| Whiteboard / sketch | [excalidraw](../excalidraw/SKILL.md) | [drawio](../drawio/SKILL.md) | — |
| Infographic | [drawio](../drawio/SKILL.md) | [canvas-design](../canvas-design/SKILL.md) | — |
| Technical documentation (embedded) | [mermaid](../mermaid/SKILL.md) | — | Renders natively in GitHub |

### Images (Raster / Generative)

| Intent | Primary | Fallback | Notes |
|--------|---------|----------|-------|
| Photo-realistic image | [nano-banana](../nano-banana/SKILL.md) (v2) | [gpt-image-2](../gpt-image-2/SKILL.md) | v2 quality; GPT-Image-2 for prompt adherence |
| Quick concept iteration | [nano-banana](../nano-banana/SKILL.md) (v1) | [nano-banana](../nano-banana/SKILL.md) (v2) | v1 faster and cheaper |
| Illustration / concept art | [gpt-image-2](../gpt-image-2/SKILL.md) | [nano-banana](../nano-banana/SKILL.md) (v2) | GPT-Image-2 follows prompts better |
| Logo / icon design | [gpt-image-2](../gpt-image-2/SKILL.md) | [nano-banana](../nano-banana/SKILL.md) (v2) | — |
| Poster / design artifact | [canvas-design](../canvas-design/SKILL.md) | [gpt-image-2](../gpt-image-2/SKILL.md) | canvas-design for design-focused |
| Product mockup | [nano-banana](../nano-banana/SKILL.md) (v2) | [gpt-image-2](../gpt-image-2/SKILL.md) | — |
| Abstract / texture / bg | [nano-banana](../nano-banana/SKILL.md) (v2) | [gpt-image-2](../gpt-image-2/SKILL.md) | — |
| Scientific schematic | [scientific-schematics](../scientific-schematics/SKILL.md) | [drawio](../drawio/SKILL.md) | Publication standards |
| Mechanism diagram | [scientific-schematics](../scientific-schematics/SKILL.md) | [drawio](../drawio/SKILL.md) | — |
| Experimental setup | [scientific-schematics](../scientific-schematics/SKILL.md) | [drawio](../drawio/SKILL.md) | — |
| Research illustration / graphical abstract | [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) | [scientific-schematics](../scientific-schematics/SKILL.md) | Content-fit visual contract, render QA, editable SVG/PDF/PPTX |
| Multi-panel scientific comparison | [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) | [matplotlib](../matplotlib/SKILL.md) | Use supplied data; no invented values |
| Journal cover / scientific cover art | [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) | [nano-banana](../nano-banana/SKILL.md) | Editorial illustration, not a data claim |

---

## Scenario-Based Dispatch

### Patent Figures (专利附图)
- Structure/relationship → [drawio](../drawio/SKILL.md) (A–H format, 15px, B&W)
- Flowchart → [drawio](../drawio/SKILL.md)
- Circuit/connection → [drawio](../drawio/SKILL.md)
- Data chart → [matplotlib](../matplotlib/SKILL.md)

### Academic Paper — English (IEEE/ACM/Elsevier/Springer)
- Architecture/pipeline → [drawio](../drawio/SKILL.md) (grayscale, EPS/PDF, LaTeX)
- Sequence → [mermaid](../mermaid/SKILL.md)
- Data/results → [matplotlib](../matplotlib/SKILL.md) (300 DPI, serif)
- Mechanism → [scientific-schematics](../scientific-schematics/SKILL.md)
- Method architecture/workflow/graphical abstract/visual table → [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) (editable SVG/vector PDF/PPTX)

### Academic Paper — Chinese (中文期刊)
- Architecture → [drawio](../drawio/SKILL.md) (宋体, 双语图注)
- Flowchart → [drawio](../drawio/SKILL.md) or [mermaid](../mermaid/SKILL.md)
- Data → [matplotlib](../matplotlib/SKILL.md) (中文标签, SimHei)
- Scientific illustration / graphical abstract → [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md)

### Technical Documentation
- Architecture → [drawio](../drawio/SKILL.md)
- Sequence/API flows → [mermaid](../mermaid/SKILL.md) (GitHub native rendering)
- ERD → [mermaid](../mermaid/SKILL.md)
- Git graphs → [mermaid](../mermaid/SKILL.md)

### Presentation / Pitch Deck
- Hero images → [nano-banana](../nano-banana/SKILL.md) (v2, 16:9)
- Architecture slides → [drawio](../drawio/SKILL.md)
- Data charts → [matplotlib](../matplotlib/SKILL.md)
- Concept illustrations → [gpt-image-2](../gpt-image-2/SKILL.md)

### Software Design (UML)
- Class/use case/component/deployment → [plantuml](../plantuml/SKILL.md)
- Sequence → [mermaid](../mermaid/SKILL.md)
- State → [mermaid](../mermaid/SKILL.md)

### Enterprise / Client Deliverable
- VSDX required → [visio](../visio/SKILL.md) (Draw.io→VSDX bridge)
- Cloud architecture → [drawio](../drawio/SKILL.md)
- BPMN → [visio](../visio/SKILL.md)

### Creative / Design
- Poster → [canvas-design](../canvas-design/SKILL.md)
- Logo → [gpt-image-2](../gpt-image-2/SKILL.md)
- Mood board → [nano-banana](../nano-banana/SKILL.md) (v1, multiple images)

---

## Tool Capability Comparison

| Capability | drawio | mermaid | visio | gpt-image-2 | nano-banana | plantuml | excalidraw | matplotlib | canvas-design | sci-schematics |
|-----------|--------|---------|-------|-------------|-------------|----------|------------|------------|--------------|----------------|
| Zero deps | ✗ | ✓ | ✗ | ✗ (API key) | ✗ (MCP) | ✓ | ✓ | ✗ (Python) | ✗ | ✗ (MCP) |
| Inline code | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Real-time preview | ✓ (MCP) | ✓ (live) | ✗ | ✗ | ✗ | ✗ | ✓ (web) | ✓ (GUI) | ✗ | ✗ |
| Vector export | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Raster export | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Cloud icons | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| LaTeX math | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| UML coverage | Med | Low | Med | ✗ | ✗ | High | ✗ | ✗ | ✗ | ✗ |
| Photo-realistic | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Hand-drawn style | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| Precise layout | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| Free / open source | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
