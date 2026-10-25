---
name: unity-game-production-execute
description: 按 Unity 已确认基线实际交付功能、资源、动画特效和音频批次，集成回归并经独立审查后完成批次。
---

# Unity 正式制作批次执行

## 执行边界与状态

这是执行 skill，不是角色说明：宿主实际读取本文件后，用可用工具完成下面的产物与验证。skill 名不是工具，文字“调用”不代表已执行；只有真正读入技能、委派成功或工具结果才记为执行。先识别用户请求的是完整阶段还是局部任务，只完成本次承诺，不自动跑整条生命周期。

复用既有工程版本、包、平台与已批准决策，不硬编码 Unity 版本或擅自升级。存在 `.unity-game/` 时，产物放 `.unity-game/deliverables/`，主代理单写共享 state/tasks/decisions；子代理仅写被分配的产物和证据。独立安装默认 `docs/unity-game/` 或用户指定目录；本文件含独立执行方法，不依赖其他技能或模板已安装。文档先写临时文件再原子替换。

任务单必须有任务 ID、输入修订、原执行 skill、owner、可写路径、依赖、验收与回传证据。真正具备 subagent 工具时才委派下表角色，按宿主并发上限分配不重叠文件；没有时由主代理按同一契约串行实现并如实记录。Scene、Prefab、序列化资源、项目配置及 `.meta` 单写，同工程 Editor 导入/测试/构建串行；资源与 `.meta` 成对保留。

## 输入与就绪

切片基线、当前里程碑、批次任务、接口、资源预算和验收场景。完整流程检查 vertical-slice 用户确认；单个功能/素材请求只执行其任务，不强迫补齐全部制作环节。

## 专项方法与任务所有权

若阶段/整包同时安装，按当前缺口读取本执行技能父目录中的 `<下表 skill>/SKILL.md`，每个都是可选专项方法；只装本 skill 时直接执行下一节等价方法。不要求无关技能或不存在的相对链接。多角色任务拆成明确单一 owner 的子任务，不能共同抢写。

| 原执行 skill（安装时实际读取） | 建议 subagent | 本轮交付 |
|---|---|---|
| `unity-game-feature-delivery` | `gameplay-programmer / tools-programmer` | feature-ID.md、实际模块及测试 |
| `unity-game-asset-production` | `technical-artist` | 源资源、导出/导入产物、许可与资源清单 |
| `unity-game-animation-vfx` | `animation-vfx-artist` | 动画/VFX 资源、状态时序及设备证据 |
| `unity-game-audio` | `audio-designer` | 音频源、事件映射、混音配置和试听记录 |

未安装专项 skill 时，任务单原执行 skill 记 `unity-game-production-execute`，由对应角色按本文件方法执行；不能把未读取的专项记成已调用。

## 实际执行

1. 从玩家可见的批次结果反推任务，逐项写“前置状态→操作→预期反馈”，绑定接口、资源预算和路径所有权；实现前查现有代码和资源，避免重复框架。
2. 先交付一条端到端小样再复制已验流程。逻辑、源素材、动画源、音频源、测试代码分开并行，按任务实际需要调度角色；场景/Prefab 和 Editor 导入单写串行。
3. 实现时覆盖对象生命周期、暂停重试、场景重载和存档迁移；资源检查尺寸/比例、命名、导入设置、许可及缺失引用，动画音频检查事件同步和循环边界。
4. 集成后执行新功能与既有关键路径回归，保存目标设备上的输入/反馈、视觉/音频及性能抽样；检查 diff 与资源引用。失败最小化后回到对应模块原执行任务，不把返工算已完成内容。

## 本阶段交付与推进

实际功能与源/导入资源、许可索引、测试/构建、回退说明及 `production-batch-ID.md`；报告承诺/实际内容、未验项、缺陷返工、下一批依赖，完成标准是玩家结果而非文件数量。

单批独立审查通过后由主代理关闭该批次；仅在里程碑所有必需批次完成并有功能覆盖证据时交接 alpha。批次通过不自动表示整个制作阶段完成。

## 独立 reviewer 与返工闭环

1. 冻结本次提交/文件哈希、任务单及证据，生成 `production-execution-rN.md`：范围、任务→原执行 skill/owner、实际产物、命令/输入/字面结果/退出码、未运行项、风险、版本与回退。仅使用真实执行得到的 `passed` / `failed` / `not_run`，静态检查不替代运行。
2. 若已安装 `unity-game-review`，实际读取该技能，再由独立 `game-reviewer` 以 profile `production` 审查本次范围和固定修订。该 skill 不存在时，在新独立 reviewer 上下文执行同样的任务验收：检查输入→产物→证据、独立复现关键检查、给 finding ID/严重度/文件与复现/原执行 skill 和 owner/验收条件，并给 `passed`、`changes_requested` 或 `blocked`。新 reviewer 不承担实现；实现者自检不冒充独立审查。宿主没有独立上下文能力时输出待审查包、注明独立审查未执行，保持阶段不推进。
3. `changes_requested` 必须携 finding ID 回到任务单记录的**原执行 skill + 原 owner**修复；不要重派 reviewer 实现或换技能掩盖问题。生成新修订，重跑受影响验证，独立 reviewer 针对新修订复审；重复返工无新证据时记录原因和待决事项，避免无界重试。
4. `blocked` 或必需运行证据 `not_run` 时，交付已完成部分和具体恢复步骤，阶段原地保持。只有独立审查 `passed` 后由主代理写阶段完成/下一步建议；完整流程还须遵守本阶段用户门。局部任务只验收本次范围，不据此宣称整个阶段通过。

## 3D模型与外部软件执行

3D资产任务由model-artist使用unity-game-modeling及其design/build/surface/rig-export子技能，按模型简报实际建模；technical-artist独占Unity导入。MCP先发现真实工具/参数/软件实例、在副本小样验证；已有软件skill先读取真实路径；CLI先doctor检查已安装软件和版本，用明确脚本在新工作目录执行。输出源模型、导出、纹理、保存重开/预览和哈希；默认导出模板不是模型生成器，--new需项目建模脚本。独立game-reviewer使用model-review检查源和导出及Unity证据，再以production汇总。缺软件不记模型完成。
