# CLAUDE.md

Unified Development Manifest — full lifecycle engineering from idea to production deployment. Covers multi-language development, Git/GitHub operations, cloud platform deployment, and enterprise governance.

## Commands

| Command | Description |
|---------|-------------|
| `/plan <domain>` | Create implementation plan for a domain or feature |
| `/scaffold <language> <archetype>` | Bootstrap new project from scenario template |
| `/implement <task>` | Implement a feature following TDD (RED-GREEN-IMPROVE) |
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
  .github/          # GitHub governance and CI/CD workflows
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

## Quality Gates (Mandatory Before Every Commit)

1. **Lint Gate**: Zero warnings from language-appropriate linter
2. **Test Gate**: 80%+ coverage, all tests pass
3. **Security Gate**: No secrets, validated inputs, authorized access
4. **Review Gate**: Embedded dual-axis subagent review in `implement`; no separate generic reviewer dispatch
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
- CHANGELOG.md maintained in Keep-a-Changelog format
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
| `GITHUB_TOKEN` | GitHub API (needs `contents: write` + `pull-requests: write`) |
| `CODECOV_TOKEN` | Coverage report upload |
| `DOCKER_USERNAME` / `DOCKER_PASSWORD` | Container registry publishing |
| Cloud credentials | Platform-specific (see `references/cloud-platforms/`) |

Secrets managed via environment variables or platform secret stores. Never hardcoded.

## Key Workflow Files

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Build, lint, matrix test, coverage |
| `.github/workflows/release.yml` | Standard release pipeline |
| `.github/workflows/hotfix.yml` | Emergency fix pipeline |
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
- Do not use or route to `superpowers` in this manifest.

### Delivery Lifecycle

1. **Research & Language Selection** — Use `/lang-select` when language choice is genuinely open.
2. **Architecture / Planning** — Apply the request-size routing above; use `/plan` only when a project-specific architecture plan is needed.
3. **Scaffold** — `/scaffold <lang> <archetype>` when bootstrapping a project.
4. **Implement** — Use the selected workflow; `/implement <task>` for the implementation phase.
5. **Quality Gate** — `/quality-gate` before every commit.
6. **Deploy Check** — `/deploy-check` before release.
7. **Cloud Deploy** — `/cloud-deploy <target> <platform>` for cloud targets.
8. **Release** — `/release` for enterprise release workflow.
9. **Maintain** — Keep CLAUDE.md current, refactor as debt accrues.
