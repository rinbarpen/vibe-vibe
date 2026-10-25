---
name: unity-game-modeling
description: 执行 Unity 游戏角色、道具和环境的 3D 模型设计、外部 DCC 建模、贴图材质、绑定导出与独立模型审查；支持通过实际可用的 MCP、软件 skill 或 CLI 操作外部软件。
---

# Unity 3D 模型全链路

## 任务与软件选择

先识别任务是概念规格、单个模型、批次资产还是完整链路；沿用用户指定的 Blender、Maya、3ds Max 或现有工作室工具，不自动更换软件。读取实际资产 ID、视觉方向、相机/互动距离、目标设备与渲染管线、现有源场景及用户编辑范围。`model-artist` 负责模型源文件，`technical-artist` 负责 Unity 导入，`art-director` 确认视觉取舍；需要动画时交 `animation-vfx-artist`。

按当前环境选择实际可操作路线，不把“支持 MCP”当成已经连接：
1. **已连接 MCP**：发现真实服务器/工具，读取参数 schema、当前文件与选择对象；先在源文件副本上做最小可验证操作，核对返回值和软件对象，再扩大批次。工具名、连接状态、保存/重开均记录实际结果，不猜测服务器或方法名。
2. **已有外部软件 skill**：定位真实安装路径并读取其 `SKILL.md`，确认支持所选软件及任务后执行；技能名称本身不证明软件已安装或工具可用。
3. **软件 CLI/API**：检查真实可执行文件、版本及项目插件。Blender 可在已安装且相关 helper 确实存在时走 CLI，先读 helper 的帮助与版本要求；Maya/Max 使用实际可用的宿主接口。只需 GUI 时走已安装的 computer-use skill。调用成功还需打开产物检查。
4. 缺少可操作软件时可完成规格与可复现操作方案；模型文件、导出、导入对应项记 `not_run`，保留具体缺口，不生成空文件冒充资产。安装软件、插件、连接服务器或上传源资产均另行确认具体动作。

同一 DCC 源场景由一个 owner 写；先检查未保存改动，保存源副本再修改，不无人值守替换现有场景。独立模型可并行；共享贴图、材质库和 Unity 序列化资源各设单写者。脚本化写入先输出临时文件，验证后原子替换受管副本；保留原件与回滚路径。

## 按环节执行 subskills

只加载当前任务需要的子技能；它们也可独立安装：
- [unity-game-model-design](unity-game-model-design/SKILL.md)：参考视图、轮廓、尺度、预算与生产规格。
- [unity-game-model-build](unity-game-model-build/SKILL.md)：实际 DCC blockout、高低模/拓扑、法线、LOD 与碰撞代理。
- [unity-game-model-surface](unity-game-model-surface/SKILL.md)：UV、烘焙、PBR 贴图、材质槽与管线匹配。
- [unity-game-model-rig-export](unity-game-model-rig-export/SKILL.md)：可选绑定、权重、动作检查、导出与 Unity 集成。
- [unity-game-model-review](unity-game-model-review/SKILL.md)：独立只读模型审查，返工闭环。

完整链路是规格冻结 → 代表模型小样 → 网格 → 表面 → 可选绑定/导出 → Unity 导入/场景验证 → 独立审查。规格和模块化设计可并行；依赖网格的 UV/烘焙及依赖骨架的动画等冻结后推进。只要求一个专项时不强制执行整个链路。

## 产物与完成判定

有 manifest 时使用 `.unity-game/deliverables/`，否则用指定目录，默认 `docs/unity-game/`。源资产、导出物、贴图放实际项目资产目录，不把交付文档当游戏资源。维护模型清单：资产 ID、owner、DCC/版本、源/导出/贴图/Unity 路径、单位/轴/pivot、预算与实测、许可、操作证据及 SHA-256。

DCC 保存、导出重开、Unity Editor 导入、场景/设备测试是不同验证项，分别记 `passed` / `failed` / `not_run`。由 Editor 生成 `.meta`，移动时资源与 `.meta` 成对保留；外部 DCC 成功不代表 Unity 可用。概念图、生成提示词、程序模板不是已交付模型。FBX 与 glTF/GLB 按实际项目 importer 和导出器版本选型；glTF 需核查项目所装 importer 及扩展支持，不假定所有 Unity 工程原生支持。先验证一个真实模型再批量。

每项交付原始工具调用/日志、重开结果、网格/贴图测量和真实预览；缺 Editor 时保留导入/场景待验。独立 `game-reviewer` 执行模型审查，再按 `unity-game-review` 的 production profile 汇总（该技能实际安装时调用）；审查者不修改模型或共享状态。`changes_requested` 返回具体源 owner/执行 skill，修复后绑定新 revision/哈希复审；生产阶段状态只由 producer 更新。

格式核对参考版本匹配的 [Unity 模型格式文档](https://docs.unity.com/en-us/engine/6000.6/manual/assets-and-media/asset-types/models/creating-dccassets/3d-formats)、[Unity glTFast Editor importer](https://github.com/Unity-Technologies/com.unity.cloud.gltfast/blob/main/Packages/com.unity.cloud.gltfast/Documentation~/ImportEditor.md) 和 [Blender FBX 文档](https://docs.blender.org/manual/en/latest/files/import_export/fbx.html)；项目版本优先于文档示例。
