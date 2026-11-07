# raylib 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

C/C++ 小型 2D/3D、教学和自定义工具链。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "text": [
    [
      "CMakeLists.txt",
      "raylib"
    ],
    [
      "Makefile",
      "raylib"
    ]
  ]
}
```

## 版本与工具链

锁定 raylib release、编译器、CMake/Make 与平台 backend；vendored 与系统库分开。

## 场景与实体

InitWindow/循环→入口；自行定义状态机、实体与关卡数据，不依赖虚构 Editor。

## 脚本与数值

C/C++ 模块化规则；资源与生命周期显式管理，接口边界清晰。

## 资产管线

纹理/模型/字体/音频 Load/Unload 成对；工作目录与打包相对路径验证。

## 坐标与尺度

2D 屏幕 Y-down、3D 通常 Y-up；Camera、碰撞和物理约定明示。

## 输入与 UI

键鼠/触控/手柄通过动作层映射；帧时间独立于移动速度。

## 存档与联网

自建文件存档 schema 与联网；内存/字节序/版本兼容按目标考虑。

## 测试与证据

纯逻辑单测/编译器检查 + 实际窗口试玩；内存与资源生命周期单独测试。

## 构建与导出

使用项目已有 CMake preset/Make target；cmake --build "$BUILD_DIR" 仅在已配置构建树后执行。

## 约束与风险

不是全功能编辑器；不得默认所有 raylib 项目使用 CMake 或可直接交叉编译。

## 官方资料

- [官方文档](https://www.raylib.com/)
