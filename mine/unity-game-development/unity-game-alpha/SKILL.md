---
name: unity-game-alpha
description: Unity 游戏 Alpha 功能完整验收、自动测试和全流程回归时使用。
---

# Alpha：证明功能闭环

## 本环节的执行入口

执行本阶段时先读取 [unity-game-alpha-execute](unity-game-alpha-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `alpha`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

## 输入与阶段决策
读取当前功能清单、主流程图、存档格式、已集成功能和构建基线。把需求映射为可重复验收场景，标明关键路径、风险、环境和责任人；文档完备与功能实际可玩分别验收。

## 按需加载 subskills
- 自动测试分层、EditMode / PlayMode、CI 与失败定位：读取 [unity-game-test-automation](unity-game-test-automation/SKILL.md)。
- 新游戏、存读档、升级、结束与重开全周期：读取 [unity-game-flow-regression](unity-game-flow-regression/SKILL.md)。
只加载本轮相关子技能；两个方向可并行设计，Editor 实跑串行。修复与最终审查使用不同代理上下文。

## 工作与交付
1. 先冻结当前验收基线和测试数据，拆出自动化与人工/设备场景，给每项指定覆盖依据。
2. 让 `qa-engineer` 编制矩阵，`gameplay-programmer` 修复最小失败，`game-reviewer` 独立复验；按依赖集成后才跑下游。
3. 交付功能验收矩阵、测试与回归证据、按严重度排序的缺陷和未覆盖项。每个结论指向构建标识、输入和实际日志。
4. 主流程阻断、存档损坏及验收必需场景未执行时保留 Alpha 待验；通过后将基线和遗留风险交给 `game-producer` 安排 Beta，不新增全流程确认门。

## 运行约定
- 先读取现有项目约定、`ProjectSettings/ProjectVersion.txt`、包锁定文件和已确认平台；使用项目版本对应官方文档，不预设 Editor 版本或设备。
- 如存在 Unity manifest，使用 `.unity-game/` 既有任务与产物；否则将产物写入用户指定位置，未指定时使用 `docs/unity-game/`。共享阶段、任务、决策由主代理单写；子代理仅交付其认领文件和证据。
- 独立文档、测试设计可按文件所有权并行；同一工程的 Unity Editor、Scene、Prefab、序列化资源和项目配置由单一写者串行处理，资源与 `.meta` 成对提交。文档采用临时文件写入后原子替换。
- 运行结论使用 `passed`、`failed`、`not_run` 并附证据。缺少 Editor、设备或凭据时记录未执行范围；静态检查不替代真实运行。已安装辅助工具时可先读 `.unity-game/scripts/unity_cli.py --help`，否则沿用项目工具及对应版本官方文档。

## 实际启动并测试游戏

使用 [unity-game-testing](unity-game-testing/SKILL.md) 执行测试计划、普通输入游玩、探索、画面、缺陷复现、修复回归及独立测试审查；EditMode/PlayMode和真人试玩继续使用各自原有技能，不互相替代。
