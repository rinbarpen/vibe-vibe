# 本地多分支与可选 PR / Issue 协作

默认用本地 Git 管理任务分支；远程仓库、托管账号、PR 和 Issue 编号都不是前置条件。配置了 remote 只表示具备远程协作条件，不等于用户要求发布代码或创建事项。

## 从只读检查开始

在项目根目录运行，无第三方 Python 依赖，也不会联网、登录或修改 Git 状态：

```bash
python3 scripts/git_collaboration.py inspect --root .
python3 scripts/git_collaboration.py inspect --root . --branch feat/search --base main
```

结果列出当前分支、提交、dirty 状态、所有本地分支、被 worktree 占用的分支、已有 remote 和待决定事项。缓存按项目 `.gitignore` 处理。它是事实快照，不是执行计划已获批准或任务已完成的证明。

检查器优先使用 NUL 分隔的 worktree 输出；旧 Git（已实测 2.34）使用普通 porcelain 格式，记录存在歧义时报错而不猜测路径。该格式和 NUL 选项见 [Git 官方 worktree 文档](https://git-scm.com/docs/git-worktree#_list_output_format)。

需要执行时使用 [git-flow 命令指南](../commands/git-flow/COMMAND.md)。通用 harness 可直接读取该文件，不假定宿主自动注册了斜杠命令。

## 本地路径：不依赖网络和平台工具

1. 核对任务范围、基线和目标分支，复用同一任务已有的分支；独立任务使用独立分支。普通命名为 `feat/search`、`fix/cache-rules`，有已有 Issue 时才可用 `feat/42-search`。
2. 保护已有修改。dirty 工作区先区分本次与他人变更；需要并行时在独立 worktree 中继续。分支已被其他 worktree 占用，就使用那个 worktree 或选新分支，不强制切换、reset、清理或抢占。
3. 从已确认基线创建分支，开发、定向暂存、提交和实际验证。分支创建不要求远程账号、Issue 或托管 CLI。
4. 任务只要求开发/验证时，交付提交与验证记录并保留分支；只有请求包含合并，才按项目既定策略本地合并。快进可用 `git merge --ff-only`；需要保留分支边界时使用项目约定的 merge。遇到冲突由 AI 分析、修复和重测；目标冲突才请求人决定。
5. 合并后核对提交祖先关系和实际结果。清理仅针对本次已合并且没有新工作的分支；不删除被其他 worktree 使用的分支，不处理无关分支。worktree 的移除也要确认干净并在本次范围内。

例如，下面是无 remote 的独立任务分支；命令中的基线与路径应来自当前项目，已有同名分支不重复创建：

```bash
git switch -c feat/search main
# 修改、针对性验证，再按明确路径 git add 和 git commit
git switch main
git merge --ff-only feat/search
git branch -d feat/search
```

本地完成不自动升级成 push、PR、Issue、Release 或部署。

## 可选远程路径：按任务范围启用

用户要求提交 PR / MR、关联 Issue 或远程合并时，使用已配置的 remote 和实际托管平台。只读预检也可显式说明意图：

```bash
python3 scripts/git_collaboration.py inspect --root . --mode hosted --remote origin
python3 scripts/git_collaboration.py inspect --root . --mode hosted --remote origin --issue 42
```

该检查仍不联网。`issue.verified=false` 表示只是给定引用，尚未向平台核实。多个 remote 必须明确目标；私有托管域名可显式传 `--provider github|gitlab|gitee`。文件系统路径 remote 可用于普通 Git 协作，但不被当成 PR 平台。`--provider` 只描述平台，不是发布许可。

| 环节 | 行为与边界 |
| --- | --- |
| Issue（独立可选） | 没有 Issue 可以直接开 PR；给定已有引用先查看内容和状态。只有明确需要新事项时才创建，先查重；不自动批量创建、关闭或改写无关 Issue。 |
| 分支与 PR | 核对源分支、base、remote、仓库和当前 SHA；复用已有 PR，或按已确认目标推送并新建。描述包含摘要、测试证据和未验证项；WIP 使用 Draft。 |
| 引用与关闭 | 仅表示关联时用 `Refs #42`。确认本 PR 完整解决目标且仓库支持关闭语义时才用 `Closes #42`；合并后实际核对 Issue 状态，不把“关联”当成“已关闭”。 |
| 检查与评审 | 读取真实 CI、评审和分支保护规则，不预设固定 reviewer 数。pending/queued 是等待，不是通过；失败修复同一分支后重测。缺登录、工具或 runner 时调查并记录等待点，不改成免检查合并。 |
| 合并 | 仅在任务包含合并、目标 SHA 的适用检查和实际评审要求满足后执行。执行前再次核对 head/base，遵守仓库 merge/squash/rebase 策略；不冒充批准或绕过保护。 |
| 同步与清理 | 远程确认已合并后，再 fetch 并快进本地目标分支；仅删除本次已合并且无新增提交的源分支。远程删除需核对当前 tip，保留其他任务/worktree。 |

GitHub 可用 `gh issue view/create`、`gh pr list/create/checks/merge`；GitLab 使用项目已有 `glab` / API，Gitee 使用既有 API / 界面。不为可选路径自动安装工具、创建远程仓库、修改全局账号或替换项目已有托管方式。选择 `--provider=git` 安装模板仍可完整使用本地流程；以后在具体请求中启用远程协作无需重新初始化项目。

## 人的决定、等待与恢复

- 已明确的本地任务或已请求的 PR/合并，AI 在既定范围内直接执行；不为每个 Git 命令重复索取确认。
- 新的发布目标、上下文尚未确定的 remote/base、范围取舍、或仓库要求的真实人工评审，才需要人的当前决定。问题应包含目标、分支/SHA、影响与选项；已有明确回答沿用，不重复询问。
- 尚未回答时只暂停依赖该决定的动作；其他独立本地分支可继续。记录等待点（范围选择、CI、登录或评审），恢复时核对分支、SHA、远程状态与回答范围，回到原等待节点，不重建 Issue / PR。
- 调查、冲突处理和测试失败先由 AI 返工。取消或更改目标不等于已回退。

## 回退与真实交付

变更前记录基线与本次提交。未提交的冲突合并可用 `git merge --abort` 回到合并前；已共享提交优先按项目策略 revert，不重写他人历史。回退文件只恢复本次拥有的路径，保留用户修改和其他分支。PR / Issue 的关闭、重新打开和引用变更按具体决定处理，不假装远程对象已撤销。

交付记录区分：本地分支已验证、PR 已创建、等待检查/评审、远程已合并、Issue 已实际关闭，以及已验证回退。列出实际提交、检查输出、PR/Issue 链接和保留/清理的分支；缺失检查如实说明。

[流程图](git-collaboration-workflow.svg) · [可编辑源](git-collaboration-workflow.json)。图描述规则，不是当前状态；AI 执行、AI 校验、人工决定各有独立泳道。从模板目录或安装后的项目根目录复用既有标准库渲染器：

```bash
python3 scripts/render_codegraph_workflow.py --source references/git-collaboration-workflow.json --output references/git-collaboration-workflow.svg
python3 scripts/render_codegraph_workflow.py --source references/git-collaboration-workflow.json --output references/git-collaboration-workflow.svg --check
```
