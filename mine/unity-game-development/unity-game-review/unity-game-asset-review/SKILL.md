---
name: unity-game-asset-review
description: 独立评审 Unity 视觉、音频、动画、VFX、UI 资产的实际文件、导入引用、游戏内效果与许可；用于切片、生产批次及发行资源验收。
---

# Unity 游戏资产审查

## 输入与执行

取得本阶段视听/UI 规格、资源清单、实际源资产与导入文件、.meta、许可/取得凭据、目标设备预算、固定工程/构建与场景内截图/视频或运行操作。

1. 逐样本核对资产真实存在、源文件/导出文件/工程引用对应，原作者与许可可追溯；记录占位和最终资产，不能把提示词、采购链接或规格文档当成已经制作的文件。
2. 检查匹配项目的导入设置：纹理尺寸/压缩/色彩与 Sprite 切片，模型比例/骨骼，动画循环/事件，材质 Shader/管线，音频采样/压缩/循环/音量。对平台相关质量以实际目标配置验证，不固定 Unity 或渲染管线版本。
3. 在实际场景核对可读性、UI 安全区/文本溢出、动画/VFX 预警与命中时机、音效反馈/混音/字幕，查看 missing reference/材质与 .meta 配对。截图适合静态检查，时序和音频必须有可播放/运行证据。
4. discovery/design 只评方向、可制作性、成本和许可风险；prototype 允许标记占位；vertical-slice 必查端到端导入/可复制生产链；production 按批查实际资产与集成；alpha/beta 查覆盖/性能/语言与可访问性；release-ready 查最终替换和渠道展示一致；live 查增量包、兼容和旧资源引用。
5. 核对真实设备资源占用、加载及回收对预算影响；所需运行/播放证据缺失为 blocked，避免根据文件尺寸或单张图推断设备性能。审查者保持源资产、场景及配置只读。

## 修复交接

源资产/导入交 `technical-artist` + `unity-game-asset-production`，方向交 `art-director` + `unity-game-art-direction`，动画/VFX 交 `animation-vfx-artist` + `unity-game-animation-vfx`，音频交 `audio-designer` + `unity-game-audio`，UI 交 `ui-ux-designer` + `unity-game-ui-ux`，许可/商店材料交 `publishing-manager` + `unity-game-store-publishing`。每项列实际 owner、资产路径/对象、复现平台和复验样本。

## 审查边界与交付

使用 `game-reviewer` 的独立代理上下文，不评审自己实现的内容；只写分配的审查报告，不修改实现、资产或共享阶段状态。有 manifest 时先读 `.unity-game/state/`，输出到 producer 分配的 `.unity-game/deliverables/` 独占路径；独立安装使用指定目录，默认 `docs/unity-game/`。不依赖父技能文件；沿用实际项目版本、平台与工具。

接收冻结需求/验收、实际产物、revision/差异与源码及产物 SHA-256、实现 owner、原始证据。直接检查源材料；记录每项具体检查、命令/输入/退出码或人工操作、实际输出和证据路径/哈希。源码有未提交差异时绑定逐文件哈希。审查者缺席由主代理记录 `review_status: not_run`，不以实现者自查批准；审查者存在但必需材料缺失记 `blocked`。

报告写明 stage、reviewer/实现 owner 与独立性、reviewed_revision、source_hashes、artifact_hashes、requirements_version、checks、issues、report_path、previous_report、approved_revision。`verdict` 为 `passed` / `changes_requested` / `blocked`：完整证据且无阻断项才通过；确定缺陷需修复为 changes_requested；缺必需证据导致判断无依据为 blocked。仅 passed 填 approved_revision，批准仅覆盖该 revision/哈希。测试状态另记 `passed` / `failed` / `not_run`，不充当审查 verdict；必需运行缺失导致审查 blocked，设计任务未要求的运行可注明不适用及理由。

问题按 critical/major（阻断）、minor/suggestion（非阻断）分级并写清理由，附需求、位置/时间点、预期/实际、复现、原始证据、**确切 owner + 执行 skill + 复验条件**。owner 未定退回 producer 分配。原 owner 调用执行 skill 修复→新 revision/证据→独立复审；保留历史问题及报告链接，不修改原实现来“完成审查”。报告保存后重读确认并回传 SHA-256。direction、vertical-slice、release 用户确认门与 review passed 分离，评审不代替用户批准。

## 3D模型与外部软件证据

模型任务核查源场景/导出文件真哈希、单位/轴/pivot、拓扑/法线/UV/PBR、贴图依赖、LOD/碰撞和可选骨架权重；读取真实DCC/插件版本、MCP schema与实际调用或CLI日志、保存重开/导出重导入和Unity导入记录。默认立方体、空FBX或模板不是已设计模型，DCC成功不替代Unity验收。按实际装有unity-game-model-review时加载专项方法；缺少必需实物/运行证据保持blocked，问题退回model-artist/原skill或technical-artist的导入任务。
