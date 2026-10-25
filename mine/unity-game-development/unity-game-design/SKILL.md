---
name: unity-game-design
description: 将 Unity 游戏简报转为可实现、可测试的玩法、数值、关卡、视听交互与技术设计，按领域加载子技能；用于 GDD/TDD 或策划细化。
---

# Unity 游戏设计

## 本环节的执行入口

执行本阶段时先读取 [unity-game-design-execute](unity-game-design-execute/SKILL.md)，由该 skill 组织下面的专项执行、集成与证据交付；不能只列出角色或计划就算完成。阶段执行后交独立上下文的 `game-reviewer` 使用 `unity-game-review`，profile 为 `design`。`changes_requested` 返回原执行 skill/owner 修复并新版本复审；`blocked` 或审查未运行时保持待验。只请求一个专项时直接运行相应子 skill，范围以用户任务为准。

先读取简报与已有决策，复用已验证规则和工程事实；用设计覆盖“玩家做什么、系统怎样响应、实现如何验证”，而非仅生成概念文案。

## 子技能路由

| 当前缺口 | 按需加载 |
|---|---|
| 循环、状态、胜负、反馈和异常规则 | [核心玩法](unity-game-core-loop/SKILL.md) |
| 成长、经济、战斗公式与调参 | [系统与平衡](unity-game-systems-balance/SKILL.md) |
| 灰盒关卡、遭遇节奏和叙事触发 | [关卡与叙事](unity-game-level-narrative/SKILL.md) |
| 美术语言、资产规格与视觉预算 | [美术方向](unity-game-art-direction/SKILL.md) |
| 用户路径、输入、界面与可访问性 | [UI/UX](unity-game-ui-ux/SKILL.md) |
| Unity 架构、版本依赖、存档与验证 | [技术设计](unity-game-technical-design/SKILL.md) |

## 编排与集成

先冻结核心循环和数据术语，再并行系统、关卡、美术、UI 与技术设计。任务包给出冻结输入、字段/资源接口、写入所有权和验收；各领域独立产物由主代理集成到 GDD/TDD 索引，冲突显式做决策，不让多个代理同时修改总文档。

优先调度对应 `game-designer`、`systems-designer`、`level-designer`、`narrative-designer`、`art-director`、`ui-ux-designer`、`unity-architect`，按宿主并发和实际需要启用。没有 subagent 时保留角色分工但如实串行执行。

完成时追踪体验支柱→规则/内容→工程接口→验收情境，核对局内/局外、暂停/重试、存档和输入的跨域一致性。预算必须能约束设计而不是仅列数字。独立审查记录未决项和设计风险。

完整生命周期中将 GDD、TDD、范围与里程碑提交用户，经 `direction` 明确确认后进入原型。只做单个系统设计时不强行补全全流程或开启原型。

存在 Unity manifest 时输出 `.unity-game/deliverables/`，主代理单写状态；独立任务默认 `docs/unity-game/` 或用户指定目录。仅引用实际存在的模板/工具，未运行验证保留 `not_run`。
