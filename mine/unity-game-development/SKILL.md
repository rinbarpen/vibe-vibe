---
name: unity-game-development
description: 编排 Unity 2D/3D 游戏从立项、策划、原型到制作、质量验证、发布运营的分层技能；用于完整游戏工作流或跨阶段任务，单项工作转给对应阶段与专项 subskill。
---

# Unity 游戏开发：技能总入口

把工作拆为可调用的能力，而非只有“某某专家”角色。**skill 定义怎么做，subagent 定义谁来做**：主代理选择当前任务需要的 skill，将输入、技能路径与验收要求一起交给合适的角色。技能本身不创建代理，也不证明宿主已执行独立审查。

## 先恢复任务环境

1. 确认当前是新项目、已有工程增量，还是仅需一个专项产物；复用用户已确认的目标和已有结果。
2. 有 unity-game manifest 时读取 `.unity-game/state/`，按其阶段与三个确认门工作，实际文档写入分配的 `.unity-game/deliverables/` 路径；共享状态仍由主代理单写。
3. 独立使用本技能时沿用项目的现有规划和工具，输出放在用户指定位置，未指定时用 `docs/unity-game/`。无需为一个专项任务重建整个流水线或额外安装 manifest。
4. 跨阶段协作先读 [执行与交接契约](references/working-contract.md)；阶段、专项路径和角色映射可查 [技能目录](references/skill-map.json)。

## 按请求渐进加载

只读取当前阶段的入口，再选与任务有关的子技能；不把整个技能树一次性塞给所有代理。

| 环节 | 阶段执行 skill | 工作方法与专项组 | 独立 reviewer |
|---|---|---|---|
| 立项 `discovery` | [unity-game-discovery-execute](unity-game-discovery/unity-game-discovery-execute/SKILL.md) | [unity-game-discovery](unity-game-discovery/SKILL.md) | `unity-game-review` / `discovery` |
| 完整策划 `design` | [unity-game-design-execute](unity-game-design/unity-game-design-execute/SKILL.md) | [unity-game-design](unity-game-design/SKILL.md) | `unity-game-review` / `design` |
| 可玩原型 `prototype` | [unity-game-prototype-execute](unity-game-prototype/unity-game-prototype-execute/SKILL.md) | [unity-game-prototype](unity-game-prototype/SKILL.md) | `unity-game-review` / `prototype` |
| 垂直切片 `vertical-slice` | [unity-game-vertical-slice-execute](unity-game-vertical-slice/unity-game-vertical-slice-execute/SKILL.md) | [unity-game-vertical-slice](unity-game-vertical-slice/SKILL.md) | `unity-game-review` / `vertical-slice` |
| 正式制作 `production` | [unity-game-production-execute](unity-game-production/unity-game-production-execute/SKILL.md) | [unity-game-production](unity-game-production/SKILL.md) | `unity-game-review` / `production` |
| Alpha 验证 `alpha` | [unity-game-alpha-execute](unity-game-alpha/unity-game-alpha-execute/SKILL.md) | [unity-game-alpha](unity-game-alpha/SKILL.md) | `unity-game-review` / `alpha` |
| Beta 优化 `beta` | [unity-game-beta-execute](unity-game-beta/unity-game-beta-execute/SKILL.md) | [unity-game-beta](unity-game-beta/SKILL.md) | `unity-game-review` / `beta` |
| 发布准备 `release-ready` | [unity-game-release-execute](unity-game-release/unity-game-release-execute/SKILL.md) | [unity-game-release](unity-game-release/SKILL.md) | `unity-game-review` / `release-ready` |
| 发布运营 `live` | [unity-game-liveops-execute](unity-game-liveops/unity-game-liveops-execute/SKILL.md) | [unity-game-liveops](unity-game-liveops/SKILL.md) | `unity-game-review` / `live` |

## 模型设计与外部软件

3D角色、道具或环境任务使用 [unity-game-modeling](unity-game-production/unity-game-modeling/SKILL.md)，下分模型设计、实际DCC建模、UV/PBR、可选绑定导出与独立模型审查。model-artist负责源模型，technical-artist负责Unity导入。可走真实已连接MCP、已读取的软件skill或已安装CLI/API；仅GUI操作时使用实际可用的GUI技能。软件、连接、工具schema、保存重开和实物路径都需核对，不预设已接入外部应用。

manifest分发 `.unity-game/references/external-tools.md`、可选MCP配置示例及 `.unity-game/scripts/dcc_cli.py`；缺这些文件时按模型skill的独立方法执行自己的任务，不假定helper存在。规格、模板、默认立方体不是模型成品，DCC和Unity验收分开。

## 独立审查 Skill

[unity-game-review](unity-game-review/SKILL.md) 由与实现者不同的实际上下文执行，按阶段选择设计、代码、资源或证据审查 subskill。它读取原始产物和日志，输出绑定输入版本/哈希的 `passed`、`changes_requested` 或 `blocked`；独立审查缺席记 `review_status: not_run`。测试的 `passed/failed/not_run` 不能代替 reviewer 结论。

**闭环**：阶段执行 skill → 实际产物/证据 → 独立 reviewer skill → 通过后检查用户确认门 → 下一阶段；要求修改则回到原执行 skill/owner，缺证据则停留当前阶段。审查后输入改变必须重新审查。

## 组合与交付

- 从实际依赖派发：例如玩法规则和 UI 规格可并行；规则冻结后才让实现依赖它，集成验证后再放行下游。
- 每个任务包附上要读取的 `SKILL.md` 路径、冻结输入、唯一可写范围、产物与验收。角色参考目录中的映射选择，超出范围的工作重新分配。
- 资源生产必须交付实际源资产/取得记录、导入文件和验收，而非只完成规格；测试、设备性能和发布状态必须有实际证据。
- 全流程使用时在方向、切片和发布处请求用户确认；单独调用某个子技能只完成该专项任务，付费、凭据及实际外部发布仍逐项确认。
- 没有 Editor、设备或制作工具时，把可交付的设计/静态检查和待运行项分开；最终交接包含真实路径、验证结果与未满足的依赖。

整包安装保留层级，父入口通过相对路径读取子技能。宿主只注册顶层技能时，直接读取所需子 `SKILL.md`；也可通过 `vibe add skill unity-game-performance TARGET` 单独安装专项技能，或安装阶段入口及其全部子技能。

## 实际玩游戏并测试

[unity-game-testing](unity-game-alpha/unity-game-testing/SKILL.md) 提供从启动、实际输入到复现/复测的测试链，适用于原型、切片、制作、Alpha/Beta、候选包和热修复。可通过已连接MCP、实际项目harness、已安装桌面/浏览器skill或设备工具执行，先核对真实能力，不虚构输入操作。
