# UI Testing — AI Agent Instructions

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

## Core Flow

1. **Analyze** — Read source code, understand component/page structure, identify test gaps
2. **Plan** — Determine test strategy (unit vs integration vs E2E), select scenario
3. **Generate** — Write tests following rules in `rules/` and patterns in `skills/patterns/`
4. **Verify** — Run tests, check coverage, fix failures
5. **Review** — Use `code-reviewer` subagent for CRITICAL/HIGH issues
6. **Integrate** — Wire into CI via `ui-testing-ci.mdc` rules

## Subagent Dispatch

| Subagent | When | What it does |
|----------|------|-------------|
| `test-planner` | New feature or bug fix | Analyzes code diff, recommends test types and coverage targets |
| `test-writer` | After plan approval | Generates test code following POM/component patterns |
| `test-runner` | During verification | Executes test suite, parses results, reports failures |
| `flaky-diagnoser` | Intermittent failures | Reads CI logs, identifies race conditions / timing / ordering issues |
| `coverage-analyzer` | Before merge | Runs coverage tool, compares against 80% threshold, flags gaps |

## Dispatch Rules

- For any **new component/page**: dispatch `test-planner` → `test-writer` → `test-runner`
- For **bug fix**: dispatch `test-writer` (regression test) → `test-runner`
- For **flaky test**: dispatch `flaky-diagnoser` → `test-writer` (fix) → `test-runner`
- For **pre-merge**: dispatch `test-runner` → `coverage-analyzer`
- For **CI failure**: dispatch `test-runner` (read logs) → `flaky-diagnoser` if intermittent

## Development Standards

- Run `npx playwright test` before any E2E commit
- Run `npx vitest run --coverage` before merge
- Use `{{UI_TESTING_MANIFEST}}` to reference this manifest's path (resolved by init script)
- Follow `.mdc` rules in `rules/` — they are always applied
- Scenario-specific rules in `scenarios/*/rules/` are opt-in via `--scenario=<name>`

## Maintenance

- Update `CLAUDE.md` when commands, architecture, or conventions change
- Keep `skills/patterns/` in sync with evolving best practices
- Run `ui-testing-init.sh` when adding new scenarios or commands
