# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **vibe-coding** toolkit that aggregates ~200+ AI skills (as git submodules) for Claude Code and other AI coding agents. It turns Claude into a multi-domain expert covering scientific research, UI/UX design, office automation, developer tooling, and more.

## Key Commands

| Command | Description |
|---------|-------------|
| `vibe list manifests` | List all available project templates |
| `vibe list skills` | List all available skills |
| `vibe list --json` | Machine-readable output |
| `vibe init <manifest> [target]` | Bootstrap a new project from a manifest template |
| `vibe add manifest <name>` | Add manifest files to an existing project |
| `vibe add skill <name>` | Install a specific skill into a project |
| `vibe add skill --all` | Install all skills |
| `vibe update` | Update managed skill submodules to latest (excluding `agent-skills` and `ai-investment-advisor`) |
| `vibe config set-repo <path>` | Configure repo path |
| `vibe stats show` | Display skill usage statistics |
| `./scripts/skills-git-pull.sh` | Pull managed skill repos (alternative to `vibe update`) |

**Install the vibe CLI:** `uv tool install -e tools/vibe_tool` (requires `uv`; see `tools/vibe_tool/install.sh`)

## Project Structure

```
.
├── skills/                  # 33+ git submodules (skill libraries from various sources)
│   ├── anthropics/          # Official Anthropic skills (16+ skills: docx, xlsx, pptx, pdf, ...)
│   ├── claude-scientific-skills/  # 140+ scientific research skills (K-Dense AI)
│   ├── ui-ux-pro-max-skill/       # 58+ UI style library + design system generator
│   ├── AI-Research-SKILLs/        # 83+ AI/ML research engineering skills
│   ├── awesome-claude-skills/     # Community skill collection (ComposioHQ)
│   └── ...                  # ~28 more submodules (see .gitmodules for full list)
│
├── mine/                    # Custom-developed first-party skills
│   ├── chinese-patent/      # Chinese patent writing pipeline (multi-stage sub-skills)
│   ├── omnidraw/            # Unified drawing skill (excalidraw, mermaid, drawio, gpt-image-2, canvas-design, nano-banana)
│   ├── omnisheet/           # Spreadsheet-style skill suite (6 domains: data-analysis, financial, project-management, business-ops, academic-research, personal-life)
│   └── paperreview-ai-review/  # AI paper review skill
│
├── manifests/               # Project initialization templates (CLAUDE.md + AGENTS.md + rules + scenarios)
│   ├── vibe-coding/         # Core full-stack development lifecycle manifest
│   ├── auto-research/       # Automated research pipeline
│   ├── auto-research-ars/   # Auto research with ARS integration
│   ├── fund-proposal/       # Grant proposal writing
│   ├── market-analysis/     # Market research & competitive analysis
│   ├── novel-writing/       # Fiction writing
│   ├── social-media/        # Social media content ops
│   ├── ui-testing/          # UI testing (Playwright, Vitest, mobile, a11y)
│   └── ...                  # More manifests
│
├── tools/vibe_tool/         # Python CLI tool (`vibe` command) for manifest/skill management
│   └── src/vibe_tool/       # Modules: cli, manifest, discovery, skill, stats, config, types
│
├── cli/                     # Standalone CLI tool definitions
│   ├── agent-browser/       # Browser automation CLI
│   ├── office-cli/          # Office automation CLI
│   └── anything-cli/        # General-purpose CLI
│
├── hooks/ralph-loop/        # Hookify rules for RFC-driven DAG orchestration workflow
│   ├── hookify.ralph-rfc-intake.local.md      # RFC intake trigger for complex features
│   ├── hookify.ralph-decompose.local.md       # DAG decomposition into work units
│   ├── hookify.ralph-unit-create.local.md     # Quality pipeline tier selection
│   ├── hookify.ralph-validation.local.md      # Per-tier validation requirements
│   ├── hookify.ralph-quality-gate.local.md    # Merge queue rules & eviction recovery
│   └── hookify.ralph-completion.local.md      # Session completion verification
│
├── .claude/skills/skills-updater/  # Skill for batch-updating all git submodules
├── config.toml              # browserwing config (browser automation tool)
├── mcp.json                 # MCP server configs (promptx, pdf-reader, chrome-devtools, drawio, scientific, windows-mcp)
├── scripts/                 # Utility scripts
│   ├── skills-git-pull.sh           # Pull all git submodules
│   └── validate-agent-compat.py     # Validate agent compatibility
└── data/                    # Runtime data directory
```

## Architecture Notes

### Skills vs Manifests
- **Skills** (`skills/`, `mine/`): SKILL.md files loaded into AI context to grant domain expertise. 200+ total across 33+ submodules and 4 custom packages.
- **Manifests** (`manifests/`): Harness-independent business contracts: discovery accepts AGENTS.md, PROJECT_RULES.md, or CLAUDE.md. Prefer plain rules/*.md with always/paths/when scope. Use `vibe setup <manifest> <target> --harness generic` for PROJECT_RULES.md plus a neutral rules/<name>/ bundle. Named host modes only add entries/copies; no Cursor output compatibility is required. Legacy MDC is source migration input and existing user folders remain intact.
- **Mine skills** (`mine/`): First-party, not submodules. Developed directly in this repo.

### How skills are discovered
The `vibe_tool` recursively scans for `SKILL.md` files. Name collisions (same directory name under different paths) are auto-resolved by encoding the relative path with hyphens.

### The vibe CLI tool
Built with Python argparse. Installed via `uv tool install`. Core workflow: `vibe init <manifest> [target]` → creates project dir → runs manifest init script or copies files. Supports `--dry-run`, `--force`, scenario selection.

### Ralph-Loop workflow
A structured methodology for complex features: RFC intake → DAG decomposition into work units with tier classification (trivial/small/medium/large) → quality pipeline per unit → merge queue with eviction recovery. Enforced via hookify rules in `hooks/ralph-loop/`.

### MCP servers configured
- `promptx-alpha` (dpml-prompt)
- `pdf-reader-mcp`
- `chrome-devtools` (browser debugging)
- `drawio` (diagrams)
- `claude-scientific-skills` (remote MCP)
- `windows-mcp`

### Updating skills

Batch update commands skip `skills/agent-skills` and `skills/ai-investment-advisor`.
They remain available to `vibe list skills` and individual installation. Update either
one manually with its explicit submodule path when needed.

```bash
# Method 1: via vibe CLI (uses git submodule update --remote --merge)
vibe update

# Method 2: via script (pulls managed submodule repos)
./scripts/skills-git-pull.sh

# Manual update for an excluded submodule
git submodule update --remote --merge -- skills/agent-skills
git submodule update --remote --merge -- skills/ai-investment-advisor
```

Some skill repos (aris, ppt-master) are nested standalone git repos not registered in `.gitmodules` — they are updated separately by the skills-updater skill.

### .gitignore
Excludes `.vibe-tool/` (auto-generated usage stats), `.claude/settings.local.json` (per-dev overrides), and `hooks/*.local.md` (per-dev hook overrides).

## MCP Tool Configuration

The `mcp.json` at repo root configures MCP servers available to Claude. Key tools:
- **chrome-devtools**: Browser automation with Chrome DevTools Protocol
- **drawio**: Draw.io diagram creation
- **pdf-reader-mcp**: PDF document reading
- **claude-scientific-skills**: Remote scientific computation MCP

## Documentation readability

- Write for the reader's task: a README gives purpose, prerequisites, the first action, and its expected result before reference details.
- Put full catalogs, options, architecture, and change records in linked reference pages; keep them discoverable without making them prerequisites for getting started.
- Do not impose badges, emoji, fixed chapter templates, or new translations. Preserve existing language pairs and verify facts, commands, paths, and support claims.
- Follow the [reader-first writing contract](manifests/vibe-coding/references/readme-guide.md). Its read-only checker validates structure, not readability or whether examples were executed.

## One-request project setup

For requests to configure a project from one natural-language goal in any file/command-capable AI harness, read [BOOTSTRAP.md](BOOTSTRAP.md). Use the shell-free `scripts/setup-project.py` / `vibe setup` path for Windows/macOS/Linux, select or author the business manifest, preview/apply/check, and preserve existing project content. This path does not alter legacy init/add/update semantics.

## Multi-project registry

Successful setup/init/add CLI operations index real projects in `~/.config/vibe-tool/projects.json` (`VIBE_PROJECTS_FILE` overrides the location). Use `vibe project list/show`, `add/rename/relocate/remove`, and `vibe project update <name> [--manifest NAME|--skill NAME] [--dry-run]`; `update --all` visits all indexed projects. Project-local installations/setup records remain authoritative. Updates use local sources, skip uninstalled dependencies, apply one backed-up transaction per project, and keep setup host copies/hashes coherent. Registry removal never deletes project files. See the CLI reference for compatibility and failure semantics.
