# Skills and template catalog

**English** | [简体中文](catalog.md)

Look up skills, project templates, and supporting tools as needed; the full catalog is not a prerequisite for getting started. See the [CLI reference](cli-reference_EN.md) for installation and updates.

## Project structure

```text
vibe-vibe/
├── .agents/skills/              # Agent skills used to maintain this repository
├── skills/                      # Community libraries: submodules and nested repos
│   ├── ANNOTATIONS.md           # Chinese skill index
│   └── ANNOTATIONS_EN.md        # English index; other directories hold skill sources
├── mine/                        # First-party drawing, presentation, office, research skills
├── manifests/                   # Project templates and human–AI collaboration contracts
│   ├── vibe-coding/             # Software lifecycle; the Manifest name is unchanged
│   ├── auto-research/           # Research, experiments, and papers
│   ├── tutor/                   # Conversational learning and learning records
│   ├── office/                  # Native office deliverables and quality checks
│   └── ...                     # See the template list below
├── workflows/writing-agent/     # Complete multi-stage writing workflow project
├── tools/vibe_tool/             # Python implementation and tests for the vibe CLI
│   ├── src/vibe_tool/           # Discovery, install, update, backup, and configuration
│   └── tests/                  # CLI regression tests
├── cli/                         # Standalone tools with their own build and usage docs
│   ├── agent-browser/
│   ├── anything-cli/
│   ├── craft-anything/
│   └── office-cli/
├── hooks/ralph-loop/            # RFC, decomposition, validation, and merge queue rules
├── docs/                        # Maintenance conventions and workflow diagram examples
├── scripts/                     # Maintenance, compatibility checks, and diagram rendering
├── tests/                       # Repository-level regression tests
├── AGENTS.md                    # Repository Agent collaboration instructions
├── CLAUDE.md                    # Repository guidance for Claude Code
└── README.md / README_EN.md     # Chinese and English documentation
```

- A **Skill** is an installable capability, discovered from `skills/` and `mine/` by default.
- A **Manifest** is a project-level collaboration package combining instructions, rules, scenarios, agents, required Skills, and initialization scripts; it is not a single Skill.
- **Workflows and standalone CLIs** keep their own usage paths; inclusion here does not automatically make them installable Skills.
- Root-level `mcp.json` is an optional configuration source. `.vibe-tool/` holds local installation records, backups, and statistics, and is Git-ignored.

## Repository contents

### Skills

`skills/` contains Git submodules from community projects and maintainers; `mine/` holds first-party Skills. The CLI recursively scans both directories for `SKILL.md`. Name collisions are resolved using relative-path-based identifiers; use the names printed by `vibe list skills` when installing.

Selected collections include:

- [Anthropic Skills](../skills/anthropics): official document, spreadsheet, presentation, PDF, frontend, and other skills
- [Claude Scientific Skills](../skills/claude-scientific-skills): research, life sciences, chemistry, medical imaging, and more
- [UI/UX Pro Max](../skills/ui-ux-pro-max-skill): design systems and UI styles
- [Impeccable](../skills/impeccable): frontend design direction, interface critique, and visual polish; install with `vibe add skill impeccable <target>`
- [Intuit to Idea](../skills/intuit-to-idea): develop a research direction into a testable hypothesis through focused AI questions and human intuition; integrated as an optional Idea route in `auto-research`; install with `vibe add skill intuit-to-idea <target>`
- [AI Research Skills](../skills/AI-Research-SKILLs): AI/ML research, training, evaluation, and paper workflows
- [Agent Skills for Context Engineering](../skills/Agent-Skills-for-Context-Engineering): context engineering methods
- [Humanizer-zh](../skills/Humanizer-zh) and [shuorenhua](../skills/shuorenhua): Chinese rewriting and expression improvement
- [Unslop](../skills/unslop): review and rewrite ordinary prose to remove formulaic writing; used by z-humanizer for ordinary writing while academic and patent routes remain separate; install with `vibe add skill unslop <target>`
- [Z-Writing](../mine/z-writing/SKILL.md): Unified Chinese/English writing entry combining AI Vibe voice/drafting with z-humanizer editing, scoped to ordinary, office, academic and proposal writing; `vibe add skill z-writing <target>`
- [Chinese-WebNovel-Skill](../skills/chinese-webnovel-skill): Chinese web-novel planning, chapter outlines, drafting, and completion review
- [Pretty Mermaid Skills](../skills/Pretty-mermaid-skills): Mermaid diagram generation and rendering
- [Visual Explainer](../skills/visual-explainer/plugins/visual-explainer): turn architectures, workflows, code changes, plans, and comparison tables into standalone HTML explanations; see the installation example below.
- [Unity Game Development](../mine/unity-game-development): end-to-end game production, 3D/DCC modeling, game testing, and executor/Reviewer roles; install a bundle, stage, or individual capability
- [State Machine Reasoning](../mine/state-machine-reasoning): model decisions, debugging, research, and workflow analysis as state machines with Mermaid visualizations
- [Omnippt](../mine/omnippt): on-demand sub-skills for requirements research, narrative outlines, slide planning, visual design, native production, and independent review of editable presentations
- [Geo Sleuth](../skills/geo-sleuth): photo geolocation and capture-time inference, clue analysis, and evidence verification; install with `vibe add skill geo-sleuth <target>`
- [X Research](../skills/x-research-skill): information retrieval and social-platform research

First-party Skills live in [mine/](../mine); complete workflow projects live in [workflows/](../workflows). Follow each workflow's own instructions: `workflows/` is not a default scan root for `vibe list skills`.

Browse the indices:

- [English Skills annotations](../skills/ANNOTATIONS_EN.md)
- [Chinese Skills annotations](../skills/ANNOTATIONS.md)

### Choose visualization skills by scenario

Use [Omnidraw](../mine/omnidraw/SKILL.md) as the entry point; the [scenario guide](../mine/omnidraw/references/visualization-scenarios_EN.md) maintains exact source identifiers and selection rules. Keep the different capabilities rather than forcing every result into HTML or an image:

| Scenario | Skill / capability | Main deliverable |
| --- | --- | --- |
| Architecture explanations, comparisons, visual reviews | Visual Explainer | HTML explanations and web presentations |
| Data charts and exploratory statistics | Matplotlib, Seaborn | Code, SVG/PDF/PNG |
| Interactive data charts | Plotly through scientific-visualization | Interactive HTML, data, and code |
| KPIs, coordinated filters, multiple dashboard views | creating-dashboards | Runnable data interface |
| Scientific statistics and multi-panel paper figures | scientific-visualization | Required static formats and provenance |
| Scientific methods, mechanisms, graphical abstracts | CCFA / scientific schematic workflows | Scientific figures and requested editable reconstruction |
| Flows, sequences, ER, state machines, small concept maps | Mermaid / PlantUML | Text sources and previews |
| Knowledge networks with real edge data and graph analysis | NetworkX | Graph data, analysis code, and visualization |
| Geographic distributions and spatial analysis | GeoPandas | Maps, spatial data, and code |

```bash
# Includes local Mermaid and Matplotlib sub-skills; add optional routes as needed
vibe add skill omnidraw ../my-project
```

The entry point does not automatically install every optional source or runtime. There is no standalone `plotly` Skill in the current catalog; use its workflow in scientific-visualization via the scenario guide. Explicit tool/format requests and the existing project stack take precedence.

### Visual explanations: Visual Explainer

The [upstream project](https://github.com/nicobailon/visual-explainer) is tracked as the `skills/visual-explainer/` Git submodule; its installable payload is `plugins/visual-explainer/`.

Use it for architecture and data-flow explanations, visual diff reviews, plan comparisons, project recaps, and HTML slides. Keep using Matplotlib, Plotly, scientific-visualization, and related skills for their existing statistical and research plotting workflows.

```bash
vibe add skill visual-explainer ../my-project
```

This installs the complete payload into `.agents/skills/visual-explainer/` in the target project, including `references/`, `templates/`, `commands/`, `kit/`, and optional export tools, rather than copying only `SKILL.md`. Example request:

```text
Use visual-explainer to explain this project's module relationships and data flow as HTML. Save it to docs/architecture.html.
```

Viewing the result requires a browser; the bundled `kit/render.mjs` renderer requires Node.js. Follow upstream setup for optional browser checks, MCP, PPTX, or video export dependencies. `vibe add skill` neither installs global tools nor automatically registers command templates as host slash commands.

### Office: capability and project layers

`vibe add skill office <target>` installs reusable office capabilities. `vibe init office <target>` creates an office-delivery project and installs Office plus companion Skills. Format guides, macros and verification tools live in the [Office Skill](../mine/office/SKILL.md); project coordination belongs to the [office Manifest](../manifests/office/README.md).

### Manifests

A Manifest is a project-level configuration package, typically containing `CLAUDE.md`, `AGENTS.md`, rules, commands, scenarios, agents, and initialization scripts.

Templates can declare required Skills in `skills.txt`; `init/add manifest` install these dependencies automatically. Missing local Skill sources are reported with a nonzero exit status, including during `--dry-run`. Check the relevant Skill sources and submodule initialization before installing.

| Manifest | Intended use |
| --- | --- |
| `vibe-coding` | General software engineering lifecycle |
| `auto-research` | Literature, experiments, papers, and figures |
| `auto-research-ars` | ARS-based multi-stage research pipeline |
| `fund-proposal` | Grant applications and project proposals |
| `git-manager` | Git repository and mirror management |
| `tutor` | Conversational tutoring for textbooks or topics, illustrated notes, and learning records |
| `market-analysis` | Industry, market, and competitive research |
| [`writing`](../manifests/writing/README.md) | Patent drafting: `vibe setup writing <target> --harness generic --scenario patent`; disclosure, claim support, figures, review and DOCX draft handoff |
| `novel-writing` | Long-form fiction and literary creation |
| `office` | Office-delivery projects: goals, sources and versions, cross-format coordination, acceptance and archiving; includes Office Skills |
| `social-media` | Social media content creation and operations |
| `ui-testing` | Web, component, mobile, visual, and accessibility testing |
| `unity-game` | End-to-end Unity game production, Claude Code/Codex roles, executor/Reviewer skills, and a [workflow SVG](../manifests/unity-game/references/workflow.svg) |

Use `vibe list manifests` for the actual available templates. `tutor` is the new name for `knowledge-learning`; use `vibe init tutor [target]` for new projects.

Find individual template documentation:

```bash
find manifests -maxdepth 2 -name README.md -print
```

### MCP servers

The CLI reads the `mcpServers` configuration from an optional `mcp.json` at the repository root; no predefined server set is assumed. Run `vibe mcp list` first to inspect the available servers. If the configuration is missing or empty, it prints `No MCP servers found.`; prepare the source configuration before installing servers.

Once configured, replace `SERVER_NAME` with an actual name from the list:

```bash
vibe mcp list
vibe mcp add SERVER_NAME ../my-project --dry-run
vibe mcp add SERVER_NAME ../my-project
```

Installation merges into the target project's `mcp.json` and preserves unrelated entries. Existing servers with the same name are skipped unless explicitly replaced with `--force`.

### Hooks, workflows, and standalone CLIs

- [ralph-loop](../hooks/ralph-loop): RFC intake → DAG decomposition → tiered validation → merge-queue Hook workflow
- [writing-agent](../workflows/writing-agent): writing system from topic selection and research to review and publication
- [cli/agent-browser](../cli/agent-browser), [cli/anything-cli](../cli/anything-cli), and [cli/office-cli](../cli/office-cli): standalone CLI projects
- [cli/craft-anything](../cli/craft-anything): upstream source for a Rust desktop app, CLI, and MCP server for evidence-backed software analysis and rebuilding; build and use following its upstream instructions, rather than installing it as a Skill.
- `paseo.json`: optional local Paseo workspace configuration; Git-ignored and not a required repository file

