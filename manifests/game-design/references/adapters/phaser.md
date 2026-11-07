# Phaser 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

浏览器 2D 游戏；需要场景、输入与物理的轻量 Web 团队。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "dependencies": [
    "phaser"
  ]
}
```

## 版本与工具链

锁定 package.json 与对应 lockfile 中 Phaser 主版本，物理插件与 bundler；不同主版本 API 单独核验。

## 场景与实体

玩法阶段→Scene，实体→GameObject，预加载与运行 Scene 分开，复用通过工厂/类。

## 脚本与数值

JS/TS，纯数值/状态机与 Scene update 分离；数据通过 JSON 配置进入。

## 资产管线

Loader/纹理图集，资源 URL、CORS、大小写与音频编码验证；首屏和分场景加载预算。

## 坐标与尺度

2D 屏幕 Y-down；逻辑分辨率、Scale 配置与 CSS/DPR 分离。

## 输入与 UI

键盘/指针/触控映射成动作；失焦暂停、触控滚动冲突和音频首次交互测试。

## 存档与联网

IndexedDB/localStorage schema；在线功能用独立后端，浏览器不持有服务端秘密。

## 测试与证据

纯逻辑单测 + 项目已有浏览器 harness；验证 Canvas/WebGL、移动浏览器与断网恢复。

## 构建与导出

沿用 package.json 实际 scripts 和锁文件包管理器；只有存在 build/test 脚本才运行，产物在真实 HTTP 服务下验收。

## 约束与风险

不为所有项目假定 npm/Vite/Playwright 已安装；浏览器包不等于原生应用或小游戏包。

## 官方资料

- [官方文档](https://docs.phaser.io/phaser/getting-started/what-is-phaser)
