# libGDX 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

Java/Kotlin 跨平台、代码优先 2D/3D。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "text": [
    [
      "build.gradle",
      "com.badlogicgames.gdx"
    ],
    [
      "build.gradle.kts",
      "com.badlogicgames.gdx"
    ],
    [
      "gradle.properties",
      "gdxVersion"
    ]
  ]
}
```

## 版本与工具链

锁定 Gradle Wrapper、JDK、gdx 与各 backend；旧 lwjgl 与 lwjgl3 区分。

## 场景与实体

Game/Screen→场景，Scene2D→UI/2D 表现；实体系统根据实际需求选择。

## 脚本与数值

Java/Kotlin，核心逻辑在 core，平台代码在 backend；数值表与资源服务分离。

## 资产管线

AssetManager/TextureAtlas/模型与字体，引用计数与 dispose 生命周期明确。

## 坐标与尺度

世界/相机与 Scene2D Viewport 分离；输入坐标转换和物理尺度验收。

## 输入与 UI

InputProcessor/InputMultiplexer 映射动作，Android 返回/暂停/恢复按平台处理。

## 存档与联网

Files/Preferences 或显式版本化存档；网络接口和线程边界明确。

## 测试与证据

已有 Gradle test 任务测逻辑，图形 backend 真实运行；安卓生命周期和资源泄漏另测。

## 构建与导出

先用 ./gradlew tasks 确认可用 backend 任务，再执行项目已有 lwjgl3/Android/其他目标构建任务。

## 约束与风险

不硬编码所有项目都有 desktop:dist；HTML backend 与反射/库兼容需查项目实际选择。

## 官方资料

- [官方文档](https://libgdx.com/wiki/)
