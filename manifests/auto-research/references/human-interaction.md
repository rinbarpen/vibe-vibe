# 宿主人机交互与实验预算门

## 定位与交互模式

此契约接入既有 `execution/runs/approval`、`BUDGET_APPROVAL.json` 和 checkpoint，不新增生命周期、审批数据库或后台调度器。结构校验只检查声明与哈希，真实用户身份和消息来源由宿主核验；本地脚本不证明消息真实，也不拦截绕过该入口的任意 shell 操作。

- 用户希望发展直觉时，按 [intuit-to-idea](intuit-to-idea.md) 一问一答。普通回答是研究输入，不是批准实验、预算或投稿。
- 已确认任务使用委托执行模式，AI 在批准范围内推进；目标/取舍改变或到达既有业务门时再请求决定。
- 工具权限由宿主处理。允许命令执行、接受默认选项或清除提问请求，都不等于预算已批准。

## 宿主适配

先核对当前环境实际可用的能力和模式，不根据 agent 名称猜接口：

| 能力 | 呈现和回传 | 约束 |
|---|---|---|
| 结构化问题 | 使用当前可用的原生提问工具，将明确选择和原始响应 ID 记入既有记录 | 仅在返回真实 `approve` 时登记批准；预选/超时/关闭保持等待 |
| 普通聊天 | 展示材料和选项，接收明确回答，记录用户原话或宿主消息引用 | “好”等回答必须结合紧邻的明确决策对象理解；泛泛认可讨论不扩展为预算批准 |
| 外部审批界面 | 宿主提供审批事件引用、响应 ID、决定人和时间 | 宿主核验来源；本地字段完整性不是身份认证 |
| 无人值守 | 复用当前有效批准；否则保存 `paused` checkpoint 和下一步 | 不补写用户回答；独立且不受此门影响的工作可以继续 |

Codex、Claude 等宿主的提问 API 只属于适配层，本文件不要求任一工具总是可用。队列消息不视作当前任务纠偏；停止/纠偏不撤销已经运行的实验。发生干预时按现有真实进程、run/attempt 和产物状态恢复。

## 版本与兼容

新项目的 `templates/EXPERIMENT_SETUP.json.example` 显式包含 `interaction_contract: budget-decision-v1`，`expand` 将其带入矩阵。成本非零时设置明确的 `cost_unit`（如货币或算力积分单位）；零成本可用 `not_applicable`。版本未知时报错。

旧项目的设置和审批文件不自动改写。未声明此契约的旧矩阵沿用原 gate 语义；迁移时先在既有设置加入该字段、声明成本单位，再 expand 并重新取得当前预算批准。使用新决策回执也会启用版本化校验。新模板更新不代表旧批准已获得新版本的来源和范围约束。

## 1. 准备可审阅决策材料

先按 [实验执行契约](experiment-execution.md) 冻结设计。正式 full suite 前核对代码审查和 sanity；付费 sanity 则先取得该范围的预算批准，再执行 sanity，避免循环等待。读取既有实际执行状态，然后运行：

```bash
python3 scripts/experiment_stats.py expand refine-logs/EXPERIMENT_SETUP.json --output refine-logs/RUN_MATRIX.json
python3 scripts/experiment_stats.py decision-request refine-logs/RUN_MATRIX.json --state refine-logs/EXECUTION_STATE.json --output refine-logs/BUDGET_REQUEST.json
```

付费 sanity 对 request 与 gate 同时使用 `--paid --sanity-only`；其他付费执行同时使用 `--paid`。默认请求上限是已花费加剩余估计；明确取舍后可以用 `--max-cost`、`--max-gpu-hours` 指定上限，再展示新请求供人决定。

宿主展示矩阵/计划及代码审查证据、成本估计依据、单位、预算上限、审查缺席风险和 approve/revise/cancel 的去向。请求的 `subject` 绑定 plan hash、完整 matrix hash、上限、成本单位、代码审查状态与本次付费/full-suite 范围。`decision_id` 从内容确定性生成；重展示相同材料保持同一 ID。请求始终为 `awaiting_decision`，不生成批准文件。

代码、数据或协议实质变化时先按原规则修订设置并重新冻结；matrix hash 不等于对仓库或外部证据自动取快照。科学事实与来源真实性仍由既有审查流程核验。

## 2. 接收真实决定，复用原审批文件

仅在收到明确批准后，由宿主把以下回执写入既有 `refine-logs/BUDGET_APPROVAL.json`。哈希、ID、plan hash、上限与缺席声明取自人实际看到的请求；回答来源取自真实会话或审批事件，不由请求生成器代填。

```json
{
  "interaction_contract": "budget-decision-v1",
  "decision_id": "BUDGET_REQUEST.decision_id",
  "subject_hash": "BUDGET_REQUEST.subject_hash",
  "decision": "approve",
  "plan_hash": "BUDGET_REQUEST.subject.plan_hash",
  "max_cost": 0,
  "max_gpu_hours": 0,
  "review_unavailable_acknowledged": false,
  "approved_by": "USER_ID",
  "approved_at": "TIMESTAMP",
  "response_source": {
    "kind": "structured_input",
    "reference": "HOST_MESSAGE_OR_APPROVAL_REFERENCE",
    "response_id": "HOST_RESPONSE_ID"
  }
}
```

以上是字段结构示例，不是有效批准。`response_source.kind` 可为 `structured_input`、`chat_message`、`external_approval`。人尚未决定时不写 `approve`；可保持没有审批文件或仅保存 `decision: pending` 的待办。调整记录 `revise` 并返回设计/预算材料；取消记录 `cancel` 并结束本次运行请求。按原 checkpoint 规则登记 paused/revised/resumed 和实际产物，不新建逐轮对话账本。

## 3. 核对并恢复

```bash
python3 scripts/experiment_stats.py gate refine-logs/RUN_MATRIX.json --approval refine-logs/BUDGET_APPROVAL.json --state refine-logs/EXECUTION_STATE.json
```

- 无回答、调整、取消、来源字段缺失均保持门关闭；没有审批文件时继续等待，不调用实验后端。
- 当前 hash、上限、审查状态或付费/full-suite 范围不匹配，回执失效，重新展示材料并请求决定。
- gate 继续检查 sanity、代码审查、依赖和“已花费 + 剩余估计 ≤ 批准上限”。预算内正常花费增长本身不使批准失效；超过上限仍关闭门。
- `decision_status` 只表示回执状态，`allowed` 才表示所有门检查是否通过。`launch_performed` 始终为 false；退出码 0 表示检查通过，不表示实验已经运行。
- gate 为只读、可重复检查。通过后，执行器先核对真实 run_id/config_hash/attempt、进程、队列和成功产物：成功复用，活动任务重连，失败明确新 attempt。避免因重复回答或重连再次提交已有任务。真实远程提交去重仍由已有执行器/队列负责，本工具不承诺分布式 exactly-once。
- 已有支出、日志、产物和历史回执保留；调整/取消不自动清除实验或回退外部状态，沿原执行与回退入口处理。

## 工作流与复现

[预算交互 SVG](budget-workflow.svg) / [可编辑源](budget-workflow.json)。复用已经随包分发的标准库渲染器，源目录与安装后项目均从各自根目录执行：

```bash
python3 scripts/render_idea_workflow.py --source references/budget-workflow.json --output references/budget-workflow.svg
python3 scripts/render_idea_workflow.py --source references/budget-workflow.json --output references/budget-workflow.svg --check
```

图仅描述现有预算门的内部交互规则，完整阶段树仍以 `lifecycle/defaults.json` 为准；图不是执行账本。`--check` 只读，缺图、漂移或引用错误返回非零。
