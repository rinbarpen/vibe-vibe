# Idea 验证、失败积累与上下文保真

本契约适用于直觉成题、自主发现及后续实验迭代；阶段树仍以 `lifecycle/defaults.json` 为准。不增加阶段 ID、后台执行器或审批系统。先检索，再核对思路与方法；先核对证据覆盖，再限定结论。

## 1. 新颖性：关键词只用于召回

在 `literature/position/novelty` 核验，在 `idea/hypotheses/comparison` 决策；方法细化后于 `idea/method/mechanism` 再核验一次。使用 `aris/research-lit` / `aris/novelty-check` 不免除本契约。

- 关键词、标题、任务或应用场景相同，只说明相关，不足以判定“已被做过”；措辞、领域或模块名不同，也不证明实质差异。
- 按问题同义词、机制描述、算法/目标函数等多路检索，并追查最相近工作的引用与被引。记录 query、日期、来源、覆盖范围和未取得全文的项目；未检出不等于首创。
- 以原始论文的方法节、公式、算法、实验协议与官方代码（若可取得）为证据，按下表比较最相近工作。摘要或二手总结仅作线索；缺少关键方法证据时保留 `unverified`，先补证据。

| 维度 | 必须对齐的内容 |
| --- | --- |
| 问题与条件 | 对象、假设、数据条件、可观察目标与适用边界 |
| 研究思路 | 核心解释、因果/信息路径、机制预测和干预逻辑 |
| 方法实现 | 关键算法步骤、目标函数、优化/推断方式、组件与输入输出 |
| 核心贡献 | 哪项机制或方法改变带来何种可测差异，是否只是命名、场景、规模或调参变化 |
| 验证路径 | 哪个对照、消融或反例能区分两个解释；实验方案是否仅复用已有套路 |

将逐项证据、原文定位、相同点、差异和未验证项写入既有 `refine-logs/contracts/NOVELTY.md`，可从 [模板](../templates/NOVELTY.md.example) 起草。每个候选关联稳定 hypothesis/claim ID 和 method revision。

采用可解释的判断，不设置关键词相似度或机械平均分阈值：

- `high_overlap`：研究思路与关键方法均高度重合，核心贡献/预测没有可辨识的实质差异；逐项说明对应关系。只换名字或领域仍可能属于此类。
- `related_but_distinct`：存在与核心贡献有关的机制或方法差异，写清差异为何重要及可区分实验。仅实现细节或指标波动不足以立此结论。
- `unverified`：关键来源或方法证据缺失、比较有争议；返回 `literature/position` 补证据，不判“已做过”或“新颖成立”。

`high_overlap` 进入既有候选比较，注明复现/扩展价值，不自动删除方向；是否继续沿用原 `idea/hypotheses/comparison` 人工决策门。方法发生实质修订后重做受影响的比较，不沿用旧版结论。

## 2. 实验：结论不得超过覆盖范围

在 `idea/method/claims` 和 design 阶段，区分核心研究假设、具体 method、实现/配置三个层次。每个 claim 预先写明：适用条件、预测、最低有效证据、反证条件、指标与判定阈值、必要对照/消融、提前停止条件。阈值由问题与协议决定，不发明通用成功率；实验后变更标准须留下旧标准、理由与版本。

分析时，将冻结矩阵与所有实际 run/attempt 逐项对照；在既有 `refine-logs/contracts/CLAIM_EVIDENCE.json` 为每个 claim 记录以下内容（是交接要求，不是新增运行时 schema）：

| 记录 | 内容 |
| --- | --- |
| 身份与范围 | hypothesis/claim ID、method revision、plan/config hash、数据/协议范围 |
| 计划与实跑 | 必需 run IDs、已完成且审计有效的 run IDs、失败/缺失/延期项与原因 |
| 证据与判断 | 原始文件及哈希、支持与反证、审计状态、混杂因素、局限 |
| 结论 | `supported` / `partially_supported` / `not_supported` / `inconclusive` / `refuted_in_scope`，并写理由 |
| 下一步 | 区分补实验、修实现、换 method、修订 hypothesis、暂停投入；标明尚未验证的条件 |

判断规则：

1. smoke/sanity、单个数据集、单个 seed、部分消融只支持相应局部结论。缺项、运行失败、资源耗尽或提前中止不自动构成反证；`deferred` 和 `not_applicable` 不计作已执行。
2. `not_supported` 表示当前有效结果未支持该 claim，不等于核心 idea 无效。method 不奏效、实现错误、协议问题、抽样波动与核心假设被反证须分开记录。
3. `refuted_in_scope` 必须核对预先定义的反证条件、必要证据、实现与协议有效性、混杂因素和独立科学审查；结论限于实际检验范围。不能仅靠部分实验推翻完整 idea。
4. 不要求盲目跑完全部矩阵：若预先定义的决定性反证/停止条件已由有效证据满足，可提前停止，列出已满足条件和未执行项；只否定该条件覆盖的 claim。若只是预算/收益原因停止，记录“停止投入、科学结论未定”，而非“idea 无效”。
5. 不支持、未定与反证都可完成分析阶段；阶段 `completed` 不是假设成立或全局否定。证据不足优先在已批准范围补齐；改方法/科学配置建立新 cycle，超预算或改变目标时走已有人工门，不无限试到正结果。

## 3. 失败方法也要沉淀研究启发

每个 attempt 无论成功、失败或取消，立即写原始日志；在 `analysis/interpretation/failures` 汇总到既有 `refine-logs/contracts/FAILURE_ANALYSIS.md`，从 [模板](../templates/FAILURE_ANALYSIS.md.example) 起草。

记录原假设与 method、预期与观察、run/attempt/commit/config/原始产物、失败层次与诊断证据、排除/尚未排除的解释、仍可能成立的机制、可复用组件、思想启迪与下一项可区分实验。没有可靠启发时明确写“暂无”，不强行编造。

“观测事实”“研究解释”“待验证启发”分栏；启发不进入论文的已验证结论。给启发稳定 ID、来源 attempt、适用前提、验证状态、后续 cycle/claim 链接与采纳/不采纳理由。新 cycle 回看相关条目后再设计；若重试相似方法，说明新增证据或条件变化，避免遗忘式重复。

## 4. 多轮修改后的上下文保真

独立 worktree 只隔离文件，不隔离错误前提。使用已有契约与 checkpoint 保持语义基线，不把滚动对话摘要或最新草稿当成事实源。

### 不同信息各归其位

- 目标/非目标/约束：既有 `QUESTION.md`、`CONSTRAINTS.md` 与已确认计划；将确认消息引用、版本和哈希留档。
- 研究基线：`HYPOTHESES.md`、`IDEA_DECISION.md`、`METHOD_SPEC.md`、`CLAIMS.json`；ID 稳定，实质修订注明旧/新版本、原因、证据与受影响依赖。
- 事实证据：`NOVELTY.md`、原始 run/attempt、`FAILURE_ANALYSIS.md` 与 `CLAIM_EVIDENCE.json`；事实、假设、启发、已反证和未知不混写。
- 进度/恢复点：已有生命周期事件与快照。交接记录含 cycle/stage/attempt、可信 commit、契约路径/哈希、有效决定、未完成项、负结果/启发索引、真实进程/产物状态及下一步。可使用 [实验日志模板](../templates/EXPERIMENT_LOG.md.example) 的交接段，不另建平行业务账本。

### 每次修订和恢复的检查

1. 迭代开始、会话压缩/切换、换模型/agent 或恢复中断前后，重新读取原始契约、当前源证据和最近有效 checkpoint，核对 ID、revision、hash 和真实运行状态；同时读取相关历史负结果，不只读上轮摘要。
2. 修改前记录“本轮改变什么、不改变什么、为什么、如何验证”；修改后对照已确认基线做语义 diff，核对目标、机制、claims、评价标准、结论强度、证据边界和预算是否漂移。
3. 活动阶段按现有 `revised` checkpoint 追加 old/new revision/hash、变更理由、影响范围及重验入口；已终结阶段或科学/配置变化按既有新 cycle 规则处理。旧稿、负结果、反证与决定保留，不用新摘要覆盖；已取代的结论标记 superseded 并链接新证据。
4. 需求或计划、方法、数据、指标、证据发生实质变化时，重验受影响的 novelty、设计、审查/审批和 Writing Plan resolved 要求，不能直接继承旧 pass/approval。目标/约束变化走已有人工门；技术修复由 AI 调查验证，不每轮重新访谈。
5. 向独立 reviewer 提供原始产物与当前契约，不提供“应当判成功/失败”的引导；按既有身份与 fresh-context 协议审查。
6. 发现上下文冲突或来源缺失时暂停依赖该判断的晋级/写作，从最后可信 checkpoint 与原始证据重建；保留当前 attempt，验证后再 promote。不可凭记忆补写批准、结果或“已完成”。

checkpoint 的文件/哈希检查验证结构与审查声明，不自动理解思路重合或证明科学判断正确。以上比较、结论边界与语义 diff 仍须由实际 research/reviewer 执行并留证；本次不新增模型调用或自动科学判定器。

## 5. 使用与兼容

双端入口均链接本契约；新项目的对应叶节点 acceptance 包含这些审查要求。现有 settings 不自动迁移；更新模板后先比对并显式合并受影响契约、保留本地路径/进展，重验其哈希与报告，不把旧审查当作已满足新要求。

- [Idea 入口与交接](intuit-to-idea.md)
- [实验运行、预算与证据资格](experiment-execution.md)
- [检查点、隔离迭代与恢复](lifecycle-runtime.md)
- [验证与迭代工作流 SVG](validation-workflow.svg) / [可编辑源](validation-workflow.json)

在 manifest 根目录或安装后的项目根目录生成与只读检查：

```bash
python3 scripts/render_idea_workflow.py --source references/validation-workflow.json --output references/validation-workflow.svg
python3 scripts/render_idea_workflow.py --source references/validation-workflow.json --output references/validation-workflow.svg --check
```

图描述规则，不代表实验已完成或判断已通过。
