# 生命周期阶段细化索引

`lifecycle/defaults.json` 的 `phase_details` 是机器可读阶段契约；本页说明每个大阶段的科学目的、进入条件、执行工作、产物、门禁、模型角色和回退路径。每个大阶段下的 `stages` 节点仍负责小阶段/小小阶段事件。

## 01 startup — 研究启动

- **目标**：将模糊意图变为有范围、资源、时间和成果定义的研究任务。
- **输入/产物**：研究意图、约束；`RESEARCH_PLAN.md`、目标与非目标、预算和里程碑。
- **门禁**：问题可一句话说明、至少有可验收产物、约束和模型绑定已登记。
- **回退**：问题变化回到 `startup/scope`，资源变化回到 `startup/roadmap`。

## 02 literature — 文献调研与问题定位

- **目标**：建立可追溯背景、研究空白、novelty 和 baseline 候选。
- **输入/产物**：研究计划和检索边界；文献综述、分类、检索日志、novelty report、`BASELINE_REVIEW.md` 初稿。
- **门禁**：原始来源、访问日期、筛选理由完整，论文报告值与复现值分开。
- **回退**：范围不清回到 `startup/scope`，证据不足回到 `literature/search`。

## 03 idea — Idea 与方法形成

- **目标**：形成可证伪机制假设、方法组件和核心 claims。
- **输入/产物**：文献空白与资源限制；`IDEA_REPORT.md`、`METHOD_SPEC.md`、research contract、claim map。
- **门禁**：每个 claim 有证伪路径，创新点不只是规模/调参，负结果解释预先登记。
- **回退**：新颖性问题回到 `literature/position`，可行性问题回到 `startup/roadmap`。

## 04 design — 对比与消融实验设计

- **目标**：把 claim 转成公平、完备、预算可执行的实验矩阵。
- **输入/产物**：方法 spec、claims、baseline 候选；`EXPERIMENT_PLAN.md`、`BASELINE_REVIEW.md`、`ABLATION_PLAN.md`、`EXPERIMENT_SETUP.json`、`RUN_MATRIX.json`。
- **门禁**：核心 claim、组件和混杂因素有覆盖或理由；baseline 版本/协议冻结；默认 `seeds=[42]`；无重复矩阵单元；预算和失败解释完整。
- **回退**：新组件回到 `idea/method`，baseline 变化回到 `literature/position`，预算变化回到 `startup/roadmap`。

## 05 execution — 实现与运行

- **目标**：按冻结矩阵生成可复现代码、运行、原始日志和结果。
- **输入/产物**：矩阵、环境 ledger、代码、数据、批准；`RUN_RECORDS.json`、`EXPERIMENT_LOG.md`、results、logs、queue state。
- **门禁**：环境/GT/评估器核实，代码审查和 sanity 通过，预算已批准，completed 必有结果和零退出码。
- **回退**：代码缺陷回到 `execution/implementation`，协议缺陷回到 `design/evaluation`，假设失败创建新 cycle 回到 `idea/hypotheses`。

## 06 analysis — 统计与论证

- **目标**：从原始结果得到可审计统计、失败解释和 claim 支持度。
- **输入/产物**：runs、结果、日志、claims；`EXPERIMENT_RESULTS.md`、统计 JSON/CSV、audit 报告、证据映射。
- **门禁**：不补零、不丢失败；配对条件一致；单 seed 不声称方差；FAIL 不成为无条件写作证据。
- **回退**：消融不足回到 `design/ablation`，协议问题回到 `design/evaluation`，unsupported claim 回到 `idea/method`。

## 07 writing — 论文组织与写作

- **目标**：将审计证据组织为可读、可评审、逐节点可追踪的论文。
- **输入/产物**：结果、审计、claims、outline、venue 规则；Writing Plan、解析计划、论文、图表和 review 报告。
- **门禁**：writer 只用 resolved node；强 claim 有合格证据；审批节点完成；节点级 review 通过或有修订计划。
- **回退**：证据变化回到 `analysis/interpretation`，叙事/贡献变化回到 `idea/method`。

## 08 internal-review — 内部评审与完善

- **目标**：投稿前独立检查科学性、证据、表达和可复现性。
- **输入/产物**：完整 draft、resolved plan、结果、venue checklist；内部评审、修订清单、补实验计划和投稿版。
- **门禁**：blocking 问题关闭或解释；新增实验重新过 design/budget/checkpoint；匿名、格式和附件通过。
- **回退**：补实验回到 design/execution，重大改写回到 `writing/plan`。

## 09 submission — 投稿

- **目标**：完成 venue 合规检查、作者确认、实际提交和回执留档。
- **输入/产物**：投稿稿件、规则、作者/附件；提交包、检查清单、回执和 submission ID。
- **门禁**：版本清单/hash、作者确认、平台回执可读取；正式提交前保留人工确认。
- **回退**：格式或材料问题回到 `internal-review/revision`。

## 10 revision — 外审、返修与转投

- **目标**：把意见变成逐条响应、可验证修订和必要补实验。
- **输入/产物**：reviewer comments、提交稿、证据和 deadline；response matrix、修订稿、补实验、回复、revision receipt。
- **门禁**：每条意见有响应；新增结论有审计证据；回复对应正确版本；实际提交有回执。
- **回退**：新 claim 回到 idea，新增实验回到 design，新稿回到 writing；拒稿转投建立新 submission ID。

## 11 acceptance — 录用、终稿与归档

- **目标**：以实际录用通知为依据完成 camera-ready、校样和可复现归档。
- **输入/产物**：录用通知、accepted manuscript、出版清单、代码/数据索引；录用记录、终稿、校样、归档索引和最终 MANIFEST。
- **门禁**：录用通知与稿件对应；camera-ready 有提交证据；大文件可读取且 hash 正确；最终 claims 与 accepted text 对齐。
- **回退**：校样问题回到 `acceptance/final`，内容变化创建新的 revision。

## 跨阶段固定规则

每个大/小/小小阶段都记录 `started`、终态和下一步，并按检查点提交 Git。模型按角色路由：研究 GPT-6 Pro、规划 GPT-6.1 Sol high、执行 Opus 5.5 high、写作 Opus 5.5 high。模型不可用时记录 `blocked_model_unavailable`，不静默替换。阶段完成不代表科学结论为正；所有失败、负结果、暂停和 skipped 都留档。
