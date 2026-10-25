---
name: unity-game-vertical-slice
description: 编排 Unity 代表性垂直切片集成与独立基线审查；在“制作垂直切片”“建立量产品质基线”时使用。
---

# Unity 垂直切片阶段

## 本环节的执行入口

执行本阶段时先读取 [unity-game-vertical-slice-execute](unity-game-vertical-slice-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `vertical-slice`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

## 按任务读取

- 需要打通代表内容、最终视听与目标平台构建：读取 [unity-game-slice-integration](unity-game-slice-integration/SKILL.md)。
- 已有固定切片版本，需要独立验收与生产基线建议：读取 [unity-game-slice-review](unity-game-slice-review/SKILL.md)。

只加载当前子任务；子技能可独立安装和执行。

## 工作位置与证据

先识别实际 Unity 项目、用户指定范围和既有产物。存在 `.unity-game/` 时读取相关状态，实际文档放 `.unity-game/deliverables/`，按需复用已存在的 templates；独立安装时使用用户指定目录，默认 `docs/unity-game/`，沿用项目现有测试和构建工具。只有实际存在时才调用 `.unity-game/scripts/unity_cli.py`，先查看其 `--help`。缺 Editor 或设备时仍可交付静态产物，但对应运行验收记 `not_run`，附具体阻塞与复现步骤；`passed` 必须有真实证据。

同一 Scene、Prefab、Animator、材质等序列化资源及其 `.meta` 只设一个写入者；同一工程的 Editor 导入、测试、场景编辑和构建串行。独立代码/规格任务可并行，依赖冻结后再集成。由 Editor 生成 `.meta`，移动时资源与 `.meta` 成对保留，不编造 GUID。已有版本和包先沿用，升级另行决策。

## 阶段编排与交付

从原型结论与项目预算中选一段有代表性的真实生产难度，不用纯展示场景替代可玩内容。冻结玩法、视听、目标设备性能与流水线可复制性验收；内容生产可并行，序列化对象和 Editor 由指定集成人员排队处理。

先集成再独立审查，修复与复验引用同一版本体系。质量不足返回相关模块或原型，不用不断加内容掩盖基础问题。归档 `vertical-slice-summary.md`，链接构建/版本、实际测量、资源链、审查发现、生产成本与接受风险。

完整生命周期中，producer 展示实际切片和已知风险，取得用户对固定版本的明确基线确认后才开始批量制作；审查意见不替代用户确认。局部切片/审查调用只交付请求部分，不自动推进全流程。
