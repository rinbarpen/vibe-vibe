# vibe-vibe

**简体中文** | [English](README_EN.md)

为 AI 编码、科研、写作和办公任务安装所需技能与项目规则。

只需要某项能力，安装一个 **Skill**；需要项目级工作约定，选择一个 **Manifest**。安装到目标项目后，由你的 AI 助手按这些规则工作。

## 让 AI 一句话配好项目

已有能读写项目文件、执行命令的 AI harness（例如 Codex、Claude Code）？在目标项目中告诉它：

> 请读取 https://github.com/rinbarpen/vibe-vibe/blob/main/BOOTSTRAP.md，为当前目录配置项目：我要做【项目目标】；自动选择或生成 manifest、安装所需 skills，使用通用 Markdown 项目规则并完成验证。

AI 会按 [配置契约](BOOTSTRAP.md) 识别环境、选择或编写项目规则、预览并安装，再核对结果与回退入口。配置入口使用 Python 3.10+ 标准库，面向 Windows、macOS、Linux，不要求 Bash 或全局安装 CLI；Git/Python 缺失时由 AI 先处理前置条件。业务代码、实验和文稿仍按你的实际任务继续完成。

## 手动使用 CLI

需要 Git、Python 3.10+ 和 [uv](https://docs.astral.sh/uv/)。在终端运行：

```bash
git clone --recurse-submodules https://github.com/rinbarpen/vibe-vibe
cd vibe-vibe
uv tool install -e tools/vibe_tool
vibe list manifests
```

最后一条命令应列出可用模板，例如 `vibe-coding`、`ui-testing`。如果已经克隆仓库，可跳过前两行；没有全局 CLI 时，见 [直接使用本地 Python 入口](docs/cli-reference.md#无需安装-cli-即可更新)。

## 选择你要做的事

| 你要做什么 | 入口 |
| --- | --- |
| 给已有项目增加单项能力 | `vibe add skill <名称> <项目目录>` |
| 为新项目配置开发规则 | `vibe setup <模板> <项目目录> --harness generic` |
| 为已有项目增加一套规则 | `vibe add manifest <模板> <项目目录>` |
| 同步已安装的规则或技能 | [更新、备份与回退](docs/cli-reference.md#同步项目中已安装的-skill--manifest) |
| 管理多个项目、按名称更新配置 | [项目登记与更新](docs/cli-reference.md#管理多个项目) |

例如，为新项目配置全栈开发规则，先预览再执行：

```bash
vibe setup vibe-coding ../my-project --harness generic --scenario=fullstack-web --provider=git --dry-run
vibe setup vibe-coding ../my-project --harness generic --scenario=fullstack-web --provider=git
```

执行后，`../my-project` 中会出现 `PROJECT_RULES.md`、普通 `AGENTS.md` 导入入口、技能与 `rules/<模板>/` 规则包。规则不依赖 Cursor；其他 harness 可直接读取 `PROJECT_RULES.md`。需要 Codex / Claude 的专用入口时使用 `--harness codex|claude|both`，见 [规则分发说明](docs/cli-reference.md#harness-无关的规则)。这是项目上下文，不是已经实现或部署好的业务应用；接下来在该目录中让 AI 助手完成具体任务。

`--provider=git` 只配置本地 Git 工作流。其他托管平台、场景与命令选项见 [CLI 参考](docs/cli-reference.md)。

## 按任务查资料

- **找技能或模板**：[能力目录](docs/catalog.md)；完整技能名以 `vibe list skills` 为准。
- **做软件界面**：[Vibe Coding 模板](manifests/vibe-coding/README.md)，包含 UI/UX 与真实操作验收规则。
- **画图或做可视化**：[按场景选择工具](mine/omnidraw/references/visualization-scenarios.md)。
- **浏览全部技能**：[中文技能索引](skills/ANNOTATIONS.md)。
- **维护或创建模板**：[工作流交付规范](docs/manifest-workflow.md)。

科研、学习、写作、办公和游戏制作等模板都在[能力目录](docs/catalog.md)中；不必一次安装全部技能。

## 常见问题

**提示缺少 Skill 来源？** 先确认子模块已初始化：

```bash
git submodule update --init --recursive
```

**源仓库更新了，已有项目为什么没变？** 安装资源是副本，需要显式运行 `vibe update skill` 或 `vibe update manifest`。更新范围、旧项目参数与恢复命令见 [更新说明](docs/cli-reference.md#同步项目中已安装的-skill--manifest)。

**想接入 MCP 或 Hook？** 它们按需安装，不随普通技能自动启用。查看 [MCP 与配套工具](docs/catalog.md#mcp-服务)。

## 维护这个仓库

[开发与验证命令](docs/cli-reference.md#开发与验证) · [仓库结构](docs/catalog.md#项目结构) · [Manifest 工作流规范](docs/manifest-workflow.md)

仓库原名 `vibe-coding`。CLI 仍叫 `vibe`，软件工程模板仍叫 `vibe-coding`，已有命令无需改名。

## 许可证

仓库自身采用 [MIT License](LICENSE)。外部技能和工作流遵循各自项目的许可证。
