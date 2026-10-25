# Unity 工程、测试和构建约定

## 版本与环境

先读取 `ProjectSettings/ProjectVersion.txt`、`Packages/manifest.json` 及已有构建脚本。记录 Editor 精确版本、包版本、渲染管线、目标平台和模块、脚本后端、输入系统与操作系统。项目版本优先，不在模板安装时升级版本或包。

`python3 .unity-game/scripts/unity_cli.py doctor --project .` 检查项目结构、Editor 选择与测试依赖。选择优先级为显式 `--editor`、`UNITY_EDITOR`、匹配版本的常见安装目录。多候选或版本不符时先明确选择/修正环境，保留诊断，不猜测使用另一版本。

没有 Editor 时可审查代码和文档；Unity 编译、测试、试玩及平台构建保持 `not_run`。没有平台模块、许可、测试包或目标设备时分别记录依赖，避免将环境不足误写成游戏缺陷或已通过。

## 代码和资源

- 核心规则尽量采用可独立测试的 C#；输入、Unity 生命周期、表现层与持久化边界清晰，避免把全部业务耦合在场景脚本。
- 按项目规模决定程序集定义和包结构，不引入与需求无关的框架。Unity API 与包接口参考项目版本官方文档。
- 资源导入规范包含单位/比例、坐标、命名、格式、贴图压缩、动画 rig、音频采样和预算；资源提交携带 `.meta`，不提交 Library/Temp 等生成缓存。
- Unity YAML/序列化资源单写者，改动后用 Editor 检查引用和序列化兼容。场景对象、Prefab 变体和 Addressables 等额外机制按项目实际使用检查。
- 存档格式定义版本和迁移策略，记录失败与恢复行为。用户数据和构建凭据不写入版本库/公开日志。

## 测试

```bash
python3 .unity-game/scripts/unity_cli.py test --project . --mode editmode
python3 .unity-game/scripts/unity_cli.py test --project . --mode playmode
```

EditMode 覆盖纯逻辑、边界值、数值公式、存档迁移；PlayMode 覆盖输入、场景切换、对象生命周期、暂停/重试、UI 与实际玩法闭环。人工试玩和目标设备性能由专门报告记录，不能由自动测试代替。

运行材料在 `.unity-game/runs/<run-id>/`：`result.json`、`stdout.txt`、`stderr.txt`、`editor.log`，实际测试另有 `results.xml`。辅助工具退出码 `0/1/2` 分别表示 `passed/failed/not_run`，记录中 `exit_code` 保留 Editor 实际结果。

每次留存：源码版本/脏工作区说明、命令及参数、输入、Editor/平台、开始结束时间、实际退出码、Editor 日志、测试 XML 及通过/失败/跳过/总数。`passed` 需要进程结果与有效结果文件共同支持；零测试、XML 缺失、解析失败、超时或测试失败单独说明。

## 构建

```bash
python3 .unity-game/scripts/unity_cli.py build --project . --target StandaloneLinux64 --execute-method UnityGameBuild.Build --output ./Builds/Linux/Game
```

`UnityGameBuild.Build` 是占位示例，须替换为项目中真实存在的静态方法。可选构建入口模板在 `.unity-game/templates/Editor/`；经 architect/release 工程师核对项目版本 API、场景列表、平台和输出约定后再拷入项目 `Assets/Editor/`，不在 manifest 安装时自动接入。

输出相对 `--project` 解析；桌面Player建议每次选独立全新目录，已有_Data、UnityPlayer、GameAssembly及Mono等已知伴随资源会在启动前阻止覆盖；每次使用不存在的新输出路径，已有文件保留。输出不应放入 Assets、Packages、ProjectSettings 或 `.unity-game`。构建入口要消费 CLI 传入的目标与输出参数，检查 `BuildReport`，失败返回非零状态。构建后验证实际目标文件/目录存在，另做安装启动与目标设备 smoke；文件存在不是商店发布证据。记录候选包哈希、源码/依赖版本、命令、日志、返回码和已知风险。

同一工程 Editor 操作串行，避免项目锁与资源导入竞争。构建失败/超时保留原始日志和局部输出说明，修复后产生新运行记录，不修改旧结果冒充成功。

## 运行证据与构建格式

helper测试/构建记录inputs-before.json与inputs-after.json，覆盖Assets、Packages、ProjectSettings内容和符号链接目标，附可用Git revision/diff摘要；不扫描Library或下载的包缓存，包来源以manifest/lock为依据。输入运行中变化使成功结论失效，应先完成导入/编译并提交稳定资源，再运行验收。

构建按目标结构检查并记录已知Player bundle哈希清单；format_status结构核验与runtime_status启动/设备结果分开。可选C#模板消费-buildReport，写schema1 BuildReport结果/目标/输出/场景/错误数和文件清单；项目已有入口可继续使用，无report时明确not_provided，仍要结构匹配。模板仅按项目版本审查后接入，未编译前不视为已验证生产入口。新增/特殊平台的结构由项目补充，不推测通用模板覆盖全部SDK组合。

## 性能与发布

先约定目标硬件、帧率、帧时间、CPU/GPU、内存、加载/包体预算；在固定场景、输入、质量级别和采样窗口记录实际数据，优化前后对比。Editor 测量仅是开发线索，最终性能结论来自目标设备构建。

发行使用 `templates/release-checklist.md`，同时检查版本号、签名/包配置、商店素材、隐私与许可、更新/存档兼容、监控和回退。三个人工确认门及额外外部操作确认参见根 `AGENTS.md`。

## 官方资料核对

以下为 Unity 官方文档入口示例；实际使用时按项目精确 Editor / Test Framework 包版本选取对应页并记录核对日期，不默认项目使用 Unity 6：
- [Unity Editor 命令行](https://docs.unity3d.com/6000.0/Documentation/Manual/EditorCommandLineArguments.html)
- [命令行构建](https://docs.unity3d.com/6000.0/Documentation/Manual/BuildPlayerPipeline.html)
- [Test Framework 命令行测试](https://docs.unity3d.com/Packages/com.unity.test-framework@1.4/manual/reference-command-line.html)
- [BuildSummary字段](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Build.Reporting.BuildSummary.html)
- [JsonUtility.ToJson](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/JsonUtility.ToJson.html)
- [资源元数据](https://docs.unity3d.com/6000.0/Documentation/Manual/AssetMetadata.html)
