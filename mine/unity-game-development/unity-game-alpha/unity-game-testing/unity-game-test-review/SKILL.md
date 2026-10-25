---
name: unity-game-test-review
description: 独立只读审查 Unity 游戏实际测试的覆盖、输入轨迹、运行证据、缺陷复现与修复复验，对明确版本给出通过、返工或证据阻塞结论。
---

# 独立游戏测试审查

仅由与测试执行者、实现者不同的 `game-reviewer` 上下文执行；只写分配的审查报告，构建/源码/原存档和共享任务状态只读。独立安装即可使用，无需父级文件。

## 实际审查

1. 接收测试范围/阶段必需标准、计划和覆盖矩阵、需求版本、源码 revision/dirty 哈希、构建 SHA-256、环境与种子、实际工具/skill 路径和版本、原始动作/日志/截图、缺陷与复验报告、实现和测试 owner。直接重读原始证据并核对文件哈希，不仅阅读执行者总结。
2. 检查需求→用例→实际执行→原始证据链，区分 `planned`、环境诊断、自动测试、真实游戏输入、辅助状态注入、人工玩家和目标设备测试。Unity 场景读取/Transform 修改、debug teleport 或工具返回 success 不足以证明正常玩家路径；WebGL 仅 DOM 存在也不足，须有 canvas 画面与实际输入反馈。
3. 核对每段输入的真实工具/schema、启动与窗口/画布目标、时间戳、参数、按下/保持时长/释放、expected/actual 和画面/日志对应；检查有界预算、重试是否完整记录、异常后输入是否释放、隔离测试数据和恢复结果。真实存档/账号改写或未确认外部操作列明确问题，不把清理缺失藏进总体通过。
4. 检查用例结论是否符合证据：确定产品偏差为 `failed`，环境/设备/输入缺失为 `not_run`；计划不算运行。AI 观察不当作人工乐趣反馈；无音频捕获、Profiler/设备采样时不能批准声音或性能指标。未测项与不适用项需分别说明，并由阶段承诺决定是否阻断。
5. 对修复核对原失败证据、新构建来源、相同复现条件、实际复验和受影响回归、波动重复次数；旧版本通过不批准新修改。需要独立复验时在隔离副本按真实通道和有界步骤操作，保存新轨迹并遵守同实例单写；缺工具则记录 `not_run`，不臆造重放成功。

## 结论与回流

`review_status` 为 `pending` / `completed` / `not_run`，执行后 `verdict` 为 `passed` / `changes_requested` / `blocked`：必需证据齐全且无未决阻断项才通过；已证问题返工；必需材料或执行环境缺失导致判断不足则 blocked，并保留已发现问题。各运行 check 的 `passed` / `failed` / `not_run` 与 verdict 分开。缺独立 reviewer 时由 producer 记审查 `not_run`，自查不冒充独立批准。

每条 issue 包含严重度/阻断理由、需求/用例、对象与时间点、expected/actual、原始证据、确切 owner + 执行 skill + 复验条件。覆盖/用例缺口交 `qa-engineer` + `unity-game-test-plan`；输入执行、探索、画面、复现和复验缺口交 QA 的相应 `unity-game-play-execution`、`unity-game-exploratory-testing`、`unity-game-visual-testing`、`unity-game-bug-reproduction`、`unity-game-fix-verification`；产品缺陷交原实现 owner + 原执行 skill，再由 QA 复验。owner 未定交 producer，不由 reviewer 修改实现。

报告绑定 `reviewed_revision`、源码/构建/证据哈希、需求版本、实现/测试/reviewer 身份与独立性、checks、issues、previous_report、report_path；仅 passed 填 `approved_revision`。保存到 producer 指定 `.unity-game/deliverables/testing/<run-id>/`，独立默认 `docs/unity-game/testing/<run-id>/` 或指定目录，重读并回传 SHA-256。新 revision 修复后重新审查，保留旧报告；此测试专项报告不自行批准整个阶段或替代用户方向、切片和发布确认。
