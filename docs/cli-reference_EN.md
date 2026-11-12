# CLI and maintenance reference

**English** | [简体中文](cli-reference.md)

Use this page for command options, update semantics, backups, and maintenance. Start at the [project homepage](../README_EN.md) for first use; commands below assume the repository root.

## `vibe` CLI

Repository discovery uses this priority: the `$VIBE_HOME` environment variable → a walk up from the current directory looking for both `manifests/` and `skills/` → `~/.config/vibe-tool/config.json`. To use the CLI outside the repository, you can first save its location with `vibe config set-repo /path/to/vibe-vibe`.

Project installation and direct-update commands support `-n/--dry-run` previews. The `target` defaults to the current directory.

Use `-f/--force` with `init/add` to explicitly overwrite existing files. In contrast, `update skill/manifest` overwrite selected resources with automatic backups.

Scenario and generation options such as `--provider`, `--owner`, `--org`, `--repo`, and `--email` apply according to the Manifest; see the relevant command's `--help`.

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

## Portable project configuration: `vibe setup`

Use [BOOTSTRAP.md](../BOOTSTRAP.md) for the one-request AI workflow. The AI selects or authors a manifest; the installer does not keyword-classify natural language. Without a global CLI, run `scripts/setup-project.py` from the source checkout with a detected Python 3.10+ interpreter and the same arguments.

```text
vibe setup --list
vibe setup vibe-coding ../my-project --harness both --scenario fullstack-web --provider git --dry-run
vibe setup vibe-coding ../my-project --harness both --scenario fullstack-web --provider git
vibe setup vibe-coding ../my-project --check
```

`--harness generic|codex|claude|both` (`--agent` is an alias) defaults to both. `.agents/skills` remains canonical; Claude/both also receive complete `.claude/skills` copies. Repeat `--skill <canonical-name>` for additional capabilities. The default provider is git; setup does not initialize Git, commit, or start cloud work. All current templates have a shell-free rendering path; existing Python installers are reused and legacy init/add behavior is unchanged.

Existing root instructions receive an idempotent import of `AGENTS.vibe-<name>.md` / `CLAUDE.vibe-<name>.md`; project README, output ledgers, release files, and business state are preserved. Other local conflicts stop before project writes. File changes, both skill locations, and installation records share one backed-up transaction with automatic failure rollback and a standalone restore script.

`.vibe-setup.json` records configuration and hashes. `--check` verifies files without simulating host activation. Rerun setup to refresh unmodified managed resources and Claude copies; preview first. Use `vibe project update <project-name>` for coordinated refresh. Legacy update commands do not maintain these copies or setup hashes. Individual skill runtime requirements still apply on Windows, macOS, and Linux.

## Harness-independent rules

A Manifest is a business collaboration contract, not an editor plugin. A new template needs at least one of `AGENTS.md`, `PROJECT_RULES.md`, or `CLAUDE.md`, with no Claude or Cursor prerequisite. Prefer ordinary `rules/*.md`; optional `always: true|false`, `paths`, and `when` headers describe applicability.

```text
vibe setup vibe-coding ../project --harness generic --provider git --dry-run
vibe setup vibe-coding ../project --harness generic --provider git
vibe setup vibe-coding ../project --check
```

Output includes `PROJECT_RULES.md`, `rules/<name>/CONTRACT.md`, `INDEX.md`, `rules/*.md`, and `rules.json`, with supporting references/commands/templates/scripts in the bundle. Rule bodies, scenario selection, path/task conditions, and source hashes are retained. Old MDC headers become index data; unknown scope requires review rather than silent global activation. Supporting scripts are files, not registered host plugins; validate their dependencies separately.

Any file-reading harness can explicitly read `PROJECT_RULES.md`, then the contract and applicable rules. Generic mode also publishes an ordinary `AGENTS.md` import and `.agents/skills`, without requiring Codex. Named modes only add host entries/skill copies, not different business gates. Report file/hash checks separately from observed host discovery and tool execution; never simulate tools or approval.

New setup does not distribute `.cursor` or `.cursorrules`; there is no Cursor compatibility commitment. Existing `.mdc` sources are migration input only. Existing project folders remain untouched and are retired from setup output tracking. Historical init/add scripts still write some old paths; use setup for a Cursor-free layout. Project updates maintain shared entries, installed rules/skills, backups, and rollback while preserving business results and independent user rules.

[Setup workflow](project-setup-workflow.svg) · [Editable source](project-setup-workflow.json). Rendering and read-only check commands are in the [setup contract](../BOOTSTRAP.md).

## Manage multiple projects

Successful `vibe setup`, `vibe init`, and `vibe add manifest/skill` operations register the real target project. Dry runs, failed installations, and internal staging directories do not. Names default to the directory name; same-named directories receive a path-derived suffix. Explicit conflicting names report an error.

### Register and inspect

```text
vibe project list
vibe project list --json
vibe project show paper
vibe project add ../old-project --name paper --source /path/to/vibe-vibe
```

`projects` is an alias for `project`. list/show work outside the source checkout and read the project's installation/setup records instead of duplicating their resource catalogs in the global index. A directory without installation records can be registered, but setup/init/add must establish its resources before updating; registration does not guess a manifest.

- `vibe project rename paper thesis` changes the lookup/display name only.
- After moving a project yourself, `vibe project relocate thesis /path/to/moved-project` rebinds its existing location; it does not move files.
- `vibe project remove thesis` removes only the registration, not files, skills, or backups. Missing paths stay indexed for inspection or relocation.

### Update by project and restore

```text
vibe project update paper --dry-run
vibe project update paper
vibe project update paper --manifest auto-research --dry-run
vibe project update paper --skill intuit-to-idea
vibe project update --all --dry-run
vibe project update --all
```

A named project defaults to all installed manifests and skills. Repeat `--manifest` / `--skill` to narrow the selection. Manifest updates include only installed dependencies; newly required or removed skill directories are not installed implicitly. Each project uses its indexed source checkout and recorded generation options, without changing directories. Updates read local sources and do not fetch/pull; source updates and project synchronization are separate operations.

All selected changes within one project share a prepared transaction and backup, including configuration, skill bundles, installation records, and setup hashes. Failure restores applied paths automatically; success prints a standalone restore command. No-op updates create no backup.

Batch updates continue with other projects after a failure, summarize results, and return nonzero if any failed. Atomicity is per project, not distributed across projects.

Setup projects refresh sidecar contracts and complete `.agents/skills` / `.claude/skills` bundles, remove stale bundle files, and synchronize `.vibe-setup.json`. Existing root user instructions, README, business state, output ledgers, and release files are preserved.

Modified managed resources or extra local skill files require review before replacement. Later `vibe add skill` operations on setup projects also update both hosts and metadata in one backed-up transaction; replacing existing skills requires explicit `--force`.

Non-setup projects receive the neutral rule entry/bundle through project update; other root resources retain the existing overwrite policy.

Legacy `vibe update manifest/skill` commands remain unchanged; prefer project update for setup projects so Claude copies and setup hashes stay coherent. Add another setup manifest through `vibe setup`; registration is not installation.

### Index location and errors

The index defaults to `~/.config/vibe-tool/projects.json` and stores only names, absolute project paths, and source checkouts. Set `VIBE_PROJECTS_FILE` for a separate work set, portable environment, or tests. Writers use platform file locks and atomic replacement; reads and previews change neither index nor project.

Import old projects explicitly rather than scanning the disk. A corrupt index is preserved and reported. Failed automatic registration warns without undoing valid local installation records; register again after repairing the index. This is not a business-progress ledger or a claim that files are unchanged. Preview current differences first. Project rollback leaves the global registration intact.

[Project-management workflow](project-management-workflow.svg) / [editable source](project-management-workflow.json). From the source checkout, run:

```text
python scripts/render-manifest-workflow.py --source docs/project-management-workflow.json --output docs/project-management-workflow.svg
python scripts/render-manifest-workflow.py --source docs/project-management-workflow.json --output docs/project-management-workflow.svg --check
```

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

Manifest updates overwrite only template-generated instructions, rules, commands, agents, platform configuration, and tool resources. Business files, research outputs, README, CONTRIBUTING, VERSION, CHANGELOG, run records, and initial outline/note indices are preserved.

Only the `vibe-coding` Manifest treats `MANIFEST.md` as an updatable instruction resource; output ledgers with the same name in other templates remain unchanged. Updates neither remove old configuration files that disappeared from the template nor replace entire project resource directories.

Required Skills are synced only when already installed. Missing dependencies are reported without installation; unrelated Skills remain untouched.

Successful `init/add` operations record sources and applicable generation options in the target project's `.vibe-tool/installations.json`. Updates reuse these records unless explicitly overridden.

A legacy project without a record must already contain at least one generated template resource. On its first update, supply every applicable generation option; the command reports missing options before writing. For a new project, use `vibe init` or `vibe add manifest` first.

An empty string selects the template default or no scenario, for example:

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

Creating a Manifest or changing its workflow requires a **workflow SVG, editable source, reproducible rendering command, and read-only drift check**, linked from its README or main instructions.

Distinguish autonomous AI execution, AI validation, and human decisions. Show branches, rework, and where AI resumes after human confirmation. See the [authoring requirements](manifest-workflow_EN.md) and [rendered example](examples/manifest-workflow/workflow.svg). Reuse Unity's existing source and renderer; template installation behavior is unchanged.

```bash
# Check the generic example against its editable source
python3 scripts/render-manifest-workflow.py \
  --source docs/examples/manifest-workflow/workflow.json \
  --output docs/examples/manifest-workflow/workflow.svg --check

# Validate rendering, branch structure, and read-only drift detection
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_manifest_workflow.py' -v
```

