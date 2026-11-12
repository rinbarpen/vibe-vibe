# Vibe Coding 项目模板

给 AI 编码助手提供开发规则、场景配置与验证入口，适用于新项目，也可增量加入已有项目。

本模板安装的是协作上下文，不是已经完成的业务应用。已有项目的业务约定、数据和运行状态需要保留。

## 开始使用

在已配置本仓库来源的 `vibe` CLI 中，先预览再创建项目：

```bash
vibe init vibe-coding ./my-app --scenario=fullstack-web --provider=git --dry-run
vibe init vibe-coding ./my-app --scenario=fullstack-web --provider=git
```

完成后，`my-app` 中会有 `MANIFEST.md`、指向它的 `AGENTS.md` / `CLAUDE.md`、规则、命令与必需技能。进入项目目录，把具体开发任务交给 AI 助手。首次使用 Matt Pocock 工程技能前，运行 `/setup-matt-pocock-skills` 完成项目设置。

已有项目使用 `vibe add manifest vibe-coding <项目目录>`；已有模板副本使用 `vibe update manifest vibe-coding <项目目录> --dry-run` 预览更新，不重复初始化。

## 按需要使用

| 任务 | 入口 |
| --- | --- |
| 日常功能与修复 | [项目协作规则](MANIFEST.md)；按任务规模选择直接修改或实现流程 |
| 简化界面、验证真实操作 | [UI/UX 契约](references/ui-usability.md) |
| 整理 README 与使用说明 | [面向读者的写作约定](references/readme-guide.md) |
| 查场景、参数、托管与依赖 | [安装与配置参考](references/setup-guide.md) |

UI/UX 文案约束：**Avoid unnecessary secondary labels and descriptions. Let the layout do the explaining.** 保留必要标签、错误和风险说明。

```text
/frontend-check usability
/frontend-check interaction
/update-docs README.md
```

`/frontend-check all` 包含六类前端检查。命令指南使用项目实际工具，不自动安装测试环境；未执行的检查如实标注。

## 文档与流程图

首页只保留使用入口；完整参数与流程说明按需查阅。以下图都是规则，不代表任务已经完成。

- [UI 操作验收流程图](references/ui-usability-workflow.svg) · [图源](references/ui-usability-workflow.json)
- [文档写作与验收流程图](references/docs-readability-workflow.svg) · [图源](references/docs-readability-workflow.json)
- [CodeGraph 查询流程图](references/codegraph-workflow.svg) · [图源](references/codegraph-workflow.json)

### 可选 CodeGraph

[CodeGraph](https://github.com/colbymchenry/codegraph) 仅在项目已经有 `.codegraph/` 时优先使用 CLI；没有索引就直接普通搜索。安装和更新不会自动装工具、建立索引或改全局配置。用户决定启用时，按上游安装说明手动执行 `codegraph init`，详见 [查询规则](MANIFEST.md#code-navigation-cli-first-codegraph)。

<details>
<summary>流程图再生成与只读检查命令</summary>

从本模板目录或安装后的项目根目录运行，复用同一个[标准库渲染器](scripts/render_codegraph_workflow.py)：

```bash
python3 scripts/render_codegraph_workflow.py --source references/ui-usability-workflow.json --output references/ui-usability-workflow.svg
python3 scripts/render_codegraph_workflow.py --source references/ui-usability-workflow.json --output references/ui-usability-workflow.svg --check
python3 scripts/render_codegraph_workflow.py --source references/docs-readability-workflow.json --output references/docs-readability-workflow.svg
python3 scripts/render_codegraph_workflow.py --source references/docs-readability-workflow.json --output references/docs-readability-workflow.svg --check
python3 scripts/render_codegraph_workflow.py --source references/codegraph-workflow.json --output references/codegraph-workflow.svg
python3 scripts/render_codegraph_workflow.py --source references/codegraph-workflow.json --output references/codegraph-workflow.svg --check
```

只读文档结构检查：

```bash
python3 .cursor/commands/update-docs/update_docs.py --root . README.md
```

此检查入口位于安装后的项目。在模板源目录，把脚本路径换成 `commands/update-docs/update_docs.py`。检查工具只读，不证明文档已经好读或示例命令已经运行。

</details>
