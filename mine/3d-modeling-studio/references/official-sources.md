# 官方资料与版本核验

整理日期：2026-11-08。入口可能随产品更新跳到新版本；执行时以实际安装版本的文档/API 为准。该列表是工作流的查证入口，不代表本环境已运行全部应用。不要照抄开发版功能到稳定版。

## 多边形、雕刻与程序化

- [Blender 4.5 手册](https://docs.blender.org/manual/en/4.5/)：固定的脚本基线，不声称是最新版。
- [Blender Bevel](https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/bevel.html)、[Subdivision](https://docs.blender.org/manual/en/4.5/modeling/modifiers/generate/subdivision_surface.html)、[Baking](https://docs.blender.org/manual/en/4.5/render/cycles/baking.html)：参数意图与限制。
- [Blender CLI](https://docs.blender.org/manual/en/4.5/advanced/command_line/arguments.html)、[Object API](https://docs.blender.org/api/4.5/bpy.types.Object.html)：命令顺序、Python 错误退出、evaluated mesh 与释放。
- [Maya Quad Draw](https://help.autodesk.com/cloudhelp/2024/ENU/Maya-Modeling/files/GUID-03933C1F-1BA7-4E7E-AAB5-31FB0E6A77B2.htm)：表面参考上的手工拓扑；文档固定 2024，其他 UI 以实际版本查证。
- [Maya 2026 Flow Retopology](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-WhatsNew/files/GUID-9BFCEFCC-AFA0-4B79-9B78-FE7C0F3B341D.htm)：云端能力与本地工作流要分开。
- [3ds Max Retopology](https://help.autodesk.com/cloudhelp/2022/ENU/3DSMax-Retopology/files/GUID-57B77A00-5300-47CB-99E1-22B9C536B060.html)、[Weighted Normals](https://help.autodesk.com/cloudhelp/2024/ENU/3DSMax-Modifiers/files/GUID-6BFC22D5-D9DA-45BC-87A7-D95BFAD083E1.htm)：输入整理与显式法线。
- [Cinema 4D Volume Builder](https://help.maxon.net/c4d/en-us/Content/html/OVOLUMEBUILDER.html)：体积生成和网格化。
- [ZBrush ZRemesher](https://help.maxon.net/zbr/en-us/Content/html/reference-guide/tool/polymesh/geometry/zremesher/zremesher.html)：引导、边界和密度控制。
- [Houdini Remesh](https://www.sidefx.com/docs/houdini/nodes/sop/remesh.html)、[PolyReduce](https://www.sidefx.com/docs/houdini/nodes/sop/polyreduce.html)、[HOM](https://www.sidefx.com/docs/houdini/hom/index.html)：节点/属性与宿主接口。
- [Nomad Sculpt manual](https://nomadsculpt.com/manual/)：移动雕刻功能与文件交换以设备/版本确认。

## 曲面、参数化与建筑

- [Rhino QuadRemesh](https://docs.mcneel.com/rhino/8mac/help/en-us/commands/quadremesh.htm)、[SubD 网格规则](https://docs.mcneel.com/rhino/8/help/en-us/information/meshingrulesofsubd.htm)：重拓扑目标和显示/导出密度的区别。
- [Rhino Python 3](https://developer.rhino3d.com/guides/rhinopython/python-3-in-rhino/)：宿主 ScriptEditor 与运行时选择。
- [Fusion Scripts and Add-Ins](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/WritingDebugging_UM.htm)：宿主 API 开发入口。
- [SolidWorks API](https://help.solidworks.com/2026/english/api/sldworksapiprogguide/Welcome.htm)：按实际版本查对象模型、返回值与运行方式。
- [FreeCAD 官方功能](https://www.freecad.org/features.php)：工作台、参数化和 Python；具体 API 从当前安装的官方文档核验。
- [SketchUp Ruby API](https://ruby.sketchup.com/)：桌面宿主扩展与事务接口。

## 表面、服装与展示

- [Substance Painter 烘焙流程](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/baking/how-to-bake-mesh-maps)、[导出模板](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/export/export-window/output-templates)：cage、烘焙日志与通道映射。
- [Substance 3D 文档](https://experienceleague.adobe.com/en/docs/substance-3d)：Designer/Painter 当前功能和接口入口。
- [Marvelous Designer Support](https://support.marvelousdesigner.com/hc/en-us)：版型、模拟与导出；脚本/API/批处理能力单独确认。
- [Marmoset 文档](https://docs.marmoset.co/)：按当前 Toolbag 版本查烘焙和材质。
- [Unreal Nanite](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-in-unreal-engine)：平台、材质/变形与性能约束会演进。
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)、[glTF 规范](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)：目标消费端和交换格式的真实能力。

## 新软件或新版本的最小适配

1. 确认几何体系、强项、宿主/脚本入口、平台和许可。
2. 验证能创建一个小对象、修改参数、保存原生文件、导出交换件并重新打开；记录实际命令、版本与结果。
3. 确认单位/轴、细分/实例、UV/法线、材质与外链的传递情况；列出不保留的信息。
4. 再把精细建模配方映射到本应用操作；未通过最小适配时保留指南/脚本状态，不宣告宿主执行成功。
