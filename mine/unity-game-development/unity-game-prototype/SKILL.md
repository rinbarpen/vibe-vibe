---
name: unity-game-prototype
description: 编排 Unity 工程准备、最小可玩闭环与原型试玩；在“开发 Unity 原型”“验证核心循环”时使用，可按需调用独立 subskills。
---

# Unity 原型阶段

## 本环节的执行入口

执行本阶段时先读取 [unity-game-prototype-execute](unity-game-prototype-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `prototype`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

## 按任务读取

- 工程/Editor/测试入口尚未就绪：读取 [unity-game-project-setup](unity-game-project-setup/SKILL.md)。
- 已有基线，需要实现最小玩法或高风险实验：读取 [unity-game-playable-prototype](unity-game-playable-prototype/SKILL.md)。
- 已有可运行版本，需要真实玩家观察与迭代决策：读取 [unity-game-prototype-playtest](unity-game-prototype-playtest/SKILL.md)。

只加载当前子任务；子技能可独立安装和执行。

## 工作位置与证据

先识别实际 Unity 项目、用户指定范围和既有产物。存在 `.unity-game/` 时读取相关状态，实际文档放 `.unity-game/deliverables/`，按需复用已存在的 templates；独立安装时使用用户指定目录，默认 `docs/unity-game/`，沿用项目现有测试和构建工具。只有实际存在时才调用 `.unity-game/scripts/unity_cli.py`，先查看其 `--help`。缺 Editor 或设备时仍可交付静态产物，但对应运行验收记 `not_run`，附具体阻塞与复现步骤；`passed` 必须有真实证据。

同一 Scene、Prefab、Animator、材质等序列化资源及其 `.meta` 只设一个写入者；同一工程的 Editor 导入、测试、场景编辑和构建串行。独立代码/规格任务可并行，依赖冻结后再集成。由 Editor 生成 `.meta`，移动时资源与 `.meta` 成对保留，不编造 GUID。已有版本和包先沿用，升级另行决策。

## 阶段编排与交付

以“验证哪个玩法/技术假设”为入口，而非做缩小版完整游戏。全生命周期先核对方向确认记录；局部原型请求只冻结本次假设、工期和排除项。环境准备 → 最小闭环 → 真实试玩按依赖展开，可复用已完成部分。

为并行代码、灰盒、UI 与测试冻结小接口和文件所有权；主代理集成后排队执行 Editor。原型允许占位资源但必须标明来源/限制。保留一次干净启动到重试的真实证据，试玩结论分开记录观察、解释与假设。

归档 `prototype-summary.md`，链接工程、可玩版本、技术实验、测试、真实试玩与继续/调整判断。文档完成不代表原型可玩；缺运行条件时相应项目记 `not_run`。交给 game-designer/producer 判断下一轮，unity-architect 记录待偿还的临时代码债务。
