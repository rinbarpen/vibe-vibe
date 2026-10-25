---
name: unity-game-prototype-execute
description: 实际准备 Unity 工程、实现最小可玩闭环并执行原型试玩，以运行证据和独立审查验证玩法假设。
---

# Unity 可玩原型执行

## 执行边界与状态

这是执行 skill，不是角色说明：宿主实际读取本文件后，用可用工具完成下面的产物与验证。skill 名不是工具，文字“调用”不代表已执行；只有真正读入技能、委派成功或工具结果才记为执行。先识别用户请求的是完整阶段还是局部任务，只完成本次承诺，不自动跑整条生命周期。

复用既有工程版本、包、平台与已批准决策，不硬编码 Unity 版本或擅自升级。存在 `.unity-game/` 时，产物放 `.unity-game/deliverables/`，主代理单写共享 state/tasks/decisions；子代理仅写被分配的产物和证据。独立安装默认 `docs/unity-game/` 或用户指定目录；本文件含独立执行方法，不依赖其他技能或模板已安装。文档先写临时文件再原子替换。

任务单必须有任务 ID、输入修订、原执行 skill、owner、可写路径、依赖、验收与回传证据。真正具备 subagent 工具时才委派下表角色，按宿主并发上限分配不重叠文件；没有时由主代理按同一契约串行实现并如实记录。Scene、Prefab、序列化资源、项目配置及 `.meta` 单写，同工程 Editor 导入/测试/构建串行；资源与 `.meta` 成对保留。

## 输入与就绪

本轮假设、核心循环、时间上限、实际工程或明确的新建请求、运行平台与验收路径。完整流程先检查 direction 用户确认；局部原型只冻结本次假设和排除项。

## 专项方法与任务所有权

若阶段/整包同时安装，按当前缺口读取本执行技能父目录中的 `<下表 skill>/SKILL.md`，每个都是可选专项方法；只装本 skill 时直接执行下一节等价方法。不要求无关技能或不存在的相对链接。多角色任务拆成明确单一 owner 的子任务，不能共同抢写。

| 原执行 skill（安装时实际读取） | 建议 subagent | 本轮交付 |
|---|---|---|
| `unity-game-project-setup` | `unity-architect / tools-programmer` | project-setup.md；版本、包、入口和运行条件 |
| `unity-game-playable-prototype` | `gameplay-programmer` | 代码/灰盒、prototype-notes.md 与闭环运行证据 |
| `unity-game-prototype-playtest` | `playtest-analyst` | prototype-playtest.md；观察、玩家反馈与下一步判断 |

未安装专项 skill 时，任务单原执行 skill 记 `unity-game-prototype-execute`，由对应角色按本文件方法执行；不能把未读取的专项记成已调用。

## 实际执行

1. 读取 ProjectVersion、包锁定、场景入口和输入实现；新工程沿用户选择的 Editor/模板创建。定位已有测试/构建入口；若存在辅助 CLI，先查看实际 --help 再使用，不假设安装就绪。
2. 先做最高风险小实验，再实现进入→操作→挑战反馈→成败→重试的最短链路。纯逻辑、灰盒与 UI 可独立实现；唯一场景写者装配并处理暂停、重载和事件重复注册。
3. 排队执行 Editor 导入、EditMode 规则测试、PlayMode/人工闭环与目标平台可用的构建。记录干净启动、完整一局及重试的实际操作、反馈与错误日志。占位资产标记来源和替换责任。
4. 让试玩角色按假设组织真实观察，分开观察事实、解释和新假设；保存参与者条件、构建标识与试玩记录。没有玩家时提交试玩方案并将对应结果保留 not_run，不伪造反馈。

## 本阶段交付与推进

实际代码/场景和可用构建、工程说明、风险实验、EditMode/PlayMode 结果、真实试玩及 `prototype-summary.md`；没有可运行闭环证据时不宣称原型可玩。记录临时代码债务与继续/调整建议。

必要闭环、实验和试玩证据经审查通过后，由主代理决定保留/调整原型并交接 vertical-slice；未通过的玩法假设先迭代，不用新美术遮盖。

## 独立 reviewer 与返工闭环

1. 冻结本次提交/文件哈希、任务单及证据，生成 `prototype-execution-rN.md`：范围、任务→原执行 skill/owner、实际产物、命令/输入/字面结果/退出码、未运行项、风险、版本与回退。仅使用真实执行得到的 `passed` / `failed` / `not_run`，静态检查不替代运行。
2. 若已安装 `unity-game-review`，实际读取该技能，再由独立 `game-reviewer` 以 profile `prototype` 审查本次范围和固定修订。该 skill 不存在时，在新独立 reviewer 上下文执行同样的任务验收：检查输入→产物→证据、独立复现关键检查、给 finding ID/严重度/文件与复现/原执行 skill 和 owner/验收条件，并给 `passed`、`changes_requested` 或 `blocked`。新 reviewer 不承担实现；实现者自检不冒充独立审查。宿主没有独立上下文能力时输出待审查包、注明独立审查未执行，保持阶段不推进。
3. `changes_requested` 必须携 finding ID 回到任务单记录的**原执行 skill + 原 owner**修复；不要重派 reviewer 实现或换技能掩盖问题。生成新修订，重跑受影响验证，独立 reviewer 针对新修订复审；重复返工无新证据时记录原因和待决事项，避免无界重试。
4. `blocked` 或必需运行证据 `not_run` 时，交付已完成部分和具体恢复步骤，阶段原地保持。只有独立审查 `passed` 后由主代理写阶段完成/下一步建议；完整流程还须遵守本阶段用户门。局部任务只验收本次范围，不据此宣称整个阶段通过。
