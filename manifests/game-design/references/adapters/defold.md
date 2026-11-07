# Defold 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

轻量 2D/3D、移动/Web 与 Lua 组件式开发。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "game.project"
  ]
}
```

## 版本与工具链

锁定 Editor/Engine/Bob 版本、JDK 和依赖 URL/commit；不假定任意 bob.jar 匹配。

## 场景与实体

Collection→场景，GameObject/Component→实体，Factory/CollectionFactory→生成。

## 脚本与数值

Lua scripts/gui_scripts 与消息系统，配置属性/资源，纯规则模块独立测试。

## 资产管线

Atlas/Tile Source/Model，依赖从构建根可达；动态 raw 文件放 Custom Resources。

## 坐标与尺度

记录世界/GUI 坐标、投影与物理尺度；相机与不同屏幕比例分别验证。

## 输入与 UI

Input binding 与 acquire_input_focus；GUI/多触点/手柄焦点管理。

## 存档与联网

sys.save/load 版本化，网络消息与游戏状态边界明确。

## 测试与证据

Lua 规则测试 + Editor 运行 + 真机；消息时序、collection 生命周期和加载失败专项测试。

## 构建与导出

在工程根模板：java -jar "$BOB" --archive --platform "$PLATFORM" resolve build bundle；核验 JDK、平台、扩展服务器与签名。

## 约束与风险

native extension 可能使用远程构建服务，先记录依赖和数据边界；构建根不可达资源不会自动进入包。

## 官方资料

- [官方文档](https://defold.com/manuals/bob/)
