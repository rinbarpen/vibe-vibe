# Godot 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

轻量 2D/3D、开源工具链与节点组合。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "project.godot"
  ]
}
```

## 版本与工具链

记录 project.godot config_version/features 与 godot --version；Godot 3/4、GDScript/C# 和导出模板分开锁定。

## 场景与实体

实体→Node；复用→PackedScene；关卡→.tscn；信号连接表达系统边界。

## 脚本与数值

GDScript 或 C# 遵循既有项目；Resource/.tres 承载配置，Autoload 仅用于必要全局服务。

## 资产管线

保留 .uid 与导入配置，缓存 .godot 不当源资产；验证 glTF、动画、碰撞和资源路径大小写。

## 坐标与尺度

2D Y-down、3D Y-up；明确像素/米制约定，分离 Control 布局和世界坐标。

## 输入与 UI

InputMap actions；处理触控、手柄 deadzone 和 UI focus。

## 存档与联网

user:// 存档加版本迁移；多人按项目选择 MultiplayerAPI 与权威节点。

## 测试与证据

headless 导入/脚本检查仅是静态入口；行为测试用项目已有 GUT/GdUnit 或自建 harness，并执行真实图形试玩。

## 构建与导出

模板："$GODOT" --headless --path "$PROJECT" --import；导出："$GODOT" --headless --path "$PROJECT" --export-release "$PRESET" "$OUTPUT"；先安装匹配导出模板、创建输出父目录。

## 约束与风险

不能将 headless import 等同于测试；C#、Web、移动导出能力查对应版本；不能自动迁移 3→4。

## 官方资料

- [官方文档](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)
