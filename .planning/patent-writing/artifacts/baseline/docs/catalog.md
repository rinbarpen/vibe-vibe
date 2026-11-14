# 能力与模板目录

**简体中文** | [English](catalog_EN.md)

按需要查找技能、项目模板和配套工具；不必在开始使用前通读全部清单。安装与更新命令见 [CLI 参考](cli-reference.md)。

## 项目结构

```text
vibe-vibe/
├── .agents/skills/              # 本仓库维护时使用的 Agent 技能
├── skills/                      # 社区技能库：Git 子模块及独立嵌套仓库
│   ├── ANNOTATIONS.md           # 中文技能索引
│   └── ANNOTATIONS_EN.md        # 英文技能索引（其余目录为技能来源）
├── mine/                        # 第一方技能：绘图、演示、办公、研究等
├── manifests/                   # 项目模板与人机协作契约
│   ├── vibe-coding/             # 软件工程全生命周期（模板名保持不变）
│   ├── auto-research/           # 科研、实验与论文
│   ├── tutor/                   # 对话式学习与学习记录
│   ├── office/                  # 原生办公文档交付与验收
│   └── ...                     # 其他模板见下方清单
├── workflows/writing-agent/     # 完整的多阶段写作工作流项目
├── tools/vibe_tool/             # vibe CLI 的 Python 实现与测试
│   ├── src/vibe_tool/           # 发现、安装、更新、备份及配置
│   └── tests/                  # CLI 回归测试
├── cli/                         # 独立工具，按各自文档构建和使用
│   ├── agent-browser/
│   ├── anything-cli/
│   ├── craft-anything/
│   └── office-cli/
├── hooks/ralph-loop/            # RFC、任务拆解、验证与合并队列规则
├── docs/                        # 维护规范与工作流图示例
├── scripts/                     # 仓库维护、兼容性校验与图渲染脚本
├── tests/                       # 仓库级回归测试
├── AGENTS.md                    # 本仓库的 Agent 协作约定
├── CLAUDE.md                    # Claude Code 仓库指引
└── README.md / README_EN.md     # 中英文使用说明
```

- **Skill** 是可按需安装的能力单元，默认从 `skills/` 与 `mine/` 发现。
- **Manifest** 是项目级协作配置包，可组合指令、规则、场景、agents、必需 Skills 与初始化脚本；它不等同于单个 Skill。
- **Workflow 与独立 CLI** 保留各自的运行方式，不会因为放进仓库就自动成为可安装 Skill。
- 根目录 `mcp.json` 是可选来源配置；`.vibe-tool/` 是本地安装记录、备份与统计目录，已被 Git 忽略。

## 仓库内容

### 技能（Skills）

`skills/` 包含来自多个社区和维护者的 Git 子模块，`mine/` 存放第一方 Skill。CLI 会递归扫描这两个目录中的 `SKILL.md`；同名 Skill 使用带相对路径的标识自动消歧，安装时以 `vibe list skills` 显示的名称为准。

重点集合包括：

- [Anthropic Skills](../skills/anthropics)：文档、表格、演示文稿、PDF、前端等官方技能
- [Claude Scientific Skills](../skills/claude-scientific-skills)：科研、生命科学、化学、医学影像等
- [UI/UX Pro Max](../skills/ui-ux-pro-max-skill)：设计系统与 UI 风格库
- [Impeccable](../skills/impeccable)：前端设计与审美、界面评审和视觉打磨；安装：`vibe add skill impeccable <target>`
- [Intuit to Idea](../skills/intuit-to-idea)：通过 AI 具体提问与用户直觉，将研究方向发展为可验证假设；已接入 `auto-research` 的按需 Idea 路线；安装：`vibe add skill intuit-to-idea <target>`
- [AI Research Skills](../skills/AI-Research-SKILLs)：AI/ML 研究、训练、评估和论文工作流
- [Agent Skills for Context Engineering](../skills/Agent-Skills-for-Context-Engineering)：上下文工程方法
- [Humanizer-zh](../skills/Humanizer-zh)、[shuorenhua](../skills/shuorenhua)：中文文本改写与表达优化
- [Unslop](../skills/unslop)：普通文案去模板感、审查与改写；`z-humanizer` 的普通写作路由采用它，学术和专利路由保持独立；安装：`vibe add skill unslop <target>`
- [Z-Writing](../mine/z-writing/SKILL.md)：中英文统一写作入口，组合 AI Vibe 的文风/写作与 z-humanizer 的保真润色；普通文本、办公、论文和基金按需分流；`vibe add skill z-writing <target>`
- [Chinese-WebNovel-Skill](../skills/chinese-webnovel-skill)：中文网文选材、构思、章纲、写作与完稿审查
- [Pretty Mermaid Skills](../skills/Pretty-mermaid-skills)：Mermaid 图表生成与渲染
- [Visual Explainer](../skills/visual-explainer/plugins/visual-explainer)：将架构、流程、代码变更、方案和对比表制作成独立 HTML 可视化图解；完整安装命令见下方。
- [Unity Game Development](../mine/unity-game-development)：覆盖游戏制作全流程、3D/DCC 建模、游戏测试与执行/Reviewer 角色，可整包、阶段或单项安装。
- [State Machine Reasoning](../mine/state-machine-reasoning)：将决策、排障、研究和工作流分析建模为状态机，并生成 Mermaid 可视化图。
- [Omnippt](../mine/omnippt)：按需加载需求调研、叙事大纲、逐页策划、视觉设计、原生制作和独立审查子技能，支持可编辑演示文稿交付。
- [Geo Sleuth](../skills/geo-sleuth)：照片拍摄地点与时间推断、线索分析和证据校验；安装：`vibe add skill geo-sleuth <target>`
- [X Research](../skills/x-research-skill)：信息检索与社交平台调研

仓库内的 [mine/](../mine) 存放第一方 Skill，[workflows/](../workflows) 存放完整工作流项目。后者按各自说明使用，不属于 `vibe list skills` 的默认扫描根目录。

浏览索引：

- [中文 Skills 标注索引](../skills/ANNOTATIONS.md)
- [英文技能索引](../skills/ANNOTATIONS_EN.md)

### 按场景使用可视化技能

统一入口是 [Omnidraw](../mine/omnidraw/SKILL.md)，完整选择规则与准确安装标识见 [场景指南](../mine/omnidraw/references/visualization-scenarios.md)。保留各类能力，不把所有任务统一成 HTML 或图片：

| 场景 | 采用的技能 / 能力 | 主要输出 |
| --- | --- | --- |
| 架构讲解、方案对比、可视化评审 | Visual Explainer | HTML 图解、网页演示 |
| 数据图表、探索性统计 | Matplotlib、Seaborn | 代码、SVG/PDF/PNG |
| 交互式数据图 | scientific-visualization 的 Plotly 路线 | 交互 HTML、数据与代码 |
| KPI、联动筛选、多视图仪表盘 | creating-dashboards | 可运行的数据界面 |
| 科研统计图、论文多面板 | scientific-visualization | 投稿所需静态格式与来源记录 |
| 科研方法架构、机制、图形摘要 | CCFA / 科学示意图路线 | 科学图与按需可编辑重建 |
| 流程、时序、ER、状态机、小型概念图 | Mermaid / PlantUML | 文本图源与预览 |
| 带真实边表与图计算的知识网络 | NetworkX | 图数据、分析代码与可视化 |
| 地理分布与空间分析 | GeoPandas | 地图、空间数据与代码 |

```bash
# 统一入口内含 Mermaid 与 Matplotlib 子技能；额外路线按需安装
vibe add skill omnidraw ../my-project
```

可选来源不随入口自动全部安装，运行时也按所选场景准备。当前没有独立 `plotly` Skill，应通过场景指南中的 scientific-visualization 来源使用其 Plotly 工作流。用户指定工具、格式与已有项目栈优先。

### 可视化图解：Visual Explainer

[上游项目](https://github.com/nicobailon/visual-explainer) 以 Git 子模块保留在 `skills/visual-explainer/`，可安装入口是其中的 `plugins/visual-explainer/`。适合架构与数据流说明、代码变更评审、方案对比、项目回顾及 HTML 幻灯片；已有统计绘图与科研图表继续使用 Matplotlib、Plotly、scientific-visualization 等技能。

```bash
vibe add skill visual-explainer ../my-project
```

命令将完整技能安装到目标项目的 `.agents/skills/visual-explainer/`，保留 `references/`、`templates/`、`commands/`、`kit/` 及可选导出工具，不只复制 `SKILL.md`。示例请求：

```text
使用 visual-explainer，将这个项目的模块关系和数据流画成 HTML 图解，保存到 docs/architecture.html。
```

查看生成页面需要浏览器；随包 `kit/render.mjs` 渲染器需要 Node.js。浏览器自动检查、MCP、PPTX 或视频导出按上游说明准备额外依赖。`vibe add skill` 不会全局安装工具，也不会自动注册命令模板为宿主的斜杠命令。

### Office：能力与项目分层

`vibe add skill office <target>` 安装通用办公能力；`vibe init office <target>` 创建办公项目并安装 Office 与配套技能。格式指南、宏和验证工具的唯一来源为 [Office Skill](../mine/office/SKILL.md)，项目协作契约见 [办公 Manifest](../manifests/office/README.md)。

### 项目模板（Manifests）

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
| `office` | 办公交付项目：目标、来源与版本、跨格式协作、验收与归档；包含 Office Skills |
| `social-media` | 社交媒体内容创作与运营 |
| `ui-testing` | Web、组件、移动端、视觉与无障碍测试 |
| `game-design` | 游戏设计与制作：32 类玩法 × 23 项引擎/框架、19 领域 94 个细工作包、12 角色并行编排、建模/资产与版本闭环及 [workflow SVG](../manifests/game-design/references/workflow.svg) |
| `unity-game` | Unity 游戏制作全流程，Claude Code/Codex 角色、执行/Reviewer 技能与 [workflow SVG](../manifests/unity-game/references/workflow.svg) |

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

### 钩子、工作流与独立命令行工具

- [ralph-loop](../hooks/ralph-loop)：RFC → DAG 拆解 → 分层验证 → 合并队列的 Hook 工作流
- [writing-agent](../workflows/writing-agent)：从选题、研究到审稿发布的写作系统
- [cli/agent-browser](../cli/agent-browser)、[cli/anything-cli](../cli/anything-cli)、[cli/office-cli](../cli/office-cli)：独立 CLI 项目
- [cli/craft-anything](../cli/craft-anything)：Rust 桌面应用、CLI 与 MCP 服务的上游源码，提供基于证据的软件分析与重建工作流；按上游说明构建和使用，不作为 Skill 安装。
- `paseo.json`：按需创建的本地 Paseo 工作区配置，已被 Git 忽略，不是仓库必备文件

