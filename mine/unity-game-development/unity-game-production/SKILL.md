---
name: unity-game-production
description: 按 Unity 已确认制作基线编排功能、美术资源、动画特效和音频批次；在“正式制作”“内容量产”“游戏功能与资源交付”时使用。
---

# Unity 正式制作阶段

## 本环节的执行入口

执行本阶段时先读取 [unity-game-production-execute](unity-game-production-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `production`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

## 按任务读取

- 玩法/工具/UI/存档等功能批次：读取 [unity-game-feature-delivery](unity-game-feature-delivery/SKILL.md)。
- 2D/3D 美术源资源、导出、导入与场景验收：读取 [unity-game-asset-production](unity-game-asset-production/SKILL.md)。
- 动画状态、动作时序、特效与性能：读取 [unity-game-animation-vfx](unity-game-animation-vfx/SKILL.md)。
- 音效/音乐、事件、混音与试听验收：读取 [unity-game-audio](unity-game-audio/SKILL.md)。

只加载当前子任务；子技能可独立安装和执行。

- 3D模型设计、外部DCC建模、UV/PBR、绑定导出与模型审查：读取 [unity-game-modeling](unity-game-modeling/SKILL.md)。

## 工作位置与证据

先识别实际 Unity 项目、用户指定范围和既有产物。存在 `.unity-game/` 时读取相关状态，实际文档放 `.unity-game/deliverables/`，按需复用已存在的 templates；独立安装时使用用户指定目录，默认 `docs/unity-game/`，沿用项目现有测试和构建工具。只有实际存在时才调用 `.unity-game/scripts/unity_cli.py`，先查看其 `--help`。缺 Editor 或设备时仍可交付静态产物，但对应运行验收记 `not_run`，附具体阻塞与复现步骤；`passed` 必须有真实证据。

同一 Scene、Prefab、Animator、材质等序列化资源及其 `.meta` 只设一个写入者；同一工程的 Editor 导入、测试、场景编辑和构建串行。独立代码/规格任务可并行，依赖冻结后再集成。由 Editor 生成 `.meta`，移动时资源与 `.meta` 成对保留，不编造 GUID。已有版本和包先沿用，升级另行决策。

## 阶段编排与交付

完整生命周期先核对切片用户基线、当前里程碑与范围；单个功能或资源任务只执行相应子技能，不强制重走整个流程。每批定义玩家可见结果、数据/事件接口、资源预算、路径所有权和验收场景，避免只有“完成脚本/素材”的无集成交付。

把无共享写路径的功能逻辑、素材源、动画源、音频源与测试设计并行分派；先做真实端到端小样，再批量复制已验收流程。序列化配置与场景由单写者集成，Editor 串行。缺角色或宿主并发能力时按同一契约串行，记录实际执行方式。

每批集成后运行回归和独立审查。归档 `production-batch-ID.md`：承诺与实际内容、源资源/许可、测试和构建、未验证项、缺陷/返工与下一批依赖。制作完成必须有可复现内容与证据，不以任务数替代功能完整度；共享任务与阶段状态只由主代理更新。
