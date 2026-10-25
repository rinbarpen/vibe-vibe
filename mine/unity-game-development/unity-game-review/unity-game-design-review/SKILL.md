---
name: unity-game-design-review
description: 独立评审 Unity 游戏立项、玩法规则、数值、关卡叙事、交互和技术方案的一致性；用于设计冻结、玩法变更及阶段设计验收，不负责实现修复。
---

# Unity 游戏设计审查

## 输入与执行

取得项目简报、同版 GDD/TDD、数值表、关卡/UI/视听规格、范围预算和当前阶段验收。对已实现体验同时取得固定可玩版本与试玩原始记录。

1. 以玩家完成一次核心循环为线索，追踪操作、挑战、信息、反馈、胜负与再来；列出规则冲突、不可达状态和未定义失败恢复，引用具体需求/设计位置。
2. 用实际公式和输入推演代表与边界数值：新手/中期/高阶、资源为零/溢出、奖励与成本循环；记录计算输入与结果，检查经济闭环及关卡节奏，不因“感觉平衡”批准。
3. 核对 UI 反馈、叙事目标、资产可读性、输入/可访问性与玩法一致；比较 TDD 的平台、存档、性能和资源方案是否支持承诺，核对里程碑及团队成本。
4. discovery 查来源、范围与风险假设；design 查完整规则和可验证原型验收；prototype 查运行是否回答风险；vertical-slice 查体验/成本可复制；production 查增量是否违背基线；alpha 查功能完整定义；beta 查平衡调整有真实样本；release-ready 查展示与实际承诺一致；live 查反馈与迭代是否变更既定方向。
5. 设计阶段可基于文档/可复算模型评审；要求可玩性的阶段须检查真实操作/试玩证据，缺失记 blocked。不把假设、设计意图或他人摘要当运行观察。

## 修复交接

玩法规则交 `game-designer` + `unity-game-core-loop`，数值交 `systems-designer` + `unity-game-systems-balance`，关卡叙事交 `level-designer` / `narrative-designer` + `unity-game-level-narrative`，UI 交 `ui-ux-designer` + `unity-game-ui-ux`，技术矛盾交 `unity-architect` + `unity-game-technical-design`。具体任务必须落到实际 agent/人员 owner，不只返回角色列表。

## 审查边界与交付

使用 `game-reviewer` 的独立代理上下文，不评审自己实现的内容；只写分配的审查报告，不修改实现、资产或共享阶段状态。有 manifest 时先读 `.unity-game/state/`，输出到 producer 分配的 `.unity-game/deliverables/` 独占路径；独立安装使用指定目录，默认 `docs/unity-game/`。不依赖父技能文件；沿用实际项目版本、平台与工具。

接收冻结需求/验收、实际产物、revision/差异与源码及产物 SHA-256、实现 owner、原始证据。直接检查源材料；记录每项具体检查、命令/输入/退出码或人工操作、实际输出和证据路径/哈希。源码有未提交差异时绑定逐文件哈希。审查者缺席由主代理记录 `review_status: not_run`，不以实现者自查批准；审查者存在但必需材料缺失记 `blocked`。

报告写明 stage、reviewer/实现 owner 与独立性、reviewed_revision、source_hashes、artifact_hashes、requirements_version、checks、issues、report_path、previous_report、approved_revision。`verdict` 为 `passed` / `changes_requested` / `blocked`：完整证据且无阻断项才通过；确定缺陷需修复为 changes_requested；缺必需证据导致判断无依据为 blocked。仅 passed 填 approved_revision，批准仅覆盖该 revision/哈希。测试状态另记 `passed` / `failed` / `not_run`，不充当审查 verdict；必需运行缺失导致审查 blocked，设计任务未要求的运行可注明不适用及理由。

问题按 critical/major（阻断）、minor/suggestion（非阻断）分级并写清理由，附需求、位置/时间点、预期/实际、复现、原始证据、**确切 owner + 执行 skill + 复验条件**。owner 未定退回 producer 分配。原 owner 调用执行 skill 修复→新 revision/证据→独立复审；保留历史问题及报告链接，不修改原实现来“完成审查”。报告保存后重读确认并回传 SHA-256。direction、vertical-slice、release 用户确认门与 review passed 分离，评审不代替用户批准。
