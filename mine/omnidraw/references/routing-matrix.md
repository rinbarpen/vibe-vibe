# Omnidraw Routing Matrix

Full decision table mapping user intent to tool sub-skill. Includes capability comparison across all tools.

## How to Use

1. Identify the user's **intent** (what kind of diagram/image)
2. Check the **scenario** (patent, paper, presentation, etc.)
3. Dispatch to the **primary sub-skill**
4. Use **fallback** if primary is unavailable or unsuitable

---

## Routing Matrix: Intent → Sub-Skill

### Diagrams (Structured Visual Logic)

| Intent | Primary | Fallback | Notes |
|--------|---------|----------|-------|
| Flowchart / process | [mermaid](../mermaid/SKILL.md) | [mermaid](../mermaid/SKILL.md) | Mermaid for text-native diagrams |
| System architecture | [mermaid](../mermaid/SKILL.md) | [mermaid](../mermaid/SKILL.md) (C4) | Mermaid C4 for text-native architecture |
| Network topology | [mermaid](../mermaid/SKILL.md) | — | Use Mermaid or PlantUML syntax |
| Cloud (AWS/GCP/Azure) | [mermaid](../mermaid/SKILL.md) | — | Represent services with labeled nodes |
| Sequence diagram | [mermaid](../mermaid/SKILL.md) | [mermaid](../mermaid/SKILL.md) | PlantUML for alternate notation |
| Class diagram | [plantuml](../plantuml/SKILL.md) | [mermaid](../mermaid/SKILL.md) | PlantUML best UML class support |
| Use case diagram | [plantuml](../plantuml/SKILL.md) | [mermaid](../mermaid/SKILL.md) | Only PlantUML has native syntax |
| Activity diagram | [plantuml](../plantuml/SKILL.md) | [mermaid](../mermaid/SKILL.md) | PlantUML activity syntax best |
| Component diagram | [plantuml](../plantuml/SKILL.md) | [mermaid](../mermaid/SKILL.md) | — |
| Deployment diagram | [plantuml](../plantuml/SKILL.md) | [mermaid](../mermaid/SKILL.md) | — |
| Timing diagram | [plantuml](../plantuml/SKILL.md) | — | Only PlantUML has timing syntax |
| State machine | [mermaid](../mermaid/SKILL.md) | [plantuml](../plantuml/SKILL.md) | stateDiagram-v2 is clean |
| ER diagram / data model | [mermaid](../mermaid/SKILL.md) (ERD) | [plantuml](../plantuml/SKILL.md) | Mermaid for quick; PlantUML for detailed |
| DB schema (production) | [mermaid](../mermaid/SKILL.md) | [mermaid](../mermaid/SKILL.md) | Mermaid for text-native schema |
| Gantt chart | [mermaid](../mermaid/SKILL.md) | [mermaid](../mermaid/SKILL.md) | — |
| Timeline | [mermaid](../mermaid/SKILL.md) | [mermaid](../mermaid/SKILL.md) | — |
| Pie / donut | [mermaid](../mermaid/SKILL.md) | [matplotlib](../matplotlib/SKILL.md) | Mermaid for markdown; matplotlib for pub |
| Bar chart | [matplotlib](../matplotlib/SKILL.md) | [mermaid](../mermaid/SKILL.md) | matplotlib for precise control |
| Line / scatter / heatmap | [matplotlib](../matplotlib/SKILL.md) | — | matplotlib is the only option |
| Error bars / stats | [matplotlib](../matplotlib/SKILL.md) | — | matplotlib only |
| Git branch graph | [mermaid](../mermaid/SKILL.md) (git) | — | Mermaid only |
| Mind map | [mermaid](../mermaid/SKILL.md) (mindmap) | [mermaid](../mermaid/SKILL.md) | — |
| BPMN | [visio](../visio/SKILL.md) | [mermaid](../mermaid/SKILL.md) | Visio-specific production workflow is not routed here |
| Org chart | [mermaid](../mermaid/SKILL.md) | [visio](../visio/SKILL.md) | Use Mermaid/PlantUML for structured relationships |
| Wireframe / UI mockup | [canvas-design](../canvas-design/SKILL.md) | [mermaid](../mermaid/SKILL.md) | Canvas Design for visual mockups |
| Whiteboard / sketch | [canvas-design](../canvas-design/SKILL.md) | [mermaid](../mermaid/SKILL.md) | — |
| Infographic | [mermaid](../mermaid/SKILL.md) | [canvas-design](../canvas-design/SKILL.md) | — |
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
| Scientific schematic | Happy Figure + figure2pptx | [scientific-schematics](../scientific-schematics/SKILL.md) | Classify figure first; produce prompt and editable reconstruction |
| Mechanism diagram | Happy Figure + figure2pptx | [scientific-schematics](../scientific-schematics/SKILL.md) | — |
| Experimental setup | Happy Figure + figure2pptx | [scientific-schematics](../scientific-schematics/SKILL.md) | — |
| Research illustration / graphical abstract | [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) | [scientific-schematics](../scientific-schematics/SKILL.md) | Content-fit visual contract, render QA, editable SVG/PDF/PPTX |
| Multi-panel scientific comparison | [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) | [matplotlib](../matplotlib/SKILL.md) | Use supplied data; no invented values |
| Journal cover / scientific cover art | [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) | [nano-banana](../nano-banana/SKILL.md) | Editorial illustration, not a data claim |

---

## Scenario-Based Dispatch

### Patent Figures (专利附图)
- Structure/relationship → [mermaid](../mermaid/SKILL.md) (A–H format, 15px, B&W)
- Flowchart → [mermaid](../mermaid/SKILL.md)
- Circuit/connection → [mermaid](../mermaid/SKILL.md)
- Data chart → [matplotlib](../matplotlib/SKILL.md)

### Academic Paper — English (IEEE/ACM/Elsevier/Springer)
- Architecture/pipeline → [mermaid](../mermaid/SKILL.md) (grayscale, EPS/PDF, LaTeX)
- Sequence → [mermaid](../mermaid/SKILL.md)
- Data/results → [matplotlib](../matplotlib/SKILL.md) (300 DPI, serif)
- Mechanism → [scientific-schematics](../scientific-schematics/SKILL.md)
- Method architecture/workflow/graphical abstract/visual table → [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md) (editable SVG/vector PDF/PPTX)

### Academic Paper — Chinese (中文期刊)
- Architecture → [mermaid](../mermaid/SKILL.md) (宋体, 双语图注)
- Flowchart → [mermaid](../mermaid/SKILL.md) or [mermaid](../mermaid/SKILL.md)
- Data → [matplotlib](../matplotlib/SKILL.md) (中文标签, SimHei)
- Scientific illustration / graphical abstract → [ccf-visual-composer](../../../skills/CCFA-Skills/ccf-visual-composer/SKILL.md)

### Technical Documentation
- Architecture → [mermaid](../mermaid/SKILL.md)
- Sequence/API flows → [mermaid](../mermaid/SKILL.md) (GitHub native rendering)
- ERD → [mermaid](../mermaid/SKILL.md)
- Git graphs → [mermaid](../mermaid/SKILL.md)

### Presentation / Pitch Deck
- Hero images → [nano-banana](../nano-banana/SKILL.md) (v2, 16:9)
- Architecture slides → [mermaid](../mermaid/SKILL.md)
- Data charts → [matplotlib](../matplotlib/SKILL.md)
- Concept illustrations → [gpt-image-2](../gpt-image-2/SKILL.md)

### Software Design (UML)
- Class/use case/component/deployment → [plantuml](../plantuml/SKILL.md)
- Sequence → [mermaid](../mermaid/SKILL.md)
- State → [mermaid](../mermaid/SKILL.md)

### Enterprise / Client Deliverable
- VSDX required → [visio](../visio/SKILL.md) (Draw.io→VSDX bridge)
- Cloud architecture → [mermaid](../mermaid/SKILL.md)
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
