---
name: unity-game-discovery
description: 为 Unity 游戏完成立项探索、受众定位和范围论证；用于新游戏点子、立项简报、竞品研究或预算风险评估，按需调用子技能。
---

# Unity 游戏立项探索

## 本环节的执行入口

执行本阶段时先读取 [unity-game-discovery-execute](unity-game-discovery-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `discovery`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

将想法变为可被策划和技术团队使用的立项基线，而非直接开始实现。先检查已有简报、已批准决策和实际 Unity 项目，区分已知事实、用户选择和待验证假设。

## 按问题逐步加载

- 想法模糊、需要明确体验和目标：加载 [立项简报](unity-game-brief/SKILL.md)。
- 不清楚为谁做、与哪些游戏比较：加载 [受众与竞品](unity-game-market-research/SKILL.md)。
- 需要确定做多大、多少资源、主要风险：加载 [范围与风险](unity-game-scope-risk/SKILL.md)。

只读当前任务需要的子技能。简报先给出受众与体验假设；研究与范围估算可在输入冻结后并行，再由 producer 处理冲突。已有可靠定位时无需重做竞品研究；单项任务不附带整条生命周期。

## 汇总与交接

输入至少包括游戏想法、现有项目事实、平台意向、时间/团队/资金限制；未知项以带验证动作的假设记录，不编造确定值。产出立项摘要，链接简报、研究和范围文件，列出明确不做项、最高风险、首个可证伪实验及其退出条件。

完整生命周期下交给 `game-designer` 和 `unity-architect` 形成 GDD/TDD，再经 `direction` 用户确认门进入原型；立项完成本身不代表已批准原型。研究可派 `market-researcher`，估算可由 producer 与架构角色独立复核；报告证据与分歧，而非用角色数量代替论证。

存在 Unity manifest 时写 `.unity-game/deliverables/`，共享状态由主代理更新；独立使用时写用户指定目录，默认 `docs/unity-game/`。不假定模板、Editor 或联网能力已经存在。
