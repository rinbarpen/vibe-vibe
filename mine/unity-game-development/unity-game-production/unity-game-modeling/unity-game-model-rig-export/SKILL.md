---
name: unity-game-model-rig-export
description: 完成 Unity 模型可选骨架/权重与动作小样、DCC 导出重开以及实际 Unity 导入检查；按已验证 importer 选择 FBX 或 glTF/GLB，静态道具可跳过绑定。
---

# 可选绑定、导出与 Unity 集成

## 输入与职责

接收真实网格/表面源、尺寸/pivot、角色静态或动画用途、骨架/socket/动作需求、预算、Unity/管线与已装 importer。`model-artist` 单写源；绑定需求与 `animation-vfx-artist` 协作；`technical-artist` 单写 Unity 导入与 Prefab。沿用用户指定 DCC，检查真实已连 MCP 工具 schema、已安装软件 skill 或 CLI 后再操作，先源副本小样，不自动安装插件或切换项目。

## 绑定分支

静态道具明确记 rig/retarget“不适用”及理由，不创建无用骨架。需要变形时检查骨架层级、命名、rest/bind pose、尺度和 socket，保留约束源；导出所需的烘焙骨骼与控制骨区分。核对未分配顶点、归一化权重、每顶点影响数与目标预算；在肩肘膝/极限姿态测试体积和穿插，不能仅凭站姿通过。

按实际需求验证 Generic 或 Humanoid、Avatar/retarget、root motion 和动画片段范围，映射不是自动成功。至少一个真实动作小样，检查根位移、骨骼缩放、blend shapes 和 socket 跟随。保留绑定源可编辑性，不盲目应用变换破坏已有 skin。

## 导出与导入

1. 先核实实际 exporter 与 Unity importer：优先现有项目兼容链路。FBX 记录软件/插件版本与选中对象、单位/轴向、mesh/骨架/动画/材质导出策略；glTF/GLB 只在工程确有对应 importer、支持所用扩展且小样验证后采用，不称所有 Unity 工程原生支持。外部依赖安装另行确认。
2. 导出到独立任务路径，核对纹理依赖、对象命名、尺寸/轴/pivot、三角化、法线/切线、材质槽与骨架；重导入新 DCC 场景检查数据，保留原源文件。记录导出参数、文件哈希、重开操作和测量结果；导出命令成功但文件缺失/损坏记失败。
3. 由唯一 Editor owner 在匹配版本的工程导入；检查编译/导入日志、import scale、法线/切线、Rig/Avatar/动画、贴图/材质与实际渲染管线，Editor 生成 `.meta`。资产移动与 `.meta` 成对，避免 GUID 丢引用；外部脚本不伪造导入完成或 GUID。
4. 在实际测试场景校准比例/朝向/pivot、碰撞、LOD 切换、材质、动作与 socket；按真实平台核对内存/绘制/骨骼预算。只在 DCC 打开过模型时，Unity 导入/场景/设备仍分别记 `not_run`。

## 输出与交接

交真实源文件、导出文件及纹理、Unity 资源与 Editor 实际生成的 `.meta`（完成导入时）、参数清单、重开/导入日志、场景/动作证据和 `model-ID-export.md`。逐项记路径/哈希、revision、检查的 `passed` / `failed` / `not_run`，缺工具/平台列具体补验操作。

独立 `game-reviewer` 用 `unity-game-model-review` 只读复核；返工返回确切 owner。文档落指定目录，manifest 默认 `.unity-game/deliverables/`，独立默认 `docs/unity-game/`；单独安装无需父技能。保存任务副本而非覆盖用户未保存源场景，保留恢复路径；共享状态由 producer 更新。

格式依据版本匹配的 [Unity 模型格式说明](https://docs.unity.com/en-us/engine/6000.6/manual/assets-and-media/asset-types/models/creating-dccassets/3d-formats)；glTF 项目依赖和行为可对照 [Unity glTFast importer 文档](https://github.com/Unity-Technologies/com.unity.cloud.gltfast/blob/main/Packages/com.unity.cloud.gltfast/Documentation~/ImportEditor.md)。
