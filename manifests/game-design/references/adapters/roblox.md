# Roblox Studio 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

UGC/多人在线平台体验；平台内发布。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "*.rbxl",
    "*.rbxlx"
  ],
  "json_keys": [
    [
      "*.project.json",
      [
        "tree"
      ]
    ]
  ]
}
```

## 版本与工具链

记录 Studio 版本、Experience/Place 快照和包版本；Rojo 可选且不能仅凭 *.project.json 认定。

## 场景与实体

DataModel/Instance/Model→对象；Workspace→世界；Services 和 Packages 明确边界。

## 脚本与数值

Luau，ServerScriptService/StarterPlayerScripts/ReplicatedStorage 区分权威、客户端与共享模块。

## 资产管线

Asset ID、模型/动画/音频许可与平台审核状态留记录；云资产快照与本地源映射。

## 坐标与尺度

Y-up、stud 单位，角色/相机/碰撞按平台约定；不与其他引擎米制值直接共用。

## 输入与 UI

跨设备动作映射、UI navigation、移动/手柄；避免仅桌面键盘体验。

## 存档与联网

DataStore 预算/重试/迁移；server authority，RemoteEvent 参数验证和多人状态同步。

## 测试与证据

Studio Play + Server & Clients，区分客户端/服务器日志；设备与网络模拟后仍需目标设备试玩。

## 构建与导出

Studio 保存/发布流程，先隔离测试 place；Rojo 同步是可选工程工具，不等同平台发布。

## 约束与风险

不默认开通 API 服务或写生产 DataStore；测试数据与生产体验分离；发布必须经过明确人工门。

## 官方资料

- [官方文档](https://create.roblox.com/docs/studio/testing-modes)
