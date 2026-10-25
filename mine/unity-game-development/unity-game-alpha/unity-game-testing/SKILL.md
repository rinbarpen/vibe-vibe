---
name: unity-game-testing
description: 实际操作并测试 Unity 游戏时使用，编排测试计划、真实输入试玩、探索与画面检查、缺陷复现、修复复验和独立测试审查；适用于原型到发行及热修复，不限 Alpha。
---

# 游戏测试：从实际输入到独立结论

`qa-engineer` 主持执行，`game-reviewer` 在独立上下文审查。此技能补足“实际玩游戏”的测试链，不把 EditMode/PlayMode 自动测试、场景检查或计划文档等同于完整的可玩性验收。

## 按任务加载实际执行技能

| 目标 | 执行 skill | 主要 owner |
|---|---|---|
| 把需求与风险变成可执行用例 | [unity-game-test-plan](unity-game-test-plan/SKILL.md) | `qa-engineer` |
| 启动游戏，用真实输入走验收路径 | [unity-game-play-execution](unity-game-play-execution/SKILL.md) | `qa-engineer` |
| 在有界时间内探索未知问题 | [unity-game-exploratory-testing](unity-game-exploratory-testing/SKILL.md) | `qa-engineer` |
| 检查实际渲染画面、UI 与分辨率 | [unity-game-visual-testing](unity-game-visual-testing/SKILL.md) | `qa-engineer`，协作 `ui-ux-designer` / `art-director` |
| 把异常缩成最小可复现步骤 | [unity-game-bug-reproduction](unity-game-bug-reproduction/SKILL.md) | `qa-engineer` |
| 用原失败步骤与受影响回归复验修复 | [unity-game-fix-verification](unity-game-fix-verification/SKILL.md) | `qa-engineer` |
| 独立核对覆盖、证据及未决问题 | [unity-game-test-review](unity-game-test-review/SKILL.md) | 独立 `game-reviewer` |

只请求某一检查时直接执行对应子技能；完整任务按“计划→执行/探索/画面→复现→owner 修复→复验→独立审查”接力。修复交原功能 owner 和原执行 skill，不由测试或 reviewer 静默修改游戏来得到绿灯。`playtest-analyst` 可协作操作难点与可用性分析；AI 操作结果不替代真实玩家的乐趣、理解、留存和主观反馈。

## 启动与实际操作通道

1. 读取当前需求、阶段标准、已知缺陷、构建来源和项目约定。绑定源码 revision / dirty 文件哈希、构建 SHA-256、Unity/包/平台版本、设备/分辨率/输入法、种子、存档基线和可用预算；没有某项就记录缺口，不编造值。
2. 发现实际可用的已连接 MCP 工具及输入 schema、项目现有测试/输入 harness、已安装原生 GUI skill，或 WebGL 项目的现有浏览器 skill；按该工具/skill 真实说明操作，不凭名称猜测 API 或启动额外服务。Unity 场景读取、修改 Transform 或调试传送不是玩家输入覆盖；记录为辅助诊断并另走正常输入路径。
3. 从隔离工程/构建、临时用户数据与测试存档启动；保留原文件哈希、备份和恢复步骤。使用虚构隔离测试数据，不覆盖真实存档或账号；联网、凭据、付费和对外操作在相应动作前单独确认，未确认的路径保留待验。
4. 给任务包指定依赖、独占报告目录、用例、预期、时间/动作/重试上限和停止条件。同一游戏实例、Editor 和输入焦点单写串行；不同隔离实例或不同证据的只读分析可并行。
5. 实际执行后保存逐步输入、按键按下/保持时长/释放、时间戳、截图/视频定位、日志、实际状态和预期；停止或异常时释放所有已按下输入并恢复测试数据，记录恢复结果。按用例输出 `passed` / `failed` / `not_run`，只写了计划的用例标 `planned` 且执行为 `not_run`。

## 交付与边界

有 manifest 时使用 producer 分配的 `.unity-game/deliverables/testing/<run-id>/`；否则使用指定目录，默认 `docs/unity-game/testing/<run-id>/`。交付计划/覆盖矩阵、工具能力清单、执行轨迹、原始日志和截图、缺陷、修复复验与独立审查报告。报告保存后重读，回传路径与 SHA-256；共享任务、阶段和批准仍由主代理单写。

缺少可执行输入通道时，完成环境诊断与可运行用例设计，将游戏执行记 `not_run`；工具连接失败与游戏缺陷分别记录。AI 观察只覆盖实际时段和条件；未接入音频、Profiler、真实设备或人工玩家时，对应声音、性能、设备与人工试玩检查分别保留 `not_run`。独立审查 verdict 使用 `passed` / `changes_requested` / `blocked`，与运行状态分开；本链结果不自行通过阶段或用户确认门。
