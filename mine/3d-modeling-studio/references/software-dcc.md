# 多边形、雕刻与程序化软件路线

## 选路表

| 软件 | 优先用途 | 执行入口 | 本 Skill 的支持层级 |
|---|---|---|---|
| Blender | 通用多边形、精细硬表面、雕刻、程序化与渲染 | `bpy` / 后台 CLI / Geometry Nodes | 附可执行审计与辅助渲染脚本 |
| Maya | 角色、动画友好拓扑、影视资产 | 宿主 Python `maya.cmds` / OpenMaya / mayapy 初始化 | 工作流与自动化入口指南 |
| 3ds Max | 硬表面、建筑、产品、批量场景 | MAXScript / 宿主 `pymxs` | 同上 |
| Cinema 4D | 设计产品、动态图形、样条和体积造型 | 宿主 `c4d` Python / 节点 | 同上 |
| Houdini | 参数资产、环境、变化体、扫描处理 | SOP / VEX / HOM `hou` / hython | 同上 |
| ZBrush | 高精度生物雕刻、硬表面雕刻、雕塑 | UI / ZScript / 版本对应的可用自动化 | 同上；不预设通用 Python 支持 |
| Nomad Sculpt | 平板草模、雕塑与概念雕刻 | UI / 文件交换 | 操作与转交指南，不预设桌面脚本接口 |

先记录安装版本和插件，再查对应版本的官方文档。以下是建模决策与栈示意，不是每种资产固定照抄的顺序。

## Blender

### 硬表面

1. 使用真实尺度搭建命名部件，必要时在副本应用非均匀缩放，再标定倒角尺寸。
2. 可调的典型路线：`Mirror / Array → Boolean → Bevel → 法线处理`。细分路线则先整理控制笼、支撑线和角点，再加入 Subdivision Surface；先后顺序取决于希望倒角作用于原形还是布尔切口。
3. Boolean 用于结构孔洞和拼接，保留 cutter 集合。检查薄片、共面和锐角；平面 n-gon 可在不细分、不变形且三角化后稳定时保留；曲面与变形区重建边流。
4. 倒角分主边/次边/微边，先以物理工艺和画面高光定宽度，再增分段。加权法线/平滑修正阴影，不修复错误轮廓。
5. 斜长软箱灯扫过曲面，找波纹、夹痕和倒角断裂；同时看线框。

### 雕刻与程序化

- Voxel Remesh / Dyntopo 适合探索拓扑；保留备份。UV、固定顶点编号、形态键或多层细节形成后，不在同一生产网格上随意重体素化。
- Multires 保存雕刻层级；大形在低层修，微细节在高层处理。拓扑变化前先验证其与现有 Multires 的兼容性。
- Geometry Nodes 的重复部件优先实例，导出器确需真实几何时只在副本 Realize Instances。让尺寸、密度、种子、LOD 成为组输入；检查极值而非仅默认值。
- 部件有不同密度需求时分对象/集合，不给整场景统一加高阶细分。

### 执行

```bash
blender --background --factory-startup --disable-autoexec --python-exit-code 1 \
  --python build_asset.py -- --output /absolute/path/model.blend
```

`build_asset.py` 是项目专属脚本，按真实宿主版本编写并运行；本 Skill 不把通用审计脚本当成资产生成器。审计/辅助图命令见执行指南。使用数据 API 减少选择态依赖；必须用 `bpy.ops` 时设置活动对象、模式和上下文。

## Maya

- Blockout 用命名 transform/组和实例，原形保留；禁止无目的全场景 Delete History 或 Freeze Transform。
- 多边形控制笼配合 Smooth Mesh Preview 校形；预览不是已导出的高模，交付时明确实际细分和烘焙状态。
- 高模设为 live surface，用 Quad Draw 手动铺设关键边流；自动 Retopologize 用于候选基础网格，眼/口/肩/肘/膝/指关节人工整理。
- 关节处让边环顺受力折叠，极点离开高曲率/强变形区域；用目标动作、Blend Shape 极值验证，而不是只看 T pose。
- 高精度硬表面用 Bevel 的分段、宽度与角点检查；Mesh Cleanup 在副本检查非流形、零面积和叠面。
- UV Toolkit 设置缝与 UDIM；导出前确定软硬边、显式法线和切线空间。
- `maya.cmds` 脚本在 Maya 宿主执行；`mayapy` 的独立运行需 `maya.standalone.initialize()`，且不代表交互式 UI/渲染器或全部插件已可用。使用 undo chunk 包裹可撤销操作。
- Maya 2026 的 Flow Retopology 涉及云处理：不是本地 Quad Draw 的同义词，也不是默认必需依赖。使用前明确上传、费用和实际功能可用性。
- 原生 `.ma/.mb`，交换按项目选 FBX/USD/Alembic；动画、缓存、材质能力分别验证。

## 3ds Max

- 常用非破坏路线：`Edit Poly → Symmetry → Chamfer → Weighted Normals`；需要平滑曲面时另选 TurboSmooth/OpenSubdiv 并整理控制笼，不把两条路线机械叠加。
- 单独检查 smoothing groups、显式法线与导出切线；平滑组不是几何圆角。
- Retopology 前清理孤立碎片、细长劣质输入和无意义噪点；保持副本，按轮廓和孔洞评估输出，再加需要的法线处理。
- Sweep/Loft/Lathe 做管线、型材和回转体，校验截面方向和拐角扭转。大场景保留 instances、代理与外部引用，交付时收集依赖。
- MAXScript 或 `pymxs.runtime` 必须走对应 3ds Max 宿主，先检测 modifier class 和插件。每次只操作命名集合，记录单位与系统单位。
- 原生 `.max`，交换 FBX/OBJ/USD（视版本插件）；跨宿主验明 chamfer/细分是否需烘焙。

## Cinema 4D

- Spline + Extrude/Lathe/Sweep 建立干净主形；用 Subdivision Surface 时给曲面布线和端盖留出规则，不以细分隐藏端盖夹痕。
- Volume Builder + Volume Mesher 适合融合软硬体块。voxel size 依据最小可见结构选取；先低分辨率验证，局部加密/分对象提高效率。
- 体积输出并非动画拓扑或精密 CAD；近景保形后再按需求重拓扑，倒角/壁厚重新测量。
- MoGraph 重复部件用 Cloner/实例，替换源部件而不是堆复制。导出前仅在交付副本做 Current State to Object/缓存。
- `c4d` Python 在宿主中读写对象并正确提交 Undo/Event；不把 Python 普通解释器当作完整 C4D。
- 原生 `.c4d`；Alembic/USD/FBX 根据层级、动画、材质支持验证。Redshift 是按可用授权选择的渲染器，不是必要前提。

## Houdini

- 建模源树与输出树分离，给 `OUT_HIGH`、`OUT_LOW`、`OUT_COLLISION` 明确 Null。HDA 暴露尺寸、密度、随机种子、detail level，写入参数范围。
- 硬表面常见 SOP：`Curve/Box → PolyExtrude/Boolean → PolyBevel → Normal`；保留 groups/attributes 标记装配和材料。
- 有机融合：VDB From Polygons / Combine / Smooth / Convert，voxel size 与最小结构绑定；保留未体素化输入。
- Remesh 均化网格用于后续处理；它主要是重采样三角网格，不自动提供动画用全四边面边流。PolyReduce 按边界、特征/属性、轮廓约束保形，检查 UV 与材质属性。
- 重复结构 Copy to Points / packed primitives；只有消费端需要时解包。程序化变体测试最小/最大/非对称参数和多个种子，检查穿插与厚度。
- HOM `hou` 使用宿主或匹配版本的 `hython`，记录 cook 日志；不要在普通 pip Python 中假设可直接 import 完整 Houdini。
- `.hip/.hiplc/.hipnc` 与许可证相关；外发 HDA、缓存和输出格式先核对对应许可和接收端能力。

## ZBrush

- SubTools 按结构/材质拆分；低分辨率先确立体块、解剖、脸部比例和轮廓。
- DynaMesh 在探索阶段解决拉伸与融合，分辨率随物体尺度变化；明确何时冻结拓扑。ZRemesher 是可引导的重拓扑起点，不是眼口关节的最终边流验收。
- 使用 Polygroups、ZRemesher guides、Keep Groups/Creases 等**当前版本实际存在**的约束；先复制原高模，重拓扑后逐级细分并小步 Project，检查嘴角、手指间和薄片投射串面。
- 大形 Move/Clay 类笔刷，平面关系用 Trim/Polish 类笔刷；具体笔刷按风格选择，不在全身机械盖同一 alpha。皮肤按部位、张力和尺度分区；毛孔在近景真正读到时才投入。
- 硬表面用 ZModeler、Panel Loops 和布尔候选；Decimation Master 适合静态派生，不当作保留动画边流的工具。
- 保存 `.ztl/.zpr` 和层级；输出 OBJ/FBX、置换/法线时记录子级、UV、位深、midlevel 和实际导出设置。
- 自动化以当前版本官方支持为准；ZScript、录制宏和 UI 都有各自边界，不虚构 `bpy` 风格的 ZBrush 接口。

## Nomad Sculpt

- 按主要体块分对象，从低密度与清楚轮廓开始；voxel remesh 在副本上逐步测试密度，注意薄片消失与邻近表面粘连。
- 图层用于可控细节，平板内存约束下分层级/分对象处理；只在派生版本做减面。
- 交到桌面工具后核对尺度、vertex color、材质、UV 与可编辑层信息；通用交换文件通常不保留原应用全部雕刻历史。
- 把它定位为确有优势的雕刻入口，而不是默认承担最终动画重拓扑、工业精度或全部批量自动化。
