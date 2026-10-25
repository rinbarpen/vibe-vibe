---
name: unity-game-liveops
description: Unity 游戏上线后反馈分诊、热修复、指标复盘与版本迭代时使用。
---

# 运营：反馈变为可验证迭代

## 本环节的执行入口

执行本阶段时先读取 [unity-game-liveops-execute](unity-game-liveops-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `live`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

## 输入与优先级
读取实际发布版本、问题渠道、监控/遥测字典、隐私约定及当前支持承诺。先分离服务事故、可复现缺陷、体验反馈和新功能建议；健康风险不被总体转化指标掩盖。

## 按需加载 subskills
- 去重、复现、事故与玩法假设：读取 [unity-game-feedback-triage](unity-game-feedback-triage/SKILL.md)。
- 紧急补丁、数据兼容与回退边界：读取 [unity-game-hotfix](unity-game-hotfix/SKILL.md)。
- 指标定义、复盘与下一轮实验：读取 [unity-game-operations-review](unity-game-operations-review/SKILL.md)。
先加载实际需求对应子技能，避免每次反馈都启动完整运营流程。

## 工作与交付
1. 由 `qa-engineer` 与 `playtest-analyst` 分诊证据，`gameplay-programmer` 处理已定位问题，`publishing-manager` 准备用户沟通；共同状态仅由主代理更新。
2. 对事故先保存证据并限制影响；对玩法假设定义样本、观测周期和验证指标，明确继续/终止条件。
3. 输出问题队列、事故/热修复记录、运营复盘与下轮依赖任务；按实际发布标识关联数据和补丁。
4. 将优先级与资源决策交给 `game-producer`。外部发版、用户通知和付费服务操作分别在已确认范围内执行，不自行增加全流程阶段门。

## 运行约定
- 先读取现有项目约定、`ProjectSettings/ProjectVersion.txt`、包锁定文件和已确认平台；使用项目版本对应官方文档，不预设 Editor 版本或设备。
- 如存在 Unity manifest，使用 `.unity-game/` 既有任务与产物；否则将产物写入用户指定位置，未指定时使用 `docs/unity-game/`。共享阶段、任务、决策由主代理单写；子代理仅交付其认领文件和证据。
- 独立文档、测试设计可按文件所有权并行；同一工程的 Unity Editor、Scene、Prefab、序列化资源和项目配置由单一写者串行处理，资源与 `.meta` 成对提交。文档采用临时文件写入后原子替换。
- 运行结论使用 `passed`、`failed`、`not_run` 并附证据。缺少 Editor、设备或凭据时记录未执行范围；静态检查不替代真实运行。已安装辅助工具时可先读 `.unity-game/scripts/unity_cli.py --help`，否则沿用项目工具及对应版本官方文档。
