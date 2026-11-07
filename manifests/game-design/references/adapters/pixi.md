# PixiJS 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

高性能 2D 渲染与定制玩法；不是完整游戏引擎。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "dependencies": [
    "pixi.js"
  ]
}
```

## 版本与工具链

锁定 pixi.js 主版本、渲染后端、扩展包和 lockfile；v7/v8 初始化/加载接口差异先核验。

## 场景与实体

显示层→Container/Sprite；另建玩法状态机与场景管理，不将显示树当完整实体系统。

## 脚本与数值

JS/TS，Ticker 驱动表现；规则、碰撞与物理库需要显式选择并与渲染解耦。

## 资产管线

Assets/图集/字体与纹理生命周期，切场景销毁 GPU 资源，检查批处理与资源卸载。

## 坐标与尺度

2D Y-down；anchor/pivot、DPR、分辨率缩放和 UI 坐标明确转换。

## 输入与 UI

Federated Events 映射动作；键盘与手柄另接输入层，测试命中区域。

## 存档与联网

自建版本化存档/网络层；不假定 renderer 附带物理或联网。

## 测试与证据

规则单测 + 浏览器输入回放/视觉基线；渲染内存和上下文丢失专项测试。

## 构建与导出

沿用项目 lockfile 与实际 scripts；静态包在 HTTP 下检查纹理/字体 URL、缓存更新与降级。

## 约束与风险

完整玩法、物理、编辑器与存档是额外设计工作；视觉快照不代表玩法通过。

## 官方资料

- [官方文档](https://pixijs.com/8.x/guides/getting-started/intro)
