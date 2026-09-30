# AGENTS.md

Instructions for AI coding agents (Cursor, Claude Code, etc.) working with this codebase.

## Repository Overview

Brief description of the project and its goals.

## Core Flow (Vibe Coding)

Choose a workflow by task size:
- Simple bounded change: inspect, vibe code directly, and run relevant checks; no plan artifact or extra process skill by default.
- Bug requiring diagnosis: `grilling` → `implement`.
- Complex feature: `grill-with-docs` → `to-spec` → `to-tickets` → `implement`.
- For medium/large work, track progress with `planning-with-files-zh` for Chinese tasks or `planning-with-files` for English tasks.
- `implement` includes independent subagent reviews for correctness (requirements, behavior, tests) and code quality (design, maintainability); do not manually invoke a separate code-review step.
- Explore, verify, and ship in proportion to the change; preserve applicable project quality/security checks.

## Subagent Dispatching

Actively suggest and launch subagents based on task complexity:

- **`explore`**: For codebase analysis and navigation.
- **`code-architect`**: For high-level design and refactoring.
- **`shell`**: For complex environment or Git operations.

## Development Standards

- **Environment**: Prefer `uv` for Python project management.
- **Network**: Run `proxy_on` before downloading files.
- **Visualization**: Matplotlib plots must use English.
- **Open Source**: Follow standards in `{{VIBE_MANIFEST}}/standards/open-source-standards.md`.

## Maintenance

- Keep `CLAUDE.md` updated with architecture and command changes.
- Use `vibe-claude-md-audit` to ensure project context quality.
