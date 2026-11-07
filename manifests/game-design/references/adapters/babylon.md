# Babylon.js 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

浏览器 3D、可选 WebXR 和较完整的场景工具链。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "dependencies": [
    "@babylonjs/core",
    "babylonjs"
  ]
}
```

## 版本与工具链

锁定 @babylonjs 全套包版本、渲染后端与 lockfile；物理插件版本匹配。

## 场景与实体

Scene/Mesh/TransformNode 与 Entity 领域层映射，关卡流式和资产容器单独设计。

## 脚本与数值

JS/TS；行为状态与渲染循环分离，配置表通过类型化数据进入。

## 资产管线

glTF/GLB、PBR、纹理、骨骼与 AssetContainer；加载/销毁和 Inspector 检查。

## 坐标与尺度

默认左手系、可切右手系；坐标选择写进 TDD，验证 glTF 转换和物理尺度。

## 输入与 UI

输入管理器/ActionManager 或自定义动作层；测试摄像机控制、UI 焦点和手柄。

## 存档与联网

存档模型独立于 Scene 快照；联网与后端权限设计单独验收。

## 测试与证据

领域单测、浏览器玩法、物理与动画回放；WebGPU/WebGL 兼容按项目目标测试。

## 构建与导出

沿用已安装包和 package scripts，HTTP 验证 asset URLs、引擎包拆分与加载失败恢复。

## 约束与风险

Havok 等物理依赖与包体成本需单独审查；WebXR 与目标设备是附加验收。

## 官方资料

- [官方文档](https://doc.babylonjs.com/)
