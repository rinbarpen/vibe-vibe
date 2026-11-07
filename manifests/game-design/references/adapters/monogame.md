# MonoGame 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

C# 2D/3D、自定义游戏架构和内容管线。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "text": [
    [
      "*.csproj",
      "MonoGame.Framework"
    ]
  ]
}
```

## 版本与工具链

锁定 .NET SDK、MonoGame NuGet、MGCB 与目标 backend；读取 global.json/项目文件。

## 场景与实体

Game/Update/Draw 为核心；自行映射场景管理、实体/组件和关卡格式。

## 脚本与数值

C# 纯规则层 + 服务/内容边界，避免把全部逻辑集中在 Game1。

## 资产管线

.mgcb/MGCB 内容管线、源资产与编译 .xnb 分离，检查平台适用性。

## 坐标与尺度

2D SpriteBatch 和 3D camera 坐标独立约定；viewport、DPI、单位与投影明示。

## 输入与 UI

Keyboard/Mouse/GamePad/Touch 统一动作层，处理设备断连。

## 存档与联网

自建版本化存档与网络层；路径按目标平台约定。

## 测试与证据

dotnet test 只针对已有测试项目；图形/音频/输入必须运行真实 Game。

## 构建与导出

沿用 csproj/sln 的 dotnet build/publish 配置、RID 与 MGCB 工具，不假定本机可交叉发布所有目标。

## 约束与风险

framework 不附带完整编辑器/游戏状态机；跨平台内容与 native 库缺失需单独诊断。

## 官方资料

- [官方文档](https://docs.monogame.net/articles/getting_started/)
