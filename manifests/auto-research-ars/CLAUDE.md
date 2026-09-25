# Auto-Research ARS Manifest

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

面向 Academic Research Skills (ARS) 的自动科研 manifest 包。以 ARS 为核心，提供深度研究、论文写作、多角色评审、端到端流水线四套技能。

## Commands

| Command | Description |
|---------|-------------|
| `ars/deep-research "topic"` | 13-agent 深度研究（7 种模式） |
| `ars/academic-paper "topic"` | 12-agent 论文写作（10 种模式） |
| `ars/academic-paper-reviewer "paper"` | 5 角色独立评审（6 种模式） |
| `ars/academic-pipeline "topic"` | 10 阶段端到端学术流水线 |
| `mine/paperreview-ai-review "paper.pdf"` | paperreview.ai 自动论文评审 |

## 仓库结构

```
auto-research-ars/
├── references/
│   ├── deep-research-guide.md      # 深度研究模式说明
│   ├── academic-paper-guide.md     # 论文写作管线
│   └── reviewer-guide.md           # 多角色评审说明
├── templates/
│   ├── RESEARCH_PLAN.md.example
│   └── PAPER_OUTLINE.md.example
├── scripts/
│   └── init-auto-research-ars.sh
├── CLAUDE.md
├── AGENTS.md
└── README.md
```

## 四条核心技能

### 1. deep-research
13-agent 深度研究团队，7 种模式：
- `full` — 完整深度研究
- `quick` — 快速简报
- `paper-review` — 论文评审
- `lit-review` — 文献综述
- `fact-check` — 事实核查
- `socratic` — 苏格拉底式引导研究
- `systematic-review` — 系统综述（含 meta 分析）

### 2. academic-paper
12-agent 论文写作管线，10 种模式：
- `full` — 完整论文写作
- `plan` — 研究计划
- `outline` — 论文大纲
- `revision` — 论文修改
- `revision-coach` — 修改指导
- `abstract` — 摘要写作
- `lit-review` — 文献综述章节
- `format-convert` — 格式转换
- `citation-check` — 引用校验
- `disclosure` — AI 使用声明

### 3. academic-paper-reviewer
5 角色独立评审：
- EIC（主编）
- 3 位领域专家 (peer reviewers)
- Devil's Advocate（反向论证）

6 种模式：full / re-review / quick / methodology / socratic / calibration

### 4. academic-pipeline
10 阶段端到端流水线编排器：
research → write → integrity check → review → revise → re-review → re-revise → final integrity → finalize

## Gotchas

- 论文草稿支持 LaTeX / Markdown 格式
- 引用校验通过 DBLP/arXiv 交叉验证
- 数值声明校验自动比对原始结果文件
- 多角色评审确保评审覆盖率
