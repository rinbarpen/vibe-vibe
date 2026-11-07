# Choose visualization by scenario

[简体中文](visualization-scenarios.md) | **English**

This is Omnidraw's scenario guide. Choose a capability from what the user needs to explain, the actual inputs, and the destination. Not every task calls for HTML, and not every dataset calls for a flowchart. Explicit tool/format requests and the existing project stack take precedence.

## Choose a production route

| Scenario and selection criteria | Capability / canonical Skill id_path | Deliverables and checks |
| --- | --- | --- |
| Architecture explanations, code changes, comparisons, or recaps that need a complete reading experience | `visual-explainer/plugins/visual-explainer` | HTML source and page; check arrows, labels, and source-code facts, using its kit renderer as needed |
| Deterministic trends, bars, scatter plots, or error bars | `omnidraw/matplotlib`; use `claude-scientific-skills/skills/matplotlib` for deeper customization | Plotting code, source data, SVG/PDF/PNG; verify units, axes, samples, and uncertainty |
| Distributions, group comparisons, correlations, or exploratory statistics | `claude-scientific-skills/skills/seaborn` | Preserve aggregation, missing values, and raw observations; separate exploration from validated conclusions |
| Hover, zoom, or legend toggles without a full application | Plotly through `claude-scientific-skills/skills/scientific-visualization` | HTML, generation code, accessible data table; export a static fallback separately and check offline assets/export dependencies |
| KPIs, coordinated views, filters, and refresh behavior in a full dashboard | `ai-design-components/skills/creating-dashboards`; select chart backends separately | Runnable page/project and data-integration notes; test filters, loading, missing data, errors, and refresh states; distinguish a prototype from a deployed system |
| Markdown flows, sequences, ER, state machines, mind maps, or small concept relationships | `omnidraw/mermaid`; use the existing PlantUML route for complex UML | Mermaid/PlantUML sources and required previews; verify branches, relationships, and reading order without forcing an HTML wrapper |
| Knowledge, citation, social, or biological networks requiring attributes, scale, or graph algorithms | `claude-scientific-skills/skills/networkx` | Node/edge data, graph model, layout, and analysis code; distinguish direction, multiedges, weights, and provenance. Mermaid is enough for purely conceptual relationships |
| Scientific statistics, multi-panel figures, uncertainty, and journal output | `claude-scientific-skills/skills/scientific-visualization` | Preserve data and transformations; check physical dimensions, fonts, legends, and uncertainty. Verify the journal's actual submission-phase rules rather than treating fixed DPI as acceptance |
| Scientific methods, mechanisms, experimental setups, or graphical abstracts | `CCFA-Skills/ccf-visual-composer`; supplement with an installed scientific-schematic route | Verify scientific objects, arrow meanings, and evidence boundaries before choosing vector/image production. Keep this distinct from statistical plotting and preserve actual experimental values |
| Geographic distributions, administrative areas, trajectories, or spatial relationships | `claude-scientific-skills/skills/geopandas` | Verify coordinate systems, spatial joins, boundaries, and data licensing; deliver maps with reproducible code rather than inferring geographic data from an image |

These are capability sources, not a requirement to install every dependency. The current repository has no standalone `plotly` Skill: Plotly is a backend covered by `scientific-visualization`. `creating-dashboards` handles the application layer, while `visual-explainer` handles explanations; neither replaces metric definitions or actual data analysis.

## Installation and resolution in installed projects

Install only the route needed for the task. The shared entry point includes local Mermaid and Matplotlib sub-skills:

```bash
vibe add skill omnidraw ../my-project
```

Choose optional capabilities as needed. These full id_path identifiers select an exact source even when similarly named skills coexist:

```bash
vibe add skill visual-explainer/plugins/visual-explainer ../my-project
vibe add skill claude-scientific-skills/skills/matplotlib ../my-project
vibe add skill claude-scientific-skills/skills/seaborn ../my-project
vibe add skill claude-scientific-skills/skills/scientific-visualization ../my-project
vibe add skill ai-design-components/skills/creating-dashboards ../my-project
vibe add skill claude-scientific-skills/skills/networkx ../my-project
vibe add skill CCFA-Skills/ccf-visual-composer ../my-project
vibe add skill claude-scientific-skills/skills/geopandas ../my-project
```

Installing a full id_path converts its path separators to hyphens for the destination directory. For example, scientific-visualization becomes `.agents/skills/claude-scientific-skills-skills-scientific-visualization/`. An existing short-name installation does not need renaming. Read the target's actual `SKILL.md` files and `.vibe-tool/installations.json`, use each recorded `source` to identify the capability, and load its real installed path. Do not reuse aggregate-relative links as target-project paths. `omnidraw/matplotlib` and `omnidraw/mermaid` ship inside the entry point and need no separate installation.

If the selected capability is missing, identify the gap and its exact installation command, or use an available capability without losing the requirement. Keep static screenshots distinct from interactive charts, and illustrative diagrams distinct from real data plots. One route's missing dependency should not block unrelated routes. New dependencies, external data transfer, background refresh, deployment, and paid image generation still follow the current agreement; installing a Skill starts none of them automatically.

## Combining routes and accepting deliverables

- **Research reports:** Matplotlib/Seaborn/Plotly produce actual data figures, scientific-visualization checks publication/accessibility requirements, and Visual Explainer may organize verified figures into a web explanation. HTML is not a substitute for submission PDF/SVG files.
- **Business dashboards:** establish metric definitions, grain, time range, provenance, and missing-value handling before creating coordinated views. Do not add real-time services, deployment, or a new framework by default.
- **System/knowledge explanations:** use Mermaid for flows and small relationships, NetworkX for edge data and graph analysis, and add Visual Explainer for interactive explanations or comparisons. Leave unsupported edges, causal claims, and weights unknown.
- **Office delivery:** preserve code, diagram sources, data, and static/interactive previews. Requested PPTX or native editable figures need the corresponding authoring route; HTML and screenshots are not editable office objects.
- **Dependencies and verification:** check only the selected route's runtimes. The HTML kit uses Node.js; statistical plots use the project's Python environment; Plotly static export/browser checks, maps, and graph algorithms have additional requirements. Skill installation does not install all these runtimes.

Report what was actually generated and checked. Syntax/structure checks are not browser visual acceptance. Preserve the user's language and format; distinguish missing input data from explicitly labeled demonstration data.

## Maintain the workflow illustration

`assets/workflow.mmd` is the editable source distributed with the skill. Its SVG describes routing rules, not execution status. From the aggregate repository root, reuse the existing Pretty Mermaid renderer; prepare its locked dependencies only when editing this illustration:

```bash
node skills/Pretty-mermaid-skills/scripts/render.mjs \
  --input mine/omnidraw/assets/workflow.mmd \
  --output mine/omnidraw/assets/workflow.svg --format svg \
  --theme github-light --font 'Noto Sans CJK SC' --bg '#ffffff' --fg '#173B47'
```

For a read-only drift check, direct the same command's `--output` to a temporary directory and compare it with the repository SVG using `cmp`. This changes neither sources nor installed projects. The source uses plain Mermaid without a YAML header unsupported by the renderer.
