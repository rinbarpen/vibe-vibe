# Stride 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

C#/.NET 组件化 3D 与 Game Studio。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "*.sdpkg"
  ],
  "text": [
    [
      "*.csproj",
      "Stride.Engine"
    ]
  ]
}
```

## 版本与工具链

锁定 Stride NuGet、.NET SDK 与 Game Studio；sln/包与项目版本保持匹配。

## 场景与实体

Scene/Entity/Component、Prefab 与场景层级映射设计；系统脚本独立。

## 脚本与数值

C# SyncScript/AsyncScript 与纯规则层分离，异步生命周期与资源访问明确。

## 资产管线

Game Studio 资产与 .sd* 描述保留；编译资产与源模型/材质分离。

## 坐标与尺度

Y-up 约定与相机投影、物理尺度写入 TDD；导入变换需实际核验。

## 输入与 UI

Input/虚拟按钮按项目实现；多设备、UI 焦点与失焦行为测试。

## 存档与联网

领域数据存档加 schema；网络库按需求选定，不假定自带完整后端。

## 测试与证据

dotnet 规则测试 + Game Studio/真实 runtime；资产编译与图形验收分别记录。

## 构建与导出

使用项目实际 sln/csproj 和平台配置构建/发布；验证目标 runtime、native 依赖与资产打包。

## 约束与风险

普通 .NET 项目不是 Stride；跨平台支持按版本/依赖核验，禁止自动迁移资产。

## 官方资料

- [官方文档](https://doc.stride3d.net/latest/en/manual/)
