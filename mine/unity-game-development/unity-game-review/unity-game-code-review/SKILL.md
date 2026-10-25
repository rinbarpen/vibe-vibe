---
name: unity-game-code-review
description: 独立评审 Unity C#、项目配置、存档与构建增量的正确性及回归证据；用于原型实现、功能批次、Alpha、候选包和热修复代码审查。
---

# Unity 游戏代码审查

## 输入与执行

取得固定源码 revision/逐文件哈希、差异、接口/需求、项目版本与包锁定、受影响场景/Prefab、原始编译和测试日志。按具体变化审查，避免对纯策划任务强加代码门。

1. 从需求追踪实际调用和场景引用，不只读 diff；检查生命周期、事件订阅与清理、销毁对象、帧率/时间依赖、暂停/切场景、边界输入和异常路径。对异步任务核对取消及对象销毁后的访问。
2. 对存档/版本迁移检查真实历史样本、部分写入、损坏恢复与回退；对项目实际联网功能查断线重连和幂等，离线项目不追加服务端要求。
3. 核对序列化字段变化、GUID/资源引用、Prefab 覆盖、包与平台配置变更；资产及 .meta 应成对，避免以手改 YAML/GUID 掩盖导入问题。只读审查，不替实现者修改场景。
4. 对照受影响逻辑检查 EditMode/PlayMode 原始 XML：测试数量、失败与跳过、测试本身是否真正触发路径；零测试或仅进程退出 0 不代表通过。同一工程的 Editor 验证串行，使用隔离副本运行以保持被审版本冻结。
5. prototype 侧重闭环/风险；production 侧重接口/增量/集成；alpha 侧重流程/存档；beta 侧重性能改动回归和平台差异；release-ready 查构建入口、配置、版本及回退；live 查最小修复范围和历史数据兼容。discovery/design 仅在存在工程/技术样例时审实际代码，不凭架构图声称运行通过。

## 修复交接

功能交 `gameplay-programmer` + `unity-game-feature-delivery`（原型用 `unity-game-playable-prototype`，热修复用 `unity-game-hotfix`）；Editor 工具交 `tools-programmer` + `unity-game-project-setup`；测试缺陷交 `qa-engineer` + `unity-game-test-automation` / `unity-game-flow-regression`；构建交 `build-release-engineer` + `unity-game-build-release`。附精确位置、最小复现和受影响回归，不直接提交修复。

## 审查边界与交付

使用 `game-reviewer` 的独立代理上下文，不评审自己实现的内容；只写分配的审查报告，不修改实现、资产或共享阶段状态。有 manifest 时先读 `.unity-game/state/`，输出到 producer 分配的 `.unity-game/deliverables/` 独占路径；独立安装使用指定目录，默认 `docs/unity-game/`。不依赖父技能文件；沿用实际项目版本、平台与工具。

接收冻结需求/验收、实际产物、revision/差异与源码及产物 SHA-256、实现 owner、原始证据。直接检查源材料；记录每项具体检查、命令/输入/退出码或人工操作、实际输出和证据路径/哈希。源码有未提交差异时绑定逐文件哈希。审查者缺席由主代理记录 `review_status: not_run`，不以实现者自查批准；审查者存在但必需材料缺失记 `blocked`。

报告写明 stage、reviewer/实现 owner 与独立性、reviewed_revision、source_hashes、artifact_hashes、requirements_version、checks、issues、report_path、previous_report、approved_revision。`verdict` 为 `passed` / `changes_requested` / `blocked`：完整证据且无阻断项才通过；确定缺陷需修复为 changes_requested；缺必需证据导致判断无依据为 blocked。仅 passed 填 approved_revision，批准仅覆盖该 revision/哈希。测试状态另记 `passed` / `failed` / `not_run`，不充当审查 verdict；必需运行缺失导致审查 blocked，设计任务未要求的运行可注明不适用及理由。

问题按 critical/major（阻断）、minor/suggestion（非阻断）分级并写清理由，附需求、位置/时间点、预期/实际、复现、原始证据、**确切 owner + 执行 skill + 复验条件**。owner 未定退回 producer 分配。原 owner 调用执行 skill 修复→新 revision/证据→独立复审；保留历史问题及报告链接，不修改原实现来“完成审查”。报告保存后重读确认并回传 SHA-256。direction、vertical-slice、release 用户确认门与 review passed 分离，评审不代替用户批准。
