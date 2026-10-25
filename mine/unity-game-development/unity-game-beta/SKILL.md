---
name: unity-game-beta
description: Unity 游戏 Beta 平衡性、性能、平台兼容与体验验收时使用。
---

# Beta：目标设备与真实玩家验证

## 本环节的执行入口

执行本阶段时先读取 [unity-game-beta-execute](unity-game-beta-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `beta`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

## 输入与取舍
读取 Alpha 证据、目标受众、平台/设备预算、核心体验目标及遗留缺陷。先区分玩法假设、性能约束和兼容性阻断，再确定各自可比较的测量基线；项目尚未定义预算时，先交付待确认预算而非宣称达标。

## 按需加载 subskills
- 平衡性与试玩实验：读取 [unity-game-balance-playtest](unity-game-balance-playtest/SKILL.md)。
- 帧耗、内存、加载、热与能耗对照：读取 [unity-game-performance](unity-game-performance/SKILL.md)。
- 设备矩阵、输入、可访问性和本地化：读取 [unity-game-compatibility](unity-game-compatibility/SKILL.md)。
仅加载当前风险相关子技能；样本分析与矩阵设计可并行，Editor 和共享资源修改串行。

## 工作与交付
1. 根据发布平台和核心循环分配验证任务；共享同一候选构建标识，性能与平衡对照改变单一主要变量。
2. `playtest-analyst` 输出证据与偏差，`performance-engineer` 做设备实测，`qa-engineer` 汇总兼容回归；`game-reviewer` 独立审查验收依据。
3. 交付 Beta 报告：基线/实验构建、样本与设备覆盖、预算对比、缺陷优先级、已知偏差、仍未运行项目。
4. 已知阻断修复并回归后向 `build-release-engineer` 和 `game-producer` 交接发布候选范围；Beta 完成不等于用户已确认发布。

## 运行约定
- 先读取现有项目约定、`ProjectSettings/ProjectVersion.txt`、包锁定文件和已确认平台；使用项目版本对应官方文档，不预设 Editor 版本或设备。
- 如存在 Unity manifest，使用 `.unity-game/` 既有任务与产物；否则将产物写入用户指定位置，未指定时使用 `docs/unity-game/`。共享阶段、任务、决策由主代理单写；子代理仅交付其认领文件和证据。
- 独立文档、测试设计可按文件所有权并行；同一工程的 Unity Editor、Scene、Prefab、序列化资源和项目配置由单一写者串行处理，资源与 `.meta` 成对提交。文档采用临时文件写入后原子替换。
- 运行结论使用 `passed`、`failed`、`not_run` 并附证据。缺少 Editor、设备或凭据时记录未执行范围；静态检查不替代真实运行。已安装辅助工具时可先读 `.unity-game/scripts/unity_cli.py --help`，否则沿用项目工具及对应版本官方文档。
