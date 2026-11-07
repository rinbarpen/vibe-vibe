# O3DE 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

开源大型 3D、组件系统与自定义管线。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "json_keys": [
    [
      "project.json",
      [
        "project_name",
        "engine"
      ]
    ]
  ]
}
```

## 版本与工具链

读取 project.json、engine.json、Gem 与 CMake preset；版本、编译器和目标平台锁定。

## 场景与实体

Entity/Component、Prefab、Level 映射玩法；Gem 边界与系统组件职责明确。

## 脚本与数值

C++/Lua/Script Canvas 按项目实际选择；配置与规则分离。

## 资产管线

Asset Processor、源资产与 asset cache 分开；Prefab 引用、材质/模型处理状态检查。

## 坐标与尺度

明确项目 Z-up/米制约定，DCC、相机和 PhysX 统一验证。

## 输入与 UI

Input 系统映射设备动作，UI 与世界输入分流。

## 存档与联网

自建版本化存档；联网使用项目选定 Gem，authority/replication 单独设计。

## 测试与证据

C++/Gem 测试 + Editor/GameLauncher，Asset Processor 失败与运行时加载分别追踪。

## 构建与导出

使用项目已验证的 CMake presets 与 O3DE export 工具；先完成资产处理，再导出目标 runtime。

## 约束与风险

构建树/资产缓存体积和编译器成本大；不使用通用 project.json 文件名直接判定。

## 官方资料

- [官方文档](https://docs.o3de.org/docs/)
