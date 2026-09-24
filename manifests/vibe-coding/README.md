# Vibe Coding Unified Manifest

Full lifecycle engineering manifest covering 0-to-1 project building → development → testing → CI/CD → production deployment across 5 languages and 5 cloud platforms.

## What's Included

- **MANIFEST.md**: Canonical AI instructions; `AGENTS.md` and `CLAUDE.md` are symlinks to it in the manifest and initialized projects.
- **15 Scenarios**: agent-dev, api-service, cli-tool, cross-platform, data-pipeline, distributed, frontend, fullstack-web, llm-dev, research, saas, desktop-electron, desktop-tauri, desktop-flutter, wechat-miniprogram.
- **17 Rules**: Core, standards, collaboration, lifecycle, deployment, backend, frontend, testing, refactoring, optimization, UI design, cloud, enterprise, agent-dev, desktop, frontend-scenario, CLAUDE.md maintenance.
- **15 Commands**: plan, scaffold, implement, quality-gate, deploy-check, lang-select, cloud-deploy, release, agent-eval, frontend-check, desktop-build, update-docker, update-docs, update-examples, update-scripts.
- **5 Cloud Platform References**: Vercel, Cloudflare, Tencent Cloud, Alibaba Cloud, Huawei Cloud.
- **5 Language Specs + Decision Trees**: Go, Rust, Python, TypeScript/JavaScript, Java.
- **GitHub Enterprise Governance**: 12 CI/CD workflows, issue/PR templates, CODEOWNERS, SECURITY.md, dependabot config.
- **Enterprise References**: Branching strategy, release process, PR conventions, tag conventions.
- **8 Skills installed on init**: Four manifest-bundled skills, `canvas-design`, and the three `wxa-skills-*` skills from the managed `ai-mode-skills` submodule.
- **Templates**: CHANGELOG, README, release checklist, roadmap.

## Quick Start

### Initialize a New Project

```bash
bash manifests/vibe-coding/scripts/vibe-init.sh \
  --scenario=fullstack-web \
  --cloud=vercel \
  --org mycompany \
  --repo my-app
```

### Available Init Flags

```
--scenario=<name>[,<name>...]   15 scenarios (agent-dev, api-service, cli-tool, cross-platform,
                                  data-pipeline, distributed, frontend, fullstack-web,
                                  llm-dev, research, saas,
                                  desktop-electron, desktop-tauri, desktop-flutter,
                                  wechat-miniprogram)
--cloud=<provider>              vercel / cloudflare / tencent / alibaba / huawei
-o, --owner <owner>             CODEOWNERS default owner
--org <org>                     GitHub organization
--repo <repo>                   GitHub repository
--email <email>                 Security contact email
--git / --no-git                Git initialization (default: auto)
-f, --force                     Overwrite existing files
-n, --dry-run                   Preview without writing
```

### Scenarios Summary

| Scenario | Focus | Languages |
|----------|-------|-----------|
| `agent-dev` | AI agent systems | Python, TypeScript |
| `api-service` | REST/gRPC backend | Go, TypeScript, Java |
| `cli-tool` | CLI utilities | Go, Rust, TypeScript |
| `cross-platform` | Multi-platform apps | TypeScript, Rust |
| `data-pipeline` | ETL and data processing | Python, Go |
| `distributed` | Distributed systems | Go, Rust |
| `fullstack-web` | Full-stack web apps | TypeScript + Go |
| `llm-dev` | LLM applications | Python, TypeScript |
| `research` | Research/experimentation | Python |
| `saas` | SaaS products | TypeScript + Go/Python |
| `frontend` | Pure frontend apps | TypeScript |
| `desktop-electron` | Electron desktop | TypeScript + Node.js |
| `desktop-tauri` | Tauri desktop | TypeScript + Rust |
| `desktop-flutter` | Flutter desktop | Dart |
| `wechat-miniprogram` | WeChat Mini Program and AI mode skills | TypeScript/JavaScript, WXML, WXSS |

## Language Support

| Language | Reviewer | Build Resolver | Patterns | Testing |
|----------|----------|----------------|----------|---------|
| Go | go-reviewer | go-build-resolver | golang-patterns | golang-testing |
| Rust | rust-reviewer | rust-build-resolver | rust-patterns | rust-testing |
| Python | python-reviewer | — | python-patterns | python-testing |
| TypeScript | typescript-reviewer | build-error-resolver | frontend-patterns | e2e-testing |
| Java | java-reviewer | java-build-resolver | java-coding-standards | springboot-tdd |
| Kotlin | kotlin-reviewer | kotlin-build-resolver | kotlin-patterns | kotlin-testing |
| C++ | cpp-reviewer | cpp-build-resolver | cpp-coding-standards | cpp-testing |
| C# | csharp-reviewer | — | dotnet-patterns | csharp-testing |
| Dart/Flutter | flutter-reviewer | dart-build-resolver | dart-flutter-patterns | flutter-test |

## Cloud Platforms

| Platform | Deploy Command | Reference |
|----------|---------------|-----------|
| Vercel | `vercel deploy --prod` | `references/cloud-platforms/vercel.md` |
| Cloudflare | `wrangler deploy` | `references/cloud-platforms/cloudflare.md` |
| Tencent Cloud | `serverless deploy` | `references/cloud-platforms/tencent-cloud.md` |
| Alibaba Cloud | `fun deploy` | `references/cloud-platforms/alibaba-cloud.md` |
| Huawei Cloud | `fgs deploy` | `references/cloud-platforms/huawei-cloud.md` |

## Desktop Frameworks

| Framework | Best For | Reference |
|-----------|----------|-----------|
| Electron | Full Node.js + Chromium access, mature ecosystem | `scenarios/desktop-electron/` |
| Tauri | Minimal binary, Rust backend, best security | `scenarios/desktop-tauri/` |
| Flutter Desktop | Shared mobile+desktop codebase | `scenarios/desktop-flutter/` |

See `references/desktop-frameworks.md` for full comparison and decision guide.

## Dependencies

- **Bash**: Init and maintenance scripts.
- **Git**: Version control.
- **GitHub CLI** (`gh`): Repository operations, CI monitoring, releases.
- **Language toolchains**: Go, Rust, Python (uv), Node (pnpm), Java (maven/gradle) as needed.
- **Cloud CLIs**: Platform-specific CLIs for cloud deployments.

## File Count

~150 files total covering the complete engineering lifecycle from idea to production.
