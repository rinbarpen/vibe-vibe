---
name: visio
description: Microsoft Visio diagram creation via Draw.io→VSDX bridge. Since Visio has no API or MCP server, uses Draw.io MCP for creation then draw.io desktop for VSDX export. For enterprise/client deliverables requiring .vsdx format.
---

# Visio

Microsoft Visio format support via Draw.io bridge workflow. Since Visio has no programmatic API or MCP server, the recommended path is: draw in Draw.io MCP → export to VSDX.

## When to Use

- Deliverable requires `.vsdx` format
- Enterprise/client mandates Visio
- Need Visio-specific stencils or templates
- BPMN with Visio stencils
- Data-linked shapes, org charts from Excel
- Integration with Microsoft Office ecosystem

**If VSDX is not required**: prefer [mermaid](../mermaid/SKILL.md) or [mermaid](../mermaid/SKILL.md).

## Draw.io → VSDX Workflow

### Step 1: Create in Draw.io
Use the [drawio sub-skill](../drawio/SKILL.md):
```
Draw a [diagram type] for [purpose]. Use standard shapes, orthogonal connectors, clear labels. Export as .drawio.
```

### Step 2: Export from Draw.io MCP
```
export_diagram to [filename].drawio
```

### Step 3: Convert to VSDX
**draw.io Desktop (free, recommended)**:
1. Download from https://github.com/jgraph/drawio-desktop/releases
2. Open `.drawio` file
3. File → Export as → VSDX

**drawio.com (online)**:
1. https://app.diagrams.net
2. File → Open from → Device → `.drawio`
3. File → Export as → VSDX

**Headless**:
```bash
drawio --export --format vsdx --output output.vsdx input.drawio
```

### Step 4: Polish in Visio
- Apply Visio themes and variants
- Add Visio-specific stencils (AWS/Azure/GCP, BPMN)
- Add data-linked shapes
- Adjust page setup (A4/Letter) for printing

## Visio Template Selection

| Purpose | Template | Tab |
|---------|----------|-----|
| Software architecture | UML Component | Software |
| Database schema | Crow's Foot DB Notation | Software |
| Network diagram | Detailed Network Diagram | Network |
| Flowchart | Basic Flowchart | Flowchart |
| Org chart | Organization Chart | Business |
| Floor plan | Floor Plan | Maps & Floor Plans |
| Timeline | Timeline | Schedule |
| BPMN | BPMN Diagram | Flowchart |

## Visio Conventions

- **Font**: Segoe UI 10-12pt labels, Calibri 14-16pt titles
- **Connectors**: Right-angle for architecture, curved for workflows
- **Layers**: Background, main, annotations
- **Page size**: A4 (210×297mm) or Letter (8.5×11")
- **Export**: PDF (vector) for review, PNG 300 DPI for embedding

## Diagram Type Mapping

| Diagram | Visio Template | Draw.io Equivalent |
|---------|---------------|-------------------|
| Flowchart | Basic Flowchart | Flowchart shapes |
| Org chart | Organization Chart | Org chart shapes |
| Network | Detailed Network Diagram | Network shapes |
| UML Class | UML Class | UML section |
| ERD | Crow's Foot DB Notation | ERD section |
| BPMN | BPMN Diagram | BPMN shapes |
| Floor plan | Floor Plan | Floor plan shapes |
| Cloud | AWS/Azure/GCP stencils | Cloud shapes |

## Limitations

- **No programmatic API** — Visio has no public API or MCP server
- **Conversion fidelity** — Draw.io→VSDX may need minor adjustments (lines, fonts)
- **Stencil differences** — some Draw.io shapes have no direct Visio equivalent
- **No live preview** — unlike Draw.io MCP, no browser-based preview

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Shapes misplaced after import | Re-apply Visio auto-layout |
| Fonts different after export | Set Visio default font before import |
| Connectors become straight | Use orthogonal connectors in Draw.io |
| Cloud icons missing | Download official Visio stencils |
