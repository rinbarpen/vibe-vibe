# 原生 subagent 并行推进契约

本契约把专业工作包转成可恢复的项目任务，而不是把所有角色同时启动。生命周期和人工决策仍以 [lifecycle.md](lifecycle.md) 为准；类型、专业包与引擎分别沿用 [类型档案](genres.md)、[专业工作包](production.md) 和 [引擎适配](engine-matrix.md)。

## 1. 谁负责什么

- **主代理 / coordinator**：恢复已有状态，裁剪适用任务，冻结只读输入与验收、记录可更新输入基线，划定文件/资源归属；调用当前宿主真实的 subagent 工具；记录派发、运行 ID、结果、集成、验证、审查、返工和恢复。
- **执行 subagent**：只处理领取的任务、输入和写入范围；实际使用已连接工具；把产物、哈希、字面日志、退出状态、风险和恢复点交回主代理，不直接修改共享调度状态。
- **集成负责人**：按约定分支/工作目录接收源码或资产，复核输入版本、实际差异、引用/ID、文件范围和预期产物；只在单写者窗口内操作共享工程。
- **QA / 验证者**：对集成后的冻结产物运行约定用例，区分静态、逻辑、引擎、设备、实际输入和真人反馈。
- **独立 reviewer**：使用不同于作者的运行上下文复核设计/实现/证据链，提出接受或返工结论。作者自检另列，缺独立上下文时明确记录 self-review，不冒称独立审查。

原生角色位于项目根 `.claude/agents/` 与 `.codex/agents/`，角色职责目录见 [subagent-roles](../agents/subagent-roles.md)。角色数量是能力目录，不是并发数量；模型和宿主工具以当前可用环境为准。

**Python runtime 负责状态、就绪判断、预留与结果校验，不调用 LLM。** 真正启动/等待/停止 subagent 由主代理使用宿主已暴露的工具完成，随后保存真实运行 ID。角色文件存在、队列已认领、测试夹具成功，都不等于实际代理已运行。

## 2. 从 94 个工作包裁剪为项目计划

1. 恢复当前项目的阶段、决策、引擎、类型和未提交工作，不重建已完成状态。
2. 从 production.json 选适用工作包，给本项目任务分配稳定实例 ID、职责和验收；当前计划内每个 package_id 绑定一个实例；额外关卡/资产批次可用 custom_reason 明确引用原专业包，并显式声明前置实例、范围和验收，不制造含糊的多实例依赖。
3. 每条前置依赖引用本计划中的任务实例。若专业目录的依赖被裁剪，记录不适用理由、替代输入及影响，不能仅删除依赖以获取并行数。
4. 写清输入文件及哈希、预期输出、允许写入的文件或目录前缀、外部资源、模式和所需人工门。未来依赖输出应在领取前存在；区分保持只读的前置材料与本任务明确负责原位更新的源/代码，领取时均记录基线哈希。
5. `design-only` 只派设计/规格任务；实际模型制作、工程修改、构建、设备测试与发布属于明确实现范围。实现模式也不替代方向、切片、发布或付费/迁移等门。
6. 设定并发上限，并与宿主当前可用槽位取较小值；主代理、集成/QA/reviewer 同样占用宿主资源。资源不足时减少批次，不排挤用户的 Editor 会话。

[工作单模板](../templates/work-order.md) 与机器模板须填写实际值后使用；模板占位内容不是已确认的项目状态。

## 3. 自动派工的主代理循环

主代理持续执行以下闭环，直到当前范围完成或明确进入等待：

1. **观察**：重读持久状态、真实运行 ID 和已有报告；确认上次未完成动作及环境变化。
2. **筛选**：挑选前置任务已完成、人工门已通过、输入匹配、模式允许且无写入/资源冲突的就绪任务；`next` 重核依赖产物与父任务审查证据，不只看 done 字符串。
3. **事务认领**：在并发上限内形成一个批次，为每个任务分配 attempt/token 与租约，保留文件/资源归属。
4. **实际派发**：读取对应原生角色，将完整工作单交给宿主真实 spawn 工具；立即把其返回的运行 ID 绑定到任务。启动失败按原任务记录原因和恢复步骤，不声称运行成功。
5. **在途维护**：观察进度与真实宿主状态，按协议维护心跳；已等待工具/设备或人的决定则明确登记，不将等待当完成。
6. **收集**：接收执行者结果及真实文件，核对任务、attempt/token、绑定的运行上下文、只读输入哈希、输出路径和字节哈希；重核依赖产物及父任务审查证据，保留原始报告与日志。原位更新输入按已分配写范围识别，原哈希保留为 baseline，新哈希进入本任务产物。
7. **集成 → 验证 → 独立审查**：每一步绑定同一冻结产物，后一步不代替前一步。作者提交仅进入已提交状态；全部约定门满足后才完成任务并释放其依赖。
8. **继续或返工**：重新计算下一批就绪任务；失败返回原 owner，记录具体缺陷与新尝试，重跑原用例与相关回归。若需改变目标/预算/依赖取舍，走真实人工门。

有就绪任务时应主动推进；无需每个细步骤等人再次催促。目标或高影响取舍需要新决定时保持等待；技术实现疑问优先由 AI 调研和实验解决。

## 4. 文件、资源与隔离

| 对象 | 协作规则 |
|---|---|
| 独立代码模块、独立设计文档、独立源资产 | 可在明确无重叠写范围的任务间并行；跨模块接口先冻结 |
| 同一 Scene/World/Prefab、事件数据库、DCC 源 | 保持单写者；文本格式也可能存在资源引用和语义冲突 |
| 同一工程 Editor 或同一外部 DCC 会话 | 用共享外部资源标识互斥，按实际应用实例串行；不同输出目录不自动代表不同会话 |
| 工具链/项目配置、依赖锁文件、全局数值源 | 分配明确 owner，其他代理提交变更建议；主代理组织集成窗口 |
| worktree / 独立工作目录 | 用于代码隔离；共享云资产、外部文件、许可证、设备与 Editor 仍需资源认领 |
| 调度状态与共享状态 | 由 coordinator 写；worker 只交报告和自己范围内的产物 |

路径预留和资源认领是协作协议，不是操作系统沙箱。宿主主代理仍需核对实际 diff、未保存场景、工程锁与外部软件状态；检测到越界修改先停止扩大影响并处理冲突，不能用队列记录宣称已实现文件系统隔离。

提交后到完成前继续保留必要归属，避免后续任务覆盖待审产物。上游仍待审查时，下游不直接改其源。已完成的模型/代码确需在原路径更新时，由新的任务显式领取该写范围并依赖原任务；领取时保留原文件 baseline 哈希，完成后提交本任务新 artifact 哈希，再走集成/验证/独立审查。

**输入分两类**：未落入本任务 writes 的只读输入保持哈希冻结；明确落入 writes 的输入是本任务负责更新的基线，可正常原位修改，而非永久只读。范围外输入、无关依赖产物与父任务审查证据在 `next`、`submit` 和各阶段重核。旧任务的审批与历史不改写成新版本通过；后继应依赖实际产出新版本的任务，并写清 baseline/new artifact 路径与哈希。若只读前置或原审查证据意外变化，协调者先处理依赖失效与返工，不以完成标签忽略漂移。

## 5. 结果与证据

每次交接至少包含：

- 项目任务/专业包 ID、角色、attempt/token、宿主实际运行 ID。
- 任务目标、允许写入路径、认领资源、只读输入/可更新输入分类，以及 baseline 与新产物版本/哈希。
- 实际修改/新增/删除路径，预期与实际输出、SHA-256、源码/资产 revision。
- 实际工具命令、cwd、输入、字面 stdout/stderr、退出状态、日志/截图路径。
- 各测试 `pass/fail/not_run`，缺环境原因、尚未验证范围、风险和下游建议。
- 作者自检、集成、QA、独立审查分别具名，注明对应冻结产物。
- 修改前恢复点及实际回退步骤，原始用例与邻近回归的恢复验收。

日志和哈希只证明各自范围：文件字节检查不证明模型质量，doctor 不证明实际建模，编译不证明可玩，AI 自动操作不代表真人体验。任何 `not_run` 均保持可见，不能自动解锁要求该项通过的后继。

## 6. 失联、超时、恢复与降级

- **租约过期**：视为需要协调者核查的状态，不自动抢占后重派。旧 worker 可能仍在写同一文件；保留归属，先查看宿主真实状态并停止/确认原运行已结束。
- **恢复**：记录停止/结束证据和原因后，由协调者执行恢复步骤，撤销旧 token、保存旧 attempt 记录，再领取新尝试。旧 token 的迟到提交不进入当前任务。
- **集成/验证/审查失败**：保留失败证据、错误 revision 和恢复点，按工作单返工；不通过改状态或换作者名跳过问题。
- **进程中断**：以持久状态和真实运行 ID 对账；原子写入/事务边界用于保证状态一致，遗留操作先诊断，不删除唯一证据或活跃锁。
- **宿主缺少 subagent**：明确记录 serial 降级，主代理顺序承担执行职责；独立审查仍需真实独立上下文，缺少时保留待审或清楚记录 self-review，状态不冒充独立通过。
- **人未决定**：保留决定 ID、选项/成本、相关 revision/hash、恢复节点；只有实际答复能形成批准记录。任务文件、角色名和调度命令不构成人工批准。

## 7. 首批任务示例

方向/接口冻结后，核心循环规格、独立数值实验、关卡草图和资产规格可形成一批；主代理收集后安排集成审查。实际实现阶段，独立玩法模块、UI 文档/组件与独立模型可并行，但共享 Scene 接线和同一 Editor 操作进入串行窗口。模型规格→制作→UV/PBR→绑定/动画→引擎导入属于依赖链，不为增加并发而同时启动所有节点。

## 8. 安装后命令与模板

以下命令从安装后的游戏项目根运行。先复制并按实际项目填写 [计划模板](../templates/parallel-plan.json)，不是直接把样例任务当作已获确认的真实设计需求：

```bash
cp .game-design/templates/parallel-plan.json .game-design/deliverables/parallel-plan.json
python3 .game-design/scripts/parallel.py --project . init --plan .game-design/deliverables/parallel-plan.json --dry-run
python3 .game-design/scripts/parallel.py --project . init --plan .game-design/deliverables/parallel-plan.json
python3 .game-design/scripts/parallel.py --project . status
python3 .game-design/scripts/parallel.py --project . next
python3 .game-design/scripts/parallel.py --project . claim --worker DESIGN --limit 2
```

`status` 与 `next` 只读；`claim` 才认领任务并给出 `claim_token`、`attempt`、`lease_until`（Unix epoch 秒）。主代理把每个任务交给真实宿主工具 spawn，拿到运行 ID 后绑定：

```bash
python3 .game-design/scripts/parallel.py --project . bind \
  --id design-loop --token "$TOKEN_LOOP" --run-id "$HOST_RUN_LOOP"
python3 .game-design/scripts/parallel.py --project . heartbeat \
  --id design-loop --token "$TOKEN_LOOP"
```

变量应取自本次真实 claim/spawn 结果。`bind` 只是登记运行 ID，不会启动代理；`heartbeat` 不替代观察宿主实际进度。`max_parallel` 是项目配置上限，调度者仍按宿主当下可用槽位缩小批次。

执行者在自己写范围内保存 [结果模板](../templates/task-result.json) 和证据，由 coordinator 收回并执行：

```bash
python3 .game-design/scripts/parallel.py --project . submit \
  --result Evidence/design-loop/result.json
python3 .game-design/scripts/parallel.py --project . integrate \
  --id design-loop --actor "$INTEGRATOR_RUN_ID" --evidence Evidence/integration/design-loop.txt
python3 .game-design/scripts/parallel.py --project . validate \
  --id design-loop --actor "$QA_RUN_ID" --decision pass --evidence Evidence/qa/design-loop.txt
python3 .game-design/scripts/parallel.py --project . review \
  --id design-loop --actor "$REVIEWER_RUN_ID" --decision pass --evidence Evidence/review/design-loop.txt
```

上述 pass 命令仅在对应实际检查通过时使用；验证的其他结论为 `fail/not_run`，审查的其他结论为 `changes_requested/not_run`。阶段证据必须是真实、非空文件，并绑定当前冻结产物；作者、集成、QA 与 reviewer 的运行身份分别记录，QA/reviewer 与作者和集成上下文区分，reviewer 也与 QA 区分。

状态顺序为 `pending → running → submitted → integrated → validated → done`。结果声明 `failed/blocked` 会保持阻断，不变成已完成；`blocked` 任务继续保留写入/资源预留。只有 `running` 占执行并发槽，但提交、集成、验证和阻断期间仍需保留其待审产物的写入/资源归属。后继依赖只接受 `done`。

### 计划机器字段

顶层为 `schema_version:1`、`mode`、`max_parallel`、`lease_seconds`、`gates`、`waivers`、`tasks`：

| 字段 | 约定 |
|---|---|
| mode | `design-only` 或 `implementation` |
| gates | `[{"id":"direction"}]` 等实际项目人工门；初始不自动批准 |
| waivers | 未选专业包前置 ID → 裁剪理由、替代输入与影响说明；不是忽略项目实例依赖的通道 |
| tasks[].id | 本计划内唯一的稳定实例 ID |
| package_id / custom_reason | 引用 production.json 的专业 task ID，或明确说明项目自定义任务原因 |
| role | agents.json 中实际存在的原生角色 ID |
| depends_on | 同一项目计划中的任务实例 ID；图需无环，依赖完成后才派发 |
| writes | 允许写入的项目/工作目录相对路径或目录前缀；不得越界、借助符号链接跨出根目录或占用共享调度状态 |
| resources | 外部排它资源 ID，例如 `editor:main-game`、`dcc:hero-source`、`device:test-phone` |
| inputs | 领取前已存在的相对文件路径，runtime 记录原哈希；writes 范围外保持只读冻结，范围内作为本任务更新 baseline |
| outputs | 本任务实际预期交付的相对文件路径，应落在 writes 范围 |
| effect | `design` 或 `implementation`；实现任务要求实现模式和非空人工门引用 |
| workspace | 可选已存在工作目录；runtime 不自动建立 worktree，coordinator 负责既有目录和集成策略 |

样例使用三个 `custom_reason` 设计任务：前两项分别写不同文档/证据目录，可并行；第三项依赖前两项的 `done`，领取时记录其基线哈希；本例只读这两份文件。实际专业任务计划应完成适用性和依赖裁剪，不直接套用样例。

### 结果机器字段

结果顶层为 `task_id/claim_token/status/summary/artifacts/evidence/tests`：

- `status` 为 `submitted/failed/blocked`。模板默认 blocked、验收 not_run，填写真实结果后再提交。
- `artifacts` 为 `[{"path":"相对产物路径","sha256":"实际SHA-256"}]`；submitted 应含本任务预期输出，failed/blocked 可以没有成品，但仍需非空实际证据文件路径列表 `evidence`，说明失败或阻断。模板证据路径须替换并写入真实非空文件。
- 所有 worker 产物和证据位于已认领 writes 范围。路径与哈希在 worker workspace 检查；产物和证据一起集成到主 project，相同相对路径的落地字节需一致。
- `tests` 各项包含 `name/status/command/exit_status`，状态为 `pass/fail/not_run`；尚未运行保持 `exit_status:null`，不编造命令成功。文件/数据检查与游戏运行分别标注。
- attempt、宿主运行 ID、租约和认领输入基线由持久状态绑定；只读材料的哈希继续冻结，写范围内的原位更新提交新 artifact，不把原哈希覆盖成“从未变更”。结果不通过自行更换 token 或角色来变更身份。

### 人工门与恢复

`approve-gate` 是 coordinator **记录已经发生的真实人决定**，不是通过 CLI 代替人作决定；批准证据在后续校验时保持同一哈希，变动后该批准不继续沿用：

```bash
python3 .game-design/scripts/parallel.py --project . approve-gate \
  --gate direction --actor "$HUMAN_DECISION_ID" --evidence Evidence/decisions/direction.txt
```

租约过期或需要返工时，先使用真实宿主工具停止原 worker/确认其已结束，保存证据，再调用：

```bash
python3 .game-design/scripts/parallel.py --project . recover \
  --id design-loop --token "$TOKEN_LOOP" --stopped \
  --evidence Evidence/recovery/design-loop.txt --reason "已确认旧运行停止，保留原件与失败证据后重试"
```

`--stopped` 是对真实停止事实的记录，不执行停止操作。恢复前后核对实际写入、工作区和外部软件；旧 token 失效后迟到结果不进入新尝试。状态留存失败/恢复历史，不删原始证据以伪装新任务。

### 增量扩展项目计划

已经初始化的队列沿用原状态；新增一批资产/关卡任务时提交**完整新计划**，保留已有 task 的静态定义和原 gate，新增稳定任务 ID。现有 running、结果、集成/审查状态及历史不通过重建计划清零。

```bash
python3 .game-design/scripts/parallel.py --project . extend \
  --plan .game-design/deliverables/parallel-plan-next.json \
  --reason "加入下一批已确认范围的关卡任务" \
  --evidence Evidence/decisions/next-batch.txt --dry-run
python3 .game-design/scripts/parallel.py --project . extend \
  --plan .game-design/deliverables/parallel-plan-next.json \
  --reason "加入下一批已确认范围的关卡任务" \
  --evidence Evidence/decisions/next-batch.txt
```

扩展记录绑定实际范围/决定证据；涉及目标、预算、平台或对外动作的新取舍仍按 lifecycle 人工门处理。`--dry-run` 仅预览，不变更调度状态。

### 从设计模式晋级到实现模式

支持通过 `extend` 单向从 `design-only` 晋级到 `implementation`，同时满足以下条件：

1. 全部已有任务已经 done，既有设计经过集成、验证与独立审查，而非仅作者提交。
2. 主代理取得并记录人对进入实现范围的真实决定；reason/evidence 写明本次取舍、revision、范围和恢复点。
3. 项目 `state/project.json` 的 mode 已按该决定实际改为 implementation；完整新计划也使用相同模式。dry-run 不替主代理修改项目画像。
4. 新完整计划保留所有旧 task 的静态定义和原 gate，追加实现任务；旧状态和审查历史不清零。
5. 每个新 implementation 任务仍引用非空人工门；新增 gate 初始 pending，由主代理使用 `approve-gate` 记录真实批准后才派发。模式晋级本身不自动批准方向、发布或其他高影响门。

其余模式改变不自动接受。需要改变已完成工作的静态定义时，以新任务和明确依赖描述新范围，不重写旧任务历史。

修改 runtime 协议时同步更新本文件与模板，并运行安装后测试。


## Codex角色发现与执行证据

项目原生角色的当前官方发现约定、local CLI版本观察与宿主实际运行的区别见 [Codex发现说明](codex-registration.md)。本模板不改用户全局配置；角色可解析、已被发现和已经运行是三种不同事实。
