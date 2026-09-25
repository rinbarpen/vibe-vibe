# CLAUDE.md — 社交媒体内容创作项目

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

社交媒体内容创作、润色和分发项目。支持微信公众号、小红书、Twitter/X、微博等平台。

## 🚀 快速上手

```bash
# 1. 从模板开始
cp templates/wechat-template.md content/my-post.md

# 2. 撰写草稿（修改模板）
# ... 在 content/my-post.md 中写作 ...

# 3. 检查排版
python scripts/lint_text.py content/my-post.md --strict

# 4. 自动修复排版问题
python scripts/lint_text.py content/my-post.md --fix

# 如果您像我一样使用中文，排版检查特别重要
```

## Commands

| 命令 | 描述 |
|------|------|
| `vibe-draft <topic>` | 根据主题生成内容草稿 |
| `vibe-polish` | 中英文排版润色和文学性提升 |
| `vibe-lint-text` | 检查中英文排版问题 |
| `vibe-gen-image-prompt` | 生成配图 AI 绘画提示词 |
| `vibe-summarize` | 将长文提炼为短内容格式 |
| `vibe-export` | 导出为 Markdown/PDF/HTML |

## Architecture

```
<root>/
  content/      # 原始草稿和定稿
  assets/       # 图片、图表和媒体文件
  templates/    # 平台特定模板
    wechat-template.md          # 公众号模板
    red-template.md             # 小红书模板
    twitter-thread-template.md  # Twitter Thread 模板
  scripts/      # 辅助脚本
    lint_text.py          # 排版检查工具（支持自动修复）
  commands/     # 命令文档
  references/   # 平台运营策略参考
  rules/        # AI 行为规则
    vibe-social-typesetting.mdc  # 排版规范
    vibe-social-platforms.mdc    # 平台特定规范
    vibe-social-quality-gate.mdc # 质量门禁
```

## Content Standards

- **排版**：遵循 `rules/vibe-social-typesetting.mdc` 中英文混排规范
- **风格**：专业、有吸引力、真实。避免 AI 填充语
- **语气**：根据平台调整（公众号→认真、小红书→口语、Twitter→简洁）
- **配图**：图表必须使用英文标签

## 创作流程

1. **选题创意**: 确定主题和目标平台
2. **草拟**: 使用 `vibe-draft` 或从模板开始撰写
3. **润色**: 使用 `vibe-polish` 提升可读性
4. **排版检查**: 使用 `vibe-lint-text --fix` 自动修复排版问题
5. **配图**: 使用 `vibe-gen-image-prompt` 生成配图提示词
6. **提炼**: 使用 `vibe-summarize` 生成摘要
7. **质量门禁**: 通过 `rules/vibe-social-quality-gate.mdc` 逐项检查
8. **导出**: 使用 `vibe-export` 导出为发布格式

## Gotchas

- **中英文排版**：中文和英文/数字之间必须有空格
- **AI 填充语**：避免 "值得注意的是"、"In a world where" 等废话
- **各平台规则**：公众号 1500-3000 字，小红书 300-800 字，Twitter <280 字符
- **发布前检查**：必须运行质量门禁清单
- **版权合规**：引用内容必须标注来源