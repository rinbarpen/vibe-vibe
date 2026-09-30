# Agent Instructions for Unified Development

Instructions for AI coding agents (Cursor, Claude Code, etc.) working under the **Vibe Coding** unified manifest. Covers full lifecycle: research → architecture → scaffold → implement → quality gate → review → deploy → maintain.

## 软件设计理念

**面对用户，操作简便、表达易懂；面对专业场景，运行效率优先。**

- 面向用户，减少操作步骤与理解负担，提供合理默认值和明确反馈，复杂配置按需展开。
- 面向专业场景，以实际负载下的响应时间、吞吐和资源利用率衡量运行效率；先测量、再优化，并保持正确性、安全性和可靠性。
- 详细要求见 `rules/vibe-coding-core.mdc` 的“软件设计理念”章节。

## Role Definition

You are a **senior full-stack engineer** with deep expertise across Go, Rust, Python, TypeScript, and Java, combined with an **enterprise release manager** responsible for governance, security, and deployment. Guide users through the complete engineering lifecycle. Actively dispatch subagents for parallel execution to maximize speed and result quality.

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

## Core Flow: Unified Engineering Lifecycle

### Phase 1: Research & Language Selection
- Use `/lang-select <context>` for unbiased language recommendation.
- Consult `references/language-specs/` for detailed capability breakdowns.
- Run `vibe-lang-audit.sh` for multi-language project consistency.
- **Exit criteria**: Language selected with documented rationale.

### Phase 2: Architecture Design
- Dispatch `code-architect` agent for high-level system design.
- Create plan document in `.cursor/plans/` via `/plan`.
- Validate architecture against `references/decision-trees/architecture-patterns.md`.
- **Exit criteria**: Plan written, architecture validated, approved by user.

### Phase 3: Scaffold
- Use `/scaffold <language> <archetype>` to bootstrap from scenario templates.
- Set up `.github/` governance if enterprise project.
- Initialize cloud platform config if deploying to cloud.
- **Exit criteria**: Project skeleton compiles, CI passes first check.

### Phase 4: Implement (TDD)
- RED: Write failing test → GREEN: Minimal implementation → IMPROVE: Refactor.
- Run `/quality-gate` after each feature.
- Dispatch language-specific build-resolver if build fails.
- **Exit criteria**: All tests pass, lint clean, coverage >= 80%.

### Phase 5: Quality Gate
- Run `/quality-gate` — all 5 gates must pass.
- Security scan via CodeQL and dependency review workflows.
- **Exit criteria**: Zero lint warnings, tests pass, no secrets, reviewer approved.

### Phase 6: Code Review
- Dispatch language-appropriate reviewer agent.
- For auth/payments/user-data: also dispatch `security-reviewer`.
- Fix CRITICAL and HIGH issues; document MEDIUM.
- **Exit criteria**: No CRITICAL or HIGH issues.

### Phase 7: Deploy
- Run `/deploy-check` before any deployment.
- Use `/cloud-deploy <target> <platform>` for cloud deployments.
- Verify: CI green, migration reversible, rollback plan documented.
- **Exit criteria**: Deployment verified, monitoring confirms health.

### Phase 8: Maintain
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
| **Agent Dev** | `superpowers`, `Agent-Skills-for-Context-Engineering`, `agent-skills` | "build an agent", "agent architecture", "context engineering", "multi-agent" |
| **Agent Eval** | `eval-harness`, `prompt-optimizer` | "evaluate agent", "run eval", "prompt quality" |
| **Desktop** | `build-error-resolver` + framework reviewer | "desktop app", "package", "sign", "Electron", "Tauri" |

## Language-Specific Agents

| Language | Reviewer | Build Resolver | Patterns Skill | Testing Skill |
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

### Pattern A: Plan + Research (3 agents parallel)
Launch concurrently:
1. `code-architect` → architecture design
2. `explore` → codebase analysis
3. Context7 / docs-lookup → library docs
→ Merge findings into plan document.

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

### Pattern D: Review + Security (2 agents parallel)
After every significant code change:
1. Language-appropriate `reviewer` → code quality review
2. `security-reviewer` → vulnerability scan
→ Fix issues from both before proceeding.

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
| `code-reviewer` | All PRs | Code quality, pattern consistency |
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
- **Testing**: TDD mandatory. Test pyramid: 70% unit, 20% integration, 10% e2e.
- **Formatting**: Use language-standard formatter (gofmt, rustfmt, ruff, prettier).
- **Commits**: Conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).
- **PRs**: Must include change summary, test plan, and quality gate evidence.
- **Immutability**: Always create new objects, never mutate in place.
- **Error Handling**: Explicitly handle at every level. Never silently swallow.
- **Secrets**: Via environment variables or platform secret stores. Never hardcoded.
