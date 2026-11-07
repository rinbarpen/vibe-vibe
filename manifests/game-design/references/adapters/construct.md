# Construct 3 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

事件表驱动的 2D/Web 和低代码原型。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "*.c3p",
    "project.c3proj"
  ]
}
```

## 版本与工具链

锁定 Editor release、插件版本和项目备份；单文件 .c3p 为容器，不按文本源文件改写。

## 场景与实体

Layout→关卡，Event Sheet→规则，Object/Family/Behavior→实体族与复用。

## 脚本与数值

事件表为主，JS 脚本是可选扩展；把数值常量整理为变量/数据表。

## 资产管线

Animation/Tilemap/Audio 与插件资源；验证导出 asset paths 和下载缓存。

## 坐标与尺度

2D Y-down；layout、layer parallax、viewport 和 fullscreen 缩放区分。

## 输入与 UI

Keyboard/Touch/Gamepad behaviors，UI 事件优先级与多点触控。

## 存档与联网

Local Storage/Savegame 或后端方案明确版本与插件兼容。

## 测试与证据

Preview/Debugger、布局跳转、事件触发顺序和导出包跨浏览器试玩，保留事件表证据。

## 构建与导出

通过 Editor Export 选择实际平台；自动化仅使用当前订阅与版本提供的接口，记录导出 preset。

## 约束与风险

低代码不是零测试；不直接解压/批改 c3p 容器，不假定全部平台导出可用。

## 官方资料

- [官方文档](https://www.construct.net/en/make-games/manuals/construct-3)
