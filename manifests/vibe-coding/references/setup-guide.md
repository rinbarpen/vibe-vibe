# Vibe Coding 安装与配置参考

初次使用从[模板首页](../README.md)开始。本页只在选择场景、托管平台和运行依赖时查阅。

## 安装方式与依赖

使用 `vibe init` 创建新项目，使用 `vibe add manifest` 为已有项目增加配置。CLI 会安装模板声明的必需 Skills；直接运行 `scripts/vibe-init.sh` 只安装骨架，不安装这些依赖。

安装不会自动完成业务应用、部署服务或运行测试。项目已有的业务约定优先，不把模板规则当成用户对外部动作的批准。

## 更新与回退

`vibe update manifest vibe-coding <项目目录> --dry-run` 预览，去掉 `--dry-run` 后更新。默认复用安装记录；旧项目按提示补齐适用的 provider/scenario/owner/org/repo/email 参数。更新保留项目 README、版本和数据，有变更时打印本次独立恢复命令。

新依赖不会通过 update 自动补装；需要时显式安装。图和文档工具只分发列明的资源，不复制任意 references/scripts。

## Skills 首次配置

Matt Pocock 工程技能在使用前需按 `/setup-matt-pocock-skills` 完成项目设置。安装副本不等于设置已执行；发布的工程/效率/杂项来源之外的翻译维护、beta 与退休内容不属于默认依赖。设计技能列表是可选资源，不保证每一项都已安装。

下面的标志是初始化脚本的接口；`vibe init --help` 与具体脚本的帮助是各自接口的依据，脚本标志不一定全部经 CLI 透传。

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
--provider=<name>             git / github / gitlab / gitee (default: github)
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

## Version records and CI/CD

Initialization creates root `VERSION` and `CHANGELOG.md` unless already present. Every version bump must add a meaningful Changelog section in the same change. Before merging, run `python3 scripts/version_guard.py check --base-ref origin/main`; tag releases use `check --tag vX.Y.Z` and publish that section only.

Optional POSIX hooks are `scripts/ci.sh` and `scripts/build.sh`; existing `dist/` files are attached to the release.

Select `--provider=git` for a local-only workflow, or choose GitHub, GitLab, or Gitee. GitLab needs runners; Gitee needs Gitee Go plus `GITEE_OWNER`, `GITEE_REPO`, and secret `GITEE_TOKEN`. Release details are maintained in the project's `.cursor/references/release-process.md`.

## Dependencies

- **Bash**: Init and maintenance scripts.
- **Git**: Version control.
- **GitHub CLI** (`gh`): Optional for GitHub repository operations and CI monitoring.
- **Language toolchains**: Go, Rust, Python (uv), Node (pnpm), Java (maven/gradle) as needed.
- **Cloud CLIs**: Platform-specific CLIs for cloud deployments.

