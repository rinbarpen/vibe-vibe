# CLAUDE.md

Unified Development Manifest — multi-language engineering with task-sized workflows, verification, Git/GitHub operations, cloud deployment, and enterprise governance.

## Commands

| Command | Description |
|---------|-------------|
| `/plan <domain>` | Create a plan when a task has meaningful architecture or coordination needs |
| `/scaffold <language> <archetype>` | Bootstrap new project from scenario template |
| `/implement <task>` | Implement a bug fix or feature; includes two-axis subagent review |
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
    plans/          # Planning files for medium/large work
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

## Quality Gates (When Preparing a Commit or Release)

1. **Lint Gate**: Zero warnings from language-appropriate linter
2. **Test Gate**: Relevant tests pass; maintain the project coverage target
3. **Security Gate**: No secrets, validated inputs, authorized access
4. **Review Gate**: For work using `implement`, confirm its independent correctness and code-quality review; do not dispatch a second general review
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

- **Simple request**: vibe code directly; make the smallest change and run relevant checks without creating planning artifacts or invoking extra workflow skills.
- **Bug fix**: `grilling` → `implement`.
- **Complex feature**: `grill-with-docs` → `to-spec` → `to-tickets` → `implement`. For medium/large work, track progress with `planning-with-files-zh` for Chinese or `planning-with-files` for English.
- **Review**: `implement` includes two independent subagent review axes—correctness (requirements, behavior, tests) and code quality (design, maintainability). Do not manually initiate a separate code-review step. Invoke security review for security-sensitive changes.
- Use `/scaffold`, `/quality-gate`, `/deploy-check`, `/cloud-deploy`, and `/release` when their concrete project or delivery need applies; they are not mandatory steps for every request.
