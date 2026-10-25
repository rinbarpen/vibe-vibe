---
name: unity-game-model-surface
description: 执行 Unity 模型 UV、烘焙、PBR 贴图、材质槽和色彩空间校验，交付可编辑表面源文件与符合实际渲染管线的纹理资源。
---

# UV、贴图与材质制作

## 输入与工具

取得实际网格/高低模、冻结材质方向、目标管线/Shader、纹理与材质预算、UV 通道用途、许可及修改范围。`model-artist` 写 UV/表面源，`technical-artist` 写 Unity 材质/import settings；同一贴图库单写。先核查所选 DCC/绘制软件真实 MCP、软件 skill 或 CLI，实际读取工具 schema/版本后小样操作；不把不存在的插件当调用接口。

## 执行

1. 检查最终拓扑与法线稳定后展 UV：按用途处理接缝、texel density、拉伸、padding 和镜像重叠。纹理复用可有意重叠；烘焙/光照 UV 按实际用途单独核查，不一概要求所有通道唯一。
2. 需要高低模烘焙时保留 cage/投射参数、对象匹配和输出尺寸；检查接缝、穿透、遮挡和硬边伪影，确认切线空间及法线图约定。参数记录与贴图必须对应同一网格 revision。
3. 实际制作/导出 Base Color、normal、metallic/roughness 或项目需要的通道；不要假定任意 DCC 的 PBR 节点可原样成为 Unity Shader。按目标 Shader 核对 metallic/smoothness 与 roughness 的换算、打包槽位和 alpha 用途，保留可编辑源和无损主纹理。
4. 颜色贴图与数据贴图区分：Base Color 等视觉颜色按实际导入流程使用颜色转换；法线、遮罩、粗糙度等数据不得误套 sRGB。记录每个贴图的通道含义、色彩空间、尺寸、位深、透明与压缩假设，Unity 端由 technical-artist 实测核对。
5. 材质槽按预算合并/复用但保留必要透明/双面区别；检查实际引用，不交断链纹理。在一致光照与游戏视角下对照参考，确认不靠 DCC 专属效果掩盖导出缺失。
6. 保存并重开源文件，重新读取贴图尺寸/通道与路径；导出结果存在且可解码后再登记完成。只对任务副本做写入，保留原件，临时保存验证后替换。

## 输出与验收

交 UV 视图/拉伸检查、真实纹理、可编辑表面源、烘焙参数、材质槽/通道映射、许可和 `model-ID-surface.md`，列每项路径/SHA-256及工具操作结果。按预算检查 texel density、内存假设、材质槽与接缝；截图不代替贴图文件。

交 `technical-artist` 在 Unity 实际管线验证 Shader、色彩空间、法线类型、mipmap/压缩和场景观感；DCC 通过但缺 Editor 时导入验收记 `not_run`。独立 reviewer 可使用 `unity-game-model-review`，本技能无需父技能即可执行。文档落指定目录，manifest 默认 `.unity-game/deliverables/`，独立默认 `docs/unity-game/`；不修改共享阶段状态或其他 owner 的 `.meta`。
