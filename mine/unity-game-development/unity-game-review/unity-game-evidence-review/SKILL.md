---
name: unity-game-evidence-review
description: 独立核验 Unity 各阶段交付的原始测试、构建、设备、试玩、发行与运营证据及版本一致性；用于阶段退出、发布候选和审查证据追溯。
---

# Unity 游戏证据审查

## 输入与执行

取得阶段验收矩阵、冻结需求/源码与产物哈希、原始命令/输入/日志、测试 XML、构建包、设备/试玩记录和已知缺口；不得只接收“全部通过”摘要。

1. 建立每项验收→实际产物→检查方法→原始结果→来源 revision/哈希的链，检查路径可读、时间/平台/配置一致；旧证据只有适用性与来源可证明才复用。
2. 自动化核对命令/输入/退出码及字面输出，解析 XML 的总数/失败/跳过；零测试、缺 XML、日志截断、超时和退出码 0 但产物不存在均单独列出。构建需核对实际输出和校验值，不推断编译成功就是可安装。
3. 人工试玩/性能核对设备、构建、场景、采样窗口、任务/操作、原始观察与视频时间点；区分事实、推断和缺失覆盖，人工操作不伪造命令退出码。
4. discovery 检查来源/日期和风险依据；design 检查数值演算/决策/原型验收；prototype 检查最小闭环真实运行；vertical-slice 检查目标设备、可玩构建和成本；production 检查批次集成；alpha 检查流程与存档回归；beta 检查样本、同条件性能及平台覆盖；release-ready 检查干净构建、安装、回退及渠道资料；live 检查实际渠道可访问版本、反馈、数据口径与热修复链。
5. 缺必需运行环境/记录时，对应 test_status 为 not_run、review verdict 为 blocked；已知运行失败记 failed 并返回缺陷。未授权外部上传不执行，发布准备批准和“已发布”严格区分。

## 修复交接

先向产物确切 owner 请求原始证据；测试交 `qa-engineer` + `unity-game-test-automation` / `unity-game-flow-regression`，性能交 `performance-engineer` + `unity-game-performance`，试玩交 `playtest-analyst` + `unity-game-balance-playtest`（原型用 `unity-game-prototype-playtest`），构建交 `build-release-engineer` + `unity-game-build-release`，渠道/运营交 `publishing-manager` + `unity-game-store-publishing` / `unity-game-feedback-triage`。证据不足不是让 reviewer 编造或替实现者补写成功记录；owner 补交新版本后再独立核验。

## 审查边界与交付

使用 `game-reviewer` 的独立代理上下文，不评审自己实现的内容；只写分配的审查报告，不修改实现、资产或共享阶段状态。有 manifest 时先读 `.unity-game/state/`，输出到 producer 分配的 `.unity-game/deliverables/` 独占路径；独立安装使用指定目录，默认 `docs/unity-game/`。不依赖父技能文件；沿用实际项目版本、平台与工具。

接收冻结需求/验收、实际产物、revision/差异与源码及产物 SHA-256、实现 owner、原始证据。直接检查源材料；记录每项具体检查、命令/输入/退出码或人工操作、实际输出和证据路径/哈希。源码有未提交差异时绑定逐文件哈希。审查者缺席由主代理记录 `review_status: not_run`，不以实现者自查批准；审查者存在但必需材料缺失记 `blocked`。

报告写明 stage、reviewer/实现 owner 与独立性、reviewed_revision、source_hashes、artifact_hashes、requirements_version、checks、issues、report_path、previous_report、approved_revision。`verdict` 为 `passed` / `changes_requested` / `blocked`：完整证据且无阻断项才通过；确定缺陷需修复为 changes_requested；缺必需证据导致判断无依据为 blocked。仅 passed 填 approved_revision，批准仅覆盖该 revision/哈希。测试状态另记 `passed` / `failed` / `not_run`，不充当审查 verdict；必需运行缺失导致审查 blocked，设计任务未要求的运行可注明不适用及理由。

问题按 critical/major（阻断）、minor/suggestion（非阻断）分级并写清理由，附需求、位置/时间点、预期/实际、复现、原始证据、**确切 owner + 执行 skill + 复验条件**。owner 未定退回 producer 分配。原 owner 调用执行 skill 修复→新 revision/证据→独立复审；保留历史问题及报告链接，不修改原实现来“完成审查”。报告保存后重读确认并回传 SHA-256。direction、vertical-slice、release 用户确认门与 review passed 分离，评审不代替用户批准。
