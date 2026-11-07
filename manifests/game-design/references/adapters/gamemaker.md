# GameMaker 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

2D、房间驱动、GML 或可视化制作。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "*.yyp"
  ]
}
```

## 版本与工具链

记录 IDE、Runtime 与目标模块版本；项目格式随版本变化，先备份再由 Editor 迁移。

## 场景与实体

Room→关卡，Object/Instance→实体，Sequence→过场，Prefab 类需求用已有对象/数据生成模式。

## 脚本与数值

GML 或项目既有可视化事件；Create/Step/Draw 生命周期与规则层分离。

## 资产管线

Sprite/TileSet/Texture Group 与音频资源；使用 Editor 修改资源引用，检查 YY 路径。

## 坐标与尺度

2D 通常 Y-down；room 坐标、camera/view 和 GUI 层区分。

## 输入与 UI

键盘/鼠标/手柄/触控映射到动作，检查不同帧率下 Step 逻辑。

## 存档与联网

版本化存档与平台沙盒目录；联网/回滚逻辑按需求另建。

## 测试与证据

调试运行、房间切换、碰撞、存档读写、目标导出包试玩；自建断言需有明确退出/报告。

## 构建与导出

以当前 IDE 的 Build/Run/Create Executable 流程与已购/可用模块为准；自动化先验证对应 Runtime/Igor 接口。

## 约束与风险

不编造跨版本通用 headless 命令；VM/YYC、许可与 console 模块能力单独核验。

## 官方资料

- [官方文档](https://manual.gamemaker.io/monthly/en/)
