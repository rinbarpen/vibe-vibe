# 全生命周期记录与模型路由

`lifecycle/defaults.json` 定义三层阶段：startup、literature、idea、design、execution、analysis、writing、internal-review、submission、revision、acceptance。大阶段→小阶段→小小阶段，每项对应科研活动而非工具调用。允许项目增补三层节点，不适用节点 skipped 并写原因。

每个大阶段的目标、输入、产物、门禁、模型角色和回退路径见 [lifecycle-stage-details.md](lifecycle-stage-details.md)；机器可读字段位于 `defaults.json.phase_details`。研究写作规则、LaTeX 模板锁定和中英文 skill 路由见 [research-writing-rules.md](research-writing-rules.md)。

## 初始化与命令

```bash
python3 scripts/research_workflow.py --project-root . init
python3 scripts/research_workflow.py --project-root . route planner
python3 scripts/research_workflow.py --project-root . status --cycle cycle-001
python3 scripts/research_workflow.py --project-root . checkpoint --stage startup --state started --role planner --actual-model ACTUAL_MODEL_ID --summary '研究目标和验收标准已确认' --next '启动目标细化' --artifact RESEARCH_PLAN.md
python3 scripts/research_workflow.py --project-root . resume --cycle cycle-001
```

标准库工具，POSIX 本地文件锁。退出码 0 成功、1 约束失败、2 I/O 错误。init 不覆盖已有 settings，不提交旧项目的未确认历史，不租资源或调用模型。根目录必须是本科研项目 Git root，避免对聚合仓库误操作。

运行设置位于 `.auto-research/lifecycle/settings.json`；事件追加于 events.jsonl；local/ 是忽略的事务日志及锁；快照在 refine-logs/history/<cycle>/<checkpoint>/。设置变更随下一检查点提交。

## 模型绑定

默认职责：research=GPT-6 Pro，planner=GPT-6 medium，executor=GPT-5.6-Luna high，writer=GPT-5.5 high。Pro 是 service_profile，不是推理等级。bindings 初始为空，由实际执行宿主核验供应商能力后填写，每项包含 provider、model_id、service_profile、reasoning_effort、available、verified_at。不可在文件中存 API key。

`route` 返回实际绑定供宿主调度；工具本身不调用模型。`--actual-model` 必须由宿主实际会话元数据提供，而不是复制默认模型名。执行记录的真实性由调用宿主提供，CLI 只验证匹配关系。availability 是宿主验证记录，不是实时连通性证明。宿主调用失败时记录 blocked，summary 以 blocked_model_unavailable 开头，可在未绑定时留档。

同一阶段可以按职责切换模型。checkpoint 支持 `--role`，项目设置中修改某职责绑定属于显式覆盖，需记录原因及新旧配置。审查使用独立上下文，保留 reviewer 实际身份；同模型新会话不标称跨模型审查。

## 状态与轮次

started→completed/failed/blocked/paused/revised；paused/failed/blocked→resumed；活动阶段可 revised，任何尚未执行且不适用的节点可 skipped。进入子节点前先启动父节点；完成父节点前所有直接子节点必须 completed/skipped。祖先暂停时先恢复父级。

每个 cycle 内同一阶段只有一个 execution_id；终态后再做该阶段必须创建新 cycle（从对应大阶段开始），稳定 stage_id 保持。`--submission-id` / `--revision-id` 标识投稿/返修，不覆盖前次记录。负结果仍可 completed，科学结论写 summary，与执行状态分离。录用确认、投稿回执、返修提交及外审决定完成时强制要求 artifact；真实性由科研人员核验。

## Git 与恢复

每次事件（进入、结束、失败、修订、暂停和恢复）都形成 commit；父阶段提交汇总其子阶段，不重复复制所有二进制产物。显式 --artifact 可重复，--input、--run-id 记录关联，--command 记录命令，--summary 和 --next 必填。所有输入只登记引用，产物才提交。

仅提交明确登记文件及生命周期账本，使用 git commit --only，保留无关 staged/unstaged 变更。进程锁让并行 run 的记录提交串行化；锁忙则重试。init 无 Git 时初始化，但不设置 user.name/email；缺身份或冲突时 checkpoint 阻塞。默认不 push、不 reset、不改历史。保存 pending 事务后提交，resume 检索 Checkpoint-ID 恢复，避免提交成功/清理前中断导致重复提交。resume 遇到已登记产物变化要求先恢复原内容；不自动覆盖用户修订。

所有快照保留；事件更正以新 revised 事件追加，不覆盖旧事件。路径限制在项目内。默认 Git 单文件上限 10 MiB；二进制/大型文件使用归档索引（artifact path、size、sha256、run/attempt、生成时间、local_only 或 archived、检查时间）。索引必须含 kind=archive_index；登记时工具实际读取本地或已挂载存储并验证大小和 SHA-256。远程对象须先挂载或同步到可验证位置；不将未核实 URL 标记为已归档。可单独运行 `research_workflow.py archive-check INDEX.json`。Git 提交前检查常见明文凭据模式，命中则先制作脱敏副本；该检查不替代人工保密检查。

resume 首先修复 pending Git 事务，然后显示最近阶段状态。它不自动重启实验。执行器必须核验实际进程、queue state 和输出，并为恢复任务记录 resumed；成功结果复用，运行任务重新连接，失败任务另建 attempt。

### Branch 生命周期

`defaults.json.branching` 默认启用阶段 branch 管理：

```text
<idea>/<stage>/<substage>
<idea>/cycle/integration
<idea>/submission/<submission_id>
<idea>/revision/<revision_id>
```

`idea`、stage 和 id 会先规范化为 Git ref 安全字符串。顶层阶段的父 branch 是
cycle integration；子阶段从直接父阶段 branch 继承。`checkpoint --state started`
会创建并切换 stage branch；`completed`、`failed`、`blocked`、`skipped` 等终态
检查点通过现有门禁后，以 `--no-ff` 合并回父 branch，并留下 merge commit。这个
层次保证每个子阶段的产物先在自己的 branch 上形成，再由父节点汇总，不把兄弟阶段
的修改混在一起。

常用操作：

```bash
python3 scripts/research_workflow.py branch init --cycle cycle-001 --idea research
python3 scripts/research_workflow.py branch start --cycle cycle-001 --stage literature/search
python3 scripts/research_workflow.py branch status --cycle cycle-001
python3 scripts/research_workflow.py branch merge --cycle cycle-001 --stage literature/search
python3 scripts/research_workflow.py branch revision --cycle cycle-001 --kind submission --id sub-001
python3 scripts/research_workflow.py branch close --cycle cycle-001
```

`branch close` 只把 cycle integration 合并回 `branching.integration_branch`（默认
`main`）。所有 branch 写入 `.auto-research/lifecycle/branches.jsonl`；本地恢复状态
位于被忽略的 `local/branch-state.json`。branch 操作要求 tracked worktree clean，
但不会吸收无关 staged/unstaged 文件；默认不删除已合并 branch、不 push、不 reset。
合并失败时保留事件和当前 branch，先修复冲突，再用同一 stage/cycle 重试。

### 隔离迭代 workspace

阶段 branch 负责阶段汇总，不代表工作目录隔离。对同一产物进行反复修改、返修或失败重试时，每轮应新建 worktree attempt；attempt 从阶段目标 branch 的当前 commit 起步，失败时保留现场并从该可信基线创建新 attempt，不覆盖旧目录。

```bash
python3 scripts/research_workflow.py branch init --cycle cycle-001 --idea research
python3 scripts/research_workflow.py workspace start --cycle cycle-001 --stage writing/draft --attempt attempt-001
python3 scripts/research_workflow.py workspace status research-cycle-001-writing-draft-attempt-001
# 在返回的 worktree 路径中修改文件
python3 scripts/research_workflow.py workspace verify research-cycle-001-writing-draft-attempt-001 --command 'pytest -q'
git switch research/writing/draft
python3 scripts/research_workflow.py workspace promote research-cycle-001-writing-draft-attempt-001
python3 scripts/research_workflow.py workspace close research-cycle-001-writing-draft-attempt-001
```

`verify` 要求显式提供至少一个 `--command`，保存每条命令的 stdout/stderr/exit status；全部通过且根目录未发生基线漂移后，自动将隔离 worktree 中的改动提交为候选 commit。`promote` 仅接受通过验证的 attempt，并要求项目根目录干净、当前分支是记录的阶段 branch，且该 branch 仍包含 attempt 基线；冲突或漂移时保留候选现场，另开 attempt 处理。`close` 只移除工具登记、已验证或已晋级且无未提交改动的 worktree；分支和 attempt 记录保留在 `.auto-research/lifecycle/local/workspaces/`。

### Research writing gate

研究场景 `writing_policy` 的默认值是 LaTeX、中文/英文双语、95% CI 省略和防御性
写作关闭。仅在 venue、研究方案、作者请求或审稿意见明确要求时打开 95% CI，并把
level、estimator、seed/replicate 聚合和理由写进 Writing Plan。草稿形成后运行
`mine/z-humanizer`；需要原则审计时调用 anti-defensive-writing 子模块的中文或
English skill。官方 venue template 的 `.cls`、`.sty`、字体、参考文献、table 和
figure style 文件必须通过 sha256 manifest 锁定，任何 style 修改都使
`template_integrity` gate 失败。

## 周期终点与写作

研究→实验→结果不支持时回到 idea/design 新 cycle；内部评审→补实验→Writing Plan 更新；外审→响应矩阵→补实验/回复→修订提交；拒稿→新 submission 与转投。每次论文节点修改遵守原 Writing Plan 的 validate/resolve/render/approval/review。

真正中稿以正式录用通知为依据；camera-ready/校样/归档是录用后单独状态。正式投稿与作者确认、撤稿等有外部影响的操作必须先获得用户确认，记录实际回执而不是模拟成功。集成测试只用标记为 fixture 的本地材料。

## 叶节点完成门（contract revision 1）

新项目默认 `enforce_stage_contracts: true`。每个叶节点完成前，按 `references/lifecycle-leaf-contracts.md` 准备输出，并在节点的 `review_path` 提交 JSON：`stage_id`、`contract_hash`、`reviewer`、`reviewed_at`、`artifacts: [{path, sha256}]`、`checks: [{criterion, status: pass, evidence}]`。criteria 必须逐字对应 acceptance。需要人工确认的节点还需 `approval: {approved: true, approved_by, approved_at}`。报告绑定当前输出哈希；输出变化后旧报告失效。

先运行 `python3 scripts/stage_contract.py --project-root . --stage STAGE_ID` 得到当前契约哈希、产物哈希和缺项，再由审查者填写报告；工具不会自动填充 pass。`checkpoint completed` 必须通过 `--artifact` 同时登记所有声明输出和审查报告。仅做文件、哈希和声明完整性检查，不验证审查者身份、不代替科学评审或平台回执核验。输入证据核对仍属于节点审查。

旧 settings 不自动覆盖，保留原运行语义。升级时显式合并默认节点契约并按项目现有路径映射输出；先审查变更，再开启 enforce_stage_contracts。跳过仅用于不适用情况并记录原因；不把 skipped 当作获得科学证据。
