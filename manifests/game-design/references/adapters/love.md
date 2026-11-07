# LÖVE 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

Lua 2D、游戏循环清晰的小型项目。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "all": [
    "main.lua",
    "conf.lua"
  ]
}
```

## 版本与工具链

锁定 love --version、LuaJIT 与第三方模块；只有 main.lua 是弱线索，显式选择也可接入。

## 场景与实体

love.load/update/draw 为入口；自行设计 Scene/Entity、状态机与内容系统。

## 脚本与数值

Lua 模块化规则，固定步长更新与 draw 分离；配置表与运行时对象区分。

## 资产管线

图片/音频/字体/图集相对路径，按打包大小写和纹理过滤验证。

## 坐标与尺度

2D Y-down；世界坐标、相机、像素比例和 DPI 分开。

## 输入与 UI

love.keyboard/mouse/touch/joystick 映射动作，处理 focus 与 resize。

## 存档与联网

love.filesystem 读写身份目录，存档 schema 与不可信数据解析隔离。

## 测试与证据

纯 Lua 测试 + love 运行输入回放；计时、碰撞、音频与窗口缩放检查。

## 构建与导出

运行模板："$LOVE" "$PROJECT"；.love 包必须以 main.lua 为根，原生分发按目标合并/打包。

## 约束与风险

不假定自带场景编辑器或测试 runner；只有 main.lua 的项目需确认而不是误判通用 Lua。

## 官方资料

- [官方文档](https://github.com/love2d/love)
