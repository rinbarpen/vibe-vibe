---
name: unity-game-test-automation
description: Unity 自动测试分层、EditMode/PlayMode 执行与 CI 失败定位时使用。
---

# Unity 测试自动化

## 输入与测试分层
读取可测需求、现有测试程序集、asmdef、包版本和最近失败日志。纯规则、数值边界与序列化转换优先 EditMode；生命周期、Scene/Prefab 绑定、物理时序和 UI 交互使用 PlayMode；平台 API 与图形表现另列设备验证，不能由编辑器测试等价替代。

## 操作
1. 为每项验收选定层级、固定随机种子与测试夹具；用显式 setup/teardown 恢复时间倍率、静态状态、输入和临时存档，避免跨测试污染。只改认领程序集及配套 `.meta`。
2. 修复前先取得可复现失败，优先窄测试定位，再运行受影响集合与关键回归；异步流程等待明确条件并设超时，避免仅凭固定 sleep 判定成功。
3. 根据实际 Test Framework 版本读官方运行说明；已有辅助工具时分别执行 `python .unity-game/scripts/unity_cli.py test --project . --mode editmode` 与 `--mode playmode`，否则运行项目既有命令。测试框架缺失先提出依赖修改方案，不能静默升级。
4. CI 保存命令、提交、Editor/包版本、输入、环境、退出码、Editor 日志和 NUnit XML；核对发现数、执行数、失败/跳过。退出码为零但缺报告、零测试或关键用例跳过，不算覆盖通过。
5. 波动测试单列重复次数与失败率；隔离需写责任人和恢复条件，不以无限重跑替代修复。

## 产物、验收与交接
交付测试代码、需求覆盖表、实际运行证据及未执行原因。假 Editor / mock 仅证明工具和参数行为；真实 Unity 验收须有对应日志/XML。将最小失败交给 `gameplay-programmer` 或 `tools-programmer`，结果由 `qa-engineer` 复验，独立 `game-reviewer` 检查是否仍有关键空白。

## 运行约定
- 先读取现有项目约定、`ProjectSettings/ProjectVersion.txt`、包锁定文件和已确认平台；使用项目版本对应官方文档，不预设 Editor 版本或设备。
- 如存在 Unity manifest，使用 `.unity-game/` 既有任务与产物；否则将产物写入用户指定位置，未指定时使用 `docs/unity-game/`。共享阶段、任务、决策由主代理单写；子代理仅交付其认领文件和证据。
- 独立文档、测试设计可按文件所有权并行；同一工程的 Unity Editor、Scene、Prefab、序列化资源和项目配置由单一写者串行处理，资源与 `.meta` 成对提交。文档采用临时文件写入后原子替换。
- 运行结论使用 `passed`、`failed`、`not_run` 并附证据。缺少 Editor、设备或凭据时记录未执行范围；静态检查不替代真实运行。已安装辅助工具时可先读 `.unity-game/scripts/unity_cli.py --help`，否则沿用项目工具及对应版本官方文档。
