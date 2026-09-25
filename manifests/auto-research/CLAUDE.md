# Auto-Research Manifest

面向自动化学术研究的 manifest 包。整合 aris（研究编排框架）、paper-review（证据驱动论文评审）、paperreview（外部自动论文评审）、autofigure（自动图表生成）、anti-defensive-writing（中英文写作原则）与 `mine/z-humanizer`（中英文 humanization）能力线。

## Commands

| Command | Description |
|---------|-------------|
| `aris/research-pipeline "topic"` | 端到端研究流水线 |
| `aris/auto-review-loop "paper"` | 自动论文评审循环 |
| `aris/auto-paper-improvement-loop` | 自动论文改进循环 |
| `aris/figure-spec "description"` | 生成确定性图表 (JSON→SVG) |
| `aris/paper-illustration "desc"` | AI 论文插图生成 |
| `aris/paper-figure "results"` | 数据驱动图表生成 |
| `aris/rebuttal "reviews"` | 自动生成审稿回复 |
| `paper-review` | 证据驱动的 ML/AI 论文评审与投稿前自审 |
| `grill-me` | 所有计划类步骤前的逐项追问与方案压力测试；也可随时直接调用 |
| `mine/paperreview-ai-review "paper.pdf"` | paperreview.ai 自动论文评审 |
| `aris/research-lit "query"` | 文献调研与综述 |
| `aris/citation-audit` | 引用校验 (DBLP/arXiv) |
| `aris/paper-claim-audit` | 数值声明校验 |
| `aris/experiment-bridge` | 实验桥接 |
| `uv run scripts/writing_plan.py init ...` | 从论文大纲初始化 Writing Plan |
| `uv run scripts/writing_plan.py validate ...` | 校验 Writing Plan schema 与引用关系 |
| `uv run scripts/writing_plan.py resolve ...` | 解析 profile、继承和审批有效性 |
| `uv run scripts/writing_plan.py render ...` | 生成只读的 `WRITING_PLAN.md` 视图 |
| `uv run scripts/writing_plan.py review ...` | 按 resolved node plan 审查正文 |
| `uv run scripts/writing_plan.py migrate ...` | 为旧项目生成兼容 Writing Plan |
| `mine/export-paper-zip "path" [--mode submission|bundle]` | 论文导出打包 — 投稿 ZIP 或文件打包 |
| `mine/paper-version-manager init <dir> [msg]` | 初始化论文版本追踪（v1） |
| `mine/paper-version-manager bump --minor <dir> [msg]` | 小版本升级（v1 → v1.1，审稿修改后） |
| `mine/paper-version-manager bump --major <dir> [msg]` | 大版本升级（v1 → v2，重大改写后） |
| `mine/paper-version-manager list <dir>` | 列出所有版本和变更日志 |
| `mine/paper-version-manager diff <dir> --from vX --to vY` | 比较两个版本的差异 |
| `mine/paper-version-manager rollback <dir> <version>` | 回滚到指定版本 |
| `python3 scripts/research_workflow.py branch init --idea <slug>` | 初始化 research cycle、`main` 与 integration branch |
| `python3 scripts/research_workflow.py branch start --stage <stage-id>` | 从父 branch 创建并切换阶段 branch |
| `python3 scripts/research_workflow.py branch status` | 查看阶段 branch、父 branch、合并状态 |
| `python3 scripts/research_workflow.py branch merge --stage <stage-id>` | 终态检查点通过后以 `--no-ff` 合并到父 branch |
| `python3 scripts/research_workflow.py branch revision --kind submission\|revision --id <id>` | 创建投稿或返修 branch |
| `python3 scripts/research_workflow.py branch close` | 将 cycle integration 合并回配置的 base branch |
| `python3 scripts/latex_template_gate.py manifest ...` | 从官方 venue 要求生成 LaTeX 模板完整性清单 |
| `python3 scripts/latex_template_gate.py verify ...` | 校验必需文件与不可变模板 style 哈希 |

## 仓库结构

```
auto-research/
├── writing/
│   ├── writing-plan.schema.json
│   ├── writing-plan.minimal.yaml
│   ├── writing-plan.full.yaml
│   ├── profiles.yaml
│   ├── venue-profiles.yaml
│   ├── figure-types.yaml
│   ├── migration-defaults.yaml
│   └── README.md
├── references/
│   ├── research-lifecycle.md     # 自动化科研生命周期
│   ├── paper-review-guide.md     # 自动论文评审
│   ├── figure-generation.md      # 自动图表生成
│   ├── venue-requirements.md     # 期刊/会议要求与图规格校验
│   ├── integration-guide.md      # 三线集成
│   └── research-writing-rules.md  # 中英文写作、LaTeX 模板与统计默认规则
├── templates/
│   ├── RESEARCH_PLAN.md.example
│   ├── PAPER_OUTLINE.md.example
│   ├── REVIEW_RESPONSE.md.example
│   └── FIGURE_SPEC.md.example
├── skills/
│   └── export-paper-zip/
│       └── SKILL.md
├── scripts/
│   ├── init-auto-research.sh
│   └── writing_plan.py
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── config.yml
│   │   ├── 01-research-idea.yml
│   │   ├── 02-paper-submission.yml
│   │   └── 03-figure-request.yml
│   └── workflows/
│       └── auto-research-ci.yml
├── CLAUDE.md
├── AGENTS.md
└── README.md
```

## 四条核心流水线

### 1. Research Pipeline
aris/research-pipeline 端到端：文献调研 → 想法生成 → 新颖性检查 → 实验计划 → 论文写作

### 2. Planned Writing and Auto Review Loop

研究完成且大纲确定后，严格执行：

`research → outline → plan-writing → validate → resolve → render-plan → approval-gates → write → review → revise`

- 首次运行若没有 `.auto-research/writing-plan.yaml`，自动执行 `migrate`；已有大纲时从大纲建节点，没有大纲时先生成大纲。
- 每次节点结构或要求变化后重新 `validate`、`resolve`、`render`。`WRITING_PLAN.md` 是生成视图，不作为输入。
- 投稿前在 Writing Plan 顶层冻结 `venue.profile`、官方 `source_url` 和 `checked_at`；resolver 将期刊/会议的页数、模板、匿名、图格式、尺寸、分辨率、caption、补充材料与必需声明注入每个 resolved node。要求变化会使审批哈希失效。
- writer 只消费 `.auto-research/resolved-writing-plan.json` 中当前节点，不直接解释原始 YAML；一次只写一个节点。
- 图节点只能使用 `writing/figure-types.yaml` 中的类型；结构图走 `figure-spec`，常规数据图走 `paper-figure`/`plot`，Nature 级论文图、多面板结果图或 venue-aware 绘图/QA 走 `nature-figure`，概念图走 `paper-illustration`。每个图记录数据输入、输出格式、caption、alt text、生成命令和 code revision。
- Nature 级论文数据图、多面板结果图与基于数据/图注/claim 的机制图，优先读取并使用 `nature-figure`（`skills/nature-skills/skills/nature-figure/SKILL.md`）；同时遵循其 figure contract、panel evidence architecture、venue spec 和导出 QA。单纯结构性架构图仍走 `figure-spec`/现有双交付规则，概念性 AI 插图仍走 `paper-illustration`。`nature-figure` 引用的共享资源位于同一子模块的 `skills/nature-shared/`，不要只复制单个 SKILL.md。
- 只有 resolved 节点的 `approval` 为 `before_write` 且 `approval_state` 不是 `approved` 时暂停。目标、受众、风格或证据等 resolved 要求变化会改变哈希，使旧审批变为 `stale`。
- review 按节点执行；失败后仅重写不合格节点。`auto_fix: constrained` 不得改变核心结论、证据标准、章节结构或已审批目标。
- 详细字段、继承和审批语义见 `writing/README.md`。

投稿前完整审稿默认并行运行三个独立 reviewer：`paper-review`、`academic-paper-reviewer` 和 gptweb ICLR prompt。每路从原始论文及附录直接评估，在 fresh session 中运行，互不共享上下文；三份报告落盘后再综合共识、分歧和有依据的 ICLR 分数。gptweb API 与综合流程见 [`references/multi-review.md`](references/multi-review.md)，prompt 见 [`references/iclr-review-prompt.md`](references/iclr-review-prompt.md)。之后可运行 aris/auto-review-loop 进行迭代改进：节点写作与审查 → 论文草稿 → 三路独立审稿 → 综合 → 改进 → 再审 → 收敛。

### 3. Evidence-based Paper Review

`paper-review` 负责从完整论文、补充材料和相关工作出发，核对贡献、主张、
baseline、消融、引用和证据链；输出 `review_<id>.txt` 与
`frontier_<subfield>.md` 到研究项目的 `outputs/`。详细接入和更新规则见
`references/paper-review-skill.md`。

### 4. Auto Figure Pipeline
aris/figure-spec + aris/paper-illustration：图规格 (JSON) → 确定性 SVG → AI 精修 → 论文集成

## 关键文件

| File | Purpose |
|------|---------|
| `references/research-lifecycle.md` | 完整自动化科研流程说明 |
| `references/version-lifecycle.md` | 论文版本管理生命周期（位于 mine/paper-version-manager/references/） |
| `references/paper-review-guide.md` | 自动评审机制和评审者独立性协议 |
| `references/figure-generation.md` | 自动图表生成管线 |
| `references/venue-requirements.md` | 期刊/会议要求、官方来源和投稿前校验 |
| `references/integration-guide.md` | aris / paperreview / autofigure 集成方式 |
| `templates/RESEARCH_PLAN.md.example` | 研究计划模板 |
| `templates/PAPER_OUTLINE.md.example` | 论文大纲模板 |
| `templates/FIGURE_SPEC.md.example` | 图表规格模板 |
| `writing/writing-plan.schema.json` | Writing Plan Draft 2020-12 schema |
| `writing/profiles.yaml` | 内置受众、风格、证据与呈现 profile |
| `writing/venue-profiles.yaml` | 期刊、会议和审稿服务要求快照 |
| `writing/figure-types.yaml` | 图类型、renderer、输入输出与验收规则 |
| `scripts/writing_plan.py` | Writing Plan 初始化、迁移、解析、渲染与审查工具 |

## Issues

- 研究想法提交 — 提交新的研究方向或课题
- 论文审阅 — 提交论文草稿请求 AI 评审
- 图表生成 — 提交图表生成请求

## Gotchas

- 评审者独立性：评审者必须从原始工件直接评估，执行者不可提前消化或总结
- 输出登记的唯一账本及追加规则见 [`MANIFEST.md`](MANIFEST.md)；本文件不重复维护清单格式
- 跨模型协议：建议执行者和评审者使用不同模型家族
- 文件版本化：每个产出需要带时间戳副本 + 固定名称最新副本
- 论文版本管理：每次修改后使用 `mine/paper-version-manager` 创建版本快照，v1/v2 为大改、vx.1/vx.2 为小改
- Writing Plan 事实源：只修改 `.auto-research/writing-plan.yaml`；写作仅使用 resolved JSON，结构变化后必须重新校验、解析和渲染
- Writing Plan 职责边界：planner 修改原始 YAML；resolver 生成无继承/无 profile/无 merge marker 的节点配置；writer 一次写一个节点；reviewer 只依据 resolved node plan 检查，不增加要求
- Research 写作默认使用 LaTeX；95% CI 默认省略，只有官方 venue 要求、研究方案、作者请求或审稿意见要求时才启用并登记理由。
- 期刊/会议官方模板是唯一排版基线；`.cls`、`.sty`、字体、参考文献样式以及模板 table/figure styles 均不可修改。缺少文件时记录缺项，不以自制 style 替代。
- 研究场景先接入 `mine/z-humanizer` 的中英文 academic/journal/conference 路由；`anti-defensive-writing` 的中英文目录由 `skills/anti-defensive-writing` 子模块管理，默认作为可选审计器而非自动改写器。

## 全生命周期运行契约

从启动到录用使用三层科研阶段树，而非仅实验阶段。权威流程见 `references/research-lifecycle.md`，检查点/Git/模型规则见 `references/lifecycle-runtime.md`，实验设计与自动统计见 `references/experiment-execution.md`。这三份契约优先于简化流水线示意。

每个大阶段的细化说明位于 `references/lifecycle-stage-details.md`；机器可读阶段契约位于 `lifecycle/defaults.json.phase_details`。

项目首次启用：`python3 scripts/research_workflow.py init`。模型角色默认：研究 GPT-6 Pro、规划 GPT-6 medium、执行 GPT-5.6-Luna high、写作 GPT-5.5 high；显式核验实际宿主绑定。实验默认 seeds=[42]。baseline 必须联网检索；消融在执行前完成覆盖矩阵；预算审批后由已有 aris 后端自动执行。

内部工具：research_workflow.py 的 init/status/route/checkpoint/resume；experiment_stats.py 的 design-review/expand/gate/summarize。不新增 vibe 公共命令。每个阶段事件 Git 留档，中间规划与日志持续保存；投稿回执、评审、返修、转投及录用记录纳入同一周期。初始化只安装资源，不启动云资源、模型或正式投稿。

### Figure 逐类实现与视觉一致性

图生成前读取 `references/figure-implementation-recipes.md` 的对应类型配方。
数据驱动论文图、多面板结果图或需要 Nature/NMI venue 规范时，另读取 `skills/nature-skills/skills/nature-figure/SKILL.md` 与其按需引用的 backend/QA 资源；先定 figure claim、证据层级、panel 架构、数据完整性与目标 venue，再绘制并执行对齐、碰撞、PDF 字号和统计标注检查。该 skill 不替代本 manifest 对图节点记录、resolved visual、code revision 和人工视觉审查的要求。
每个 renderer 消费 resolved figure 的 `type_requirements.implementation` 与 `resolved_visual`；
全论文使用稳定 series_colors，类别同时用线型/形状区分。优先白底、轻网格、无装饰阴影。
配色预设位于 `writing/figure-palettes.yaml`，允许文档/文件/节点/单图覆盖及自定义 HEX 组合。
最终尺寸、灰度打印、色觉模拟、标签碰撞和证据忠实度均进入视觉审查，人工审查结果随 Git checkpoint 留档。

### 五类结构图双交付覆盖规则

Arch/Flow/Pipeline/Algo/Concept 使用 gpt-image 视觉版 + GPT 编排、ppt-master 导出的原生可编辑 PPTX。不得使用旧 figure-spec 渲染器静默替代，不将图像嵌入 PPT 冒充可编辑结果。以共享节点/标签/关系规格核对两个版本；缺少实际模型或工具绑定时阻塞。其余数据图继续代码绘制，字体和层级服从 resolved_visual。

### 子阶段执行契约

启动、文献、idea、实验、分析、写作、评审、投稿、返修和录用的叶节点详见 `references/lifecycle-leaf-contracts.md`。新项目完成叶节点前须运行 stage_contract.py 并登记当前输出哈希与逐项审查记录；不得自动填充 pass 或伪造人工确认。已存在实际输出可被交接文件引用，无须重跑。配置身份、真实模型API、远端运行和科学审查仍由执行宿主负责，契约校验不等于科学任务完成。

### 可追踪 LaTeX 主结果表

多数据集、多baseline、多指标数值表使用 `writing/table-plan.schema.json` 和 `scripts/table_plan.py`：先从 experiment_stats 结果解析原始文件/审计/seed，再渲染LaTeX；禁止将示例画廊数值用于论文证据。按 references/table-plan.md 在 Writing Plan 的 presentation.tables 关联计划、resolved和输出目录。正文数值优先使用 ResearchValue 引用并运行单独review；手写数字和科学结论仍需审查。所有生成记录使用已有生命周期检查点归档。

### 章节文风、论证与图表联合规划

写章节前先确定 `style.strategy`、`style.paragraph_rules` 和节点局部
`composition`：论证顺序、页数预算、图表的用途/归属/首次引用/讨论位置，以及
栏宽、浮动偏好和溢出策略。图表按证据先准备，正文解释重点而非逐格复述。
参考 `references/writing-composition.md`。使用 `writing_plan.py packet` 导出
resolved 单节点任务包；外部宿主另行提供核验后的证据、术语和邻接正文摘要。
生成后运行节点 review，再编译并视觉检查最终尺寸、标签、浮动距离和页数。
当前工具仅导出任务包和检查源码引用；视觉 warning 不代表投稿验收通过。
