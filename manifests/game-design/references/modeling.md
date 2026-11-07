# 建模、动画与资产接力：从规格到游戏内验收

本流程处理真实资产生产，不把参考图、提示词、导出脚本或文件名当成模型成品。`design-only` 交付资产规格、预算、管线和验收计划；进入 `implementation` 后才执行已约定的软件操作。角色是职责，可顺序承担；同一源场景只有一个写入 owner。

## 1. 先分资产种类，再加载工作包

- **纯 2D**：概念/像素或矢量稿 → 分层源文件 → Sprite/Tile/字体/图集 → 可选骨骼或逐帧动画 → 引擎导入。3D 拓扑、UV、PBR 和骨架任务可标 `not_applicable`，须写理由；2D 仍需像素密度、锚点、切片、碰撞、动作节拍和屏幕可读性验收。
- **静态 3D**：规格 → blockout → 网格/重拓扑 → UV/PBR → LOD/碰撞 → 导出/重导入 → 引擎接力。绑定/角色动画可不适用。
- **角色/可变形 3D**：增加骨架/rest pose、权重、极限姿态、动作剪辑、root motion/retarget/socket；导出模板只处理静态网格的能力，不能替代这些专项。
- **程序化/模块化**：另记生成器/种子/参数、模块接口/接缝/网格对齐、导出 revision 和再生成一致性。烘焙结果与生成源分别保留。
- **外部采购/扫描/生成资产**：先验许可、来源、可编辑性、依赖与预算，再进入同一导入/质量链。图像生成不是三维几何制作，第三方云生成/上传/付费是独立决策。

资产 ID 贯穿 REQ-ID、规格、源文件、交换文件、资源引用、测试与版本；开始前填写 [资产规格](../templates/asset-spec.md) 与 [资产登记表](../templates/asset-register.csv)。

## 2. 粗环节与细环节

| 环节 / owner | 输入与真实操作 | 产物 | 验收与返工入口 |
|---|---|---|---|
| 规格 / 设计+美术负责人 | 冻结用途、轮廓/参考及来源、游戏相机/视距、尺寸/轴/单位/pivot、风格和交互需求 | ASSET-ID 规格、参考/多视图、预算、必须/可选项 | 每个预算有单位、测量工具、阈值与对应游戏场景；方向冲突回设计决策 |
| blockout / 模型作者 | 在实际 DCC 创建粗模，以游戏相机验证比例、轮廓、支撑面、模块接缝/交互空间 | 可编辑粗模、实际视图、尺寸报告 | 与规格尺寸/轮廓一致，主要玩法空间可用；问题返回 blockout，不先投入高模细节 |
| 网格制作 / 模型作者 | 选低模直建或高模→重拓扑；处理退化/重复/内部隐藏面、意外孔洞、自交、边流、法线和切线 | 网格源文件、对象/材质列表、求值后统计 | 按导出/引擎后的三角形/顶点数核预算；有意开放面/非流形注明用途；变形区通过姿态检查 |
| UV / 表面作者 | 规划 UV、接缝、texel density、padding、重叠策略；需要烘焙时锁定高低模和 cage revision | UV 源、烘焙输入/输出、棋盘格视图 | 拉伸和接缝可接受；padding 按最终 mip/纹理尺寸验证；重叠是明确设计而非漏检 |
| PBR/贴图 / 表面作者 | 按目标 shader 准备颜色/法线/粗糙度/金属度等实际通道；核对法线方向、颜色空间/alpha、采样与压缩 | 可编辑材质源、纹理、通道映射表 | 在参考光照和游戏相机检查；DCC 专属节点有明确烘焙/重建路线；缺贴图回表面制作 |
| 绑定 / 绑定作者（可选） | 建骨架/命名/rest pose、权重/影响数、约束与控制；只在副本处理变换 | 源骨架/权重、极限姿态与蒙皮报告 | 无断裂/异常塌陷；骨骼数/影响数满足目标预算；已有骨架不盲目 apply transforms |
| 动画 / 动画作者（可选） | 动作拆分、起止/采样率/事件、循环、根运动、retarget 和 socket；测试混合/取消窗 | 动作源与导出 clip 清单、实际播放记录 | 动作节拍与玩法窗口一致；循环无非预期跳变、脚滑按阈值检查；命中/足步事件有游戏验证 |
| LOD/碰撞 / 模型+技术美术 | 按真实视距制作 LOD；制作简化碰撞代理，记录 convex/concave/通道和触发器 | LOD、碰撞源、命名与切换距离 | 检查轮廓跳变/材质连续性、穿透/卡人、物理成本；渲染高模不默认直接作为碰撞 |
| 导出 / 技术美术 | 冻结 exporter/选项；导出到新目录，带齐纹理、骨架、clip、依赖与真实哈希 | 可编辑源、交换文件、依赖闭包、导出 preset、日志 | 导出重导入核对 bounds/轴/单位/法线/UV/材质/骨架/动作；文件存在只算文件检查 |
| 引擎接力 / 引擎实现者 | 按已选 adapter/importer 导入，保持资源 ID；配置材质/LOD/碰撞/动画状态与 Prefab/Entity | 实际引擎资源、导入设置、场景引用、日志/截图 | 验引用与游戏相机观感；引擎缺 importer 时保持 `not_run`，不直接登记已导入 |
| 性能与游玩 / QA | 在目标设备/代表场景实际运行，采集帧时、内存、批次/DrawCall、纹理和动画成本 | 测量条件/样本、原始采样、输入回放、缺陷单 | 按项目 p95/峰值/时间窗阈值；未测设备记 `not_run`；超预算回对应网格/材质/LOD/动画 owner |
| 复核与入库 / reviewer+版本负责人 | 对冻结 revision/hash 审核技术、视觉与许可；核对源/导出/引擎三方版本 | 只读审查报告、资产登记/变更记录、版本提交 | `passed/changes_requested/blocked` 具名；缺独立 reviewer 记 self-review 或独立审查 `not_run`，不冒称独立通过 |

**不把“软件执行成功”“本地文件契约通过”“技术预算通过”“审美通过”“引擎导入通过”“目标设备通过”合成一个布尔值。** 资产登记表分别记录 DCC、交换、引擎、设备、技术与视觉结果。

## 3. 预算不是通用魔法数字

三角形/顶点、骨骼/单顶点影响数、材质槽、贴图尺寸/数量/显存、texel density、LOD 切换、碰撞复杂度、动画采样与音频格式，均从平台、画面距离、同屏数量和目标性能预算反推。没有已同意阈值时保留 `pending`，先做样本测量；不直接给所有角色套“固定面数”。规范需同时写**源数据预算**与**引擎导入/设备实测预算**，例如 modifier、顶点分裂与 shader 变体会改变最终成本。

## 4. Blender 的实际执行入口

安装包按 canonical 源显式分发 `.game-design/scripts/dcc_cli.py` 与 `.game-design/templates/Blender/export_model.py`，来源/哈希由安装器记录；源码维护仍在既有 Unity 工具处，不维护第二份实现。helper 的执行/文件协议不依赖 Unity Editor；选中的引擎接力另由 adapter 完成。

以下命令从**安装后项目根**运行，先把工具、源工程和脚本路径绑定为真实值，输出目录每次使用全新名称：

```bash
python3 .game-design/scripts/dcc_cli.py doctor \
  --blender "$BLENDER" --output-dir Evidence/blender-doctor-001

# 已有真实模型：导出模板不负责从零创作
python3 .game-design/scripts/dcc_cli.py run \
  --blender "$BLENDER" --project Art/source/robot.blend \
  --script .game-design/templates/Blender/export_model.py \
  --settings Art/presets/robot-export.json \
  --output-dir Evidence/robot-export-001

# 从零建模：提供按资产规格编写、实际创建几何体的本地 creation 脚本
python3 .game-design/scripts/dcc_cli.py run \
  --blender "$BLENDER" --new --script Art/scripts/create_robot.py \
  --output-dir Evidence/robot-create-001
```

helper 先核版本、计算源 SHA-256 并复制，冻结执行脚本，在新输出目录运行，最后核对源未变。产物含 `job.json`、`operation.py`、版本/执行 stdout/stderr、`result.json` 与脚本实际保存/导出的文件。源路径锁只协调此 helper，不代替团队的仓库锁和 Editor 单写者。

自定义脚本读取 `-- --job <job.json>`，字段为 `schema_version:1`、`create_new`、`source_copy`、`output_dir`、`settings`；完成后写 `asset-result.json`：`status`、实际 `audit.mesh_count/triangles`、`artifacts` 中真实 `path/role/sha256`。至少交可编辑 `.blend` 与 `.fbx/.glb/.gltf` 交换物。新建路径应清理默认启动物体并实际完成规格；默认立方体和未执行脚本不登记已完成模型。

模板静态网格导出不承诺保留绑定/动作/所有 shader；需要专项 exporter 脚本和验收。复制工程可能改变相对纹理/链接库路径，应在准备阶段打包依赖，或只对工作副本重新映射并检查。helper 会核 glTF 本地 buffers/images 依赖闭包，但它不是拓扑、完整格式或审美验证器。

canonical 导出模板的 `asset-result.json.audit` 已包含拓扑/材质/贴图、bounds 与单位等实际 DCC 信息；按项目预算复核，不另维护第二份 Blender 审计实现。安装包的 `templates/assets.json` 是登记清单模板，复制到 deliverables 后填写真实 `assets` 数组：每项 `id/source/source_sha256/exports[{path,sha256}]/license/engine_import{status,evidence}/review{status,evidence}`。在实际输出存在后执行：

```bash
python3 .game-design/scripts/asset_checks.py --project . \
  --manifest .game-design/deliverables/assets.json
```

`asset_checks.py` 只读核源/交换产物、真实哈希与必需证据；其通过不替代 DCC 重开、图像检查、引擎导入或设备测试。工具未就绪标 `not_run/blocked_dependency`，保留恢复命令；不要先生成空文件来满足路径检查。

## 5. 23 个引擎如何接模型

按 [引擎矩阵](engine-matrix.md) 读取**所选一项**，不是把每个模型导入 23 次。具体 importer/插件、交换格式、资源 ID、坐标/尺度、材质、骨骼、动画、LOD 与碰撞方案记入 TDD：

- Unity 保留 `.meta`/GUID，核对实际 FBX 或 glTF importer，不把 `.blend` 直导作为所有机器的无依赖路线。
- Unreal 保留 `.uasset/.umap` 与实际导入设置，轴/单位/骨架/碰撞按工程约定；不以文本批改二进制资源。
- Godot 保留源资源与 `.uid`、必要导入设置，缓存与源分离；节点/资源引用需要真实打开场景验证。
- Cocos/Web 运行时核对 asset bundle、GLB/glTF/解码器/纹理压缩与 URL 依赖；渲染库所缺碰撞/动画/玩法层显式补足。
- GameMaker/Construct/GDevelop/Ren'Py/RPG Maker 以其 2D/事件/图片资源链为主；确有 3D 插件/扩展时按实际能力接力，否则走离线渲染 Sprite/背景路线并保留渲染源。
- 其他代码框架与 Roblox/O3DE/Stride 使用对应 adapter 的加载/资源 ID/资产处理规则；没有内置 importer 的格式先验证导入工具和许可证。

## 6. 返工、恢复和批准边界

网格缺陷→模型作者，贴图/通道缺陷→表面作者，蒙皮/clip 缺陷→绑定/动画作者，格式/引用/碰撞缺陷→技术美术/引擎 owner。修复生成新 revision/hash，重跑原问题用例及相邻回归。改变风格支柱、采购费用、依赖/云服务或超出预算时走人工变更门；既定规格内的技术修复由 AI 自主闭环。

回退同时考虑源工程、交换文件、贴图/骨架、引擎 ID 和关联场景；不要只删 `.meta/.uid` 或单独回退模型。保持旧包、源快照及原始证据，后续编辑冲突先核对 owner，不覆盖新的有效工作。

## 资料与复用

- Blender [命令行参数](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)、[glTF 导入导出](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html)：使用时匹配实际安装版本，文档链接不代表软件已运行。
- 既有 canonical `unity-game-model-design/build/surface/rig-export/review` 的方法与 reviewer 分工通过 [工具与技能路由](tool-routing.md) 复用；非 Unity 项目仅复用适用方法，替换引擎接力和验收，不将 Unity API 直接照搬。
