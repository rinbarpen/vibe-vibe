# Unity 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

2D/3D、移动与跨平台；复杂项目可接既有 unity-game 专项流程。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "all": [
    "ProjectSettings/ProjectVersion.txt",
    "Assets"
  ]
}
```

## 版本与工具链

读取 ProjectVersion.txt、Packages/manifest.json 与 packages-lock.json；锁定 Editor、渲染管线和测试框架。

## 场景与实体

GDD 实体→GameObject/Component；关卡→Scene；复用→Prefab/Variant。

## 脚本与数值

C# 组件与纯领域层分离；数值→ScriptableObject 或有版本的外部表。

## 资产管线

Assets/.meta 配对提交，GUID 不重建；DCC 源文件与导出物分离，Addressables 按实际依赖选用。

## 坐标与尺度

3D 通常 Y-up、1 单位按 1m 约定；2D 指定 Pixels Per Unit，验证根运动、物理和 UI 缩放。

## 输入与 UI

确认旧 Input Manager 或 Input System；Action 映射键鼠/手柄/触控，处理失焦与重绑定。

## 存档与联网

存档按 persistentDataPath 和 schema 迁移；联网库与 authority 单独选型，单机设计不默认联网。

## 测试与证据

EditMode 验纯逻辑；PlayMode 验场景与生命周期；真实构建试玩、Profiler 与目标设备各留证据。

## 构建与导出

模板："$UNITY" -batchmode -projectPath "$PROJECT" -runTests -testPlatform EditMode -testResults "$RESULTS" -logFile "$LOG"；构建使用项目已存在的 executeMethod，不能把测试命令当构建。

## 约束与风险

同工程 Editor 操作串行；不得自动升级管线/包；console 导出依平台 SDK 和资格；可选手动安装 unity-game-development，不复制其技能目录。

## 官方资料

- [官方文档](https://docs.unity.com/en-us/engine/6000.5/manual/scripting/test-framework-introduction/running-tests/run-tests-from-command-line)
