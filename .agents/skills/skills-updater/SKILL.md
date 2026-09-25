---
name: skills-updater
description: Bulk update all git submodules (skills/) and standalone repos in the vibe-coding project. Handles SSH fallback, merge conflict recovery, and network diagnosis automatically.
version: 1.0.0
category: operations
tags: [git, submodule, update, maintenance, skills]
---

# Skills Updater

批量更新本项目下所有 skills/ 子模块和独立仓库到各自上游的最新版本。

## 何时使用

- 用户说"更新skill"、"更新子模块"、"同步技能库"
- 定期项目维护：将所有第三方 skill 仓库拉取到最新
- HTTPS 连接 GitHub 失败时的自动回退处理

## 工作流

整个更新流程按以下步骤顺序执行：

### 1. 网络诊断

检查 GitHub 的 HTTPS 和 SSH 可达性，选择可用的协议：

```bash
# 测试 HTTPS
curl -sI --connect-timeout 5 https://github.com >/dev/null 2>&1 && echo "HTTPS: OK" || echo "HTTPS: FAIL"

# 测试 SSH
ssh -T -o ConnectTimeout=5 -o StrictHostKeyChecking=no git@github.com 2>&1 | grep -q "authenticated" && echo "SSH: OK" || echo "SSH: FAIL"
```

### 2. 协议回退（如需要）

如果 HTTPS 不通但 SSH 通，配置全局 URL 重写，让 git 自动走 SSH：

```bash
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

恢复 HTTPS 的命令：

```bash
git config --global --unset url."git@github.com:".insteadOf
```

### 3. 更新注册子模块

对 `.gitmodules` 中除排除项外的注册子模块执行远端更新：

批量更新默认跳过以下两个子模块：

- `skills/agent-skills`
- `skills/ai-investment-advisor`

它们仍保留在 `.gitmodules` 中，也可以通过显式路径手动更新。

```bash
# 先同步 URL
git submodule sync

# 更新到各自上游的最新 commit（排除上述两个子模块）
managed_paths=$(git config --file .gitmodules --get-regexp '^submodule\..*\.path$' \
  | awk '$2 != "skills/agent-skills" && $2 != "skills/ai-investment-advisor" {print $2}')
git submodule update --remote --merge -- $managed_paths
```

`git submodule update --remote` 在任意子模块失败时会整体退出。如需逐个容错执行，使用 `foreach`：

```bash
git submodule foreach 'git fetch origin 2>&1 && \
  git checkout origin/HEAD 2>&1 || git checkout origin/main 2>&1 || git checkout origin/master 2>&1'
```

### 4. 处理冲突

`ai-skills` 等子模块可能出现索引冲突。解决方法：

```bash
# 中止合并 → 重置 → 重新更新
git -C skills/<子模块名> merge --abort
git -C skills/<子模块名> reset --hard HEAD
git submodule update --remote skills/<子模块名>
```

### 5. 处理网络超时

部分仓库（如 `nuwa-skill`）可能因体积较大或网络问题 fetch 超时。如遇超时：

```bash
# 单独重试失败的子模块，加大超时
git submodule update --remote skills/nuwa-skill
```

### 6. 验证

检查所有子模块状态，确认更新成功：

```bash
git submodule status
```

- `+` 前缀 = 已更新到新 commit
- ` ` 前缀 = 无变化（已是最新）
- `-` 前缀 = 未初始化

## 完整脚本

以下脚本可一次性执行完整更新流程（不包含冲突处理，需人工介入）：

```bash
#!/usr/bin/env bash
set -e

echo "=== 1. 网络诊断 ==="
curl -sI --connect-timeout 5 https://github.com >/dev/null 2>&1 && echo "HTTPS: OK" || echo "HTTPS: FAIL"
ssh -T -o ConnectTimeout=5 -o StrictHostKeyChecking=no git@github.com 2>&1 | grep -q "authenticated" && echo "SSH: OK" || echo "SSH: FAIL"

echo "=== 2. 协议回退 ==="
if ! curl -sI --connect-timeout 5 https://github.com >/dev/null 2>&1; then
  if ssh -T -o ConnectTimeout=5 -o StrictHostKeyChecking=no git@github.com 2>&1 | grep -q "authenticated"; then
    echo "HTTPS 不通，配置 SSH 回退..."
    git config --global url."git@github.com:".insteadOf "https://github.com/"
  fi
fi

echo "=== 3. 同步子模块 URL ==="
git submodule sync

echo "=== 4. 更新注册子模块 ==="
managed_paths=$(git config --file .gitmodules --get-regexp '^submodule\..*\.path$' \
  | awk '$2 != "skills/agent-skills" && $2 != "skills/ai-investment-advisor" {print $2}')
git submodule update --remote --merge -- $managed_paths \
  || echo "部分子模块更新失败，请检查 git submodule status"

echo "=== 5. 处理失败子模块 ==="
# 对 network timeout 的子模块可在此单独重试
# git submodule update --remote skills/nuwa-skill

echo "=== 6. 最终状态 ==="
git submodule status
```

## 子模块清单

### 注册子模块（来自 `.gitmodules`）

| 路径 | 上游仓库 |
|------|----------|
| skills/AI-Research-SKILLs | Orchestra-Research/AI-Research-SKILLs |
| skills/Agent-Skills-for-Context-Engineering | muratcankoylan/Agent-Skills-for-Context-Engineering |
| skills/Humanizer-zh | op7418/Humanizer-zh |
| skills/Pretty-mermaid-skills | imxv/Pretty-mermaid-skills |
| skills/academic-research-skills | Imbad0202/academic-research-skills |
| skills/academic-research-skills-codex | Imbad0202/academic-research-skills-codex |
| skills/agent-skills | vercel-labs/agent-skills（不参与批量更新） |
| skills/ai-design-components | ancoleman/ai-design-components |
| skills/ai-investment-advisor | AllenAI2014/ai-investment-advisor（不参与批量更新） |
| skills/ai-skills | sanjay3290/ai-skills |
| skills/anthropics | anthropics/skills |
| skills/aris | wanshuiyin/Auto-claude-code-research-in-sleep |
| skills/awesome-claude-skills | ComposioHQ/awesome-claude-skills |
| skills/beautiful_prose | SHADOWPR0/beautiful_prose |
| skills/chinese-copywriting-guidelines | sparanoid/chinese-copywriting-guidelines |
| skills/chinese-novelist-skill | PenglongHuang/chinese-novelist-skill |
| skills/claude-scientific-skills | K-Dense-AI/claude-scientific-skills |
| skills/data-structure-protocol | k-kolomeitsev/data-structure-protocol |
| skills/drawio-skills | bahayonghang/drawio-skills |
| skills/humanizer | blader/humanizer |
| skills/marketingskills | coreyhaines31/marketingskills |
| skills/notebooklm-skill | PleasePrompto/notebooklm-skill |
| skills/nuwa-skill | alchaincyf/nuwa-skill |
| skills/planning-with-files | othmanadi/planning-with-files |
| skills/ralph | snarktank/ralph |
| skills/skill-seekers | yusufkaraaslan/Skill_Seekers |
| skills/skills | better-auth/skills |
| skills/summarize-slides-skill | Li-Baichuan-James/summarize-slides-skill |
| skills/superpowers | obra/superpowers |
| skills/ui-ux-pro-max-skill | nextlevelbuilder/ui-ux-pro-max-skill |
| skills/video-summarizer | liang121/video-summarizer |
| skills/x-research-skill | rohunvora/x-research-skill |

### 备选仓库（当前未注册，上游仍然存在）

以下目录当前未在 `.gitmodules` 中配置且本地目录已移除，但上游仓库仍可用，如需恢复可手动添加：

| 路径 | 上游仓库 | 说明 |
|------|----------|------|
| manifests/agent-browser | vercel-labs/agent-browser | 浏览器自动化 manifest |
| skills/axton-obsidian-visual-skills | axtonliu/axton-obsidian-visual-skills | Obsidian 可视化技能 |

## Red Lines

- **不要**在 `git submodule update` 失败后不检查 `git submodule status` 就跳过 — 可能是冲突或网络问题
- **不要**对未初始化的子模块（`-` 前缀）执行 `git submodule update --remote`，需要先 `git submodule init`
- **不要**使用 `git submodule update --remote --force` 强制覆盖本地修改，除非确认本地无未提交更改
- **不要**跳过 `git submodule sync` — URL 变更后不 sync 会导致 fetch 失败
