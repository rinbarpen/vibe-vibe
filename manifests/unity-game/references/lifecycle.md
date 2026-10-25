# Unity 游戏生命周期

每阶段都用稳定 ID 记录目标、负责人、输入版本、交付路径和退出证据。主代理更新 `.unity-game/state/status.md`，子代理提供候选更新。以下路径均相对安装后的 `.unity-game/`。阶段完成是对证据的判断，不由文档数量自动推导。

## 1. discovery — 立项与可行性

**阶段 skill**：`unity-game-discovery`；按任务读取 `unity-game-brief`、`unity-game-market-research`、`unity-game-scope-risk`。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-discovery-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `discovery` 审查实际版本。通过后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- 输入：用户想法或现有工程、目标平台、团队、工期、预算和资源约束。
- 并行：`market-researcher` 查受众/竞品与来源；`game-designer` 提出核心玩法；`unity-architect` 检查技术风险。主代理限制方案数量和范围，选择依据由用户决定。
- 交付：使用 `templates/project-brief.md` 形成项目简报，包含受众、差异化、明确不做项、风险验证顺序、现有代码/资源盘点。
- 退出：目标与边界可陈述，最大技术/玩法风险有验证任务；关键未知仍显式列出，不假装已解决。

## 2. design — 策划与技术基线

**阶段 skill**：`unity-game-design`；按任务读取 `unity-game-core-loop`、`unity-game-systems-balance`、`unity-game-level-narrative`、`unity-game-art-direction`、`unity-game-ui-ux`、`unity-game-technical-design`。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-design-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `design` 审查实际版本。通过并取得 `direction` 用户确认后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- 并行：玩法/GDD、系统数值、关卡叙事、视觉音频、UI/可访问性、TDD。各文档引用同一个核心循环与范围版本，冲突由 producer 记录决策解决。
- 交付：`gdd.md`、`tdd.md`、`systems-balance.md`、`level-narrative.md`、`asset-spec.md`、`milestones.md` 对应的实际文档。
- 定义 Unity 版本、平台/设备、管线、输入、存档/迁移、离线/联网边界、关键包、资源生产路径、性能预算和测试策略。联网与服务端按需开启，不给离线项目额外加服务。
- **direction 确认门**：向用户展示玩法、差异化、范围、工期/资源、技术风险与原型验收；记录批准的文档版本后进入 prototype。

## 3. prototype — 最小可玩闭环

**阶段 skill**：`unity-game-prototype`；按任务读取 `unity-game-project-setup`、`unity-game-playable-prototype`、`unity-game-prototype-playtest`。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-prototype-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `prototype` 审查实际版本。通过后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- 先实现最小“操作 → 挑战 → 反馈 → 成败/再来”闭环，以占位资产验证手感和关键技术。避免在玩法未验证前批量生产资产。
- `gameplay-programmer` 与 `tools-programmer` 按不重叠路径并行；`qa-engineer` 编写 EditMode/PlayMode 测试；`playtest-analyst` 设计可观察任务与访谈。
- 交付：可运行工程/原型包、实际测试与试玩报告，失败假设、继续/调整/停止建议。
- 退出：玩家可完成预定闭环，关键风险有运行证据。尚无 Editor 或真人试玩时相应验收维持待完成；变化影响方向则重新通过 direction 门。

## 4. vertical-slice — 垂直切片

**阶段 skill**：`unity-game-vertical-slice`；按任务读取 `unity-game-slice-integration`、`unity-game-slice-review`。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-vertical-slice-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `vertical-slice` 审查实际版本。通过并取得 `vertical-slice` 用户确认后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- 选择一段代表性关卡/体验，把玩法、UI、美术、动画/VFX、音频、存档、测试和目标平台构建链路打通。
- 在目标设备建立 CPU/GPU/内存/加载时间等基线；资产许可与生产成本在切片阶段就检查。
- 交付：代表性可玩内容、质量基准截图/视频或构建、性能/试玩/审查证据、完整资源管线与剩余成本估算。
- **vertical-slice 确认门**：用户确认体验、目标品质与成本可接受，冻结制作基线后进入批产；不把漂亮效果图等同可玩切片。

## 5. production — 按批次制作

**阶段 skill**：`unity-game-production`；按任务读取 `unity-game-feature-delivery`、`unity-game-asset-production`、`unity-game-animation-vfx`、`unity-game-audio`。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-production-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `production` 审查实际版本。通过后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- 将功能与内容拆成有依赖的任务包，按最短可集成增量开发；独立 C# 模块、数值表、资源规格、测试和评审尽量并行。
- art-director 冻结规格，model-artist 承接源模型制作；technical-artist 承接基础 Sprite/贴图的制作或获取及 Unity 导入，动画/VFX 与音频交给对应角色。逐项登记实际源文件、独占路径、工具或外部作者、许可和“占位→制作/获取→导入→最终验收”证据；能力缺口交由主代理安排工具或外部制作，保留占位与待办。
- Scene/Prefab/项目设置指定单写者；跨模块接口先冻结再实现。每批次结束执行导入/编译、相关测试、构建或试玩与独立审查。
- 交付：功能增量、关卡/资源、缺陷和验收矩阵、变更日志。保留删减清单，新增范围必须同步里程碑。
- 退出：计划功能和内容达到 Alpha 定义，不以“所有任务已分派”代替已完成。

模型任务由model-artist按unity-game-modeling执行规格→外部DCC建模→UV/PBR→可选绑定/导出→模型审查；MCP/软件skill/CLI按真实可用能力接入。源场景副本、实际导出、纹理依赖、保存重开与哈希是交付证据，technical-artist单写Unity导入。

## 6. alpha — 功能完整

**阶段 skill**：`unity-game-alpha`；按任务读取 `unity-game-test-automation`、`unity-game-flow-regression`、`unity-game-testing`（含实际游玩、探索、视觉、复现、复测与独立测试审查）。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-alpha-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `alpha` 审查实际版本。通过后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- QA 依据需求验收矩阵覆盖新开局、完整流程、死亡/失败/重试、暂停/恢复、切场景、存档/读档、退出重进、异常输入。
- 对有迁移需求的项目验证历史存档；联网项目验证断线/重连与服务异常。建立缺陷等级、复现步骤、责任人与阻断条件。
- 交付：功能完整版本、缺陷表、测试/独立审查记录；删除功能同步 GDD 与范围。
- 退出：主流程闭环，发布阻断缺陷有清晰修复计划，Beta 内容与测试样本已定义。

## 7. beta — 平衡、优化与兼容

**阶段 skill**：`unity-game-beta`；按任务读取 `unity-game-balance-playtest`、`unity-game-performance`、`unity-game-compatibility`。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-beta-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `beta` 审查实际版本。通过后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- `playtest-analyst` 分析难度、引导、节奏和流失点；`systems-designer` 依据数据迭代，区分观察和推断。
- `performance-engineer` 在代表硬件和固定场景实测预算；优化前后同版本配置、同输入、同采样窗口比较。
- QA 回归目标平台、分辨率、手柄/键鼠/触屏、语言、字幕/色觉/按键重绑等项目承诺的能力。
- 交付：试玩、性能与兼容报告，最终缺陷状态和回归证据。
- 退出：发行承诺覆盖，预算实测达标或用户明确接受偏差；无实际设备的结果标明覆盖缺口。

## 8. release-ready — 候选包与发行

**阶段 skill**：`unity-game-release`；按任务读取 `unity-game-build-release`、`unity-game-store-publishing`、`unity-game-release-readiness`。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-release-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `release-ready` 审查实际版本。通过并取得 `release` 用户确认后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- `build-release-engineer` 固定源码、Editor、包版本、平台配置和构建命令；验证干净环境构建、安装、启动、版本号、存档兼容与回退。
- `publishing-manager` 准备商店描述、截图/视频、分级、隐私/数据声明、资源许可、价格/地区及客服路径；以渠道现行官方要求核对并保留日期。
- 交付：候选包及校验值、测试结果、商店素材、许可清单、版本说明、监控和回退方案。
- **release 确认门**：用户批准指定候选包、渠道、时间和已知风险。凭据或外部上传另行确认；批准准备材料不等于批准发布。

## 9. live — 发布运营与迭代

**阶段 skill**：`unity-game-liveops`；按任务读取 `unity-game-feedback-triage`、`unity-game-hotfix`、`unity-game-operations-review`。实际路径见 `references/skills.md` 与技能包目录。

**执行与审查**：由 `unity-game-liveops-execute` 执行本环节，专项任务随技能路径分派；独立 `game-reviewer` 使用 `unity-game-review` / profile `live` 审查实际版本。通过后才进入下游；修改退回原 skill/owner，证据缺口或无独立审查则停留。

- 记录实际发布版本、渠道、时间和可访问证据；离线发行也保留问题反馈与修复流程。
- 在隐私与平台要求内定义采集项、指标口径、保留期限和访问权；需要第三方服务时先确认费用及凭据。
- 按崩溃/存档损坏/阻断/一般问题分级，热修复经过复现→修复→回归→构建→发布确认，不跳过证据。
- 使用 `operations-retrospective.md` 汇总反馈、指标、成本和下一轮优先级；重大方向/平台/商业模式变化重新走相关确认门。

## 统一阶段记录

记录：阶段 ID、输入版本、任务/产物 ID、验证状态、日志/构建路径、独立审查结论、遗留问题、审批引用、下一步。阶段可因新证据回退；保留旧结果而非覆盖历史。只有 `passed` 证据支撑的项才勾选完成；`not_run` 与失败不能被“其他检查通过”冲抵。
