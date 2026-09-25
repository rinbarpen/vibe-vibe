# AGENTS.md

Instructions for AI coding agents (Cursor, Claude Code, etc.) working with this codebase.

## Repository Overview

Brief description of the project and its goals.

## Core Flow (Vibe Coding)

Follow these phases for development:

1.  **Route**: Simple/local requests use lightweight vibe coding; bug fixes use `grilling` → `implement`; complex features use `grill-with-docs` → `to-spec` → `to-tickets` → `implement`.
2.  **Planning notes**: For complex work only, use `planning-with-files` (English) or `planning-with-files-zh` (Chinese).
3.  **Explore**: Inspect directly for local work; use `SemanticSearch` or an `explore` subagent when broader codebase discovery is needed.
4.  **Implement**: Small, incremental changes with immediate `ReadLints` verification.
5.  **Verify**: Run tests and provide evidence of success.
6.  **Review**: `implement` includes subagent review across two independent axes; do not launch a separate generic code-review workflow.
7.  **Ship**: Create PR with a detailed test plan and update `CLAUDE.md`.

## Subagent Dispatching

Use subagents only for complex tasks with independent work; simple/local requests remain with the main agent. Use the host runtime's available delegation mechanism; if unavailable, proceed sequentially.

- **`explore`**: For codebase analysis and navigation.
- **`code-architect`**: For high-level design and refactoring.
- **Embedded implement review**: Dual-axis subagent review as part of implementation.
- **`shell`**: For complex environment or Git operations.

For every delegation, specify the goal, context, file ownership/read-only boundary, expected deliverable, and verification. Start independent tasks together, wait for results, integrate in the coordinating agent, and run final combined checks. Never split dependent steps or permit concurrent edits to the same files.

## Development Standards

- **Environment**: Prefer `uv` for Python project management.
- **Network**: Run `proxy_on` before downloading files.
- **Visualization**: Matplotlib plots must use English.
- **Open Source**: Follow standards in `{{VIBE_MANIFEST}}/standards/open-source-standards.md`.

## Maintenance

- Keep `CLAUDE.md` updated with architecture and command changes.
- Use `vibe-claude-md-audit` to ensure project context quality.
