# vibe-coding — Agent Instructions

Skills aggregation monorepo. NOT a development project — the repo is an orchestrator that
bundles ~200+ AI skills (as git submodules) and project scaffolds (manifests).

## Structure

- `skills/` — 40+ git submodules each containing `SKILL.md` files (discovered recursively by `vibe list skills`).
  Name collisions auto-resolved by hyphenated relative path.
- `workflows/` — Multi-stage agent workflows and full Claude Code plugin projects (e.g. writing-agent with skills, agents, workflows, and desktop app).
- `manifests/` — 10 project bootstrap templates. Each needs a `CLAUDE.md` to be discoverable.
- `tools/vibe_tool/` — Python CLI (`vibe`). Entrypoint: `vibe_tool.cli:main`.
- `cli/` — 3 standalone CLI tool projects (agent-browser, anything-cli, office-cli).
- `mine/` — First-party custom skills (chinese-patent, export-paper-zip, git-manager, manifest-to-skill, omnidraw, omnisheet, paper-version-manager, paperreview-ai-review).
- `hooks/` — Hookify rules organized by name (e.g. `ralph-loop/` for ralph-loop workflow rules).
- `mcp.json` — 6 MCP servers configured (chrome-devtools, drawio, scientific, pdf-reader, etc.). Install on-demand into projects via `vibe mcp add`.

No root `CLAUDE.md` exists — the repo is a meta-package, not a source project.
No root-level CI workflows — each sub-project has its own.

## vibe CLI (primary tool)

Install: `uv tool install -e tools/vibe_tool` or `./tools/vibe_tool/install.sh`
Requires `uv` (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

| Command | Description |
|---------|-------------|
| `vibe list manifests` | List all available project templates |
| `vibe list skills` | List all available skills |
| `vibe list --json` | Machine-readable output |
| `vibe init <manifest> [target]` | Bootstrap a project from a manifest template |
| `vibe add manifest <name>` | Add manifests to an existing project |
| `vibe add skill <name>` | Install a specific skill |
| `vibe add skill --all` | Install all skills |
| `vibe update` | Batch-update managed skill repos; skips `agent-skills` and `ai-investment-advisor` |
| `vibe update skill <name> [target]` | Sync one installed Skill from local sources with automatic backup |
| `vibe update manifest <name> [target]` | Sync Manifest resources and installed required Skills with automatic backup |
| `vibe config set-repo <path>` | Persist repo path to `~/.config/vibe-tool/config.json` |
| `vibe config show` | Show current configuration |
| `vibe stats show` | Display skill usage statistics (recorded by PostToolUse hook) |
| `vibe mcp list` | List available MCP servers in this repo |
| `vibe mcp add <name> [target]` | Install a specific MCP server into a project (merges with existing) |
| `vibe mcp add --all [target]` | Install all MCP servers into a project |
| `vibe hook list` | List available hook sets in this repo |
| `vibe hook add <name> [target]` | Install a hook set (e.g. ralph-loop) into a project |
| `vibe hook add --all [target]` | Install all hook sets |

### Repo root discovery (CLI)
Priority: `$VIBE_HOME` env var > cwd walk-up (looks for `manifests/` + `skills/`) > `~/.config/vibe-tool/config.json`

## PostToolUse hook

`tools/vibe_tool/src/vibe_tool/record_skill.py` — reads tool usage from hook stdin,
records Skill tool invocations to `.vibe-tool/skill-stats.json` (gitignored).

Configured as PostToolUse hook in Claude Code / Codex / opencode settings.

## MCP on-demand loading

`vibe mcp add <name> [target]` installs a MCP server from this repo's `mcp.json` into
a target project's `mcp.json`. It **merges** with existing servers — never overwrites
unrelated entries. Use `--force` to replace an existing server config.

```bash
# List available servers
vibe mcp list

# Install drawio into current project
vibe mcp add drawio

# Install all servers into specific project
vibe mcp add --all /path/to/project

# Preview without writing
vibe mcp add chrome-devtools --dry-run
```

## Hook on-demand loading

`vibe hook add <name> [target]` installs hooks from this repo's `hooks/` directory into
a target project's `hooks/` directory. Use `--force` to replace an existing hook set.

```bash
# List available hook sets
vibe hook list

# Install ralph-loop into current project
vibe hook add ralph-loop

# Install all hook sets
vibe hook add --all /path/to/project
```

## Updating installed project resources

`vibe update skill <name> [target]` replaces the whole installed `.agents/skills/<name>` directory, including removing stale files. `vibe update manifest <name> [target]` updates only generated configuration/tool resources, preserving project data, README, VERSION, CHANGELOG, and output ledgers. Only `vibe-coding`'s `MANIFEST.md` is an updatable instruction source. Required Skills are updated only when already installed; unrelated Skills and missing dependencies are left untouched.

These commands read local sources without fetching Git. They default to the current directory, accept `-n/--dry-run`, and require one name (no `--all`). Dry-run writes no project state or backups. Add/init retain their existing overwrite policy; direct update overwrites with a backup under `.vibe-tool/backups/<id>/`, including `changes.json`, originals, and standalone `restore.py`. Run the printed `python .../restore.py` command to restore. Application failure automatically rolls back the same transaction, including dependencies and installation records; no-op updates create no backup.

Successful init/add record canonical names, repository-relative sources, and applicable generation options in `.vibe-tool/installations.json` (schema version 1). Update reuses recorded options; explicit `provider/scenario/owner/org/repo/email` override them. For legacy projects, at least one generated resource must already exist; otherwise use init/add. Supply all applicable options on the first manifest update; omitted fields are reported before writing, while explicit empty strings select defaults/no scenario. `vibe add manifest` also accepts `--scenario`.

```bash
vibe update skill taste-skill ../project --dry-run
vibe update skill taste-skill ../project
vibe update manifest ui-testing ../project --scenario=web-e2e
# Legacy vibe-coding project: make every applicable choice explicit.
vibe update manifest vibe-coding ../project --provider=git --scenario='' --owner='' --org='' --repo='' --email=''
# Standalone rollback, using the path printed by update:
python /path/to/project/.vibe-tool/backups/<id>/restore.py
```

## Updating skill source repositories

Batch update commands intentionally skip `skills/agent-skills` and
`skills/ai-investment-advisor`. They remain discoverable and installable. Update either
one manually by passing its path to Git:

```bash
git submodule update --remote --merge -- skills/agent-skills
git submodule update --remote --merge -- skills/ai-investment-advisor
```

```bash
# Method 1 — via vibe CLI
vibe update

# Method 2 — pull managed skill repos
./scripts/skills-git-pull.sh

# Method 3 — for standalone nested repos (aris, ppt-master):
# These are NOT in .gitmodules — update them individually.
```

## Manifest structure

Each manifest directory requires `CLAUDE.md` to be discoverable.
Optional: `AGENTS.md`, `agents/` (Claude Code + Codex agent definitions),
`scenarios/` (scenario sub-manifests), `scripts/*init*.sh` (custom init scripts),
`skills.txt` (required skill names, one per line — installed automatically by
`vibe add manifest` / `vibe init`; resolved from both `skills/` and `mine/`).

## Manifest workflow deliverables

A manifest is a human–AI collaboration contract, not only a scaffold. When creating
one or changing its workflow, deliver a corresponding workflow SVG, editable source,
a reproducible rendering command, a read-only drift check, and links from its README
or main instructions. Follow [Manifest workflow authoring](docs/manifest-workflow.md).

Distinguish AI execution, AI validation/review, and human decisions. AI resolves
implementation uncertainty through investigation and tests within agreed boundaries;
human intervention is for new decisions, changed goals/constraints, or predefined
high-impact gates. Label branches, rework/waiting paths, applicable rollback, and
where AI resumes after a human decision. Diagrams describe rules, not actual status.

Reuse existing canonical sources/renderers (such as Unity's skill catalog); do not
create duplicate sources or migrate unrelated legacy manifests. If an installer or
skill conversion promises these assets, distribute source and renderer as well as
SVG and verify links/regeneration in the installed layout. General asset copying is
not implied by this authoring requirement.

## Key conventions

- `AGENTS.md` and `CLAUDE.md` exist per-manifest and per-sub-project — do not conflate root-level with nested ones.
- `vim`-based save pattern used for reliability: write to temp → `os.replace`.
- Hooks (`hooks/*.local.md`) are gitignored — keep per-dev overrides there.
- Local Claude settings at `.claude/settings.local.json` (gitignored).
- Agent files exist in both `.claude/agents/` (Claude Code) and `.codex/agents/` (Codex TOML format) — validated by `scripts/validate-agent-compat.py`.
- Skills index: `skills/ANNOTATIONS.md` (Chinese) and `skills/ANNOTATIONS_EN.md` (English).
