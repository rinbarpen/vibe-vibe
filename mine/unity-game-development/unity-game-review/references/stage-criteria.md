# 九阶段独立审查标准

按稳定 stage ID 查阅。先读项目需求/风险与本阶段约定的退出条件，以“实际交付能力”判断；以下是检查方向，不是在每阶段强加所有发行标准。每阶段均核对实际产物与来源版本/哈希、责任 owner/执行 skill、证据完整性。运行检查的真实记录和测试状态与独立审查 verdict 分开。

## discovery — 立项

- 设计：目标受众、玩家任务、差异化、预算/工期及明确不做项是否一致；高风险假设是否拆为可验证任务。
- 证据：竞品/受众判断能追溯来源和日期，观察与推断分开；已有工程/资源盘点真实存在，估算有依据。
- 退出：可执行的项目简报和风险验证顺序；尚未知事项显式列出而非虚构证实。此阶段通常不要求 Unity 运行。
- 回流：简报→`game-producer` / `unity-game-brief`；受众来源→`market-researcher` / `unity-game-market-research`；范围风险→`game-producer` / `unity-game-scope-risk`。

## design — 策划与方案

- 设计：核心循环与胜负/失败反馈闭合；规则/数值可推演；关卡节奏、UI 输入/可访问性、视听反馈引用同版 GDD。
- 工程/资产方案：TDD 对应项目平台、Editor/包、渲染管线、存档、性能预算和测试；资产规格给出真实生产路径与许可责任，不将占位当最终资产。
- 证据：代表性数值演算、方案权衡、里程碑依赖和原型验收条件可复核；需求冲突已有决策或阻断项。
- 退出：方向资料独立审查后仍须用户 `direction` 批准固定版本。仅设计交付不要求构建运行。
- 回流：玩法→`game-designer` / `unity-game-core-loop`；数值→`systems-designer` / `unity-game-systems-balance`；技术→`unity-architect` / `unity-game-technical-design`；资产方向→`art-director` / `unity-game-art-direction`。

## prototype — 原型

- 设计/代码：实际运行最小“输入→挑战→反馈→成败/再来”；验证最高风险假设，而非以类结构或截图代替可玩。
- 证据：工程/原型包与 revision 对应；测试日志和试玩任务/观察能支撑继续、调整或停止建议。占位资产可用，但须标明。
- 退出：约定闭环与风险已有真实运行证据；必需 Editor/设备/试玩缺失为 `blocked`。
- 回流：工程→`tools-programmer` / `unity-game-project-setup`；玩法→`gameplay-programmer` / `unity-game-playable-prototype`；试玩→`playtest-analyst` / `unity-game-prototype-playtest`。

## vertical-slice — 垂直切片

- 玩法/资产：代表性关卡把玩法、UI、美术、动画/VFX、音频、存档串起来；检查导入与 `.meta`、Prefab 引用、反馈同步、资源许可和新增内容成本。
- 证据：固定目标构建、目标设备性能基线、真实试玩、测试/构建原始日志；漂亮视频不代替可交互切片。
- 退出：生产链可复制，目标品质与成本有证据；独立通过后仍须用户 `vertical-slice` 确认。
- 回流：集成→`gameplay-programmer` / `unity-game-slice-integration`；切片专项复验→独立 `game-reviewer` / `unity-game-slice-review`；性能→`performance-engineer` / `unity-game-performance`。

## production — 批次制作

- 代码/设计：逐批对照冻结功能验收及接口；集成差异、错误路径、生命周期/存档兼容和相关测试真实覆盖。
- 资产：实际源资产、导入文件、许可、场景内效果齐备；规格完成、任务已分派或占位图不等于内容完成。
- 证据：导入/编译、相关测试、增量构建/试玩来源一致；跨批次影响有回归和剩余风险。
- 退出：本批次阻断修复并复审；仅已集成验证的批次进入下游。
- 回流：功能→`gameplay-programmer` / `unity-game-feature-delivery`；基础资产→`technical-artist` / `unity-game-asset-production`；模型→`model-artist` / `unity-game-modeling`（Unity导入→`technical-artist`）；动画→`animation-vfx-artist` / `unity-game-animation-vfx`；音频→`audio-designer` / `unity-game-audio`。

## alpha — 功能完整

- 功能：新开局、完整流程、死亡/失败重试、暂停恢复、切场景、退出重进及存档/迁移按需求贯通；联网场景按项目承诺验证。
- 证据：验收矩阵对应真实测试 XML/人工步骤、失败项和缺陷复现；零测试或只编译成功不代表回归通过。
- 退出：功能完整与遗留缺陷的阶段容忍度一致；遗留项保留 owner、修复版本和 Beta 验收，不改名隐藏阻断。
- 回流：实际游玩/缺陷复现/修复复测→`qa-engineer` / `unity-game-testing`；测试证据审查→独立 `game-reviewer` / `unity-game-test-review`；自动化→`qa-engineer` / `unity-game-test-automation`；流程存档→`qa-engineer` / `unity-game-flow-regression`；代码修复→对应 owner / `unity-game-feature-delivery`。

## beta — 平衡、性能与兼容

- 体验：难度/经济/引导调整有样本口径，观察与因果推断分开；避免以平均值隐藏卡关或付出成本。
- 性能：代表硬件、固定场景与窗口的 CPU/GPU/内存/加载实测；前后配置一致，不把编辑器帧率等同设备表现。
- 兼容：目标平台、分辨率、输入、语言及承诺的可访问性；不漏低配、长时与存档回归。
- 退出：预算与发行承诺有实测或明确的偏差决策；缺必需设备证据为 `blocked`。
- 回流：平衡→`systems-designer` / `unity-game-balance-playtest`；性能→`performance-engineer` / `unity-game-performance`；兼容→`qa-engineer` / `unity-game-compatibility`。

## release-ready — 发布候选

- 构建：冻结源码/Editor/包/配置、命令与输出校验值，干净环境可复现；真实安装启动、版本号、存档兼容及回退演练。
- 资产/发行：商店展示与包内行为一致；资源许可、分级、数据声明、地区/价格、客服按实际渠道官方要求核对日期。
- 证据：全部必需回归及已知风险绑定当前候选包，不能挪用旧候选测试；发布与回退权限清晰。
- 退出：独立通过仍须用户 `release` 确认具体候选包/渠道/时间/风险；上传和凭据操作另行确认。
- 回流：构建→`build-release-engineer` / `unity-game-build-release`；商店→`publishing-manager` / `unity-game-store-publishing`；发布清单→`game-producer` / `unity-game-release-readiness`。

## live — 发布运营

- 实际状态：渠道可访问版本、时间、包哈希与发布记录一致；未上传的包不记“已发布”。
- 问题/热修复：反馈分级可追溯，崩溃和存档问题有复现；修复通过回归、构建、独立复审及相应发布确认，回退条件可执行。
- 数据：采集项/口径/样本窗口与隐私承诺一致，复盘区分数据事实、解释和下一步假设。
- 退出：当前迭代结论对应实际版本；重大方向变化重新过相关用户门。
- 回流：反馈→`publishing-manager` / `unity-game-feedback-triage`；修复→`gameplay-programmer` / `unity-game-hotfix`；复盘→`game-producer` / `unity-game-operations-review`。
