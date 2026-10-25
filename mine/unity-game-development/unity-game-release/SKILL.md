---
name: unity-game-release
description: Unity 游戏发布候选构建、商店资料、上线核对与发布确认时使用。
---

# 发布：候选包到可追溯交付

## 本环节的执行入口

执行本阶段时先读取 [unity-game-release-execute](unity-game-release-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `release-ready`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

## 输入与发布边界
读取 Beta 证据、渠道/平台、候选提交、已知问题、资源权利清单及发布计划。内部构建、资料准备、外部上传、商店提交和正式开放是不同操作；逐项记录所需确认与凭据，不从准备工作推导外部操作许可。

## 按需加载 subskills
- 可复现构建、哈希与安装冒烟：读取 [unity-game-build-release](unity-game-build-release/SKILL.md)。
- 商店当期要求、素材、许可与隐私：读取 [unity-game-store-publishing](unity-game-store-publishing/SKILL.md)。
- Go / No-Go、发布步骤与回退演练：读取 [unity-game-release-readiness](unity-game-release-readiness/SKILL.md)。
资料与构建设计按独立文件并行，最终候选包必须统一版本与哈希。

## 工作与交付
1. 先产出候选清单与证据索引；`build-release-engineer` 管构建，`publishing-manager` 管渠道准备，`game-reviewer` 独立审查。
2. 将安装运行、商店合规材料、已知风险、值守及可行回退结果汇总为发布候选报告，不用打勾清单替代证据。
3. 在全流程第三个确认门取得用户对该候选及风险的发布确认；此前的方向、垂直切片确认不替代此次确认。实际外部上传/提交/开放及付费操作仍按明确操作范围确认。
4. 执行已确认步骤时记录时间、操作者、候选哈希、渠道返回和停止条件；将发布记录与观测窗口交给 `game-producer` 和运营责任人。

## 运行约定
- 先读取现有项目约定、`ProjectSettings/ProjectVersion.txt`、包锁定文件和已确认平台；使用项目版本对应官方文档，不预设 Editor 版本或设备。
- 如存在 Unity manifest，使用 `.unity-game/` 既有任务与产物；否则将产物写入用户指定位置，未指定时使用 `docs/unity-game/`。共享阶段、任务、决策由主代理单写；子代理仅交付其认领文件和证据。
- 独立文档、测试设计可按文件所有权并行；同一工程的 Unity Editor、Scene、Prefab、序列化资源和项目配置由单一写者串行处理，资源与 `.meta` 成对提交。文档采用临时文件写入后原子替换。
- 运行结论使用 `passed`、`failed`、`not_run` 并附证据。缺少 Editor、设备或凭据时记录未执行范围；静态检查不替代真实运行。已安装辅助工具时可先读 `.unity-game/scripts/unity_cli.py --help`，否则沿用项目工具及对应版本官方文档。
