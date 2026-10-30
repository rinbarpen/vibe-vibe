# vibe-coding

一个面向 Claude Code、Codex、Cursor 等 AI coding agent 的 **Skills 聚合与项目脚手架仓库**。

它本身不是一个业务应用，而是一层可复用的 AI 工作流基础设施：把分散的技能库、项目级上下文、MCP 配置、Hook 工作流和初始化脚本集中到一个仓库，并通过 `vibe` CLI 安装到目标项目。

[English README](README_EN.md)

## 你可以用它做什么

| 场景 | 可用能力 |
| --- | --- |
| 软件开发 | 全栈开发、API、CLI、数据管道、LLM 应用、桌面应用、测试与部署 |
| 科研与写作 | 文献调研、实验规划、论文写作、论文评审、图表生成、基金申请 |
| 设计与前端 | 设计系统、UI/UX、前端界面、主题、生成艺术、视觉检查 |
| 办公自动化 | DOCX、XLSX、PPTX、PDF 与企业沟通文档 |
| 内容生产 | 中文写作、小说、社交媒体、学术改写、文本总结 |
| Agent 基础设施 | Skill 创建、MCP 服务、浏览器自动化、Hook 与多智能体工作流 |

## 30 秒开始

### 1. 获取仓库

建议同时初始化 Skill 子模块：

```bash
git clone --recurse-submodules https://github.com/rinbarpen/vibe-coding
cd vibe-coding
```

如果仓库已经克隆完成：

```bash
git submodule update --init --recursive
```

### 2. 安装 `vibe` CLI

需要 Python 3.10+ 和 [uv](https://docs.astral.sh/uv/)。

```bash
./tools/vibe_tool/install.sh
# 或
uv tool install -e tools/vibe_tool
```

检查安装：

```bash
vibe --version
vibe list manifests
vibe list skills
```

### 3. 初始化一个项目

```bash
# 创建完整的 Vibe Coding 工程上下文
vibe init vibe-coding ../my-project --scenario=fullstack-web

# 为已有项目加入 UI 测试配置
vibe add manifest ui-testing ../my-project

# 为已有项目加入单个 Skill
vibe add skill taste-skill ../my-project
```

初始化后，项目中通常会出现：

```text
my-project/
├── CLAUDE.md / AGENTS.md       # 项目级 agent 指令
├── .agents/skills/             # 已安装 Skills
├── .cursor/
│   ├── commands/              # 可调用命令
│   └── rules/                 # 项目规则
├── .claude/agents/             # Claude Code agent 定义（按 Manifest 提供）
└── .codex/agents/              # Codex agent 定义（按 Manifest 提供）
```

## `vibe` CLI

仓库定位优先级为 `$VIBE_HOME` 环境变量 → 从当前目录向上查找同时包含 `manifests/` 和 `skills/` 的目录 → `~/.config/vibe-tool/config.json`。在仓库外使用时，可以先通过 `vibe config set-repo /path/to/vibe-coding` 固定仓库路径。

项目安装与直接更新命令支持 `-n/--dry-run` 预览；`init/add` 使用 `-f/--force` 显式覆盖已有文件，`update skill/manifest` 则覆盖选定资源并自动备份。`target` 默认为当前目录；场景与 `--provider`、`--owner`、`--org`、`--repo`、`--email` 等生成参数按模板适用，详情见相应命令的 `--help`。

| 命令 | 用途 |
| --- | --- |
| `vibe list manifests` | 列出可用项目模板 |
| `vibe list skills` | 递归列出可用 Skills |
| `vibe list --json` | 输出机器可读的清单 |
| `vibe init <manifest> [target]` | 从模板初始化新项目 |
| `vibe add manifest <name> [target]` | 向已有项目加入 Manifest |
| `vibe add skill <name> [target]` | 向已有项目加入单个 Skill |
| `vibe add skill --all [target] --yes` | 批量安装全部 Skills |
| `vibe update` | 更新受管理的 Skill 子模块 |
| `vibe update skill <name> [target]` | 从本地仓库同步项目中已安装的 Skill，自动备份 |
| `vibe update manifest <name> [target]` | 从本地仓库同步 Manifest 配置及已安装的必需 Skills，自动备份 |
| `vibe config set-repo <path>` | 设置仓库路径 |
| `vibe config show` | 查看当前配置 |
| `vibe mcp list` | 列出可用 MCP 服务 |
| `vibe mcp add <name> [target]` | 合并安装 MCP 服务配置 |
| `vibe mcp add --all [target]` | 安装全部 MCP 服务配置 |
| `vibe hook list` | 列出可用 Hook 集合 |
| `vibe hook add <name> [target]` | 向项目安装 Hook 集合 |
| `vibe hook add --all [target]` | 安装全部 Hook 集合 |
| `vibe stats show` | 查看 Skill 使用统计 |

常用选项（下列 `add/hook` 示例假设 `demo` 已存在；`--dry-run` 本身不会创建目标目录）：

```bash
vibe init vibe-coding demo --dry-run
vibe add manifest office demo --force
vibe add skill --all demo --yes --dry-run
vibe mcp list
vibe hook add ralph-loop demo
```

## 仓库内容

### Skills

`skills/` 包含来自多个社区和维护者的 Git 子模块，`mine/` 存放第一方 Skill。CLI 会递归扫描这两个目录中的 `SKILL.md`；同名 Skill 使用带相对路径的标识自动消歧，安装时以 `vibe list skills` 显示的名称为准。

重点集合包括：

- [Anthropic Skills](skills/anthropics)：文档、表格、演示文稿、PDF、前端等官方技能
- [Claude Scientific Skills](skills/claude-scientific-skills)：科研、生命科学、化学、医学影像等
- [UI/UX Pro Max](skills/ui-ux-pro-max-skill)：设计系统与 UI 风格库
- [AI Research Skills](skills/AI-Research-SKILLs)：AI/ML 研究、训练、评估和论文工作流
- [Agent Skills for Context Engineering](skills/Agent-Skills-for-Context-Engineering)：上下文工程方法
- [Humanizer-zh](skills/Humanizer-zh)、[shuorenhua](skills/shuorenhua)：中文文本改写与表达优化
- [Chinese-WebNovel-Skill](skills/chinese-webnovel-skill)：中文网文选材、构思、章纲、写作与完稿审查
- [Pretty Mermaid Skills](skills/Pretty-mermaid-skills)：Mermaid 图表生成与渲染
- [Unity Game Development](mine/unity-game-development)：覆盖游戏制作全流程、3D/DCC 建模、游戏测试与执行/Reviewer 角色，可整包、阶段或单项安装。
- [State Machine Reasoning](mine/state-machine-reasoning)：将决策、排障、研究和工作流分析建模为状态机，并生成 Mermaid 可视化图。
- [Omnippt](mine/omnippt)：按需加载需求调研、叙事大纲、逐页策划、视觉设计、原生制作和独立审查子技能，支持可编辑演示文稿交付。
- [X Research](skills/x-research-skill)：信息检索与社交平台调研

仓库内的 [mine/](mine) 存放第一方 Skill，[workflows/](workflows) 存放完整工作流项目。后者按各自说明使用，不属于 `vibe list skills` 的默认扫描根目录。

浏览索引：

- [中文 Skills 标注索引](skills/ANNOTATIONS.md)
- [English Skills Annotations](skills/ANNOTATIONS_EN.md)

### Manifests

Manifest 是项目级配置包，通常包含 `CLAUDE.md`、`AGENTS.md`、规则、命令、场景、agents 和初始化脚本。

模板可通过 `skills.txt` 声明必需 Skills，`init/add manifest` 会自动安装这些依赖。缺少本地 Skill 来源时，命令会提示并返回非零状态；`--dry-run` 同样检查依赖。安装前先检查对应 Skill 来源与子模块初始化状态。

| Manifest | 适用方向 |
| --- | --- |
| `vibe-coding` | 通用软件工程全生命周期 |
| `auto-research` | 文献、实验、论文与图表自动化 |
| `auto-research-ars` | 基于 ARS 的多阶段科研流水线 |
| `fund-proposal` | 基金申请与项目建议书 |
| `git-manager` | Git 仓库与镜像管理 |
| `tutor` | 对话式学习导师：教材/主题辅导、自动图文笔记与学习记录 |
| `market-analysis` | 行业研究、市场与竞品分析 |
| `novel-writing` | 长篇小说与文学创作 |
| `office` | DOCX / XLSX / PPTX / PDF：正文写作、原生可编辑交付、全量视觉验收与独立 QA |
| `social-media` | 社交媒体内容创作与运营 |
| `ui-testing` | Web、组件、移动端、视觉与无障碍测试 |
| `unity-game` | Unity 游戏制作全流程，Claude Code/Codex 角色、执行/Reviewer 技能与 [workflow SVG](manifests/unity-game/references/workflow.svg) |

实际可用模板以 `vibe list manifests` 为准。`tutor` 是原 `knowledge-learning` 的新名称，新项目使用 `vibe init tutor [target]`。

查看每个模板的细节：

```bash
find manifests -maxdepth 2 -name README.md -print
```

### MCP 服务

CLI 从仓库根目录可选的 `mcp.json` 读取 `mcpServers` 配置，不假定已经预置服务。先运行 `vibe mcp list` 查看当前可用清单；缺少配置或没有服务时会显示 `No MCP servers found.`，此时需先准备源配置再安装。

配置就绪后，把 `SERVER_NAME` 替换为清单中的实际名称：

```bash
vibe mcp list
vibe mcp add SERVER_NAME ../my-project --dry-run
vibe mcp add SERVER_NAME ../my-project
```

安装会合并目标项目的 `mcp.json`，保留无关条目；同名服务默认跳过，只有显式指定 `--force` 才替换。

### Hooks、工作流与独立 CLI

- [ralph-loop](hooks/ralph-loop)：RFC → DAG 拆解 → 分层验证 → 合并队列的 Hook 工作流
- [writing-agent](workflows/writing-agent)：从选题、研究到审稿发布的写作系统
- [cli/agent-browser](cli/agent-browser)、[cli/anything-cli](cli/anything-cli)、[cli/office-cli](cli/office-cli)：独立 CLI 项目
- `paseo.json`：按需创建的本地 Paseo 工作区配置，已被 Git 忽略，不是仓库必备文件

## 更新与维护

### 同步项目中已安装的 Skill / Manifest

直接更新使用当前本地仓库内容，**不隐式拉取远程**。`target` 默认为当前目录；每次指定一个名称，不支持 `--all`。

```bash
# 先预览，再同步整个已安装 Skill 目录（包括清理旧版本残留）
vibe update skill taste-skill ../my-project --dry-run
vibe update skill taste-skill ../my-project

# 同步配置，默认复用安装时记录的生成参数
vibe update manifest vibe-coding ../my-project

# 需要时显式覆盖参数；add manifest 同样支持 --scenario
vibe update manifest ui-testing ../my-project --scenario=web-e2e
vibe add manifest ui-testing ../my-project --scenario=component
```

Skill 更新会替换整个已安装目录，自定义文件也包含在更新前的备份中。尚未安装时先运行 `vibe add skill <name> [target]`。

Manifest 更新只覆盖模板生成的指令、规则、commands、agents、平台配置和工具资源；保留业务文件、研究成果、README、CONTRIBUTING、VERSION、CHANGELOG、运行记录及初始化大纲/笔记索引。仅 `vibe-coding` 的 `MANIFEST.md` 是更新资源，其他模板的同名产出账本保持原样。不删除新模板已移除的旧配置，也不整体替换项目资源目录。必需 Skills 中只同步已经安装的条目，缺失依赖仅提示，无关 Skills 不变。

`init/add` 会在目标项目的 `.vibe-tool/installations.json` 记录来源及适用的生成参数。之后更新默认复用记录，显式选项优先。没有记录的旧项目，需已有至少一项模板资源，首次更新还需明确所有适用参数（命令会列出缺项）；全新项目先使用 `vibe init` 或 `vibe add manifest`。空字符串表示模板默认值或无场景，例如：

```bash
vibe update manifest vibe-coding ../legacy-project \
  --provider=git --scenario='' --owner='' --org='' --repo='' --email=''
```

`--dry-run` 仅输出将新增、覆盖及跳过的路径，不写项目、安装记录或备份。实际变更前自动备份到 `.vibe-tool/backups/<唯一ID>/`，包含原始内容、校验值与变更清单；成功后打印恢复命令：

```bash
python /path/to/project/.vibe-tool/backups/BACKUP_ID/restore.py
```

将 `BACKUP_ID` 替换为本次备份目录名，或直接使用更新命令打印的恢复命令。恢复脚本独立运行，无需安装 `vibe`。配置、依赖 Skill 与安装记录在同一事务中更新，应用失败自动恢复已触及内容；内容及记录均未变化时不创建备份。

### 更新仓库中的 Skill 来源

裸命令仍更新受管理的 Skill 子模块：

```bash
vibe update
```

也可以使用仓库脚本：

```bash
./scripts/skills-git-pull.sh
```

`agent-skills` 和 `ai-investment-advisor` 默认不参与批量更新，需要单独执行：

```bash
git submodule update --remote --merge -- skills/agent-skills
git submodule update --remote --merge -- skills/ai-investment-advisor
```

部分 Skill 仓库（例如 `aris`、`ppt-master`）是独立嵌套仓库，不在 `.gitmodules` 中，按其自身仓库方式更新。

## 开发与验证

修改 CLI 或 Manifest 后，建议运行：

```bash
# 验证 Claude Code 与 Codex agent 文件兼容性
python scripts/validate-agent-compat.py

# 运行 vibe-tool 测试
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src python -m pytest tools/vibe_tool/tests -v
```

新增 Manifest 至少需要包含 `CLAUDE.md`，这样才能被 `vibe list manifests` 发现。新增 Skill 则应在 Skill 目录中提供 `SKILL.md`。

新建 Manifest 或修改其工作流时，还需同步交付 **workflow SVG、可编辑源、可复现生成命令和只读一致性检查**，并从 README/主指令链接。图上区分 AI 自主执行、AI 验证与人工决策，标注分支、返工及人工确认后的恢复路径。详见 [Manifest 工作流图交付规范](docs/manifest-workflow.md) 与 [真实 SVG 示例](docs/examples/manifest-workflow/workflow.svg)。现有 Unity 图源与渲染器继续复用；本约定不改变模板安装策略。

```bash
# 检查通用示例图是否与可编辑源一致
python3 scripts/render-manifest-workflow.py \
  --source docs/examples/manifest-workflow/workflow.json \
  --output docs/examples/manifest-workflow/workflow.svg --check

# 验证渲染、分支结构和只读漂移检查
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_manifest_workflow.py' -v
```

## 许可证

仓库自身采用 [MIT License](LICENSE)。`skills/` 与 `workflows/` 中的外部项目遵循各自仓库的许可证；分发或修改时请同时查看对应子模块的许可文件。
