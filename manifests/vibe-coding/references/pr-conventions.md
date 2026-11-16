# PR Conventions Guide

本指南只在显式启用远程 PR 协作时适用。本地多分支不要求 PR 或 Issue；PR 也可不关联 Issue。完整路由、等待/恢复和回退见[本地优先协作契约](git-collaboration.md)。已有 Issue 用 `Refs` 关联；仅当完整解决且需要关闭时用 `Closes`，合并后核对实际关闭状态。

## PR Title Format

所有 PR 标题必须遵循以下格式（由 `pr-conventions.yml` 强制检查）：

```
<type>(<scope>): <description>
```

### 示例

| Title | 是否符合 | 说明 |
|-------|----------|------|
| `feat(api): add user login endpoint` | ✅ | type + scope + desc |
| `fix(database): handle null in user query` | ✅ | bug fix |
| `docs(readme): update installation steps` | ✅ | 文档更新 |
| `refactor: extract auth middleware` | ✅ | 可以不写 scope |
| `fix bug` | ❌ | 缺少 type 和 scope |
| `feat(api)add login` | ❌ | 缺少 `: ` 分隔符 |

### Type 列表

| Type | 含义 | Changelog 映射 |
|------|------|----------------|
| `feat` | 新功能 | Added |
| `fix` | Bug 修复 | Fixed |
| `docs` | 文档变更 | Documentation |
| `style` | 代码格式（不影响逻辑） | 无 |
| `refactor` | 代码重构 | Changed |
| `perf` | 性能优化 | Changed |
| `test` | 测试相关 | 无 |
| `chore` | 构建/CI/工具 | 无 |
| `ci` | CI 配置变更 | 无 |

### Scope 示例（可选）

```
feat(api):      API 相关
fix(frontend):  前端相关
docs(readme):   文档相关
refactor(db):   数据库相关
chore(deps):    依赖更新
perf(cache):    缓存优化
```

## PR Size Labels

由 `pr-conventions.yml` 自动计算并标记：

| Label | 变更行数 | 建议 |
|-------|----------|------|
| `size/xs` | 0-10 | 直接 approve（小修复/文档） |
| `size/s` | 11-50 | 正常 review |
| `size/m` | 51-200 | 详细 review |
| `size/l` | 201-800 | 需要多人 review |
| `size/xl` | >800 | ⚠️ 建议拆分（自动 warn comment） |

## Merge Strategy

| 分支来源 → 目标 | 合并方式 | 原因 |
|----------------|----------|------|
| `feature/*` → `main` | **Squash merge** | 保持 main 历史清晰，每个 squash 对应一个完整功能 |
| `release/*` → `main` | **Merge commit** | 保留发布记录的完整 timeline |
| `hotfix/*` → `main` | **Merge commit** | 保留修复记录，便于未来审计 |
| `main` → `develop` (Git Flow) | **Merge commit** | 保持同步记录 |

### Squash Merge 说明

Squash merge 将所有 commits 合并为一条 commit 进入目标分支：

```
Feature 分支 commits:
  feat: add A    →    Squash merge →    feat: add login (单条)
  fix: typo      →                     
  chore: format  →                     
```

- ✅ 优点：main 历史清晰线性
- ❌ 缺点：丢失了 feature 分支的详细 commit 历史

## Merge Queue

PR 通过 review 后，可以加入 GitHub Merge Queue：

```
1. PR approved ✓
2. 加入 Merge Queue
3. 队列自动批量 CI（merge_group 事件）
4. 自动 squash merge
```

Merge Queue 的好处：
- 防止并行 PR 合并时的竞争条件
- 自动 rebase 到最新 main
- 批量 CI 节省资源

### 使用方式

1. 在仓库 Settings > Branches 中启用 merge queue
2. 设置 `merge-queue.yml` 作为 merge_group 事件的 CI
3. PR 通过后点击 "Merge when ready"

## Draft PR

使用场景：

| 状态 | 操作 | 说明 |
|------|------|------|
| **Draft** | 创建 PR 时选择 Draft | WIP 状态，不会自动请求 review |
| **Ready** | 标记为 Ready for Review | CI 通过后，自动触发 reviewer 分配 |
| **Closed** | 未合并直接关闭 | 放弃该 PR |

最佳实践：
- 代码未完成时先开 Draft PR
- Draft PR 也可以触发 CI，尽早发现集成问题
- Ready 前确保所有 checklist 已勾选
