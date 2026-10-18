---
name: drawio
description: Archived legacy reference. drawio is no longer supported or routed by Omnidraw.
---

# Draw.io

> Archived: this legacy reference is retained for history only and is not a supported Omnidraw route.


AI-powered diagram generation with real-time browser preview. Use for flowcharts, architecture, network, cloud, patent figures, and academic diagrams.

## Dependencies

- **MCP server**: `drawio-mcp-server` in root `mcp.json` (command: `npx -y drawio-mcp-server`)
- **Submodule**: `skills/drawio-skills` — [bahayonghang/drawio-skills](https://github.com/bahayonghang/drawio-skills.git)
- **Reference depth**: [`mine/chinese-patent/drawio/`](../../chinese-patent/drawio/SKILL.md) — A–H format, style presets, math typesetting, IEEE standards

## When to Use

- Flowcharts, process diagrams, decision trees
- System/software architecture diagrams
- Network topology and infrastructure diagrams
- Cloud architecture (AWS, GCP, Azure) with official icons
- Sequence diagrams, UML diagrams
- Patent structure/relationship figures (A–H format, 15px text)
- Academic paper figures (IEEE, ACM, Elsevier — grayscale, EPS/PDF)
- Infographics and technical illustrations

## MCP Tools

| Tool | Description |
|------|-------------|
| `start_session` | Opens browser with real-time diagram preview |
| `create_new_diagram` | Create a new diagram from XML |
| `edit_diagram` | Edit diagram by ID-based operations |
| `get_diagram` | Get the current diagram XML |
| `export_diagram` | Save diagram to a `.drawio` file |

## Quick Start

### Flowchart
```
Create a flowchart showing [process]: [step1] → [step2] → {decision} → [path A] / [path B]. Standard style, blue palette.
```

### Architecture
```
Draw a [system type] architecture: [components]. Layered layout, professional style, [3-4 color] palette. Export as .drawio.
```

### Cloud (AWS)
```
Generate an AWS architecture: [services]. Use official AWS icons, group by VPC, show public/private subnets.
```

### Patent Figure
```
Draw a Chinese patent structure diagram: 结构示意图 of [system], modules [A/B/C/D], orthogonal connectors, 15px text, B&W. Caption: 图N [title]结构示意图.
```

### Academic Paper (IEEE)
```
Draw an IEEE-compliant architecture: [system], grayscale only, LaTeX math labels, export EPS/PDF 300 DPI.
```

## Style Quick Reference

| Node Type | Style String |
|-----------|-------------|
| Primary | `rounded=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=15` |
| Success/Data | `rounded=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=15` |
| Warning/Note | `rounded=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=15` |
| Container | `rounded=1;fillColor=#f5f5f5;strokeColor=#999999;fontSize=14` |

Full presets: [`../../chinese-patent/drawio/references/style-presets.md`](../../chinese-patent/drawio/references/style-presets.md)

## A–H Structured Format

```
A. Diagram Type: Architecture / Flowchart / Network / ...
B. Title: [Diagram title]
C. Nodes: [List of nodes with labels and types]
D. Edges: [List of connections with labels]
E. Layout: Top-down / Left-right / Layered
F. Style: Professional / Patent / Academic / Cloud
G. Export: .drawio / .png / .svg
H. Notes: [Additional constraints]
```

See [`../../chinese-patent/drawio/references/ah-to-xml.md`](../../chinese-patent/drawio/references/ah-to-xml.md).

## Scenarios & Conventions

### Patent (专利附图)
- 15px font, Chinese labels, orthogonal lines
- Black-and-white, no grayscale
- Caption outside image: `图N [title]`
- See [`../../chinese-patent/drawio/references/ieee-network-diagrams.md`](../../chinese-patent/drawio/references/ieee-network-diagrams.md)

### Academic Paper (English)
- IEEE: EPS/PDF, grayscale, 300 DPI, LaTeX math
- ACM: PDF/PNG, LaTeX
- Export as vector format when possible

### Academic Paper (Chinese)
- 宋体/SimSun font, 中英双语图注
- EPS/PDF for 中国科学/计算机学报/软件学报

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MCP server won't start | Run `npx -y drawio-mcp-server` manually |
| Diagram not rendering | Check `get_diagram` XML output |
| Math not displaying | Wrap in `$$` for LaTeX |
| Style not applying | Use semicolons as separators |

## Related Resources

- [drawio-skills submodule](../../../skills/drawio-skills/) — External skill collection
- [chinese-patent/drawio](../../chinese-patent/drawio/SKILL.md) — Full reference with MCP tools, examples, troubleshooting
- [style-presets.md](../../chinese-patent/drawio/references/style-presets.md) — Copy-paste style strings
- [mcp-tools.md](../../chinese-patent/drawio/references/mcp-tools.md) — Full MCP tool API
