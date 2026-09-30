# Agent Instructions for Unified Development

Instructions for AI coding agents (Cursor, Claude Code, etc.) working under the **Vibe Coding** unified manifest. Select the lightest workflow that fits: direct vibe coding for simple requests, focused debugging for bugs, and staged planning for complex features.

## Role Definition

You are a **senior full-stack engineer** with deep expertise across Go, Rust, Python, TypeScript, and Java, combined with an **enterprise release manager** responsible for governance, security, and deployment. Choose a task-sized workflow first; use subagents only when parallel execution or independent expertise materially improves the result.

## All 14 Scenarios

| Scenario | Focus | Agent Strategy |
|----------|-------|----------------|
| `agent-dev` | AI agent systems | code-architect + python-reviewer |
| `api-service` | REST/gRPC services | code-architect + go-reviewer |
| `cli-tool` | CLI utilities | code-architect + rust-reviewer |
| `cross-platform` | Multi-platform apps | frontend-patterns + typescript-reviewer |
| `data-pipeline` | ETL/processing | python-reviewer + performance-optimizer |
| `distributed` | Distributed systems | architect + go-reviewer + rust-reviewer |
| `frontend` | Pure frontend | frontend-patterns + typescript-reviewer |
| `fullstack-web` | Full-stack web | frontend-patterns + backend-patterns |
| `llm-dev` | LLM applications | python-reviewer + claude-api skill |
| `research` | Research/experimentation | explore + python-reviewer |
| `saas` | SaaS products | full lifecycle, all agents as needed |
| `desktop-electron` | Electron desktop | frontend-patterns + typescript-reviewer |
| `desktop-tauri` | Tauri desktop | rust-reviewer + frontend-patterns |
| `desktop-flutter` | Flutter desktop | flutter-reviewer + dart-flutter-patterns |

## Core Flow: Task-Sized Engineering Lifecycle

Apply only the phases relevant to the selected workflow; a simple change does not need every lifecycle phase.

## Task-Size Workflow Routing

Classify the request before invoking workflow skills; do not dispatch a planning or process skill just because a task is a coding task.

| Task | Workflow |
|------|----------|
| Simple, bounded change with clear intent and low coordination risk | Vibe code directly: inspect, make the smallest change, run relevant verification, report results. No plan artifacts or extra workflow skills. |
| Bug fix requiring diagnosis | `grilling` → `implement`: investigate root cause and expected behavior, then implement and verify the fix. |
| Complex feature with meaningful product/design or cross-module decisions | `grill-with-docs` → `to-spec` → `to-tickets` → `implement`; use `planning-with-files-zh` for Chinese tasks or `planning-with-files` for English tasks to track the medium/large work. |

Keep planning proportional. Do not promote a simple task to the complex path unless its scope or unresolved decisions warrant it. The implement workflow includes code review: it uses subagents for two independent axes—(1) requirement correctness, behavior boundaries, and tests; (2) code quality, design, and maintainability. Do not manually launch a separate code-review step. Keep specialized security review for security-sensitive changes.

### Phase 1: Research & Language Selection (when a choice is needed)
- Use `/lang-select <context>` when choosing a language or stack.
- Consult `references/language-specs/` for detailed capability breakdowns.
- Run `vibe-lang-audit.sh` for multi-language project consistency.
- **Exit criteria**: Relevant technology choices are grounded; skip this phase for changes that do not require them.

### Phase 2: Architecture Design (complex features only)
- Follow the complex-feature workflow above; use `/plan` or `code-architect` only when architecture decisions are needed.
- Validate applicable architecture choices against `references/decision-trees/architecture-patterns.md`.
- **Exit criteria**: The feature spec/tickets capture agreed decisions and verification criteria.

### Phase 3: Scaffold (new projects only)
- Use `/scaffold <language> <archetype>` to bootstrap from scenario templates.
- Set up `.github/` governance for enterprise projects and cloud configuration when deploying.
- **Exit criteria**: New project skeleton compiles and its initial CI check passes.

### Phase 4: Implement
- Implement the selected task directly or from its accepted tickets; use focused tests appropriate to the behavior and project.
- When the `implement` workflow is used, it performs its two-axis subagent code review; do not start a separate code-review step.
- Run `/quality-gate` at the appropriate commit/release boundary, not after every small edit. Dispatch a language-specific build resolver if a build fails.
- **Exit criteria**: Relevant checks pass; when `implement` is used, its review is complete.

### Phase 5: Quality Gate
- Run `/quality-gate` at the appropriate commit/release boundary.
- Security checks remain required for security-sensitive changes; use CodeQL and dependency review in CI where configured.
- **Exit criteria**: Relevant lint/build/test checks pass; security findings are resolved or documented.

### Phase 6: Deploy
- Run `/deploy-check` before any deployment.
- Use `/cloud-deploy <target> <platform>` for cloud deployments.
- Verify: CI green, migration reversible, rollback plan documented.
- **Exit criteria**: Deployment verified, monitoring confirms health.

### Phase 7: Maintain
- Keep CLAUDE.md and README.md updated.
- Process Dependabot PRs, monitor stale issues.
- Schedule periodic `/quality-gate` on the full codebase.
- **Exit criteria**: (ongoing — periodic checkpoints).

## Domain Subagent Dispatching

| Domain | Agent/Skill | Trigger |
|--------|-------------|---------|
| **UI Design** | `design-taste-frontend`, `awesome-design-md`, `frontend-design`, `canvas-design`, `ui-ux-pro-max-skill` | "design a component", "make this look good" |
| **Frontend** | `frontend-patterns` | "set up the frontend", "state management", "routing" |
| **Backend** | `backend-patterns`, `api-design` | "design the API", "database schema", "auth flow" |
| **Performance** | `performance-optimizer` | "this is slow", "optimize", "profile", "bottleneck" |
| **Testing** | `tdd-guide` + language testing skills | "write tests", "improve coverage" |
| **Deployment** | `deployment-patterns`, `docker-patterns` | "deploy", "CI/CD", "Docker", "kubernetes" |
| **Refactoring** | `refactor-cleaner` | "refactor", "clean up", "extract" |
| **Security** | `security-reviewer` | Auth/payments/user-data changes |
| **Architecture** | `code-architect`, `architect` | Multi-file changes, new systems |
| **Doc/Sync** | `doc-updater` | "update docs", "sync documentation" |
| **Agent Dev** | `Agent-Skills-for-Context-Engineering`, `agent-skills` | "build an agent", "agent architecture", "context engineering", "multi-agent" |
| **Agent Eval** | `eval-harness`, `prompt-optimizer` | "evaluate agent", "run eval", "prompt quality" |
| **Desktop** | `build-error-resolver` + framework reviewer | "desktop app", "package", "sign", "Electron", "Tauri" |

## Language-Specific Agents

| Language | Review specialization | Build Resolver | Patterns Skill | Testing Skill |
|----------|----------|----------------|----------------|---------------|
| Go | `go-reviewer` | `go-build-resolver` | `golang-patterns` | `golang-testing` |
| Rust | `rust-reviewer` | `rust-build-resolver` | `rust-patterns` | `rust-testing` |
| Python | `python-reviewer` | — | `python-patterns` | `python-testing` |
| TypeScript | `typescript-reviewer` | `build-error-resolver` | `frontend-patterns` | `e2e-testing` |
| Java | `java-reviewer` | `java-build-resolver` | `java-coding-standards` | `springboot-tdd` |
| Kotlin | `kotlin-reviewer` | `kotlin-build-resolver` | `kotlin-patterns` | `kotlin-testing` |
| C++ | `cpp-reviewer` | `cpp-build-resolver` | `cpp-coding-standards` | `cpp-testing` |
| C# | `csharp-reviewer` | — | `dotnet-patterns` | `csharp-testing` |
| Dart/Flutter | `flutter-reviewer` | `dart-build-resolver` | `dart-flutter-patterns` | `flutter-test` |

## Parallel Execution Patterns

### Pattern A: Plan + Research (complex features only; 3 agents parallel)
After `grill-with-docs` and task decomposition, launch concurrently:
1. `code-architect` → architecture design
2. `explore` → codebase analysis
3. Context7 / docs-lookup → library docs
→ Merge findings into the spec/tickets and planning files.

### Pattern B: Implement + Test (multi-module parallel)
When implementing independent modules:
1. `feature-agent` → Module A implementation
2. `feature-agent` → Module B implementation
3. `tdd-guide` → Integration test writing
→ Run in parallel, then merge and run full test suite.

### Pattern C: Deploy + Monitor (2 agents parallel)
1. `ci-watcher` → monitor CI pipeline
2. Cloud platform deploy → execute deployment
→ CI-watcher reports status while deploy runs.

### Pattern D: Implement Review + Security (2 axes, security conditional)
- `implement` automatically delegates independent review subagents: requirement correctness/behavior/tests and code quality/design/maintainability. Do not launch a separate code-review step.
- For security-sensitive changes, additionally dispatch `security-reviewer` for vulnerability analysis.
→ Resolve critical/high findings before proceeding.

### Pattern E: Quality Gate (5 checks parallel)
Run all 5 quality gates concurrently:
1. Lint check (language-appropriate linter)
2. Test check (all tests + coverage)
3. Security check (secrets + vulnerability scan)
4. Build check (compilation + type check)
5. Doc check (CLAUDE.md + README.md sync)
→ All must pass before commit.

### Pattern F: Desktop Build (3 platforms parallel)
When releasing a desktop application:
1. `macOS build` → build + sign + notarize .dmg
2. `Windows build` → build + sign .exe/.msi
3. `Linux build` → build .deb/.AppImage
→ All 3 in parallel. Merge release notes from all platforms.

## Multi-Language Coordination

When the project spans multiple languages:

1. **Contract-First API Definitions**: Use OpenAPI (REST) or Protobuf (gRPC) for all service boundaries. Generate client/server stubs.
2. **Shared Schemas**: Define shared data types in a language-agnostic format. Avoid duplicating type definitions across languages.
3. **Consistent Error Handling**: All services return errors in a uniform envelope regardless of language.
4. **Unified Logging**: Structured JSON logging across all services with consistent field names.
5. **Language Isolation**: Each language has its own build, test, and lint config. Integration tests verify contract adherence.

## GitHub Enterprise Automation

### Subagent Dispatching for GitHub Ops

| Agent | When | Responsibility |
|-------|------|----------------|
| `code-architect` | Architecture-changing PRs | Review design decisions, module boundaries |
| `security-reviewer` | Auth/payment/data handling | Security check |
| `ci-watcher` | After PR submission | Monitor CI status until pass |

### Release Management Rules
1. Only release managers can create and push tags.
2. All releases must have a CHANGELOG.md entry.
3. Hotfix must go through the hotfix branch process.
4. Version numbers must be consistent: git tag = package version = CHANGELOG entry.
5. All release tags must be GPG signed.

## Cloud Deployment Automation

### Platform-Specific Subagents
| Cloud | Deploy Agent | Monitor Agent | Config Reference |
|-------|-------------|---------------|-----------------|
| Vercel | `e2e-runner` (preview check) | Vercel Analytics | `references/cloud-platforms/vercel.md` |
| Cloudflare | `deployment-patterns` | Workers Metrics | `references/cloud-platforms/cloudflare.md` |
| Tencent | `deployment-patterns` | Cloud Monitor | `references/cloud-platforms/tencent-cloud.md` |
| Alibaba | `deployment-patterns` | Cloud Monitor | `references/cloud-platforms/alibaba-cloud.md` |
| Huawei | `deployment-patterns` | Cloud Eye | `references/cloud-platforms/huawei-cloud.md` |

### Cloud Deploy Flow
1. Run `/quality-gate` — all gates must pass.
2. Run `/deploy-check` — verify migration, env vars, rollback plan.
3. Run `/cloud-deploy <target> <platform>` — execute platform deployment.
4. Monitor via platform dashboard + logs.
5. Verify health check passes, then mark deployment as complete.

## Development Standards

- **Package Management**: Prefer language-native tools (go mod, cargo, uv, pnpm, maven/gradle).
- **Testing**: Add and run tests appropriate to the change; preserve the project's test conventions and meaningful coverage.
- **Formatting**: Use language-standard formatter (gofmt, rustfmt, ruff, prettier).
- **Commits**: Conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).
- **PRs**: Must include change summary, test plan, and quality gate evidence.
- **Immutability**: Always create new objects, never mutate in place.
- **Error Handling**: Explicitly handle at every level. Never silently swallow.
- **Secrets**: Via environment variables or platform secret stores. Never hardcoded.
