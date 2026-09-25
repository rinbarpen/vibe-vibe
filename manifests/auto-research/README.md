# Auto-Research Manifest

面向自动化学术研究的独立 manifest 包。

## 场景

整合研究编排、证据审查、图表生成与中英文论文写作规则，并用版本化 Writing Plan 连接研究结果与节点级写作：
- **aris** — 研究编排框架（文献调研、想法发现、实验规划、论文写作）
- **paper-review** — 证据驱动的 ML/AI 论文评审与投稿前自审（由根目录 `skills/paper-review` Git 子模块管理）
- **paperreview** — 自动论文评审（4 轮自主评审循环、数值声明校验、引用校验）
- **autofigure** — 自动图表生成（确定性 SVG 架构图、AI 插图、数据驱动图表）
- **nature-figure** — `skills/nature-skills` 上游子模块中的 Nature 级论文绘图技能，依赖同仓库 `nature-shared`；用于高质量数据图、多面板结果图和 venue-aware figure QA
- **anti-defensive-writing** — 中英文 anti-defensive writing skill，作为可选写作审计器管理（根目录 `skills/anti-defensive-writing` Git 子模块）
- **z-humanizer** — `mine/z-humanizer` 的中英文 academic/journal/conference humanization，先接入 research 写作节点

## 使用方式

```bash
# 初始化到目标研究项目
./scripts/init-auto-research.sh /path/to/your/research-project
```

## 快速开始

1. 在每次制定研究、实验或论文计划前调用 `grill-me`；也可在任意阶段直接调用
2. 创建一个研究方向 issue
3. 运行 `aris/research-pipeline "topic"` 启动全流程
4. 大纲确定后初始化计划：`uv run scripts/writing_plan.py init --outline PAPER_OUTLINE.md --output .auto-research/writing-plan.yaml`
5. 依次运行 `validate`、`resolve`、`render`，仅将 resolved node plan 交给 writer
6. 在计划中选择 `venue.profile`，刷新官方 author guide/CFP 和 `checked_at`
7. 按 `writing/figure-types.yaml` 为架构图、流程图、对比图、消融图、曲线、热力图、定性图和概念图创建 figure node
8. 写作后运行 `review`，只局部修订未通过节点，再运行 `aris/auto-review-loop`
9. 需要投稿前自审时调用 `paper-review`，将问题绑定到论文中的表格、公式、实验设置或引用
10. 投稿前完整评审默认并行启动 `paper-review`、`academic-paper-reviewer` 与 gptweb ICLR prompt 三路独立 reviewer；每路直接读取原始论文及附录，分别保存报告后再综合。见 [`references/multi-review.md`](references/multi-review.md) 和 [`references/iclr-review-prompt.md`](references/iclr-review-prompt.md)
11. 按 `CLAUDE.md` 的图表路由选择 `nature-figure`、`aris/figure-spec`、`aris/paper-figure` 或 `aris/paper-illustration`；Nature 级数据图、多面板结果图和 venue-aware QA 优先读取 `nature-figure`
12. 论文正文使用官方 venue LaTeX 模板；锁定 `.cls`/`.sty`/字体/参考文献/table/figure styles，不修改模板样式文件
13. 默认省略 95% CI；只有 venue、研究方案、作者或审稿意见明确要求时才启用，并在 Writing Plan 记录理由
14. 先运行 `mine/z-humanizer` 的中英文 research 写作路由；需要时再运行 `anti-defensive-writing` 的中英文审计目录

完整写作顺序：

`research → outline → plan-writing → validate → resolve → render-plan → approval-gates → write → review → revise`

字段、继承、稳定 ID、审批哈希和迁移说明见 [`writing/README.md`](writing/README.md)。
投稿要求和图生成规则见 [`references/venue-requirements.md`](references/venue-requirements.md)。
`nature-figure` 随根目录 `skills/nature-skills` Git 子模块提供；更新时保留整个子模块，以满足 `nature-shared` 等相对资源依赖。
写作默认规则、LaTeX 模板锁定和中英文 skill 接入见 [`references/research-writing-rules.md`](references/research-writing-rules.md)。

## 全生命周期运行契约

从启动到录用使用三层科研阶段树，而非仅实验阶段。权威流程见 `references/research-lifecycle.md`，检查点/Git/模型规则见 `references/lifecycle-runtime.md`，实验设计与自动统计见 `references/experiment-execution.md`。这三份契约优先于简化流水线示意。

项目首次启用：`python3 scripts/research_workflow.py init`。模型角色默认：研究 GPT-6 Pro、规划 GPT-6 medium、执行 GPT-5.6-Luna high、写作 GPT-5.5 high；显式核验实际宿主绑定。实验默认 seeds=[42]。baseline 必须联网检索；消融在执行前完成覆盖矩阵；预算审批后由已有 aris 后端自动执行。

### paper-review 子模块

根目录 `skills/paper-review/` 是上游仓库的完整 checkout，不复制或改写其中的 `SKILL.md` 与参考资料。首次获取或更新：

```bash
git submodule update --init -- skills/paper-review
vibe update
```

`vibe list skills` 会递归发现该 skill；`vibe update` 会把它纳入批量更新。评审产物应写入研究项目的 `outputs/`，不要写回子模块目录。

### anti-defensive-writing 子模块

上游仓库同时提供中文 `skills/anti-defensive-writing` 与英文
`skills/anti-defensive-writing-en`。在本仓库中作为一个子模块管理：

```bash
git submodule update --init -- skills/anti-defensive-writing
```

研究场景默认不启用防御性写作；需要审计时按段落语言选择对应目录。写作事实、
数字、引用 key、LaTeX 命令和术语由 `mine/z-humanizer` 保留，审计器不改模板样式。

内部工具：research_workflow.py 的 init/status/route/checkpoint/resume；experiment_stats.py 的 design-review/expand/gate/summarize。不新增 vibe 公共命令。每个阶段事件 Git 留档，中间规划与日志持续保存；投稿回执、评审、返修、转投及录用记录纳入同一周期。初始化只安装资源，不启动云资源、模型或正式投稿。
