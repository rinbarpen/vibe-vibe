# GDevelop 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

事件驱动 2D/轻量 3D、低代码快速验证。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "json_keys": [
    [
      "*.json",
      [
        "gdVersion",
        "layouts",
        "properties"
      ]
    ]
  ]
}
```

## 版本与工具链

记录 Editor/gdVersion、扩展版本与导出工具；同名 game.json 不能仅凭文件名识别。

## 场景与实体

Scene→关卡，Object/Behavior→实体，External Events/Layouts→复用。

## 脚本与数值

事件与变量作用域明确，JS 扩展沿用项目；数值用可追溯表驱动。

## 资产管线

Resources 资源映射与相对路径，源文件和导出目录分离；检查大小写与远程资产。

## 坐标与尺度

2D 场景坐标、相机和层 UI 分开；3D 行为需固定坐标/尺度约定。

## 输入与 UI

事件条件映射键鼠/触控/手柄；检查多触点、暂停、窗口尺寸变化。

## 存档与联网

Storage/JSON 版本化；平台服务与多人扩展仅在需求明确后引入。

## 测试与证据

Preview/Debugger + 事件边界与变量检查 + 导出包试玩；真机网络/性能另测。

## 构建与导出

记录 Editor 或已验证 gdexport 工作流，导出平台配置与云/本地构建成本明确。

## 约束与风险

不能把有 properties 的任意 JSON 当项目；云导出不是默认允许的自动发布。

## 官方资料

- [官方文档](https://wiki.gdevelop.io/gdevelop5/)
