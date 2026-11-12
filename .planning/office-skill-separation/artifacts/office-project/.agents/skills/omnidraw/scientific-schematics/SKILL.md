---
name: scientific-schematics
description: Publication-quality scientific diagrams and schematics via claude-scientific-skills MCP. Mechanism diagrams, experimental setups, research proposals. Journal-specific formatting for Nature, Science, Cell, and Chinese journals.
---

# Scientific Schematics

Publication-quality scientific diagrams via the `claude-scientific-skills` MCP server.

## Dependency

- **MCP server**: `claude-scientific-skills` configured in root `mcp.json` at `https://mcp.k-dense.ai/claude-scientific-skills/mcp`

## When to Use

- Mechanism diagrams for papers and proposals
- Experimental setup illustrations
- Research proposal figures (NSFC, NIH, etc.)
- Journal-specific formatted schematics
- When publication conventions matter (Nature, Science, Cell, etc.)

**Not for**: data charts (use [matplotlib](../matplotlib/SKILL.md)), architecture diagrams (use [mermaid](../mermaid/SKILL.md)).

## Quick Start

Use the MCP tools from `claude-scientific-skills` to generate schematics. Describe the scientific concept, mechanism, or setup in natural language.

```
Generate a scientific schematic showing [mechanism/concept]. Include [key components]. Journal-ready formatting for [target journal].
```

## Journal Conventions

| Journal | Style | Notes |
|---------|-------|-------|
| Nature | Minimal, clean lines | Sans-serif, limited colors |
| Science | Clean, high-contrast | Bold labels |
| Cell | Colorful but restrained | Consistent palette |
| PNAS | Professional, clear | Grayscale-compatible |
| NSFC (国自然) | 学术规范, 结构清晰 | 中英文标注 |

## Templates

```
Mechanism diagram:
  Generate a scientific schematic of [biological/chemical/physical mechanism]: [steps/components]. Journal-quality, clean lines, consistent labeling. Export as vector graphic.

Experimental setup:
  Generate a schematic of [experiment]: [apparatus], [samples], [measurement points]. Include scale bars or dimensions where relevant.

Research proposal figure:
  Generate an NSFC-style technical roadmap schematic: [research plan phases], [connections between phases], [key scientific questions at each stage]. Clean academic style, Chinese/English bilingual labels.
```

## Related

- [mermaid](../mermaid/SKILL.md) — Fallback for general diagrams
- [matplotlib](../matplotlib/SKILL.md) — Data charts for papers
- [chinese-patent/drawio](../../chinese-patent/drawio/SKILL.md) — Patent-specific diagram conventions
