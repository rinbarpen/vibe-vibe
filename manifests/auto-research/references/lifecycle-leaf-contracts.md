# 小阶段与小小阶段执行契约

本页由 lifecycle/defaults.json 生成。71 个叶节点对应具体操作，24 个父节点聚合交付。

## 文件与兼容边界

- refine-logs/contracts/ 下的文件是交接证据，可引用已有真实项目产物及其哈希，不要求重建已有数据或正文。Markdown/JSON 路径分别对应叙述与结构化记录。
- 输入清单是所需证据，不是严格执行顺序：例如启动时可先建立作者意向，正式作者确认发生在投稿前；遇到尚未生成的输入应阻塞或由项目显式调整契约。
- 默认新项目在叶节点 completed 时检查声明输出、当前契约哈希和逐项审查记录；检查输入文件内容的科学真实性仍由登记的审查者负责。
- 老项目 settings 不自动覆盖。升级需显式合并契约、调整本地路径、复核并启用 enforce_stage_contracts；关闭该开关须留档，视为旧兼容模式而非科学验收通过。
- 图表生产、模型调用、远程实验执行和真实venue模板仍需各自后端接入；契约不代表这些调用已实现。

## startup/scope/question

- 操作：界定对象、问题、可观察结果与非目标
- 角色：research
- 输入：`USER_BRIEF.md`
- 输出：`refine-logs/contracts/QUESTION.md`
- 验收：问题包含对象、可证伪目标和排除范围
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/startup--scope--question.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "startup/scope"}

## startup/scope/constraints

- 操作：登记数据、伦理、计算、时间和访问限制
- 角色：planner
- 输入：`refine-logs/contracts/QUESTION.md`
- 输出：`refine-logs/contracts/CONSTRAINTS.md`
- 验收：每个限制有来源、负责人和影响
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/startup--scope--constraints.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "startup/scope"}

## startup/roadmap/milestones

- 操作：安排可验收里程碑、依赖与停止条件
- 角色：planner
- 输入：`refine-logs/contracts/QUESTION.md`, `refine-logs/contracts/CONSTRAINTS.md`
- 输出：`refine-logs/contracts/MILESTONES.md`
- 验收：每个里程碑有产物、期限、决策人和退出条件
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/startup--roadmap--milestones.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "startup/roadmap"}

## startup/roadmap/budget

- 操作：估计计算、存储、人工成本和预算上限
- 角色：planner
- 输入：`refine-logs/contracts/CONSTRAINTS.md`, `refine-logs/contracts/MILESTONES.md`
- 输出：`refine-logs/contracts/BUDGET.md`
- 验收：估计依据、币种、资源上限和审批边界完整
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/startup--roadmap--budget.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "startup/roadmap"}

## literature/search/queries

- 操作：拆解概念同义词、检索源和时间范围
- 角色：research
- 输入：`refine-logs/contracts/QUESTION.md`
- 输出：`refine-logs/contracts/SEARCH_PROTOCOL.md`
- 验收：检索式、数据库、纳排标准和截止日期可复用
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/literature--search--queries.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "literature/search"}

## literature/search/screening

- 操作：检索原始来源、去重并逐篇记录纳排
- 角色：executor
- 输入：`refine-logs/contracts/SEARCH_PROTOCOL.md`
- 输出：`refine-logs/contracts/SCREENING.json`
- 验收：每条记录含来源、检索日期、版本及纳排理由
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/literature--search--screening.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "literature/search"}

## literature/position/taxonomy

- 操作：按问题、假设、数据、方法与评估协议分类
- 角色：research
- 输入：`refine-logs/contracts/SCREENING.json`
- 输出：`refine-logs/contracts/TAXONOMY.md`
- 验收：关键分类均有来源且区别报告值与复现值
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/literature--position--taxonomy.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "literature/position"}

## literature/position/gap

- 操作：比较已有证据与未解决问题
- 角色：research
- 输入：`refine-logs/contracts/TAXONOMY.md`
- 输出：`refine-logs/contracts/GAP.md`
- 验收：gap有多来源支持并记录反例和检索局限
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/literature--position--gap.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "literature/position"}

## literature/position/novelty

- 操作：对最相近工作逐项核对机制与贡献差异
- 角色：research
- 输入：`refine-logs/contracts/GAP.md`, `refine-logs/contracts/TAXONOMY.md`
- 输出：`refine-logs/contracts/NOVELTY.md`
- 验收：近邻方法、重合点、差异及不确定性有引用；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；关键词仅用于召回；以原始方法证据逐项比较研究思路、核心机制、关键方法与贡献，给出重合/差异/未验证结论；研究思路与关键方法均高度重合才判high_overlap；缺证据保留unverified，不以未检出证明首创
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/literature--position--novelty.json`
- 回退：{"invalid_input": "startup/scope", "failed_check": "literature/position"}

## idea/hypotheses/candidates

- 操作：提出竞争解释、可测预测和否定条件
- 角色：research
- 输入：`refine-logs/contracts/GAP.md`, `refine-logs/contracts/NOVELTY.md`, `refine-logs/contracts/CONSTRAINTS.md`
- 输出：`refine-logs/contracts/HYPOTHESES.md`
- 验收：每个候选含预测、反证和最小验证实验；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；候选以稳定hypothesis/claim ID关联NOVELTY中的思路与方法对照，区分核心假设、method及实现配置
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/idea--hypotheses--candidates.json`
- 回退：{"invalid_input": "literature/position", "failed_check": "idea/hypotheses"}

## idea/hypotheses/comparison

- 操作：按新颖性、可证伪性、成本和风险选择方案
- 角色：planner
- 输入：`refine-logs/contracts/HYPOTHESES.md`, `refine-logs/contracts/BUDGET.md`
- 输出：`refine-logs/contracts/IDEA_DECISION.md`
- 验收：保留淘汰理由及关键假设未验证项；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；淘汰或保留理由引用思路与关键方法的实质对照，不以关键词命中判已做过；高度重合仍记录复现或扩展价值
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/idea--hypotheses--comparison.json`
- 回退：{"invalid_input": "literature/position", "failed_check": "idea/hypotheses"}

## idea/method/mechanism

- 操作：明确输入输出、数学定义、算法步骤和假设
- 角色：research
- 输入：`refine-logs/contracts/IDEA_DECISION.md`
- 输出：`refine-logs/contracts/METHOD_SPEC.md`
- 验收：公式符号、张量接口和伪代码一致；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；method修订后重验思路与关键方法的重合及贡献差异，保留旧新版本和未验证项
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/idea--method--mechanism.json`
- 回退：{"invalid_input": "literature/position", "failed_check": "idea/method"}

## idea/method/components

- 操作：拆分组件接口、开关、依赖与替代实现
- 角色：planner
- 输入：`refine-logs/contracts/METHOD_SPEC.md`
- 输出：`refine-logs/contracts/COMPONENTS.json`
- 验收：每个组件有稳定ID、接口和可实施干预
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/idea--method--components.json`
- 回退：{"invalid_input": "literature/position", "failed_check": "idea/method"}

## idea/method/claims

- 操作：登记主张、证伪阈值和所需证据
- 角色：research
- 输入：`refine-logs/contracts/METHOD_SPEC.md`, `refine-logs/contracts/COMPONENTS.json`
- 输出：`refine-logs/contracts/CLAIMS.json`
- 验收：所有核心claim都有证据类型和失败解释；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；逐claim预先登记最低有效证据、适用范围、反证阈值、必要对照和提前停止条件；区分hypothesis与method失败
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/idea--method--claims.json`
- 回退：{"invalid_input": "literature/position", "failed_check": "idea/method"}

## design/baselines/search

- 操作：联网刷新标准、最新强方法和最相近方法
- 角色：executor
- 输入：`refine-logs/contracts/NOVELTY.md`, `refine-logs/contracts/CLAIMS.json`
- 输出：`refine-logs/contracts/BASELINE_SEARCH.json`
- 验收：原始链接、检索时间、查询词和代码来源齐全
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/design--baselines--search.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/baselines"}

## design/baselines/selection

- 操作：按相关性、可复现性和资源选择基线
- 角色：research
- 输入：`refine-logs/contracts/BASELINE_SEARCH.json`, `refine-logs/contracts/BUDGET.md`
- 输出：`refine-logs/contracts/BASELINE_SELECTION.json`
- 验收：纳排理由完整且不混淆文献值与实跑值
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/design--baselines--selection.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/baselines"}

## design/baselines/protocol

- 操作：冻结数据split、版本、调参预算和评估器
- 角色：planner
- 输入：`refine-logs/contracts/BASELINE_SELECTION.json`, `refine-logs/contracts/CONSTRAINTS.md`
- 输出：`refine-logs/contracts/BASELINE_PROTOCOL.json`
- 验收：各方法公平性差异明确且引用版本可定位
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/design--baselines--protocol.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/baselines"}

## design/ablation/decomposition

- 操作：识别组件、训练目标、资源和潜在混杂
- 角色：research
- 输入：`refine-logs/contracts/COMPONENTS.json`, `refine-logs/contracts/CLAIMS.json`
- 输出：`refine-logs/contracts/ABLATION_FACTORS.json`
- 验收：每项变化对应机制假设和控制变量
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/design--ablation--decomposition.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/ablation"}

## design/ablation/coverage

- 操作：覆盖移除、增加、替代、交互及边界实验
- 角色：planner
- 输入：`refine-logs/contracts/ABLATION_FACTORS.json`, `refine-logs/contracts/CLAIMS.json`
- 输出：`refine-logs/contracts/ABLATION_COVERAGE.json`
- 验收：每个claim和因素为covered或有延期/不适用理由；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；覆盖矩阵关联claim最低证据与反证条件；缺失、延期和不适用不冒充已执行
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/design--ablation--coverage.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/ablation"}

## design/ablation/matrix

- 操作：选择有科学意义的组合并估算成本
- 角色：planner
- 输入：`refine-logs/contracts/ABLATION_COVERAGE.json`, `refine-logs/contracts/BASELINE_PROTOCOL.json`
- 输出：`refine-logs/contracts/ABLATION_MATRIX.json`
- 验收：组合唯一、参考明确且交互不盲目穷举
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/design--ablation--matrix.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/ablation"}

## design/evaluation/metrics

- 操作：定义指标公式、方向、聚合单位与选择准则
- 角色：research
- 输入：`refine-logs/contracts/CLAIMS.json`, `refine-logs/contracts/BASELINE_PROTOCOL.json`
- 输出：`refine-logs/contracts/METRIC_PROTOCOL.json`
- 验收：主次指标、缺失值规则和测试集使用边界明确
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/design--evaluation--metrics.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/evaluation"}

## design/evaluation/seeds

- 操作：默认使用单seed并配置多seed配对策略
- 角色：planner
- 输入：`refine-logs/contracts/METRIC_PROTOCOL.json`, `refine-logs/contracts/ABLATION_MATRIX.json`
- 输出：`refine-logs/contracts/SEED_PLAN.json`
- 验收：seed列表唯一且区分数据抽样与训练随机性
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/design--evaluation--seeds.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/evaluation"}

## design/evaluation/budget

- 操作：合并实验设置、估算全矩阵资源和审批范围
- 角色：planner
- 输入：`refine-logs/contracts/SEED_PLAN.json`, `refine-logs/contracts/ABLATION_MATRIX.json`, `refine-logs/contracts/BUDGET.md`
- 输出：`refine-logs/contracts/EXPERIMENT_SETUP.json`
- 验收：矩阵覆盖与预算对应且未批准任务不执行
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/design--evaluation--budget.json`
- 回退：{"invalid_input": "idea/method", "failed_check": "design/evaluation"}

## execution/prepare/environment

- 操作：验证依赖、设备、驱动及最小计算操作
- 角色：executor
- 输入：`refine-logs/contracts/EXPERIMENT_SETUP.json`
- 输出：`refine-logs/contracts/ENVIRONMENT.json`
- 验收：环境版本、真实设备输出和依赖锁可追踪
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--prepare--environment.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/prepare"}

## execution/prepare/data

- 操作：核验数据来源、标注、split和泄漏风险
- 角色：executor
- 输入：`refine-logs/contracts/BASELINE_PROTOCOL.json`, `refine-logs/contracts/CONSTRAINTS.md`
- 输出：`refine-logs/contracts/DATA_MANIFEST.json`
- 验收：数据哈希、划分ID、访问许可和泄漏检查完整
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--prepare--data.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/prepare"}

## execution/prepare/evaluator

- 操作：以已知答案和边界样本验证评估器
- 角色：executor
- 输入：`refine-logs/contracts/METRIC_PROTOCOL.json`, `refine-logs/contracts/DATA_MANIFEST.json`
- 输出：`refine-logs/contracts/EVALUATOR_CHECK.json`
- 验收：固定输入输出、错误案例与指标方向验证通过
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--prepare--evaluator.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/prepare"}

## execution/implementation/code

- 操作：实现方法、配置开关与baseline接口
- 角色：executor
- 输入：`refine-logs/contracts/METHOD_SPEC.md`, `refine-logs/contracts/COMPONENTS.json`, `refine-logs/contracts/ENVIRONMENT.json`
- 输出：`refine-logs/contracts/IMPLEMENTATION.md`
- 验收：代码revision、入口命令和组件映射完整
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--implementation--code.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/implementation"}

## execution/implementation/review

- 操作：独立上下文检查实现、评估与数据泄漏
- 角色：executor
- 输入：`refine-logs/contracts/IMPLEMENTATION.md`, `refine-logs/contracts/METHOD_SPEC.md`
- 输出：`refine-logs/contracts/CODE_REVIEW.json`
- 验收：审查者身份、发现、严重度和关闭证据完整
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--implementation--review.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/implementation"}

## execution/implementation/sanity

- 操作：检查小样本过拟合、梯度、形状和最小全链路
- 角色：executor
- 输入：`refine-logs/contracts/CODE_REVIEW.json`, `refine-logs/contracts/EVALUATOR_CHECK.json`
- 输出：`refine-logs/contracts/SANITY.json`
- 验收：每种实现的实际命令、退出码与判定阈值齐全
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--implementation--sanity.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/implementation"}

## execution/runs/approval

- 操作：对冻结计划核对预算并取得运行批准
- 角色：planner
- 输入：`refine-logs/contracts/SANITY.json`, `refine-logs/contracts/EXPERIMENT_SETUP.json`
- 输出：`refine-logs/contracts/BUDGET_APPROVAL.json`
- 验收：plan hash、批准人、时间和资源上限一致
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/execution--runs--approval.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/runs"}

## execution/runs/baseline

- 操作：运行冻结baseline并保留每次attempt
- 角色：executor
- 输入：`refine-logs/contracts/BUDGET_APPROVAL.json`, `refine-logs/contracts/BASELINE_PROTOCOL.json`
- 输出：`refine-logs/contracts/BASELINE_RUNS.json`
- 验收：run ID、seed、revision、退出码和结果引用齐全
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--runs--baseline.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/runs"}

## execution/runs/main

- 操作：按冻结主实验矩阵执行和监控
- 角色：executor
- 输入：`refine-logs/contracts/BUDGET_APPROVAL.json`, `refine-logs/contracts/IMPLEMENTATION.md`
- 输出：`refine-logs/contracts/MAIN_RUNS.json`
- 验收：实际进程、配置哈希、成本与结果可核查
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--runs--main.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/runs"}

## execution/runs/ablation

- 操作：执行消融组合并核对唯一变化
- 角色：executor
- 输入：`refine-logs/contracts/BUDGET_APPROVAL.json`, `refine-logs/contracts/ABLATION_MATRIX.json`
- 输出：`refine-logs/contracts/ABLATION_RUNS.json`
- 验收：控制条件一致且失败重试不冒充新seed
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--runs--ablation.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/runs"}

## execution/runs/collection

- 操作：收集所有成功、失败和未完成运行
- 角色：executor
- 输入：`refine-logs/contracts/BASELINE_RUNS.json`, `refine-logs/contracts/MAIN_RUNS.json`, `refine-logs/contracts/ABLATION_RUNS.json`
- 输出：`refine-logs/contracts/RUN_RECORDS.json`
- 验收：每个矩阵单元有状态且文件哈希可核验
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/execution--runs--collection.json`
- 回退：{"invalid_input": "design/evaluation", "failed_check": "execution/runs"}

## analysis/statistics/integrity

- 操作：检查缺失、重复、配置漂移和评估协议
- 角色：executor
- 输入：`refine-logs/contracts/RUN_RECORDS.json`, `refine-logs/contracts/EXPERIMENT_SETUP.json`
- 输出：`refine-logs/contracts/RESULT_INTEGRITY.json`
- 验收：不补零、不挑旧高分attempt、不静默删失败
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/analysis--statistics--integrity.json`
- 回退：{"invalid_input": "execution/runs", "failed_check": "analysis/statistics"}

## analysis/statistics/aggregation

- 操作：按数据、配置和seed聚合指标
- 角色：executor
- 输入：`refine-logs/contracts/RESULT_INTEGRITY.json`, `refine-logs/contracts/RUN_RECORDS.json`
- 输出：`refine-logs/contracts/EXPERIMENT_STATISTICS.json`
- 验收：单seed标准差为空、多seed用样本SD且保留原始值
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/analysis--statistics--aggregation.json`
- 回退：{"invalid_input": "execution/runs", "failed_check": "analysis/statistics"}

## analysis/statistics/comparison

- 操作：计算协议匹配的配对差值并选择统计方法
- 角色：research
- 输入：`refine-logs/contracts/EXPERIMENT_STATISTICS.json`, `refine-logs/contracts/METRIC_PROTOCOL.json`
- 输出：`refine-logs/contracts/COMPARISONS.json`
- 验收：配对单位明确、方向正确、检验假设有依据
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/analysis--statistics--comparison.json`
- 回退：{"invalid_input": "execution/runs", "failed_check": "analysis/statistics"}

## analysis/interpretation/ablation

- 操作：区分移除效应、顺序增益和交互
- 角色：research
- 输入：`refine-logs/contracts/COMPARISONS.json`, `refine-logs/contracts/ABLATION_COVERAGE.json`
- 输出：`refine-logs/contracts/ABLATION_INTERPRETATION.md`
- 验收：结论不超出控制条件并解释负结果
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/analysis--interpretation--ablation.json`
- 回退：{"invalid_input": "execution/runs", "failed_check": "analysis/interpretation"}

## analysis/interpretation/failures

- 操作：区分工程失败、方法失效和抽样波动
- 角色：research
- 输入：`refine-logs/contracts/RUN_RECORDS.json`, `refine-logs/contracts/COMPARISONS.json`
- 输出：`refine-logs/contracts/FAILURE_ANALYSIS.md`
- 验收：案例选取规则、失效边界和后续行动明确；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；区分实现、协议、抽样、method与hypothesis失败；部分实验不佳不等于整体idea无效；保留原始attempt与负结果，分列事实、解释和待验证启发，登记可复用机制及后续验证/cycle引用或明确暂无启发
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/analysis--interpretation--failures.json`
- 回退：{"invalid_input": "execution/runs", "failed_check": "analysis/interpretation"}

## analysis/interpretation/claims

- 操作：逐项判定支持、部分支持或不支持
- 角色：research
- 输入：`refine-logs/contracts/CLAIMS.json`, `refine-logs/contracts/COMPARISONS.json`, `refine-logs/contracts/FAILURE_ANALYSIS.md`
- 输出：`refine-logs/contracts/CLAIM_EVIDENCE.json`
- 验收：每个结论引用run与证据且保留反证；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；逐claim对照冻结矩阵与实跑有效证据，列明已测范围、失败/缺失/延期项和结论边界；不足时保留inconclusive；refuted_in_scope须满足预设反证条件并排查实现/协议与混杂；决定性证据可提前停止，资源中止不等于idea无效
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/analysis--interpretation--claims.json`
- 回退：{"invalid_input": "execution/runs", "failed_check": "analysis/interpretation"}

## analysis/interpretation/audit

- 操作：独立核验统计、归因和选择性报告
- 角色：research
- 输入：`refine-logs/contracts/CLAIM_EVIDENCE.json`, `refine-logs/contracts/RESULT_INTEGRITY.json`
- 输出：`refine-logs/contracts/SCIENTIFIC_AUDIT.json`
- 验收：审查身份和阻断项明确且不将缺席视为通过；产物包含来源/版本与实际执行记录；示例数据和未完成工作明确标注；独立核对覆盖与结论强度、提前停止依据及失败启发的未验证标记，不从部分实验或method失败推出idea全局无效
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/analysis--interpretation--audit.json`
- 回退：{"invalid_input": "execution/runs", "failed_check": "analysis/interpretation"}

## writing/plan/story

- 操作：围绕合格证据安排贡献与论证顺序
- 角色：writer
- 输入：`refine-logs/contracts/CLAIM_EVIDENCE.json`, `refine-logs/contracts/SCIENTIFIC_AUDIT.json`
- 输出：`refine-logs/contracts/STORY.md`
- 验收：贡献不超过证据支持度并保留局限
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/writing--plan--story.json`
- 回退：{"invalid_input": "analysis/interpretation", "failed_check": "writing/plan"}

## writing/plan/outline

- 操作：定义章节、标题与图表承载的论点
- 角色：planner
- 输入：`refine-logs/contracts/STORY.md`, `refine-logs/contracts/METHOD_SPEC.md`
- 输出：`refine-logs/contracts/OUTLINE.md`
- 验收：每节有问题、核心信息和证据来源
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/writing--plan--outline.json`
- 回退：{"invalid_input": "analysis/interpretation", "failed_check": "writing/plan"}

## writing/plan/writing-plan

- 操作：创建校验解析writing plan并生成审批视图
- 角色：planner
- 输入：`refine-logs/contracts/OUTLINE.md`, `refine-logs/contracts/CLAIM_EVIDENCE.json`
- 输出：`refine-logs/contracts/WRITING_PLAN.md`
- 验收：resolved节点无继承标记且审批与当前要求匹配
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/writing--plan--writing-plan.json`
- 回退：{"invalid_input": "analysis/interpretation", "failed_check": "writing/plan"}

## writing/draft/methods

- 操作：按resolved节点写方法并核对实现
- 角色：writer
- 输入：`refine-logs/contracts/WRITING_PLAN.md`, `refine-logs/contracts/METHOD_SPEC.md`, `refine-logs/contracts/ENVIRONMENT.json`
- 输出：`refine-logs/contracts/METHODS_REVIEW.md`
- 验收：数学、伪代码、实现版本与复现实验条件一致
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/writing--draft--methods.json`
- 回退：{"invalid_input": "analysis/interpretation", "failed_check": "writing/draft"}

## writing/draft/results

- 操作：从冻结统计写结果并引用真实图表
- 角色：writer
- 输入：`refine-logs/contracts/WRITING_PLAN.md`, `refine-logs/contracts/EXPERIMENT_STATISTICS.json`, `refine-logs/contracts/CLAIM_EVIDENCE.json`
- 输出：`refine-logs/contracts/RESULTS_REVIEW.md`
- 验收：正文数字、单位、样本量与来源完全对应
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/writing--draft--results.json`
- 回退：{"invalid_input": "analysis/interpretation", "failed_check": "writing/draft"}

## writing/draft/discussion

- 操作：解释机制、替代解释、局限和适用边界
- 角色：writer
- 输入：`refine-logs/contracts/WRITING_PLAN.md`, `refine-logs/contracts/FAILURE_ANALYSIS.md`, `refine-logs/contracts/CLAIM_EVIDENCE.json`
- 输出：`refine-logs/contracts/DISCUSSION_REVIEW.md`
- 验收：区分观察与推断且不补写无证据结论
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/writing--draft--discussion.json`
- 回退：{"invalid_input": "analysis/interpretation", "failed_check": "writing/draft"}

## writing/draft/figures

- 操作：生成逐图逐表规格、原生LaTeX与可编辑图源
- 角色：executor
- 输入：`refine-logs/contracts/WRITING_PLAN.md`, `refine-logs/contracts/EXPERIMENT_STATISTICS.json`
- 输出：`refine-logs/contracts/VISUAL_ASSET_MANIFEST.json`
- 验收：数据到单元格/面板可追踪且编译尺寸和标记正确
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/writing--draft--figures.json`
- 回退：{"invalid_input": "analysis/interpretation", "failed_check": "writing/draft"}

## writing/draft/citations

- 操作：核对bib身份、原始来源与引用支撑关系
- 角色：writer
- 输入：`refine-logs/contracts/SCREENING.json`, `refine-logs/contracts/WRITING_PLAN.md`
- 输出：`refine-logs/contracts/CITATION_AUDIT.json`
- 验收：无虚构引用、缺失键或张冠李戴的结论
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/writing--draft--citations.json`
- 回退：{"invalid_input": "analysis/interpretation", "failed_check": "writing/draft"}

## internal-review/review/scientific

- 操作：独立评审问题价值、创新性和因果归因
- 角色：research
- 输入：`refine-logs/contracts/SCIENTIFIC_AUDIT.json`, `refine-logs/contracts/CLAIM_EVIDENCE.json`
- 输出：`refine-logs/contracts/SCIENTIFIC_REVIEW.json`
- 验收：每个问题含严重度、定位、证据和关闭条件
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/internal-review--review--scientific.json`
- 回退：{"invalid_input": "writing/draft", "failed_check": "internal-review/review"}

## internal-review/review/evidence

- 操作：核验正文、图表与原始证据一致性
- 角色：research
- 输入：`refine-logs/contracts/RUN_RECORDS.json`, `refine-logs/contracts/VISUAL_ASSET_MANIFEST.json`
- 输出：`refine-logs/contracts/EVIDENCE_REVIEW.json`
- 验收：关键数字可回溯且不把格式通过当科学通过
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/internal-review--review--evidence.json`
- 回退：{"invalid_input": "writing/draft", "failed_check": "internal-review/review"}

## internal-review/review/presentation

- 操作：检查结构、可读性、图表、匿名性与交叉引用
- 角色：writer
- 输入：`refine-logs/contracts/WRITING_PLAN.md`, `refine-logs/contracts/CITATION_AUDIT.json`
- 输出：`refine-logs/contracts/PRESENTATION_REVIEW.json`
- 验收：编译日志、断链、溢出和匿名泄漏均有处置
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/internal-review--review--presentation.json`
- 回退：{"invalid_input": "writing/draft", "failed_check": "internal-review/review"}

## internal-review/revision/experiments

- 操作：将补实验要求转为新设计与预算请求
- 角色：planner
- 输入：`refine-logs/contracts/SCIENTIFIC_REVIEW.json`, `refine-logs/contracts/EVIDENCE_REVIEW.json`
- 输出：`refine-logs/contracts/SUPPLEMENT_EXPERIMENT_PLAN.json`
- 验收：新增实验关联意见ID并重新进入design而非直接执行
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/internal-review--revision--experiments.json`
- 回退：{"invalid_input": "writing/draft", "failed_check": "internal-review/revision"}

## internal-review/revision/rewrite

- 操作：只修订不合格节点并复审
- 角色：writer
- 输入：`refine-logs/contracts/PRESENTATION_REVIEW.json`, `refine-logs/contracts/SCIENTIFIC_REVIEW.json`
- 输出：`refine-logs/contracts/REVISION_LOG.md`
- 验收：变更定位、要求失效审批和复审结果可追踪
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/internal-review--revision--rewrite.json`
- 回退：{"invalid_input": "writing/draft", "failed_check": "internal-review/revision"}

## internal-review/revision/submission-check

- 操作：检查阻断问题、格式和附件闭环
- 角色：planner
- 输入：`refine-logs/contracts/REVISION_LOG.md`, `refine-logs/contracts/EVIDENCE_REVIEW.json`
- 输出：`refine-logs/contracts/SUBMISSION_CHECK.json`
- 验收：blocking项已关闭或有明确批准的处置
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/internal-review--revision--submission-check.json`
- 回退：{"invalid_input": "writing/draft", "failed_check": "internal-review/revision"}

## submission/prepare/venue

- 操作：读取目标venue当年官方要求并冻结模板
- 角色：planner
- 输入：`refine-logs/contracts/SUBMISSION_CHECK.json`
- 输出：`refine-logs/contracts/VENUE_SNAPSHOT.json`
- 验收：来源、访问时间、track、截止日期与时区明确
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/submission--prepare--venue.json`
- 回退：{"invalid_input": "internal-review/revision", "failed_check": "submission/prepare"}

## submission/prepare/materials

- 操作：编译正文补充材料并检查匿名与文件清单
- 角色：executor
- 输入：`refine-logs/contracts/VENUE_SNAPSHOT.json`, `refine-logs/contracts/VISUAL_ASSET_MANIFEST.json`
- 输出：`refine-logs/contracts/SUBMISSION_MANIFEST.json`
- 验收：文件哈希、页数、字体嵌入和匿名性检查齐全
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/submission--prepare--materials.json`
- 回退：{"invalid_input": "internal-review/revision", "failed_check": "submission/prepare"}

## submission/prepare/authors

- 操作：确认作者顺序、贡献、声明与提交权限
- 角色：planner
- 输入：`refine-logs/contracts/SUBMISSION_MANIFEST.json`
- 输出：`refine-logs/contracts/AUTHOR_CONFIRMATION.json`
- 验收：全部必要作者确认绑定到当前稿件版本
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/submission--prepare--authors.json`
- 回退：{"invalid_input": "internal-review/revision", "failed_check": "submission/prepare"}

## submission/submit/approval

- 操作：请求正式提交的明确人工批准
- 角色：planner
- 输入：`refine-logs/contracts/AUTHOR_CONFIRMATION.json`, `refine-logs/contracts/SUBMISSION_MANIFEST.json`
- 输出：`refine-logs/contracts/SUBMISSION_APPROVAL.json`
- 验收：批准对象、版本哈希和实际动作范围一致
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/submission--submit--approval.json`
- 回退：{"invalid_input": "internal-review/revision", "failed_check": "submission/submit"}

## submission/submit/receipt

- 操作：由获准操作者提交并保存真实回执
- 角色：executor
- 输入：`refine-logs/contracts/SUBMISSION_APPROVAL.json`
- 输出：`refine-logs/contracts/SUBMISSION_RECEIPT.json`
- 验收：回执、submission ID与提交文件版本对应
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/submission--submit--receipt.json`
- 回退：{"invalid_input": "internal-review/revision", "failed_check": "submission/submit"}

## revision/decision/receipt

- 操作：登记编辑决定、审稿意见和截止时间
- 角色：planner
- 输入：`refine-logs/contracts/SUBMISSION_RECEIPT.json`
- 输出：`refine-logs/contracts/EDITOR_DECISION.json`
- 验收：原始意见、稿件ID、轮次和时区可核实
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/revision--decision--receipt.json`
- 回退：{"invalid_input": "revision/decision", "failed_check": "revision/decision"}

## revision/decision/response-matrix

- 操作：逐条拆解意见并关联证据与稿件位置
- 角色：planner
- 输入：`refine-logs/contracts/EDITOR_DECISION.json`
- 输出：`refine-logs/contracts/RESPONSE_MATRIX.json`
- 验收：每条意见有稳定ID且无遗漏合并
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/revision--decision--response-matrix.json`
- 回退：{"invalid_input": "revision/decision", "failed_check": "revision/decision"}

## revision/decision/strategy

- 操作：决定接受、澄清、反驳或补实验的策略
- 角色：research
- 输入：`refine-logs/contracts/RESPONSE_MATRIX.json`, `refine-logs/contracts/BUDGET.md`
- 输出：`refine-logs/contracts/REVISION_STRATEGY.md`
- 验收：每项策略有科学依据、成本、责任人与期限
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/revision--decision--strategy.json`
- 回退：{"invalid_input": "revision/decision", "failed_check": "revision/decision"}

## revision/revise/experiments

- 操作：为外审补实验建立新周期设计
- 角色：planner
- 输入：`refine-logs/contracts/REVISION_STRATEGY.md`, `refine-logs/contracts/RESPONSE_MATRIX.json`
- 输出：`refine-logs/contracts/REVISION_EXPERIMENT_PLAN.json`
- 验收：不绕过协议预算审批且每项对应意见ID
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/revision--revise--experiments.json`
- 回退：{"invalid_input": "revision/decision", "failed_check": "revision/revise"}

## revision/revise/manuscript

- 操作：逐节点修稿并生成版本差异
- 角色：writer
- 输入：`refine-logs/contracts/REVISION_STRATEGY.md`, `refine-logs/contracts/CLAIM_EVIDENCE.json`
- 输出：`refine-logs/contracts/MANUSCRIPT_CHANGES.json`
- 验收：每处修改关联意见及证据，新增claim重新审计
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/revision--revise--manuscript.json`
- 回退：{"invalid_input": "revision/decision", "failed_check": "revision/revise"}

## revision/revise/response

- 操作：写逐条回复并指向准确页行或节点
- 角色：writer
- 输入：`refine-logs/contracts/MANUSCRIPT_CHANGES.json`, `refine-logs/contracts/RESPONSE_MATRIX.json`
- 输出：`refine-logs/contracts/RESPONSE_LETTER.md`
- 验收：回复与最终修订稿一致且未完成事项不称完成
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/revision--revise--response.json`
- 回退：{"invalid_input": "revision/decision", "failed_check": "revision/revise"}

## revision/revise/resubmit

- 操作：确认返修版本并经批准重投
- 角色：executor
- 输入：`refine-logs/contracts/RESPONSE_LETTER.md`, `refine-logs/contracts/SUBMISSION_MANIFEST.json`
- 输出：`refine-logs/contracts/REVISION_RECEIPT.json`
- 验收：人工批准、真实回执、revision ID与新版本对应
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/revision--revise--resubmit.json`
- 回退：{"invalid_input": "revision/decision", "failed_check": "revision/revise"}

## acceptance/decision/confirm

- 操作：核验正式录用通知与稿件身份
- 角色：planner
- 输入：`refine-logs/contracts/EDITOR_DECISION.json`
- 输出：`refine-logs/contracts/ACCEPTANCE_RECORD.json`
- 验收：不将建议接收或条件接收误记为正式录用
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/acceptance--decision--confirm.json`
- 回退：{"invalid_input": "acceptance/decision", "failed_check": "acceptance/decision"}

## acceptance/final/camera-ready

- 操作：按出版要求完成终稿作者信息和附件
- 角色：executor
- 输入：`refine-logs/contracts/ACCEPTANCE_RECORD.json`, `refine-logs/contracts/VENUE_SNAPSHOT.json`
- 输出：`refine-logs/contracts/CAMERA_READY_RECEIPT.json`
- 验收：终稿与获准版本差异明确且提交证据真实
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/acceptance--final--camera-ready.json`
- 回退：{"invalid_input": "acceptance/decision", "failed_check": "acceptance/final"}

## acceptance/final/proofs

- 操作：逐页核对校样公式、图表、引用和作者信息
- 角色：writer
- 输入：`refine-logs/contracts/CAMERA_READY_RECEIPT.json`
- 输出：`refine-logs/contracts/PROOF_CORRECTIONS.json`
- 验收：修改有定位与确认，不静默新增科学结论
- 审批：human_confirmation
- 审查记录：`.auto-research/lifecycle/reviews/acceptance--final--proofs.json`
- 回退：{"invalid_input": "acceptance/decision", "failed_check": "acceptance/final"}

## acceptance/final/archive

- 操作：归档代码数据环境正文图表与重现命令
- 角色：executor
- 输入：`refine-logs/contracts/PROOF_CORRECTIONS.json`, `refine-logs/contracts/RUN_RECORDS.json`
- 输出：`refine-logs/contracts/FINAL_ARCHIVE_INDEX.json`
- 验收：实际文件可读取、哈希可核验且许可和敏感信息已检查
- 审批：auto
- 审查记录：`.auto-research/lifecycle/reviews/acceptance--final--archive.json`
- 回退：{"invalid_input": "acceptance/decision", "failed_check": "acceptance/final"}
