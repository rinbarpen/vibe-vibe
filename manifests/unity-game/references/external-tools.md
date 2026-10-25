# 模型设计与外部软件接入

此 manifest 支持以 **MCP、已有软件 skill、CLI/API、GUI** 操作实际 DCC 软件。安装本模板只分发说明、配置示例和脚本；不会安装软件、下载插件、启动服务或改写宿主配置。Blender 是已提供 CLI 适配器的实现，现有 Maya/3ds Max 工作流通过实际可用接口或软件 skill 接入。

## 3D 任务链与责任

`unity-game-modeling` 包含模型设计、实际建模、UV/PBR 表面、可选绑定/导出、独立模型审查五个子技能。`model-artist` 写源模型，`technical-artist` 负责 Unity 导入，`art-director` 验视觉，独立 `game-reviewer` 用 model-review 再汇总 production profile。

先冻结资产 ID、参考视图/来源、轮廓、尺度/轴/pivot、相机距离、LOD/碰撞及预算。交付可编辑源工程、交换模型、纹理/材质、软件/插件版本、操作日志、保存重开/真实预览及 SHA-256。每一项分别验收：DCC 保存、导出重导入、Unity 导入/场景、目标设备；文本规格不等于模型成品。

## 通道一：接已有 MCP

[固定版本配置示例](external-tools/mcp.example.json) 采用 `mcpServers` JSON 形式。它是待选择的配置片段，不是连接成功记录；只合并需要的条目，保留原有服务器和设置。不同宿主配置结构不同，按宿主/维护者文档转换，不把 JSON 直接当作所有客户端的原生格式。

核验基线日期 **2026-10-25**：
- Blender 示例固定 `mcp-for-blender==2.2.4`，该版本已在 [PyPI 官方元数据](https://pypi.org/pypi/mcp-for-blender/2.2.4/json) 发布；[维护者仓库](https://github.com/ahujasid/mcp-for-blender) 说明需要匹配的 Blender addon。架构是 MCP stdio 服务连接 addon socket，不是凭空填写 Blender HTTP 端点。
- Unity 示例固定 [CoplayDev/unity-mcp v10.3.0](https://github.com/CoplayDev/unity-mcp/tree/v10.3.0)。先核对项目版本与 [UPM 包元数据](https://github.com/CoplayDev/unity-mcp/blob/v10.3.0/MCPForUnity/package.json)，需要时由用户确认安装 `https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#v10.3.0`；服务命令依据 [该版本服务说明](https://github.com/CoplayDev/unity-mcp/blob/v10.3.0/Server/README.md)。示例不是项目必须使用的 Unity 版本或插件。
- 上游版本是可复查示例，启用时再核对兼容、来源及具体权限；示例遥测环境变量按各自上游配置，不代表所有第三方功能都不联网。生成模型 API、素材库、上传和付费操作独立确认。

首次操作：确认实际服务器在线 → 发现工具/资源及参数 schema → 确认当前应用实例/文件/未保存改动 → 在副本上做最小读写小样 → 保存重开并核对对象 → 扩大已批准范围。记录真实工具名、输入/输出和场景版本；不预编造 `create_model` 等不存在的方法。MCP 具备多客户端能力也不改变同场景和 Unity Editor 的单写者约束。

当前仓库根 `mcp.json` 缺失，`vibe mcp add blender` 尚不是这份可选示例的安装接口。启用前按实际宿主合并选定条目；不要为了启用此模板覆盖项目现有 MCP 配置。

## 通道二：调用已安装的软件 Skill

记录 skill 的真实路径，读取其 `SKILL.md` 并核对软件版本、入口、插件及可操作对象。由该 skill 执行已经批准的建模/导出任务，返回源文件、工具证据和审计报告。宿主只注册顶层 skill 时直接读取所需子文件，不能把技能名称当成一个已存在的工具调用。

可接入本地 Blender/Maya/3ds Max、材质或动画软件的实际 skill；没有对应 skill 或软件时先登记缺口，不自动下载未知包。只有确实需要 GUI 且 CLI/API/MCP 覆盖不了当前操作时，按已安装的 computer-use skill 控制可见窗口，避免与用户争用未保存场景。

## 通道三：Blender CLI / Python

安装后运行：
```bash
python3 .unity-game/scripts/dcc_cli.py doctor --blender /path/to/blender --output-dir Evidence/blender-doctor-001
python3 .unity-game/scripts/dcc_cli.py run --blender /path/to/blender --project Art/source.blend --script .unity-game/templates/Blender/export_model.py --output-dir Evidence/model-export-001
# 新模型必须明确提供按模型简报编写的实际建模脚本
python3 .unity-game/scripts/dcc_cli.py run --blender /path/to/blender --new --script Art/create_model.py --output-dir Evidence/model-create-001
```

显式路径优先，其次 `BLENDER_BINARY`，最后 PATH。已有工程按源文件哈希加锁并复制，在全新输出目录运行冻结后的脚本，记录版本、job、命令/退出码、stdout/stderr、保存工程和导出文件的真实哈希。默认模板只导出静态网格，拒绝用 `--new` 的启动立方体冒充完成建模；新模型脚本根据 job 创建实际模型、保存工程、导出并写真实审计。协议见安装后 `.unity-game/templates/Blender/README.md`（源目录为 `templates/Blender/README.md`）。

只接受已审查的本地脚本。它仍是任意 Python，helper 的复制/哈希检查不是进程隔离或文件系统权限控制；保留原工程备份，在任务允许的目录执行。相对纹理/外部链接库会受副本位置影响，应先打包或在工作副本重映射并验证；原工程保持原样。CLI `passed` 仅表示本次输出契约成立，不表示模型符合美术要求、源文件已重开或 Unity 验收通过。

CLI接受glTF时会核对buffers/images的本地URI依赖闭包，检查文件与哈希并拒绝缺失、外部URL或越出本次交付目录的依赖；data URI嵌入数据单独验证。自包含GLB/FBX也仍需真实导出重开与Unity导入，不把格式/哈希检查当美术或运行验收。

## 导出、Unity 接力与回退

- 保留可编辑源工程；生产交换格式按工程导入器选择。Unity [模型格式说明](https://docs.unity3d.com/6000.0/Documentation/Manual/3D-formats.html) 推荐模型交换路线；`.blend` 直导依赖 DCC 软件。glTF/GLB 要核对 [实际 glTFast 等 importer](https://docs.unity3d.com/Packages/com.unity.cloud.gltfast@6.0/manual/index.html)，不当成所有项目的默认原生导入器。
- 轴向、单位、法线、UV、材质/色彩空间、绑定与动画要在导出重开和 Unity 真实导入后比较；FBX 模板选项不是各项目通用的正确配置。脚本依据 [Blender CLI](https://docs.blender.org/manual/en/4.5/advanced/command_line/arguments.html)、[保存 API](https://docs.blender.org/api/4.5/bpy.ops.wm.html) 与 [FBX API](https://docs.blender.org/api/5.0/bpy.ops.export_scene.html)，使用时匹配实际软件版本。
- technical-artist 在唯一 Editor 作业中导入，生成/配对 `.meta`、检查 GUID 和引用；不可因为 DCC 导出成功就覆盖发布用模型。
- 输出使用新目录，失败保留日志和局部资产。回退通过恢复事先保存的源版本及成对资源进行，不能只删 `.meta` 或覆盖用户更新的原工程。原文件哈希改变时立即停止并交主代理核对备份。

本环境未安装 Blender / Unity，也未启用这些 MCP 服务；示例配置、伪程序测试和脚本语法检查不等同真实软件连接、建模、渲染或导入。
