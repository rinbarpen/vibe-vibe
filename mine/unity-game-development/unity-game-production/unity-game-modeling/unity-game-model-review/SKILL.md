---
name: unity-game-model-review
description: 独立只读审查 Unity 3D 模型的源文件、网格、UV/PBR 贴图、可选绑定、导出与 Unity 导入证据；对指定模型 revision 给出通过、返工或证据阻塞结论。
---

# 独立模型审查

## 输入与只读边界

由与实现者不同的 `game-reviewer` 上下文执行，只写分配的报告，模型源、纹理、场景、Prefab、配置和共享状态保持只读。接收模型需求/冻结规格、实际源/导出/贴图/Unity 资源及 `.meta`、DCC/Editor 版本、制作 owner、revision/差异、逐文件 SHA-256、许可和原始操作/运行证据。完整生产审查还需阶段与验收范围；单个规格审查不强求未请求的制作证据。

有 manifest 时读相关 `.unity-game/state/` 并在 producer 分配的 `.unity-game/deliverables/` 独占路径写报告；独立安装用指定目录，默认 `docs/unity-game/`，无需父技能。读取模型时使用只读/隔离副本，不触发原场景保存或更新 importer。

## 实际检查

1. 验证源文件/导出/纹理真实存在且可读取，ID、依赖、版本、哈希、许可与引用一致。截图、提示词、生成脚本或“工具返回成功”不能代替真实资产；导出重开与 Unity 导入证据分别核对。
2. 对照参考视图与游戏相机检查轮廓、比例、尺寸/轴/pivot、模块接口/socket和碰撞；统计真实网格三角形/顶点、材质槽、LOD 与预算，定位退化/非预期孔洞、法线/切线问题及轮廓跳变。
3. 检查 UV 拉伸/接缝/合理 padding、重叠是否有意、烘焙对应 revision，实际贴图的尺寸/通道/色彩空间与目标 Shader 映射；DCC 专属节点不自动视作已在 Unity 复现。
4. 静态道具允许 rig 不适用并记录理由；有绑定则检查层级/rest pose、权重/影响数、实际极限姿态和动作，retarget/root motion/socket 必须有相应证据。
5. 检查实际 exporter/importer 版本与扩展支持；glTF/GLB 缺 importer 不能登记 Unity 已导入。核对 Editor 日志、导入设置、资产与 `.meta` 配对、Prefab 引用和游戏场景观感；真实设备成本不由文件体积或截图推断。

## 判定、返工与交付

记录 stage（默认 production）、reviewer/实现 owner及独立性、reviewed_revision、requirements_version、source_hashes、artifact_hashes、checks、issues、previous_report、report_path、approved_revision。对每项列实际命令/工具调用或人工步骤、输入/退出码、结果及原始证据路径/哈希。

`verdict` 仅为 `passed` / `changes_requested` / `blocked`：证据完整且无阻断缺陷才通过并填 approved_revision；确定缺陷返工；必需源/导入/动作证据缺失为 blocked。运行检查另记 `passed` / `failed` / `not_run`，不充当 review verdict。若未安排独立 reviewer，由 producer 记录 `review_status: not_run`，实现者自查不替代独立通过。

每条问题记录 critical/major（阻断）或 minor/suggestion、需求与对象/位置、预期/实际、复现和确切 owner + 执行 skill + 复验条件：规格交 `model-artist` + `unity-game-model-design`；网格交 `model-artist` + `unity-game-model-build`；UV/贴图交 `model-artist` + `unity-game-model-surface`；骨架/导出交 `model-artist`（协作 `animation-vfx-artist`）+ `unity-game-model-rig-export`；Unity 导入交 `technical-artist` + `unity-game-model-rig-export`。owner 未定退回 producer 分配。

原 owner 修复→新 revision/哈希与证据→独立复审，保留旧问题和报告链接。保存报告后重读并回传 SHA-256；批准仅覆盖该 revision/哈希。已安装总审查技能时将报告交 `unity-game-review` production profile 汇总；本报告不自行批准整个制作阶段或替代用户确认门。
