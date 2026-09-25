# Integration Guide: research + paper-review + humanizers + LaTeX + autofigure

## 研究场景集成架构

```
                    ┌─────────────────────────────────────────────────────┐
                    │              research-pipeline                     │
                    │                                                     │
  ┌─────────────────┼─────────────────────────────────────────────────────┼──┐
  │   aris          │                                                     │  │
  │                 ▼                                                     │  │
  │  research-lit ──► idea-discovery ──► novelty-check                    │  │
  │       │               │                  │                            │  │
  │       ▼               ▼                  ▼                            │  │
  │  experiment-plan → bridge → run/queue → analyze/audit            │  │
  │       │                                      │                       │  │
  │       ▼                                      ▼                       │  │
  │  paper-plan → Writing Plan → node-write/review                │  │
  │       │                                                              │  │
  ├───────┼──────────────────────────────────────────────────────────────┼──┤
  │  writing rules                                                       │  │
  │  LaTeX template lock → z-humanizer (zh/en) → anti-defensive audit    │  │
  │       │                  │                        │                   │  │
  │  paper│review            │                        │                   │  │
  │       ▼                                                              │  │
  │  paper-write ──► paper-review ──► auto-review-loop (4 rounds)        │  │
  │       │                  │                        │                   │  │
  │       │                  ▼                        ▼                   │  │
  │       └──────────────► paper-claim-audit ──► citation-audit            │  │
  │       │                  │                        │                   │  │
  │       └──────────────► auto-paper-improvement-loop                    │  │
  │       │                                                              │  │
  ├───────┼──────────────────────────────────────────────────────────────┼──┤
  │  auto │figure                                                         │  │
  │       ▼                                                              │  │
  │  figure-spec ──► paper-illustration ──► paper-figure ──► paper-compile│  │
  └──────────────────────────────────────────────────────────────────────┴──┘
```

## 集成点

### Research writing rules

写作节点先解析 venue 官方投稿要求，再锁定官方 LaTeX 模板。正文不直接修改模板的
`.cls`、`.sty`、字体、参考文献、table 或 figure styles；所有必需文件、编译命令、
版本和哈希写入 template manifest。95% CI 默认省略，仅在 Writing Plan 明确要求
时启用。

草稿形成后，`mine/z-humanizer` 按中英文和 academic/journal/conference 域处理；
需要时才运行 `skills/anti-defensive-writing` 的中文或 English skill 做审计。两者
都保留事实、数字、引用 key、LaTeX 命令和术语，不代替 `paper-review` 的证据审查。

### aris + paper-review + paperreview

自动集成位置在 `research-pipeline` 管线内部：

```
paper-write 形成可审稿草稿后
    ↓ 自动触发
paper-review（绑定主张、证据、baseline、消融和外部引用）
    ↓ 投稿前自审记录
auto-review-loop（始于论文草稿路径，最多 4 轮）
    ↓ 评审报告
paper-claim-audit（校验声明一致性）
    ↓ 校验报告
citation-audit（校验引用）
    ↓
auto-paper-improvement-loop（按评审意见改进）
```

`paper-review` 来自根目录的 `skills/paper-review` 子模块，负责证据链和
相关工作核验；`paperreview`/`auto-review-loop` 负责独立评审循环。两者可以
串联使用，前者的 frontier notes 与问题定位可作为后续修改的输入，但不能
替代独立评审。

### aris + autofigure

自动集成位置在 `paper-writing` 管线内部：

```
paper-plan 完成后
    ↓ 自动触发
figure-spec（生成论文所需图表结构）
    ↓ SVG 图表
paper-illustration（生成 AI 插图）
    ↓ 插图
paper-compile（图表 + 文本 = 终稿）
```

### paperreview → autofigure

当评审意见指出图表问题时：

```
评审意见: "Figure 3 不够清晰"
    ↓ 自动触发
figure-spec 重新生成
    ↓ 或
paper-illustration 改进插图
    ↓
paper-compile 重新编译
```

### Branch-aware 全集成

使用 `aris/research-pipeline` 一键执行全部阶段：

```
aris/research-pipeline "topic description"
```

该命令按顺序执行：
1. Discover（aris）
2. Produce（aris）
3. Self-review（paper-review）
4. Review（paperreview）
5. Write (official LaTeX template + z-humanizer)
6. Self-review（paper-review + optional anti-defensive audit）
7. Polish（autofigure）
8. Close cycle integration branch and merge to configured base branch

## 输出清单

每次产出追加到研究项目根目录的唯一账本 [`MANIFEST.md`](../MANIFEST.md)，格式、状态记录和审稿登记规则均以该文件为准；其他说明文档只链接，不复制清单协议。

## 生命周期优先规则

上述能力图只表示能力关系，不是阶段账本。端到端记录以 [科研生命周期](research-lifecycle.md) 和 [Git/模型契约](lifecycle-runtime.md) 为准；实验对比/消融、预算与统计遵循 [执行契约](experiment-execution.md)。自动 audit 的上游 advisory 行为在本 scaffold 收紧为声明门控：FAIL 结果保留但不支持 claim。
