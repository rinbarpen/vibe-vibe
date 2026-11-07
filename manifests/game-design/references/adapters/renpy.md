# Ren'Py 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

视觉小说、分支叙事和对话系统。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "game/options.rpy"
  ]
}
```

## 版本与工具链

记录 Ren'Py SDK 与 Python 版本、屏幕语言/插件和发行目标；保留源 .rpy。

## 场景与实体

剧情节点→label/jump/call，界面→screen，立绘/背景→image，分支→menu/状态变量。

## 脚本与数值

Ren'Py script + Python，default/define 生命周期明确；分支可达性和变量更新可测试。

## 资产管线

立绘差分、背景、音频、字体、翻译单独列清单，文件名/图层与版权可追踪。

## 坐标与尺度

虚拟分辨率与 screen/transform 锚点；触控 UI、字体与语言溢出验证。

## 输入与 UI

键鼠/触控/手柄、快进/自动/历史/回滚与可访问性按目标验收。

## 存档与联网

save/load 与 persistent 区分；分支状态/存档兼容和 rollback 行为必须测试。

## 测试与证据

模板："$RENPY_SH" "$PROJECT" lint --error-code；lint 后仍需测试各结局、存取档、回滚、翻译和音频。

## 构建与导出

SDK Launcher Build Distributions 按目标导出；CLI 接口依 SDK 核验，移动目标另需工具链。

## 约束与风险

lint 不是全分支覆盖；旧存档兼容、Python 对象可序列化性和 screen 脚本上下文需审查。

## 官方资料

- [官方文档](https://www.renpy.org/doc/html/cli.html)
