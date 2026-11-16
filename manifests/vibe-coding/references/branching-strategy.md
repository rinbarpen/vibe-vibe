# Branch Strategy Guide

## 本地优先，远程按需

无 remote、账号、PR 或 Issue 编号也支持独立本地分支与 worktree。已有 remote 不自动触发发布；任务要求 PR/MR 或远程合并时才使用实际平台。[完整交互流程](git-collaboration.md)覆盖范围选择、Issue 可选关联、CI/评审等待、恢复、合并、清理和回退。

本地多任务先查看 `git branch -vv`、`git worktree list --porcelain` 和 `git status --short`，或运行项目根目录的 `python3 scripts/git_collaboration.py inspect --root .`。保护 dirty 修改；已被 worktree 占用的分支不强制切换。只开发时可保留分支，不强制合并或创建 PR。

## Strategy Comparison

| 维度 | GitHub Flow | Git Flow | Trunk-based Development |
|------|-------------|----------|------------------------|
| **适用场景** | 快速迭代 SaaS、小团队 | 多版本维护、合规要求高 | DevOps 极致效率、大团队 |
| **主要分支** | `main` + short feature branches | `main`, `develop`, `release/*`, `hotfix/*` | `main` + short-lived feature branches |
| **Feature 分支** | 从 `main` 创建，PR 合并回 `main` | 从 `develop` 创建，PR 合并回 `develop` | 从 `main` 创建，rebase 后 fast-forward |
| **合并方式** | Squash merge | Merge commit | Rebase + fast-forward |
| **Release** | 从 `main` 打 tag | `release/*` 分支 → `main` + `develop` | 从 `main` 打 tag |
| **Hotfix** | 从 `main` 创建 → 修复 → PR | `hotfix/*` → `main` + `develop` | 从 `main` 创建 → 修复 → PR |
| **保护规则** | 2 reviews + status checks | 分层保护（develop/release/main） | 1 review + 自动合并 |
| **优势** | 简单、快速部署 | 多版本并行、严格的发布管理 | 最小化分支冲突、持续集成 |
| **劣势** | 不适合多版本维护 | 复杂、merge 频繁 | 需要高测试覆盖率 |

## 选择建议

- **SaaS / Web 应用**：GitHub Flow（最简单）
- **库/框架/SDK**：Git Flow（需要维护多个版本）
- **合规/监管行业**：Git Flow（审计追踪）
- **大型团队（>50 人）**：Trunk-based（减小 merge 冲突）
- **移动 App**：Git Flow（发版节奏明确）

## Branch Naming Convention

```
<type>/<kebab-description>
# 关联已有 Issue 时可选：<type>/<issue-number>-<kebab-description>
```

### Types

| Prefix | Purpose | Source Branch | Merge Into |
|--------|---------|---------------|------------|
| `feat/` | 新功能 | `main` (GitHub Flow) / `develop` (Git Flow) | 源分支 |
| `fix/` | Bug 修复 | `main` / `develop` | 源分支 |
| `docs/` | 文档 | `main` | `main` |
| `refactor/` | 重构 | `main` / `develop` | 源分支 |
| `test/` | 测试 | `main` | `main` |
| `chore/` | 工具/CI/杂项 | `main` | `main` |

### Special Branches

| Branch Pattern | Purpose |
|----------------|---------|
| `release/vMAJOR.MINOR.PATCH` | 发布准备分支（Git Flow） |
| `hotfix/vMAJOR.MINOR.PATCH` | 紧急修复分支 |
| `feat/42-add-login` | 功能分支（含 issue 编号） |
| `fix/87-npe-on-null` | 修复分支（含 issue 编号） |

Issue 编号不作为创建本地分支或 PR 的前提，例如 `feat/search`、`fix/cache-rules` 均有效。上表是可选团队策略示例，不强制启用 GitHub 或 Git Flow；review 数与保护规则以实际项目为准。

## Branch Lifecycle

- **本地**：核对任务 → 隔离分支/worktree → 实现、提交与本地验证 → 保留分支，或按请求本地合并 → 核实结果并定向清理。
- **显式远程**：沿用同一本地基线 → 可选 Issue 关联 → 推送并复用/创建 PR → 真实 CI/评审与等待恢复 → 按请求合并 → 同步本地并定向清理。
- 没有要求合并就不强制合并；PR 没有关联 Issue 也有效。保护规则只读取实际项目配置，不自动套用示例 review 数。

[协作流程图](git-collaboration-workflow.svg) · [图源](git-collaboration-workflow.json)。图表示规则，不是任务状态。

## Branch Protection Rules

以下是启用 GitHub 托管时可供团队选用的示例，并非本地流程的前提或对所有仓库的固定要求；执行时读取实际配置，不自动改保护规则。在 GitHub Web UI 中配置（Settings > Branches > Add rule）：

### main 分支保护

| Rule | Value |
|------|-------|
| Require pull request reviews | 2 |
| Dismiss stale reviews | ✅ |
| Require review from Code Owners | ✅ |
| Require status checks | ci (lint, test, build, coverage) |
| Require branches up-to-date | ✅ |
| Require signed commits | ✅ |
| Include administrators | ✅ |
| Allow squash merging | ✅ |
| Allow auto-merge | ✅ |
| Do not allow bypass | ✅ |

### develop 分支保护（Git Flow）

| Rule | Value |
|------|-------|
| Require pull request reviews | 1 |
| Require status checks | ci (lint, test) |
| Allow squash merging | ✅ |
| Allow auto-merge | ✅ |

### release/* 分支保护（Git Flow）

| Rule | Value |
|------|-------|
| Require pull request reviews | 1 |
| Require status checks | ci (lint, test) |
| Allow merge commits | ✅ |
| Restrict deletions | ✅ |
