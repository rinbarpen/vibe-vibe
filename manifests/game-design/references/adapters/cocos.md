# Cocos Creator 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

移动、Web 与小游戏平台，组件化 2D/3D。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "json_keys": [
    [
      "package.json",
      [
        "creator"
      ]
    ]
  ]
}
```

## 版本与工具链

读取 package.json creator.version；2.x/3.x 分支与构建参数分别处理，小游戏 SDK 跟平台锁定。

## 场景与实体

关卡→Scene，实体→Node/Component，复用→Prefab，UI→Canvas/Widget。

## 脚本与数值

3.x TypeScript 组件；数值配置与生命周期分离，资源 UUID 和序列化引用保持稳定。

## 资产管线

assets/.meta 成对保存，Asset Bundle/图集/纹理压缩按分包预算设计。

## 坐标与尺度

记录 2D UI 与 3D 坐标约定；适配分辨率、安全区、DPR 与相机投影。

## 输入与 UI

事件系统/触摸输入；小游戏平台返回、暂停、音频激活和触点冲突专项测试。

## 存档与联网

本地存储与平台用户数据分离；联网重试、平台登录和业务版本迁移分别设计。

## 测试与证据

纯逻辑测试 + Creator 预览 + 平台开发者工具 + 真机，分包加载/后台恢复/弱网留日志。

## 构建与导出

3.x 模板："$CREATOR" --project "$PROJECT" --build "configPath=$CONFIG"；从当前 Editor 构建面板导出配置。3.8 文档成功码为 36，失败码 32/34，不能套统一 exit=0。

## 约束与风险

小游戏不是普通 Web 页面；GUI/SDK/签名依实际工具链；2.x 的 --path 不能直接套到 3.x。

## 官方资料

- [官方文档](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html)
