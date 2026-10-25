---
name: unity-game-review
description: 独立评审 Unity 游戏九阶段的设计、实现、资产和验收证据，派发专项 reviewer，形成带版本绑定的问题清单及修复复审闭环；用于阶段退出或增量交付审查。
---

# Unity 游戏独立审查

由 `game-reviewer` 主持，按任务加载设计、代码、资产、证据子技能。**执行 skill 负责产出，review skill 负责独立判断**，角色名称、执行者自查或一份测试成功摘要均不代表审查完成。

## 开始审查

- 接收阶段 ID、冻结需求与验收条件、实际产物、源码 revision/差异与 SHA-256 清单、构建来源、原始日志/测试 XML/设备采样，以及实现者身份和任务所有权。直接检查原始材料，不只读实现者总结。
- 读取 [阶段标准](references/stage-criteria.md) 中当前阶段一节；只评估当前目标，避免把原型按正式发行包标准验收。保留项目既有 Unity、包和平台版本。
- 审查者与实现者使用不同代理上下文。实现者可说明复现环境，审查判断和结论由独立 reviewer 完成；`game-reviewer` 自身实现的内容另派独立上下文评审。
- 若宿主缺独立 reviewer，主代理记录 `review_status: not_run` 和阻塞原因，不得以自查替代批准；已有独立 reviewer 但缺必需材料，结论记 `blocked`。
- 有 manifest 时读取 `.unity-game/state/`，在 producer 分配的 `.unity-game/deliverables/` 写独占审查报告；独立安装默认 `docs/unity-game/` 或用户指定目录。共享状态、阶段和用户审批由主代理单写，reviewer 只返回候选状态。

## 按实际变化选择子技能

| 内容 | 子技能 | 适用范围 |
|---|---|---|
| 用户价值、规则、范围及方案 | [设计审查](unity-game-design-review/SKILL.md) | 立项/策划必选；原型、切片、玩法调整、运营方向变化时选用 |
| C#、配置、存档及构建逻辑 | [代码审查](unity-game-code-review/SKILL.md) | 工程建立起按增量选用；测试与热修复同时检查回归 |
| 美术/UI、音频、动画/VFX及导入 | [资产审查](unity-game-asset-review/SKILL.md) | 对实际资产和工程内表现审查；仅规格阶段只评规格 |
| 日志、测试、设备、发行/运营凭据 | [证据审查](unity-game-evidence-review/SKILL.md) | 九阶段均执行，使用当前阶段适用证据而非统一要求全部运行 |

独立内容可并行审查，子报告绑定同一冻结 revision；同一 Unity 工程的 Editor 操作串行。对没有变化/不适用的领域记录理由，避免为了凑角色产生空报告。独立安装子技能时，它们不依赖父目录文件。

## 结论、问题回流与复审

1. 建立需求→产物→具体检查→原始证据矩阵；注明检查命令、输入、退出码、输出路径/关键原文、设备配置与采样窗口，人工操作注明步骤及截图/视频时间点。
2. 分级：`critical` 是崩溃、存档损坏、范围/发行边界破坏等阻断；`major` 是承诺功能/质量条件未满足的阻断；`minor` 是不影响阶段承诺的非阻断问题；`suggestion` 是偏好或改进建议。问题都附阻断理由，项目已有分级可映射采用。
3. 审查 verdict 仅为 `passed`、`changes_requested`、`blocked`：必需证据齐全且无未解决阻断项才 `passed`；已确认缺陷需修复为 `changes_requested`；缺必需材料/环境导致判断无依据为 `blocked`。同时存在缺陷和证据缺口时以 `blocked` 汇总并保留已确认问题。
4. 测试执行状态单列 `passed` / `failed` / `not_run`；不能拿它们代替审查结论。阶段要求真实运行时，缺 Editor、设备、XML 或运行日志使该验收 `not_run`、审查 `blocked`；文档阶段未要求的运行检查可标 `not_applicable` 并说明依据。
5. 每个问题给出 ID、严重度/是否阻断、需求、文件/对象/行或时间点、预期/实际、复现步骤、原始证据、**确切 owner、需执行的 skill、验收条件**。未分配 owner 时退给 producer 明确，不把“开发团队”当责任人。
6. producer 将问题交回原 owner，用对应执行 skill 修复，生成新 revision 和证据；reviewer 不修改实现。重新检查修复、新增差异和受影响回归，形成新报告并链接旧报告；未受影响证据仅在来源和适用性可证明时复用。批准只覆盖报告中的具体 revision 与产物哈希。

## 交付契约

报告包含 `stage`、`reviewer`/`implementation_owner` 及独立性说明、`review_status`（`pending` / `completed` / `not_run`）、`verdict`（执行后填写）、`reviewed_revision`、`source_hashes`、`artifact_hashes`、`requirements_version`、`checks`、`issues`、`report_path`、`previous_report`、`approved_revision`。仅 `passed` 时填写 `approved_revision`，其余留空；源码不干净时绑定逐文件哈希而不是只写 HEAD。

每项 check 包含验收条件、实际检查与结果、原始证据路径/哈希、测试状态、版本/平台限制；每项 issue 按上述字段填写。报告自身使用独占路径保存后重读确认，附 SHA-256；向 producer 返回路径、结论、阻断项和复审任务。

`direction`、`vertical-slice`、`release` 三个人工确认门仍由用户对固定版本确认；独立审查 `passed` 不替代用户批准，也不授权采购、凭据使用或外部发布。
