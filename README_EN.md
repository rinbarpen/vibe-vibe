# vibe-vibe

**English** | [简体中文](README.md)

Install the skills and project rules needed for AI-assisted coding, research, writing, and office work.

Install a **Skill** for one capability, or choose a **Manifest** for project-level working conventions. Your AI assistant uses the installed resources in the target project.

## Let your AI set up the project

Already using an AI harness that reads/writes project files and runs commands, such as Codex or Claude Code? Give it one request in your target project:

> Read https://github.com/rinbarpen/vibe-vibe/blob/main/BOOTSTRAP.md and configure this directory for [project goal]: select or create a suitable manifest, install its skills using ordinary Markdown project rules, and verify the setup.

The AI follows the [setup contract](BOOTSTRAP.md): inspect the environment, select or author the workflow, preview and install, then verify resources and report rollback. The setup entry uses Python 3.10+ standard libraries on Windows, macOS, and Linux; no Bash or globally installed CLI is needed. The AI handles missing Git/Python prerequisites first. Configuration does not replace the actual application, research, or writing task.

## Use the CLI manually

You need Git, Python 3.10+, and [uv](https://docs.astral.sh/uv/). Run:

```bash
git clone --recurse-submodules https://github.com/rinbarpen/vibe-vibe
cd vibe-vibe
uv tool install -e tools/vibe_tool
vibe list manifests
```

The last command should list available templates such as `vibe-coding` and `ui-testing`. Skip the first two lines if you already cloned the repository. Without a global CLI, use the [local Python entry point](docs/cli-reference_EN.md#update-without-installing-the-cli).

## Choose a task

| What you need | Entry point |
| --- | --- |
| Add one capability to an existing project | `vibe add skill <name> <project-directory>` |
| Configure development rules for a new project | `vibe setup <template> <project-directory> --harness generic` |
| Add a rule set to an existing project | `vibe add manifest <template> <project-directory>` |
| Sync installed rules or skills | [Updates, backups, and rollback](docs/cli-reference_EN.md#sync-installed-skills-and-manifests) |
| Track projects and update by name | [Project registry and updates](docs/cli-reference_EN.md#manage-multiple-projects) |

For example, preview and then apply full-stack development rules to a new project:

```bash
vibe setup vibe-coding ../my-project --harness generic --scenario=fullstack-web --provider=git --dry-run
vibe setup vibe-coding ../my-project --harness generic --scenario=fullstack-web --provider=git
```

This creates `PROJECT_RULES.md`, an ordinary `AGENTS.md` import entry, skills, and a `rules/<template>/` bundle in `../my-project`. No Cursor loader is required; other harnesses can read `PROJECT_RULES.md` directly. Select `--harness codex|claude|both` for named host entries; see [rule distribution](docs/cli-reference_EN.md#harness-independent-rules). It provides project context, not an implemented or deployed application. Open that directory in your AI assistant and give it the actual task.

`--provider=git` selects a local Git workflow. See the [CLI reference](docs/cli-reference_EN.md) for other hosting providers, scenarios, and options.

## Find guidance for your task

- **Find a skill or template:** use the [catalog](docs/catalog_EN.md); `vibe list skills` supplies canonical installation names.
- **Build application UI:** use the [Vibe Coding template](manifests/vibe-coding/README.md), including UI/UX and real interaction checks.
- **Create diagrams or visualizations:** [choose tools by scenario](mine/omnidraw/references/visualization-scenarios_EN.md).
- **Browse all skills:** use the [English skill index](skills/ANNOTATIONS_EN.md).
- **Maintain or create templates:** follow the [workflow authoring guide](docs/manifest-workflow_EN.md).

Research, learning, writing, office, and game-production templates are in the [catalog](docs/catalog_EN.md). You do not need to install every skill.

## Common questions

**A required Skill source is missing?** Make sure submodules are initialized:

```bash
git submodule update --init --recursive
```

**The source repository changed, but an existing project did not?** Installed resources are copies. Sync them explicitly with `vibe update skill` or `vibe update manifest`. See [update semantics](docs/cli-reference_EN.md#sync-installed-skills-and-manifests) for scope, legacy options, and restore commands.

**Need MCP or Hooks?** Install them as needed; ordinary skills do not enable them automatically. See [MCP and supporting tools](docs/catalog_EN.md#mcp-servers).

## Maintain this repository

[Development checks](docs/cli-reference_EN.md#development-and-validation) · [Repository structure](docs/catalog_EN.md#project-structure) · [Workflow authoring](docs/manifest-workflow_EN.md) ([Chinese reference](docs/manifest-workflow.md))

The repository was previously named `vibe-coding`. The CLI remains `vibe`, and the software-engineering template remains `vibe-coding`; existing commands do not need renaming.

## License

This repository uses the [MIT License](LICENSE). External skills and workflows retain their own licenses.
