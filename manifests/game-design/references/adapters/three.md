# Three.js 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

自定义浏览器 3D、轻量交互和实验性游戏；属于渲染库。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "dependencies": [
    "three"
  ]
}
```

## 版本与工具链

锁定 three revision、addons、GLTF/DRACO/KTX2 解码器与构建锁文件。

## 场景与实体

Scene/Object3D/Mesh 负责显示层，另建实体生命周期、关卡与玩法状态机。

## 脚本与数值

JS/TS；render loop 与固定步长模拟分离，物理/寻路/碰撞库单独选择。

## 资产管线

glTF/GLB、PBR、纹理颜色空间和压缩贴图；显式 dispose 几何体/材质/纹理。

## 坐标与尺度

通常右手 Y-up，单位由项目约定；相机、物理和 DCC 缩放统一。

## 输入与 UI

Pointer/Keyboard/Gamepad/WebXR 按目标映射动作；Raycaster 仅是拾取不是完整交互系统。

## 存档与联网

单独设计存档、网络同步和 authority；避免渲染对象序列化成为存档格式。

## 测试与证据

领域单测 + 浏览器交互 + GPU/帧时/上下文恢复；实际触控与设备测试独立。

## 构建与导出

按 package scripts 构建，HTTP 验证模型/解码器路径、CORS、WebGL 能力与部署 base URL。

## 约束与风险

不自带完整玩法/物理/编辑器；不能将可旋转模型示例称为可玩原型。

## 官方资料

- [官方文档](https://threejs.org/manual/#en/fundamentals)
