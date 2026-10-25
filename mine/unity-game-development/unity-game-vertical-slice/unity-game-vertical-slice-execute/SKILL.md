---
name: unity-game-vertical-slice-execute
description: 实际集成代表性可玩内容、最终视听和目标平台品质证据，独立审查后形成 Unity 量产基线。
---

# Unity 垂直切片执行

## 执行边界与状态

这是执行 skill，不是角色说明：宿主实际读取本文件后，用可用工具完成下面的产物与验证。skill 名不是工具，文字“调用”不代表已执行；只有真正读入技能、委派成功或工具结果才记为执行。先识别用户请求的是完整阶段还是局部任务，只完成本次承诺，不自动跑整条生命周期。

复用既有工程版本、包、平台与已批准决策，不硬编码 Unity 版本或擅自升级。存在 `.unity-game/` 时，产物放 `.unity-game/deliverables/`，主代理单写共享 state/tasks/decisions；子代理仅写被分配的产物和证据。独立安装默认 `docs/unity-game/` 或用户指定目录；本文件含独立执行方法，不依赖其他技能或模板已安装。文档先写临时文件再原子替换。

任务单必须有任务 ID、输入修订、原执行 skill、owner、可写路径、依赖、验收与回传证据。真正具备 subagent 工具时才委派下表角色，按宿主并发上限分配不重叠文件；没有时由主代理按同一契约串行实现并如实记录。Scene、Prefab、序列化资源、项目配置及 `.meta` 单写，同工程 Editor 导入/测试/构建串行；资源与 `.meta` 成对保留。

## 输入与就绪

原型结论、设计方向、范围、代表内容、目标设备和性能/视听预算。先选择能暴露真实生产难度的一段玩法，不能只选展示性场景；局部集成请求只执行该切片。

## 专项方法与任务所有权

若阶段/整包同时安装，按当前缺口读取本执行技能父目录中的 `<下表 skill>/SKILL.md`，每个都是可选专项方法；只装本 skill 时直接执行下一节等价方法。不要求无关技能或不存在的相对链接。多角色任务拆成明确单一 owner 的子任务，不能共同抢写。

| 原执行 skill（安装时实际读取） | 建议 subagent | 本轮交付 |
|---|---|---|
| `unity-game-slice-integration` | `gameplay-programmer / technical-artist` | 代表场景、资源链、目标构建及性能采样 |
| `unity-game-slice-review` | `game-reviewer` | slice-review.md；固定版本的品质、产能与未验项 |

未安装专项 skill 时，任务单原执行 skill 记 `unity-game-vertical-slice-execute`，由对应角色按本文件方法执行；不能把未读取的专项记成已调用。

## 实际执行

1. 把切片验收写成一条可体验路线，覆盖最终玩法、UI、视听反馈、加载与目标设备指标；冻结接口和代表关卡范围。制作简单耗时表，区分一次性工具成本和单位内容成本。
2. 并行派代码、源美术、音频与 UI 文件，分别指定 gameplay-programmer、technical-artist、audio-designer、ui-ux-designer。唯一集成人员串行装配场景、Prefab、材质、音频事件和 .meta。
3. 执行导入/缺脚本与引用检查、代表路线运行、目标配置构建和目标设备采样；记录资源从源文件到导入结果的实际步骤与工时，证明流水线可复制。
4. 冻结切片提交及构建哈希，将路线录像、测试、性能、单位内容成本和残余风险交给独立 reviewer；对根本玩法失败退回原型，对局部品质问题修复具体模块，不扩大内容掩盖。

## 本阶段交付与推进

代表性场景/资源/可玩构建、流水线说明和实测工时、运行与性能记录、`vertical-slice-summary.md`；运行证据与产能证据分别验收，纯展示截图不替代完整切片。

审查通过后主代理向用户展示该固定切片与风险，取得 `vertical-slice` 明确确认才批量 production；独立切片审查任务仅返回结论。

## 独立 reviewer 与返工闭环

1. 冻结本次提交/文件哈希、任务单及证据，生成 `vertical-slice-execution-rN.md`：范围、任务→原执行 skill/owner、实际产物、命令/输入/字面结果/退出码、未运行项、风险、版本与回退。仅使用真实执行得到的 `passed` / `failed` / `not_run`，静态检查不替代运行。
2. 若已安装 `unity-game-review`，实际读取该技能，再由独立 `game-reviewer` 以 profile `vertical-slice` 审查本次范围和固定修订。该 skill 不存在时，在新独立 reviewer 上下文执行同样的任务验收：检查输入→产物→证据、独立复现关键检查、给 finding ID/严重度/文件与复现/原执行 skill 和 owner/验收条件，并给 `passed`、`changes_requested` 或 `blocked`。新 reviewer 不承担实现；实现者自检不冒充独立审查。宿主没有独立上下文能力时输出待审查包、注明独立审查未执行，保持阶段不推进。
3. `changes_requested` 必须携 finding ID 回到任务单记录的**原执行 skill + 原 owner**修复；不要重派 reviewer 实现或换技能掩盖问题。生成新修订，重跑受影响验证，独立 reviewer 针对新修订复审；重复返工无新证据时记录原因和待决事项，避免无界重试。
4. `blocked` 或必需运行证据 `not_run` 时，交付已完成部分和具体恢复步骤，阶段原地保持。只有独立审查 `passed` 后由主代理写阶段完成/下一步建议；完整流程还须遵守本阶段用户门。局部任务只验收本次范围，不据此宣称整个阶段通过。
