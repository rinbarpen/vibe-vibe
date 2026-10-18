# Vibe Coding Commands

Complete command index for the unified development manifest. All commands are available after initialization under `.cursor/commands/`.

## Planning & Architecture

| Command | File | Description |
|---------|------|-------------|
| `/plan <domain>` | `plan/COMMAND.md` | Create implementation plan with problem statement, approach, files to change, test strategy, risk assessment |
| `/lang-select <context>` | `lang-select/COMMAND.md` | Get language recommendation with rationale based on decision tree and spec references |

## Development

| Command | File | Description |
|---------|------|-------------|
| `/scaffold <language> <archetype>` | `scaffold/COMMAND.md` | Bootstrap new project from scenario template with language-appropriate structure |
| `/implement <task>` | `implement/COMMAND.md` | Implement a bug fix or feature with proportional verification and implicit two-axis subagent review |

## Agent Development

| Command | File | Description |
|---------|------|-------------|
| `/agent-eval <mode>` | `agent-eval/COMMAND.md` | Run agent eval suite (regression/benchmark/adversarial) with metrics & reporting |

## Quality Assurance

| Command | File | Description |
|---------|------|-------------|
| `/quality-gate` | `quality-gate/COMMAND.md` | Run applicable lint, test, security, embedded-review confirmation, and documentation checks |
| `/deploy-check` | `deploy-check/COMMAND.md` | Pre-deployment verification: CI status, migration reversibility, rollback plan, env vars |

## Deployment

| Command | File | Description |
|---------|------|-------------|
| `/cloud-deploy <target> <platform>` | `cloud-deploy/COMMAND.md` | Deploy to cloud platform (vercel/cloudflare/tencent/alibaba/huawei) |
| `/release` | `release/COMMAND.md` | Execute enterprise release workflow: VERSION/CHANGELOG validation, GPG-signed tag, provider Release |
| `/frontend-check <mode>` | `frontend-check/COMMAND.md` | Frontend quality check: a11y, performance (CWV), bundle size, visual regression |
| `/desktop-build <framework> <platform>` | `desktop-build/COMMAND.md` | Build, package, sign desktop app (Electron/Tauri/Flutter × mac/win/linux) |

## Maintenance

| Command | File | Description |
|---------|------|-------------|
| `/update-docker` | `update-docker/COMMAND.md` | Sync Docker configuration with project state |
| `/update-docs` | `update-docs/COMMAND.md` | Sync docs/ documentation with current implementation |
| `/update-examples` | `update-examples/COMMAND.md` | Sync examples/ with current implementation |
| `/update-scripts` | `update-scripts/COMMAND.md` | Sync scripts/ utilities with project state |

## GitHub Operations

| Command | Description |
|---------|-------------|
| `gh pr create --fill` | Create PR from current branch |
| `gh pr checks` | Monitor CI/CD status |
| `gh pr status` | View PR state |
| `gh pr view --web` | Open PR in browser |
| `gh run list` | View recent GitHub Actions runs |
| `gh release create v1.2.3` | Create GitHub Release |
| `git tag -s v1.2.3 -m "v1.2.3"` | Create GPG-signed tag |

## Subagent Dispatch

Use the host runtime's subagent/task-delegation mechanism for bounded, independent work on complex tasks only. Keep simple/local work in the main agent, run dependent tasks sequentially, specify ownership and deliverables, then collect/integrate results and verify centrally. If delegation is unavailable, proceed sequentially.

| Agent | When | Effect |
|-------|------|--------|
| `code-architect` | Architecture changes | Design review, module boundaries |
| Embedded `implement` review | Implementation workflow | Dual-axis subagent review; no separate generic review dispatch |
| `security-reviewer` | Auth/payments/data | Security audit |
| `tdd-guide` | New features | TDD workflow enforcement |
| `performance-optimizer` | Slow code | Profile, optimize |
| `refactor-cleaner` | Tech debt | Clean up, extract |
| `build-error-resolver` | Build fails | Fix compilation errors |
| `ci-watcher` | After PR | Monitor CI until pass |

---

*Commands are installed during `vibe-init.sh` under `.cursor/commands/` in the target project.*
