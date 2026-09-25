#!/bin/bash
# vibe-init-fund: 基金本子项目初始化脚本

set -e

# 获取 manifest 源路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT=$(pwd)

echo "Initializing Fund Proposal project (Fund_Craft_Pro) from: $MANIFEST_DIR"

# 1. 创建项目目录结构
mkdir -p draft outline refs assets final .cursor/rules .cursor/plans

# 2. 复制核心配置文件
[ ! -f CLAUDE.md ] && cp "$MANIFEST_DIR/CLAUDE.md" CLAUDE.md && echo "Created CLAUDE.md"
[ ! -f AGENTS.md ] && cp "$MANIFEST_DIR/AGENTS.md" AGENTS.md && echo "Created AGENTS.md"
[ ! -f MANIFEST.md ] && cp "$MANIFEST_DIR/MANIFEST.md" MANIFEST.md && echo "Created MANIFEST.md"
[ ! -f .cursorrules ] && cp "$MANIFEST_DIR/.cursorrules" .cursorrules && echo "Created .cursorrules"

# 3. 复制规则文件
if [ -d "$MANIFEST_DIR/rules" ]; then
    for file in "$MANIFEST_DIR/rules"/*.mdc; do
        filename=$(basename "$file")
        cp "$file" ".cursor/rules/$filename"
        echo "Installed rule: $filename"
    done
fi

# 4. 创建初始大纲文件
[ ! -f outline/skeleton.md ] && touch outline/skeleton.md
[ ! -f outline/innovations.md ] && touch outline/innovations.md
[ ! -f outline/key_problems.md ] && touch outline/key_problems.md

echo "------------------------------------------------"
echo "基金本子项目初始化成功！"
echo "请在对话框中输入 /init 开始您的撰写之旅。"
echo "------------------------------------------------"
