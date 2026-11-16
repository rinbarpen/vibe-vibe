---
description: 本地多分支协作；按需启用远程 PR / Issue，不依赖平台账号完成本地任务。
---

# Git Flow Command

`git-flow` 是 AI 执行指南，通用 harness 可直接读取；宿主是否提供 `/git-flow` 入口以实际能力为准。遵循[完整协作契约](../../references/git-collaboration.md)，不代替原生 Git，也不自动执行网络操作。

## 输入与默认值

输入是当前任务、本地基线/分支、是否只开发或还需合并，以及可选的 remote、PR、Issue。**默认 local**；没有 remote、账号、Issue 编号或 `gh` 也能完成。已有 remote 不自动选择 hosted。

## 执行

1. 从项目根目录运行 `python3 scripts/git_collaboration.py inspect --root .`，读取状态、所有分支与 worktree 占用。它只读且不联网；不要把预检输出称为变更或远程状态已验证。
2. 沿用当前任务分支；独立任务创建或选用独立分支/worktree。保留 dirty 工作区和其他任务，不 reset、抢占分支或批量清理。分支名允许 `<type>/<description>`，Issue 编号可选。
3. 修改、按路径提交、实际验证。只要求开发时保留已验证分支；请求包含本地合并时，按项目策略合并、验证祖先关系与结果，再清理本次无新增工作的已合并分支。
4. 只有请求包含远程协作才进入 hosted：明确 remote/base/SHA，按需查看或关联既有 Issue；没有 Issue 仍可开 PR，不默认新建事项。查重、复用已有 PR，按选定平台工具推送和创建。
5. PR 的摘要与测试计划必须真实；`Refs` 仅关联，`Closes` 仅用于完整解决且需要关闭的事项。监控目标 SHA 的适用检查，pending/queued 记录等待，失败返工；实际分支保护与人工评审要求不能被预检脚本代替。
6. 请求包含远程合并且检查/评审满足时，再核对 head/base 执行合并。验证 PR、Issue 和远程分支的真实状态，快进本地目标分支，只清理本次范围内已合并且无新工作的分支。

## 人的输入与恢复

只对新的发布目标、上下文无法决定的 remote/base/范围、或仓库要求的真实评审提问。已请求的 PR/合并不重复询问。未回答时保存当前等待点；有效回答后核对 SHA 并回到该节点，避免重复创建 Issue / PR。技术问题先由 AI 调查和重测。

## 回退与结果

复用 Git 的 `merge --abort` / revert 和项目原有恢复机制；保留其他任务和用户文件。报告实际提交、验证、PR/Issue 状态、等待点和分支清理结果。未合并分支不报告已合并，关联 Issue 不报告已关闭。
