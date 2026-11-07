# Bevy 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

Rust ECS、系统组合与定制 2D/3D。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "text": [
    [
      "Cargo.toml",
      "BEVY_DEPENDENCY"
    ]
  ]
}
```

## 版本与工具链

锁定 Cargo.lock、rust-toolchain 和 Bevy 主次版本；插件 API 随版本快速变化。

## 场景与实体

Entity/Component/System→玩法对象，States/Schedules→流程，Scenes/Assets→内容。

## 脚本与数值

Rust ECS 系统；事件/消息与资源按当前版本 API，领域逻辑可脱离渲染 App 测试。

## 资产管线

AssetServer/Handle、glTF/纹理，异步加载状态与卸载检查。

## 坐标与尺度

2D/3D 与 transform、camera、物理插件坐标统一，固定时间步与渲染更新分离。

## 输入与 UI

Action mapping 基于当前输入 API 或已锁定插件，焦点/手柄/触控检查。

## 存档与联网

显式序列化领域数据，不直接存 ECS world；联网插件与 authority 单独确定。

## 测试与证据

cargo test 测纯逻辑/无窗口 App；cargo check 不等同测试；GPU/输入/音频需真实运行。

## 构建与导出

工程根 cargo check --locked、cargo test --locked；发布按实际 target/features 的 cargo build --release --locked，并包含资产。

## 约束与风险

workspace 继承版本需按 member 解析；不把任意 Cargo 项目识别为 Bevy，不自动升级生态插件。

## 官方资料

- [官方文档](https://github.com/bevyengine/bevy)
