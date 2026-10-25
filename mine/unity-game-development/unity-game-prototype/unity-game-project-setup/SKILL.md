---
name: unity-game-project-setup
description: 建立或核查 Unity 原型工程、Editor/包版本与测试入口；在“创建原型项目”“Unity 环境检查”“工程初始化”时使用。
---

# Unity 原型工程准备

## 工作位置与证据

先识别实际 Unity 项目、用户指定范围和既有产物。存在 `.unity-game/` 时读取相关状态，实际文档放 `.unity-game/deliverables/`，按需复用已存在的 templates；独立安装时使用用户指定目录，默认 `docs/unity-game/`，沿用项目现有测试和构建工具。只有实际存在时才调用 `.unity-game/scripts/unity_cli.py`，先查看其 `--help`。缺 Editor 或设备时仍可交付静态产物，但对应运行验收记 `not_run`，附具体阻塞与复现步骤；`passed` 必须有真实证据。

同一 Scene、Prefab、Animator、材质等序列化资源及其 `.meta` 只设一个写入者；同一工程的 Editor 导入、测试、场景编辑和构建串行。独立代码/规格任务可并行，依赖冻结后再集成。由 Editor 生成 `.meta`，移动时资源与 `.meta` 成对保留，不编造 GUID。已有版本和包先沿用，升级另行决策。

## 输入与决策

取得现有仓库、目标平台、2D/3D、已选 Editor 版本和项目创建权限。已有工程以 `ProjectSettings/ProjectVersion.txt`、`Packages/manifest.json` 和锁文件为事实源，不因本技能切换渲染管线、输入方案或升级包。新工程缺少类型/平台等关键选择时先确认；没有明确选择时不预设 2D、3D 或 URP。

## 操作

1. 盘点 `Assets/`、`Packages/`、`ProjectSettings/`、测试程序集、构建入口和现有 `.gitignore`；记录工作树已有变更，保留用户资源。
2. 将所需 Editor 版本与实际可用 Editor 对比，检查平台模块；通过显式路径或 `UNITY_EDITOR` 选版本，多个匹配候选时明确路径。已安装 manifest 时可运行 `doctor --project PROJECT`。预检通过只说明环境可用。
3. 新建工程使用用户选定版本的受支持创建方式；没有 Editor 时交付精确创建参数和待办，不伪装出已可运行工程。添加代码目录、程序集或 Test Framework 前检查既有结构，最小增量接入，包缺失时先确认兼容版本和依赖变更。
4. 检查文本序列化/可见 meta 现状及版本控制忽略项；更改项目设置前说明必要性与影响。排除 Library、Temp、Logs 等生成目录，但不忽略 `Assets/*.meta`、项目设置或包锁。
5. 先完成一次真实导入/编译，再用现有最小测试或用户认可的烟测场景检查启动。测试数、日志、Editor 版本和退出码留档；“零测试”与“无错误编译”分开记录。

## 输出与验收

交付 `project-setup.md`：工程路径、源码版本、Editor/平台/管线、依赖差异、目录约定、实际命令、结果文件和环境阻塞。通过条件是工程真实打开并编译，烟测可复现，用户内容未被覆盖；未执行的运行步骤保持 `not_run`。

交给 `unity-architect` 核对技术基线，`gameplay-programmer` 接最小玩法，`qa-engineer` 接可复现测试入口。只接到环境任务时到此结束，不自动推进整个生命周期。
