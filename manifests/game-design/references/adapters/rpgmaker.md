# RPG Maker MZ/MV 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

地图/事件/数据库驱动 RPG；MZ 与 MV 分开管理。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "*.rmmzproject",
    "*.rpgproject"
  ]
}
```

## 版本与工具链

记录 MZ/MV、runtime 与插件顺序；绝不混用两代 API、插件和项目文件。

## 场景与实体

Map/MapEvent→关卡互动，Common Event→复用，Actor/Class/Skill/Enemy/Troop→系统数据。

## 脚本与数值

事件页、开关/变量优先；JS 插件是版本化扩展，数值按数据库 ID 绑定。

## 资产管线

img/audio/tilesets 与数据库 JSON/插件保留引用，地图和数据库通过 Editor 管理。

## 坐标与尺度

地图格坐标与像素移动分离；按 tileset、UI 分辨率、相机与插件核验。

## 输入与 UI

键盘/手柄/触控、菜单/对话输入、事件页触发优先级专项测试。

## 存档与联网

存档中的开关/变量/插件对象兼容；数据库 ID 不随意重排。

## 测试与证据

Test Play、战斗测试、事件死锁/传送/支线可达性、旧存档与部署包 QA。

## 构建与导出

Editor Deployment 按目标发布；剔除未使用资源前检查插件动态引用，签名与商店发布独立。

## 约束与风险

不把插件兼容当默认；动态资源误删和开关编号冲突是重点风险。

## 官方资料

- [官方文档](https://rpgmakerofficial.com/product/MZ_help-en/)
