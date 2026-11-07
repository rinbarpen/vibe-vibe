# vibe-vibe

A **cross-domain toolkit of skills, project templates, and workflows** for AI agents such as Claude Code, Codex, and Cursor, covering software development, research, learning, writing, design, and office automation.

vibe-vibe brings community Skill libraries, first-party skills, project-level instructions, complete workflows, and standalone CLIs into one repository. Use the `vibe` CLI to install a single Skill or bootstrap a reusable human–AI collaboration environment with a Manifest, adding MCP configuration and Hooks as needed. The repository itself is not a business application.

> Formerly named `vibe-coding`, the project is now `vibe-vibe` to reflect its scope beyond coding. The CLI command remains `vibe`, and the general software engineering Manifest remains `vibe-coding`; existing commands and project names do not need to change.

[中文 README](README.md)

## What you can do with it

| Use case | Capabilities |
| --- | --- |
| Software development | Full-stack development, APIs, CLIs, data pipelines, LLM applications, desktop apps, testing, and deployment |
| Research and writing | Literature research, experiment planning, paper writing and review, figures, and grant proposals |
| Design and frontend | Design systems, UI/UX, frontend interfaces, themes, generative art, and visual inspection |
| Office automation | DOCX, XLSX, PPTX, PDF, and business communication documents |
| Content production | Chinese writing, fiction, social media, academic rewriting, and summarization |
| Agent infrastructure | Skill creation, MCP servers, browser automation, Hooks, and multi-agent workflows |

## Quick start

### 1. Get the repository

Initialize the Skill submodules when cloning:

```bash
git clone --recurse-submodules https://github.com/rinbarpen/vibe-vibe
cd vibe-vibe
```

For an existing clone:

```bash
git submodule update --init --recursive
```

### 2. Install the `vibe` CLI

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/). To update an existing project, you can also skip CLI installation; see [Update without installing the CLI](#update-without-installing-the-cli).

```bash
./tools/vibe_tool/install.sh
# Or:
uv tool install -e tools/vibe_tool
```

Check the installation:

```bash
vibe --version
vibe list manifests
vibe list skills
```

### 3. Initialize a project

```bash
# Create a complete Vibe Coding project context
vibe init vibe-coding ../my-project --scenario=fullstack-web

# Add UI testing configuration to an existing project
vibe add manifest ui-testing ../my-project

# Add an individual Skill to an existing project
vibe add skill taste-skill ../my-project
```

Depending on the Manifest, the resulting project typically includes:

```text
my-project/
├── CLAUDE.md / AGENTS.md       # Project-level agent instructions
├── .agents/skills/             # Installed Skills
├── .cursor/
│   ├── commands/              # Callable commands
│   └── rules/                 # Project rules
├── .claude/agents/             # Claude Code agents, when provided by the Manifest
└── .codex/agents/              # Codex agents, when provided by the Manifest
```

## `vibe` CLI

Repository discovery uses this priority: the `$VIBE_HOME` environment variable → a walk up from the current directory looking for both `manifests/` and `skills/` → `~/.config/vibe-tool/config.json`. To use the CLI outside the repository, you can first save its location with `vibe config set-repo /path/to/vibe-vibe`.

Project installation and direct-update commands support `-n/--dry-run` previews. Use `-f/--force` with `init/add` to explicitly overwrite existing files; `update skill/manifest` overwrite the selected resources with automatic backups. The `target` defaults to the current directory. Scenario and generation options such as `--provider`, `--owner`, `--org`, `--repo`, and `--email` apply according to the Manifest; see the relevant command's `--help`.

| Command | Purpose |
| --- | --- |
| `vibe list manifests` | List available project templates |
| `vibe list skills` | Recursively list available Skills |
| `vibe list --json` | Output machine-readable inventories |
| `vibe init <manifest> [target]` | Initialize a project from a template |
| `vibe add manifest <name> [target]` | Add a Manifest to an existing project |
| `vibe add skill <name> [target]` | Add an individual Skill to a project |
| `vibe add skill --all [target] --yes` | Install all Skills without a confirmation prompt |
| `vibe update` | Update managed Skill submodules |
| `vibe update skill <name> [target]` | Sync an installed Skill from local sources with automatic backup |
| `vibe update manifest <name> [target]` | Sync Manifest configuration and already-installed required Skills with backup |
| `vibe config set-repo <path>` | Save the repository location |
| `vibe config show` | Show the current configuration |
| `vibe mcp list` | List available MCP servers |
| `vibe mcp add <name> [target]` | Merge MCP server configuration into a project |
| `vibe mcp add --all [target]` | Install all available MCP server configurations |
| `vibe hook list` | List available Hook sets |
| `vibe hook add <name> [target]` | Install a Hook set into a project |
| `vibe hook add --all [target]` | Install all Hook sets |
| `vibe stats show` | Show Skill usage statistics |

Common options (the `add/hook` examples below assume `demo` already exists; `--dry-run` itself does not create the target directory):

```bash
vibe init vibe-coding demo --dry-run
vibe add manifest office demo --force
vibe add skill --all demo --yes --dry-run
vibe mcp list
vibe hook add ralph-loop demo
```

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

- [Anthropic Skills](skills/anthropics): official document, spreadsheet, presentation, PDF, frontend, and other skills
- [Claude Scientific Skills](skills/claude-scientific-skills): research, life sciences, chemistry, medical imaging, and more
- [UI/UX Pro Max](skills/ui-ux-pro-max-skill): design systems and UI styles
- [Impeccable](skills/impeccable): frontend design direction, interface critique, and visual polish; install with `vibe add skill impeccable <target>`
- [Intuit to Idea](skills/intuit-to-idea): develop a research direction into a testable hypothesis through focused AI questions and human intuition; integrated as an optional Idea route in `auto-research`; install with `vibe add skill intuit-to-idea <target>`
- [AI Research Skills](skills/AI-Research-SKILLs): AI/ML research, training, evaluation, and paper workflows
- [Agent Skills for Context Engineering](skills/Agent-Skills-for-Context-Engineering): context engineering methods
- [Humanizer-zh](skills/Humanizer-zh) and [shuorenhua](skills/shuorenhua): Chinese rewriting and expression improvement
- [Unslop](skills/unslop): review and rewrite ordinary prose to remove formulaic writing; used by z-humanizer for ordinary writing while academic and patent routes remain separate; install with `vibe add skill unslop <target>`
- [Chinese-WebNovel-Skill](skills/chinese-webnovel-skill): Chinese web-novel planning, chapter outlines, drafting, and completion review
- [Pretty Mermaid Skills](skills/Pretty-mermaid-skills): Mermaid diagram generation and rendering
- [Unity Game Development](mine/unity-game-development): end-to-end game production, 3D/DCC modeling, game testing, and executor/Reviewer roles; install a bundle, stage, or individual capability
- [State Machine Reasoning](mine/state-machine-reasoning): model decisions, debugging, research, and workflow analysis as state machines with Mermaid visualizations
- [Omnippt](mine/omnippt): on-demand sub-skills for requirements research, narrative outlines, slide planning, visual design, native production, and independent review of editable presentations
- [Geo Sleuth](skills/geo-sleuth): photo geolocation and capture-time inference, clue analysis, and evidence verification; install with `vibe add skill geo-sleuth <target>`
- [X Research](skills/x-research-skill): information retrieval and social-platform research

First-party Skills live in [mine/](mine); complete workflow projects live in [workflows/](workflows). Follow each workflow's own instructions: `workflows/` is not a default scan root for `vibe list skills`.

Browse the indices:

- [Chinese Skills annotations](skills/ANNOTATIONS.md)
- [English Skills annotations](skills/ANNOTATIONS_EN.md)

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
| `novel-writing` | Long-form fiction and literary creation |
| `office` | DOCX / XLSX / PPTX / PDF: substantive writing, native editable delivery, full visual acceptance, and independent QA |
| `social-media` | Social media content creation and operations |
| `ui-testing` | Web, component, mobile, visual, and accessibility testing |
| `unity-game` | End-to-end Unity game production, Claude Code/Codex roles, executor/Reviewer skills, and a [workflow SVG](manifests/unity-game/references/workflow.svg) |

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

- [ralph-loop](hooks/ralph-loop): RFC intake → DAG decomposition → tiered validation → merge-queue Hook workflow
- [writing-agent](workflows/writing-agent): writing system from topic selection and research to review and publication
- [cli/agent-browser](cli/agent-browser), [cli/anything-cli](cli/anything-cli), and [cli/office-cli](cli/office-cli): standalone CLI projects
- [cli/craft-anything](cli/craft-anything): upstream source for a Rust desktop app, CLI, and MCP server for evidence-backed software analysis and rebuilding; build and use following its upstream instructions, rather than installing it as a Skill.
- `paseo.json`: optional local Paseo workspace configuration; Git-ignored and not a required repository file

## Updates and maintenance

### Sync installed Skills and Manifests

Initialized projects support **in-place updates without running `vibe init` again**. Installed resources are copies, so source repository changes require an explicit sync to each target project. Projects keep their installed versions until you choose to update them.

Before updating:

- Ensure the local source repository contains the version you need; fetch changes to the main repository or the relevant Skill source first when a newer remote version is needed.
- Identify an existing target project directory and the Skill or Manifest name to update.
- Ensure the resource is already installed. Installation records let updates reuse sources and generation options; legacy project requirements are described below.

Direct updates use the current local repository contents and **do not implicitly fetch from remotes**. The `target` defaults to the current directory. Specify one name per command; `--all` is not supported for these direct updates.

```bash
# Preview, then sync an entire installed Skill directory, removing stale files
vibe update skill taste-skill ../my-project --dry-run
vibe update skill taste-skill ../my-project

# Preview, then sync configuration, reusing recorded generation options by default
vibe update manifest vibe-coding ../my-project --dry-run
vibe update manifest vibe-coding ../my-project

# Override options when needed; add manifest also supports --scenario
vibe update manifest ui-testing ../my-project --scenario=web-e2e
vibe add manifest ui-testing ../my-project --scenario=component
```

Skill updates replace the entire installed directory, including any custom files, which are included in the pre-update backup. If the Skill is not installed yet, first run `vibe add skill <name> [target]`.

Manifest updates overwrite only template-generated instructions, rules, commands, agents, platform configuration, and tool resources. They preserve business files, research outputs, README, CONTRIBUTING, VERSION, CHANGELOG, run records, and initial outline/note indices. Only the `vibe-coding` Manifest treats `MANIFEST.md` as an updatable instruction resource; output ledgers with the same name in other templates remain unchanged. Updates do not remove old configuration files that disappeared from the template or replace entire project resource directories. Required Skills are synced only when already installed; missing dependencies are reported without installation, and unrelated Skills remain untouched.

Successful `init/add` operations record sources and applicable generation options in the target project's `.vibe-tool/installations.json`. Updates reuse these records unless explicitly overridden. Legacy projects without a record must already contain at least one generated template resource and must explicitly supply every applicable generation option on their first update; the command reports missing options before writing. For a new project, use `vibe init` or `vibe add manifest` first. An empty string selects the template default or no scenario, for example:

```bash
vibe update manifest vibe-coding ../legacy-project \
  --provider=git --scenario='' --owner='' --org='' --repo='' --email=''
```

`--dry-run` reports paths to add, overwrite, or skip without writing project files, installation records, or backups. Before actual changes, the CLI automatically creates a backup under `.vibe-tool/backups/<id>/`, including originals, checksums, and a change inventory. A successful update prints a restore command:

```bash
python /path/to/project/.vibe-tool/backups/BACKUP_ID/restore.py
```

Replace `BACKUP_ID` with that backup directory's name, or use the restore command printed by the update. The restore script runs independently without installing `vibe`. Configuration, dependency Skills, and installation records are updated in one transaction; application failures automatically restore touched resources. No backup is created when both content and installation records are unchanged.

### Update without installing the CLI

You only need Python 3.10+ and a local source repository, with no `uv`, global `vibe` installation, or third-party Python dependencies. Prepare the installed resources and existing project as described above, then run the Python entry point directly from the source tree:

```bash
REPO=/path/to/vibe-vibe
PROJECT=/path/to/existing-project

# Temporary function, available only in the current terminal session
vibe_local() {
  VIBE_HOME="$REPO" \
  PYTHONPATH="$REPO/tools/vibe_tool/src" \
  python3 -B -m vibe_tool "$@"
}

# Preview the updates you need
vibe_local update skill taste-skill "$PROJECT" --dry-run
vibe_local update manifest ui-testing "$PROJECT" --dry-run

# After reviewing the previews, run the relevant update commands
vibe_local update skill taste-skill "$PROJECT"
vibe_local update manifest ui-testing "$PROJECT"
```

Replace the paths and resource names with your actual values. These commands use the same update prerequisites, overwrite boundaries, automatic backups, and standalone rollback rules.

### Update Skill source repositories

Bare `vibe update` only updates managed Skill source submodules. Fetch Manifest changes through the main repository separately; existing projects still require an explicit sync using the `update skill/manifest` commands above:

```bash
vibe update
```

Alternatively, use the repository script:

```bash
./scripts/skills-git-pull.sh
```

`agent-skills` and `ai-investment-advisor` are excluded from batch updates by default. Update them explicitly when needed:

```bash
git submodule update --remote --merge -- skills/agent-skills
git submodule update --remote --merge -- skills/ai-investment-advisor
```

Some Skill repositories, such as `aris` and `ppt-master`, are standalone nested repositories rather than entries in `.gitmodules`. Update them using their own repository workflow.

## Development and validation

After changing the CLI or a Manifest, run:

```bash
# Validate Claude Code and Codex agent compatibility
python scripts/validate-agent-compat.py

# Run the vibe-tool tests
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src python -m pytest tools/vibe_tool/tests -v
```

A new Manifest must contain at least `CLAUDE.md` to be discovered by `vibe list manifests`. A new Skill must provide `SKILL.md` in its Skill directory.

Creating a Manifest or changing its workflow also requires a **workflow SVG, editable source, reproducible rendering command, and read-only drift check**, linked from its README or main instructions. Distinguish autonomous AI execution, AI validation, and human decisions; show branches, rework, and where AI resumes after human confirmation. See the [Manifest workflow authoring requirements](docs/manifest-workflow.md) and the [rendered SVG example](docs/examples/manifest-workflow/workflow.svg). Reuse Unity's existing source and renderer; this convention does not change template installation behavior.

```bash
# Check the generic example against its editable source
python3 scripts/render-manifest-workflow.py \
  --source docs/examples/manifest-workflow/workflow.json \
  --output docs/examples/manifest-workflow/workflow.svg --check

# Validate rendering, branch structure, and read-only drift detection
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_manifest_workflow.py' -v
```

## License

The repository itself uses the [MIT License](LICENSE). External projects under `skills/` and `workflows/` retain their own licenses; check the corresponding submodule's license before distributing or modifying it.
