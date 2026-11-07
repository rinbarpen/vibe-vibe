# Unreal Engine 适配器

> 由 engines.json 生成；修改数据后运行 render-adapters。

高保真 3D、大型关卡、Blueprint/C++ 协同与多人体验。

状态：设计/工程映射已登记；运行时验证 **not_run**。

识别规则（仅线索，不选择/升级引擎）：

```json
{
  "files": [
    "*.uproject"
  ]
}
```

## 版本与工具链

读取 .uproject EngineAssociation、插件和 Target.cs；匹配已装 UE 与工具链，禁止隐式资产升级。

## 场景与实体

规则→GameMode/GameState；玩家→Controller/Pawn；关卡→World/Level；复用→Actor/Component/Blueprint。

## 脚本与数值

C++ 保持稳定接口，Blueprint 负责可视化组合；数值→DataAsset/DataTable。

## 资产管线

.uasset/.umap 属二进制，使用 LFS/文件锁或项目既有分工；导入材质、骨骼、LOD 和碰撞需要 Editor 核验。

## 坐标与尺度

Z-up、厘米；DCC 米制转换、左右手坐标差异、导航代理与根运动统一验收。

## 输入与 UI

Enhanced Input 的 Action/Mapping Context；测试 UI 焦点、手柄与触控。

## 存档与联网

SaveGame 版本化；多人明确 server authority、Replication/RPC 与断线重连。

## 测试与证据

Automation/Functional Test + PIE 多客户端；Shipping/Development 包分别测试，检查 cook 日志与 Insights。

## 构建与导出

模板："$RUN_UAT" BuildCookRun -project="$UPROJECT" -platform="$PLATFORM" -build -cook -stage -pak；按主机选 RunUAT.sh/bat，补项目实际打包/归档参数。

## 约束与风险

PIE 通过不代表 cook 后通过；禁止文本批改二进制资产；World Partition、插件和平台 SDK 随版本核验。

## 官方资料

- [官方文档](https://dev.epicgames.com/documentation/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine)
