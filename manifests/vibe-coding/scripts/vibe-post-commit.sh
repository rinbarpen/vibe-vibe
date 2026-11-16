#!/bin/bash
# vibe-post-commit: Commit 后的自动化维护脚本
# 职责：本地维护；GitHub 状态仅在显式 --hosted-github 时查询

set -e

HOSTED_GITHUB=false
for argument in "$@"; do
    case "$argument" in
        --hosted-github) HOSTED_GITHUB=true ;;
        --help|-h) echo "Usage: vibe-post-commit.sh [--hosted-github]"; exit 0 ;;
        *) echo "Unknown option: $argument" >&2; exit 2 ;;
    esac
done

echo "🚀 Running Vibe Coding Post-Commit Automation..."

# 1. 更新 CLAUDE.md 和 README.md
echo "📝 Syncing documentation (CLAUDE.md, README.md)..."
if [ -f ".cursor/commands/update-claude-md/update_claude_md.py" ]; then
    python3 .cursor/commands/update-claude-md/update_claude_md.py
fi

if [ -f ".cursor/commands/update-readme/update_readme.py" ]; then
    python3 .cursor/commands/update-readme/update_readme.py
fi

for cmd in update-docker update-docs update-examples update-scripts; do
    if [ -f ".cursor/commands/$cmd/update_${cmd#update-}.py" ]; then
        python3 ".cursor/commands/$cmd/update_${cmd#update-}.py"
    fi
done

# 2. 自动化测试生成与运行 (建议调用 subagent 或特定工具)
echo "🧪 Checking for test coverage and generating tests if needed..."
# 这里可以集成具体的测试生成逻辑或提示用户启动 subagent
# 例如：vibe-check (如果已定义)
if command -v vibe-check &> /dev/null; then
    vibe-check
fi

# 3. 本地任务不因安装了 gh 而自动联网。
if $HOSTED_GITHUB && command -v gh &> /dev/null; then
    echo "🐙 Checking GitHub status..."
    gh pr status || echo "No active PR found."
fi

echo "✅ Post-commit automation completed."
