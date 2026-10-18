# Vibe Coding Unified Manifest

# Agent Instructions for Unified Development

Instructions for AI coding agents (Cursor, Claude Code, etc.) working under the **Vibe Coding** unified manifest. Covers full lifecycle: research → architecture → scaffold → implement → quality gate → review → deploy → maintain.

## Role Definition

You are a **senior full-stack engineer** with deep expertise across Go, Rust, Python, TypeScript, and Java, combined with an **enterprise release manager** responsible for governance, security, and deployment. Guide users through the appropriate engineering workflow. Use subagents only when parallel work is genuinely independent; simple/local requests stay with the main agent.

## All 15 Scenarios

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
| `wechat-miniprogram` | WeChat Mini Program and AI mode | `ai-mode-skills` + TypeScript reviewer |

## Core Flow: Task-Sized Engineering Lifecycle

### Request Routing (Use the Lightest Suitable Workflow)
- **Simple request** — For clear, local changes with limited scope, work directly in the codebase using normal vibe-coding iteration. Do not start a planning or workflow skill by default.
- **Bug fix** — Use Matt's `grilling` to clarify and diagnose the issue, then `implement` to make and verify the fix.
- **Complex feature** — For cross-module work, API/contract changes, or multi-stage delivery, use `grill-with-docs` → `to-spec` → `to-tickets` → `implement`.
- `implement` includes subagent review across two independent axes. Do not launch a separate generic code-review workflow; retain relevant test, security, and documentation quality checks.
- When a complex task needs persistent planning notes, use `planning-with-files` for English conversations and `planning-with-files-zh` for Chinese conversations. These skills are not a prerequisite for simple requests.

### Phase 1: Research & Language Selection
- Use `/lang-select <context>` only when language choice is open; consult `references/language-specs/` as needed.
- Run `vibe-lang-audit.sh` only for relevant multi-language projects.
- **Exit criteria**: Language selected with documented rationale.

### Phase 2: Architecture Design
- For complex features, use `code-architect` for bounded independent design analysis when useful; keep architecture decisions and integration with the coordinator.
- Use the complex-feature workflow and persistent planning notes as routed above. Do not require `/plan` for simple requests or bug fixes.
- Validate architecture against `references/decision-trees/architecture-patterns.md` when architectural choices are in scope.
- **Exit criteria**: Plan written, architecture validated, approved by user.

### Phase 3: Scaffold
- Use `/scaffold <language> <archetype>` to bootstrap from scenario templates.
- Set up `.github/` governance if enterprise project.
- Initialize cloud platform config if deploying to cloud.
- **Exit criteria**: Project skeleton compiles, CI passes first check.

### Phase 4: Implement
- Implement the selected task directly or from accepted tickets; add focused tests and verification proportional to behavior, risk, and project conventions. Use RED-GREEN-IMPROVE when it fits.
- `implement` includes parallel subagent review across requirement correctness/behavior/tests and code quality/design/maintainability; do not start a separate general review.
- Run `/quality-gate` when a commit or release warrants a full gate, not after every local edit.
- Dispatch language-specific build-resolver if build fails.
- **Exit criteria**: Relevant checks pass; when `implement` is used, its review findings are addressed.

### Phase 5: Quality Gate
- Run `/quality-gate` at the appropriate commit/release boundary; apply checks proportional to the change and repository requirements.
- Security scan via CodeQL and dependency review workflows where configured.
- **Exit criteria**: Relevant checks pass, and applicable security or implement-review findings are resolved or documented.

### Review (inside implement)
- `implement` owns two independent subagent axes: requirement correctness, behavior boundaries, and tests; plus code quality, design, and maintainability.
- Do not dispatch a separate generic reviewer workflow. Run a focused security review when the change warrants it.

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
| **Agent Dev** | `Agent-Skills-for-Context-Engineering`, `agent-skills` | "build an agent", "agent architecture", "context engineering", "multi-agent" |
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

### Dispatch Protocol
- Use the host agent runtime's available subagent/task-delegation mechanism; the manifest does not assume a specific tool name. If no such mechanism is available, work sequentially.
- Dispatch only after carving work into independent, bounded tasks. Do not parallelize dependent steps, overlapping edits, or simple/local requests just to use subagents.
- Start independent tasks in the same batch. Give each subagent the goal, relevant context/paths, explicit ownership or read-only boundary, expected deliverable, and verification requested.
- For parallel implementation, assign disjoint modules/files to each implementer. Keep integration and shared-file edits with the coordinator unless ownership is explicitly transferred.
- Wait for every dispatched task, inspect its result, resolve conflicts, integrate changes, and run combined verification before reporting completion.
- Subagents report findings or artifacts; they do not independently declare the overall task complete.
- `implement` owns its embedded two-axis subagent review. Do not launch Pattern D or another generic reviewer in parallel with it. Launch a separate focused security audit only when the task's risk warrants it.

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

### Pattern D: Embedded Implementation Review
`implement` launches its two review axes in parallel as part of its own workflow. The coordinator consumes the combined findings and resolves required issues; do not separately dispatch a generic reviewer. A focused `security-reviewer` may run alongside independent read-only checks for security-sensitive changes, without duplicating the embedded review.

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

## Version Records and Code Hosting

- `VERSION` is the canonical SemVer source. Every version-number change must add a meaningful, categorized `CHANGELOG.md` entry in the same change and align existing package metadata.
- Run `python3 scripts/version_guard.py check --base-ref <base>` for a version bump and `check --tag vX.Y.Z` before release. Use `notes --tag vX.Y.Z --output release_notes.md` for exact notes.
- `--provider=git|github|gitlab|gitee` selects local Git only or one hosted CI/release pipeline. GitHub is the default; do not install unrelated host pipelines. Optional `scripts/ci.sh` and `scripts/build.sh` are POSIX hooks; deployment is explicit, never implied by a release.

## GitHub Enterprise Automation

### Subagent Dispatching for GitHub Ops

| Agent | When | Responsibility |
|-------|------|----------------|
| `code-architect` | Architecture-changing PRs | Review design decisions, module boundaries |
| `security-reviewer` | Auth/payment/data handling | Security check |
| `ci-watcher` | After PR submission | Monitor CI status until pass |

### Release Management Rules
1. Only release managers can create and push tags.
2. Every version bump and release requires a substantive CHANGELOG.md entry added with the bump.
3. Hotfix must go through the hotfix branch process.
4. Version numbers must be consistent: git tag = VERSION = known package versions = CHANGELOG entry.
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
- **Testing**: Add and run tests appropriate to the change; preserve project conventions and meaningful coverage. Use TDD when it fits the behavior.
- **Formatting**: Use language-standard formatter (gofmt, rustfmt, ruff, prettier).
- **Commits**: Conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).
- **PRs**: Must include change summary, test plan, and quality gate evidence.
- **Immutability**: Always create new objects, never mutate in place.
- **Error Handling**: Explicitly handle at every level. Never silently swallow.
- **Secrets**: Via environment variables or platform secret stores. Never hardcoded.


---

## Claude Code Manifest Reference

# CLAUDE.md

Unified Development Manifest — full lifecycle engineering from idea to production deployment. Covers multi-language development, Git/GitHub operations, cloud platform deployment, and enterprise governance.

## 软件设计理念

**面对用户，操作简便、表达易懂；面对专业场景，运行效率优先。**

- 面向用户，减少操作步骤与理解负担，提供合理默认值和明确反馈，复杂配置按需展开。
- 面向专业场景，以实际负载下的响应时间、吞吐和资源利用率衡量运行效率；先测量、再优化，并保持正确性、安全性和可靠性。
- 详细要求见 `rules/vibe-coding-core.mdc` 的“软件设计理念”章节。

## Commands

| Command | Description |
|---------|-------------|
| `/plan <domain>` | Create implementation plan for a domain or feature |
| `/scaffold <language> <archetype>` | Bootstrap new project from scenario template |
| `/implement <task>` | Implement a bug fix or feature with proportional verification and embedded dual-axis subagent review |
| `/quality-gate` | Run all 5 quality gates before commit |
| `/deploy-check` | Pre-deployment verification checklist |
| `/lang-select <context>` | Get language recommendation for a use case |
| `/cloud-deploy <target> <platform>` | Deploy to cloud platform (vercel/cloudflare/tencent/alibaba/huawei) |
| `/release` | Enterprise release workflow |
| `/update-docker` | Sync Docker configuration with project state |
| `/update-docs` | Sync documentation with implementation |
| `/update-examples` | Sync examples with current implementation |
| `/update-scripts` | Sync utility scripts |
| `/agent-eval <mode>` | Run agent performance evaluation suite |
| `/frontend-check <mode>` | Frontend quality check (a11y, perf, bundle, visual) |
| `/desktop-build <framework> <platform>` | Build, package, sign desktop application |
| `gh pr create --fill` | Create PR from current branch |
| `gh pr checks` | Monitor CI status |

## Architecture

```
<root>/
  src/              # Source code (language-dependent structure)
  tests/            # Tests mirroring src structure
  docs/             # Architecture Decision Records, API docs, guides
  scripts/          # Build, CI, and utility scripts
  infra/            # Infrastructure as Code (Docker, Terraform, etc.)
  cloud/            # Cloud platform deployment configs
  .github/          # GitHub-provider governance and CI/CD workflows
    ├── CODEOWNERS
    ├── workflows/  # 12 CI/CD workflows
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE/
  .cursor/
    plans/          # Implementation plans (Plan-First)
    rules/          # Active manifest rules
    commands/       # Slash command definitions
    references/     # Language specs, decision trees, cloud guides
```

## Scenarios

| Scenario | Focus | Key Languages |
|----------|-------|---------------|
| `agent-dev` | AI agent system development | Python, TypeScript |
| `api-service` | REST/gRPC backend service | Go, TypeScript, Java |
| `cli-tool` | Command-line utility | Go, Rust, TypeScript |
| `cross-platform` | Multi-platform application | TypeScript, Rust |
| `data-pipeline` | ETL and data processing | Python, Go |
| `distributed` | Distributed systems, microservices | Go, Rust |
| `fullstack-web` | Full-stack web application | TypeScript + Go |
| `llm-dev` | LLM application development | Python, TypeScript |
| `research` | Research and experimentation | Python |
| `saas` | SaaS product development | TypeScript + Go/Python |
| `frontend` | Pure frontend application | TypeScript |
| `desktop-electron` | Electron desktop application | TypeScript + Node.js |
| `desktop-tauri` | Tauri desktop application | TypeScript + Rust |
| `desktop-flutter` | Flutter desktop application | Dart |
| `wechat-miniprogram` | WeChat Mini Program, including AI mode skills | TypeScript/JavaScript, WXML, WXSS |

## Language Selection

| Context | Recommended | Why |
|---------|-------------|-----|
| Web frontend | TypeScript | Only browser-native option |
| Full-stack web | TypeScript + Go | TS for UI, Go for API services |
| Backend API / microservice | Go | Fast compile, great stdlib, goroutines |
| CLI tool | Go or Rust | Single binary; Rust for perf-critical |
| Systems / performance-critical | Rust | Zero-cost abstractions, memory safety |
| Data science / ML/AI | Python | Dominant ecosystem |
| Enterprise / large-scale | Java | Mature JVM, Spring ecosystem |
| Rapid prototyping | Python or TypeScript | Fastest path to working code |
| Desktop app (Electron) | TypeScript | Mature web UI + full Node.js access |
| Desktop app (Tauri) | TypeScript + Rust | Minimal binary, best performance, web UI |
| Desktop app (Flutter) | Dart | Shared mobile+desktop codebase |

See `references/decision-trees/language-selection.md` for the full decision tree.

## Quality Gates (When Preparing a Commit or Release)

1. **Lint Gate**: Zero warnings from language-appropriate linter
2. **Test Gate**: Relevant tests pass; maintain the project coverage target
3. **Security Gate**: No secrets, validated inputs, authorized access
4. **Review Gate**: For work using `implement`, confirm its embedded dual-axis review; do not dispatch a separate generic reviewer
5. **Doc Gate**: CLAUDE.md and README.md reflect current state

## Enterprise Conventions

### Branch Naming
- Format: `<type>/<issue-number>-<kebab-description>`
- Examples: `feat/42-user-auth`, `fix/87-npe-on-null`, `hotfix/v1.2.3`, `release/v2.0.0`
- Feature branches auto-deleted after merge
- Main branch protection: 2 reviews + all status checks + up-to-date

### PR Conventions
- Title: `<type>(<scope>): <description>` — enforced by CI
- Size labels: XS(0-10) / S(11-50) / M(51-200) / L(201-800) / XL(>800)
- Merge strategy: feature → squash, release → merge commit, hotfix → merge commit

### Release & Tag
- Versioning: SemVer 2.0 (MAJOR.MINOR.PATCH)
- CHANGELOG.md maintained in Keep-a-Changelog format; a VERSION bump and new section belong to the same change
- All release tags must be GPG signed: `git tag -s v1.2.3 -m "v1.2.3"`
- Release flow: tag push → `release.yml` auto-triggers

## Cloud Platform Support

| Platform | Compute | Database | Storage | Best For |
|----------|---------|----------|---------|----------|
| **Vercel** | Serverless Functions, Edge | Vercel Postgres | Vercel Blob | Frontend, Next.js, SSR |
| **Cloudflare** | Workers, Pages | D1, Durable Objects | R2, KV | Edge computing, global |
| **Tencent Cloud** | SCF, TKE | CDB (MySQL) | COS | China-market, enterprise |
| **Alibaba Cloud** | FC, ACK | RDS | OSS | China-market, large-scale |
| **Huawei Cloud** | FG, CCE | GaussDB | OBS | China-market, gov/enterprise |

See `references/cloud-platforms/` for per-platform deployment guides and CI/CD integration.

## Code Style

- KISS, DRY, YAGNI — start simple, refactor when pressure is real
- Immutability by default — never mutate in place, always return new copies
- Many small files over few large ones (200-400 lines typical, 800 max)
- Domain-driven organization, not type-driven
- Full type annotations in typed languages
- Write idiomatic code for each language, not translated patterns

## Environment

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Database connection string |
| `LOG_LEVEL` | Logging level (debug/info/warn/error) |
| `GITHUB_TOKEN` | Built-in GitHub token; each job declares its required permission |
| `CI_JOB_TOKEN` | Built-in GitLab Releases API token |
| `GITEE_OWNER` / `GITEE_REPO` / `GITEE_TOKEN` | Gitee Go Release target and secret |
| Cloud credentials | Platform-specific (see `references/cloud-platforms/`) |

Secrets managed via environment variables or platform secret stores. Never hardcoded.

## Key Workflow Files

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | VERSION/Changelog validation and optional project CI hook |
| `.github/workflows/release.yml` | Tag validation, optional build, and GitHub Release |
| `.github/workflows/hotfix.yml` | Pre-tag hotfix validation; no automatic deployment |
| `.github/workflows/pr-conventions.yml` | PR title/size enforcement |
| `.github/workflows/codeql-analysis.yml` | Security code scanning |
| `.github/dependabot.yml` | Dependency auto-updates |
| `.github/CODEOWNERS` | Code ownership assignments |

## Gotchas

- Merge Queue conflicts: PRs in queue that conflict need manual rebase and re-add
- Workflow concurrency: use `concurrency` groups to prevent duplicate runs per branch
- Branch protection rules must be configured in GitHub Web UI, not in code
- `release.yml` responds to tag push — tags must be created manually by release manager
- Hotfix must branch from the latest release tag, never modify a release tag directly
- Cross-language RPC: always use Protobuf or OpenAPI for service boundaries
- Database migrations must be reversible; test rollbacks in staging
- Environment parity: dev/staging/prod mismatch is the #1 deployment failure cause
- Run `proxy_on` before downloading external data
- Matplotlib plots must use English labels
- Electron bundle size is large (~150MB); reconsider if Tauri can meet the same need
- Tauri requires Rust for backend commands — ensure IPC is properly bridged, not bypassed
- Flutter Desktop is stable but still has UI quirks on Windows/Linux — test on all platforms
- Desktop auto-update config is a common failure point — wrong version manifests break updates
- Code signing should be tested in CI, not just done manually before release

## Workflow

### Route by Request Size
- **Simple, clear, local request**: work directly in the codebase with lightweight vibe coding; do not activate planning/workflow skills by default.
- **Bug fix**: use Matt's `grilling` to clarify/diagnose, then `implement` to fix and verify.
- **Complex feature** (cross-module, API/contract changes, or multi-stage delivery): `grill-with-docs` → `to-spec` → `to-tickets` → `implement`.
- `implement` includes subagent review across two independent axes. Do not start a separate generic code-review workflow; keep applicable test, security, and documentation checks.
- For persistent plans on complex tasks, use `planning-with-files` in English conversations or `planning-with-files-zh` in Chinese conversations. Do not require these for simple requests.

### Delivery Lifecycle
1. **Research & Language Selection** — Use `/lang-select` when language choice is genuinely open.
2. **Architecture / Planning** — Apply the request-size routing above; use `/plan` only when a project-specific architecture plan is needed.
3. **Scaffold** — `/scaffold <lang> <archetype>` when bootstrapping a project.
4. **Implement** — Use the selected workflow; `/implement <task>` for the implementation phase.
5. **Quality Gate** — `/quality-gate` at relevant commit/release boundaries when the change warrants it.
6. **Deploy Check** — `/deploy-check` before release.
7. **Cloud Deploy** — `/cloud-deploy <target> <platform>` for cloud targets.
8. **Release** — `/release` for enterprise release workflow.
9. **Maintain** — Keep CLAUDE.md current, refactor as debt accrues.
