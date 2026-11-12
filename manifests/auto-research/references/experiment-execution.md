# 实验设计、执行与统计契约

## 边界与职责

本 scaffold 编排现有 aris skills，不运行新的后台调度器。`experiment_stats.py` 做本地矩阵展开、审批检查和统计；模型宿主/agent 调用现有 run/queue。配置设置并不等于模型或实验已执行。

1. researcher 分析 idea、claims、机制与混杂因素。
2. planner 在 grill-me 共识后制定检索、对比和消融计划。
3. executor 联网检索原始论文、作者官方仓库、官方 benchmark，记录检索日期、query、来源与实际筛选；检索失败显式留档，不标称最新。
4. researcher 判断候选的相关性、新颖性和可比性；planner 冻结协议和矩阵。
5. executor 使用 experiment-bridge 实现，独立会话代码审查，然后 sanity、预算门和正式执行。
6. executor 采集原始结果并运行统计；researcher 解释与审计；writer 只接收有审计标记的证据。

## 设计文件

沿用 `refine-logs/EXPERIMENT_PLAN.md` 和 `EXPERIMENT_TRACKER.md`；增加 BASELINE_REVIEW.md、ABLATION_PLAN.md。当前设置使用 `refine-logs/EXPERIMENT_SETUP.json`，从模板复制。设计阶段的设置是执行参数和记录交换文件，不是另一个继承式 Experiment Plan schema。

### 联网 baseline

同时检索近期强方法、标准 baseline、最接近 idea 的方法。每个候选记录论文/官方代码 URL、发表时间、检索时间、code revision、数据 split、协议、资源与纳入/排除理由。首次必须检索；正式部署时检索超过 30 天（设置可覆盖）先刷新并重新审批计划变化。官方代码缺失或不适用的候选放在文献表，不伪造执行记录。

冻结训练/评估代码与数据版本。相同数据划分、指标、评估器和可比预算；差异必须明确。论文报告值只在文献表，复现值与 checkpoint 评估值分组展示。

### 完备消融

对每个 claim、新增组件和混杂因素列覆盖项，设计：组件移除、增量、替代、交互、训练目标、敏感性、资源匹配、失效边界。仅对有科学意义的组合做交互研究，不穷举所有组合。

每项写清变化、控制条件、假设、指标、结果解释、成本和配置。覆盖表状态为 covered/deferred/not_applicable，后两者必须给理由。covered 引用实际实验 ID。负结果同样留档；预算外候选不得自动运行。主结果后 ablation-planner 可以提建议，先更新计划再审批。

## 覆盖、负结果与科学结论

按 [Idea 验证契约](idea-validation.md) 预先定义 claim 的最低证据、反证/停止条件，并在分析中逐项对照冻结矩阵与实际 runs。缺失/失败/延期不算反证；smoke、部分实验和具体 method 失败不推出整体 idea 无效。决定性有效反证可触发预设提前停止，但只给出受测范围内结论；资源中止记未定。全部 attempt 及失败方法的启发分别写入既有日志、FAILURE_ANALYSIS 与 CLAIM_EVIDENCE，下一 cycle 回看，不强行跑到正结果。

每轮修订/恢复核对目标、方法与 claim revision、配置哈希、有效审批、原始证据和真实进程；语义 diff 与交接写入原 checkpoint/日志。独立 worktree 不替代上下文保真。审查变化后的科学结论，再交 Writing Plan。

## 执行接口

```bash
python3 scripts/experiment_stats.py design-review refine-logs/EXPERIMENT_SETUP.json --output refine-logs/DESIGN_CHECK.json
python3 scripts/experiment_stats.py expand refine-logs/EXPERIMENT_SETUP.json --output refine-logs/RUN_MATRIX.json
python3 scripts/experiment_stats.py gate refine-logs/RUN_MATRIX.json --approval refine-logs/BUDGET_APPROVAL.json --state refine-logs/EXECUTION_STATE.json
python3 scripts/experiment_stats.py summarize refine-logs/RUN_MATRIX.json --records logs/RUN_RECORDS.json --content-root . --output results/EXPERIMENT_STATISTICS.json
```

返回 0 成功，1 配置/验收失败或结果不完整，2 I/O 错误。所有报告采用临时文件加 os.replace；运行记录由 executor 在每个 attempt 后原子更新并通过阶段 checkpoint 提交。统计报告历史由检查点快照保留。

默认 seeds=[42]，max_parallel=4；实验块可覆盖 seeds。任务按 dataset × grid × seed 展开，重复 seed/网格单元报错。run_id 稳定标识矩阵单元，config_hash 检测设置变化；重试使用递增 attempt，不作为新 seed。

SSH 下 >=10 任务或有依赖使用 experiment-queue；其余使用 run-experiment，每批最多 max_parallel。非 SSH 后端不调用 SSH queue。保存 code revision、environment ledger、精确 argv、日志、退出码、原始 JSON/CSV、checkpoint 索引和实际模型。sanity 每个新实现或变体先做必要 smoke test。

环境复用 `.aris/compute/<provider>.md`，核实数据/GT 来源和评估器实际输出。不得仅以 import 成功标记环境就绪。

### 预算与重试

免费已有算力 sanity 可自动执行；付费云 sanity 加 `gate --paid --sanity-only`。full suite 必须 gate；执行状态至少提供 sanity_passed、code_review、spent_cost、spent_gpu_hours。审批文件记录 plan_hash、approved_by、approved_at、max_cost、max_gpu_hours，以及审查缺席时的 review_unavailable_acknowledged。

同一矩阵预算内不反复询问。运行中可提供 remaining_estimated_cost / remaining_estimated_gpu_hours（只算未完成任务），检查已花费+剩余是否超上限。计划 hash 变化重新审批。费用和 GPU 小时均必须给有限非负值。

代码审查缺席记 REVIEW_UNAVAILABLE，预算门人工确认；科学审计缺席不等于通过。自动修复改变 batch size/lr/数据/指标时必须修订配置并重新审批，不能将新配置结果冒充旧配置。

执行器必须从实际进程、退出码和输出判断状态。queue 原生 pending/running/completed/failed_oom/failed_other/stuck 映射为 tracker 的 TODO/RUNNING/DONE/RETRY_PENDING/FAILED/BLOCKED；记录原生状态，不把终态 stuck 当依赖成功。监控直接读已记录远端 queue_state.json，现有 monitor-experiment 不保证原生支持它。

恢复先校验进程是否仍活跃，再查 config_hash、结果路径和退出码。成功且配置一致的任务复用；活动任务重新连接；其余明确重试。不能仅凭 screen 消失或 tracker DONE 判成功。对 queue 的依赖在提交下一波前再次验证成功产物。

## 结果记录与统计

`RUN_RECORDS.json` 是数组，每个 attempt 包含 run_id、attempt、config_hash、status、exit_code、result_path、audit；同时记录实际 command、code_revision、environment、started_at、ended_at、stdout/stderr 路径和耗时/费用。精简字段示例见模板；completed 必须对应 exit_code=0 和现存结果文件。

status: completed/failed/blocked/cancelled/running。JSON 原始结果为 {"metrics":{"accuracy":0.75}}；CSV 为一行指标名/值，单次运行单独文件。每个 attempt 目录独立，保存全部尝试。汇总采用该 run 的最新 attempt；失败不回退选择旧的更高分数。

统计生成 JSON、summary CSV、comparisons CSV，包含每个 run 的状态、原始文件校验和及 claim IDs。单 seed 标准差为 null，多 seed 用样本标准差；缺失/失败不补零。配对差值仅使用同数据、协议、comparison_group、来源种类和 seed 的唯一 baseline，存在多 baseline 配置时分别设置 comparison_group。零 baseline 相对变化为空；maximize/minimize 分离原始差值和改善方向。不默认输出显著性、置信区间或稳健性结论。

证据门：PASS→eligible，WARN/REVIEW_UNAVAILABLE→provisional，FAIL/未完成→ineligible。全部值照常展示，避免按审计结果选择性删除数据，但 writer 必须遵守 evidence_status。主张支持度由 researcher 判断，统计脚本不代替科学审计。
