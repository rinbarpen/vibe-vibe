# Unity Game Manifest

面向独立开发者和小团队的 Unity 2D / 3D 游戏全流程工作流。以 **subagent 优先、依赖驱动并行、真实运行证据、里程碑人工确认** 推进，从创意立项到发布运营。

## 立即开始

1. 读取项目根 `AGENTS.md`，然后读取 `.unity-game/README.md` 与 `.unity-game/references/lifecycle.md`。
2. 若当前处于 manifest 源目录，参考资料在 `references/`、模板在 `templates/`；安装后均位于 `.unity-game/`。以下运行路径以安装后的项目根为基准。
3. 恢复 `.unity-game/state/{status,tasks,decisions,artifacts}.md`，核对现有 Unity 工程与已完成产物；从第一个未完成任务继续，不重新初始化。
4. 首次立项明确类型、2D/3D、目标玩家与平台、团队、预算、工期、联网需求，以及已有资源/代码；尚未确定的选择写入简报的待决策项。
5. 主代理采用 `game-producer` 职责，按 `.unity-game/references/orchestration.md` 派发独立任务；所有共享状态由主代理单写。

## 默认工作方式

- 以 `.unity-game/templates/` 为起点，将实际项目文档放入 `.unity-game/deliverables/`。模板不是完成证据。
- 进入正式开发前确认 Unity Editor 版本、渲染管线、输入系统、目标平台、包依赖、性能预算和版本管理方式；通用模板不预设它们。
- 先完成策划和可玩闭环，再进入垂直切片、内容批产、Alpha/Beta、发布及运营；允许有证据的回退与迭代。
- 三个用户确认门：**方向确认、垂直切片确认、发布确认**。每次确认必须绑定具体产物版本及遗留风险。
- Scene、Prefab、`.meta`、序列化资源和项目设置按单写者管理；同一工程的 Unity Editor 命令串行执行。
- 代码、文档、测试与审查尽量并行，前提是输入已冻结且编辑路径不重叠；依赖批次集成验证后才启动下游。
- 没有 Editor 或平台模块时仍可完成设计与静态检查；运行验收保持 `not_run`，不宣称可玩、性能达标或发布成功。

## 技能入口

完整阶段路由见 `.unity-game/references/skills.md`；游戏专项技能总入口是 `.agents/skills/unity-game-development/SKILL.md`。按阶段先选择对应 `*-execute` skill，再分派专项 subskill。交付后由独立 game-reviewer 使用 unity-game-review/profile 审查；修复回到原 skill/owner，证据或审查缺失时不推进。流程图在 `.unity-game/references/workflow.svg`。

## 模型设计与软件接入

3D模型使用unity-game-modeling及其5个子技能；model-artist写源模型，technical-artist接Unity。外部MCP、软件skill或Blender CLI按实际环境选择；接入与配置说明在 `.unity-game/references/external-tools.md`，模型简报和交付模板位于 `.unity-game/templates/`。

## 工具入口

```bash
python3 .unity-game/scripts/unity_cli.py doctor --project .
python3 .unity-game/scripts/unity_cli.py test --project . --mode editmode
python3 .unity-game/scripts/unity_cli.py test --project . --mode playmode
# METHOD 是项目中实际存在的静态构建入口；此例仅示意参数。
python3 .unity-game/scripts/unity_cli.py build --project . --target StandaloneLinux64 --execute-method UnityGameBuild.Build --output ./Builds/Linux/Game
```

Editor 可通过 `--editor PATH` 明确指定。先执行 `doctor`，再按对应 Unity 版本的官方文档检查调用参数；可选构建入口模板在 `.unity-game/templates/Editor/`，确认后才接入游戏工程。流程约定见 `.unity-game/references/unity-engineering.md`。

## 测试游戏入口

要求“测试游戏/跑一遍/找bug”时加载 `.agents/skills/unity-game-development/unity-game-alpha/unity-game-testing/SKILL.md`；实际输入游玩与缺陷复测由QA负责，独立game-reviewer执行test-review。说明/模板见 `.unity-game/references/game-testing.md`，无真实游戏或输入通道保留not_run。
