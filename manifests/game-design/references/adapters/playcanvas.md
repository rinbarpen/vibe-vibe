# PlayCanvas 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

Web 3D；云 Editor 或 Engine-only 两种工作方式。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "dependencies": [
    "playcanvas"
  ]
}
```

## 版本与工具链

记录 Engine npm 版本或 Editor 导出版本、项目 ID 和下载快照；云端工程不凭本地空目录识别。

## 场景与实体

Entity/Component、Scene/Template 映射设计对象；云端项目记录资源 ID 与场景版本。

## 脚本与数值

沿用项目 Script 类型/JS/TS 规范；系统数值与实体脚本分离。

## 资产管线

Asset Registry、GLB、贴图压缩与异步加载，云导出时保留可复建的资源映射。

## 坐标与尺度

Y-up，尺度按米约定；摄像机、光照/烘焙、碰撞和 UI 布局核验。

## 输入与 UI

Keyboard/Mouse/Touch/Gamepad 接统一动作层；移动输入与 UI 焦点专项验证。

## 存档与联网

自定义存档后端；云编辑协作不等于游戏运行时多人同步。

## 测试与证据

Editor Launch + 下载包真实 HTTP 试玩；Engine-only 逻辑单测和浏览器 QA。

## 构建与导出

区分 Editor 的发布/下载与 Engine-only bundler；记录导出快照、缓存与 URL，不自动云发布。

## 约束与风险

不假定拥有云会话或 API TOKEN；本地依赖检测覆盖 Engine-only，Editor 模式需人工记录。

## 官方资料

- [官方文档](https://developer.playcanvas.com/user-manual/)
