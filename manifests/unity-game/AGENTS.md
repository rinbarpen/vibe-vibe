# Unity Game — Agent Instructions

## 工作入口与事实源

本项目采用 Unity 游戏全流程 manifest。主代理承担 `game-producer` 职责，统一分解、派发、集成和验收。流程细则位于 `.unity-game/references/lifecycle.md`，编排契约位于 `.unity-game/references/orchestration.md`，工程要求位于 `.unity-game/references/unity-engineering.md`。源模板内对应目录为 `references/`。

唯一共享事实源是 `.unity-game/state/` 的 `status.md`、`tasks.md`、`decisions.md`、`artifacts.md`。开始前恢复它们并核对实际文件；主代理单写，子代理只通过任务返回提交状态建议。初始化脚本仅在缺失时播种状态，升级模板不重置游戏进度。

## Subagent 调度

角色定义位于 `.claude/agents/*.md` 与 `.codex/agents/*.toml`，完整职责索引位于 `.unity-game/agents/subagent-roles.md`。

| 能力组 | 可调度角色 |
|---|---|
| 制作与定位 | `game-producer`, `market-researcher` |
| 玩法与内容 | `game-designer`, `systems-designer`, `level-designer`, `narrative-designer` |
| 视听 | `art-director`, `model-artist`, `technical-artist`, `animation-vfx-artist`, `audio-designer` |
| 工程与交互 | `unity-architect`, `gameplay-programmer`, `tools-programmer`, `ui-ux-designer` |
| 质量 | `qa-engineer`, `playtest-analyst`, `performance-engineer`, `game-reviewer` |
| 发行 | `build-release-engineer`, `publishing-manager` |

- 独立且有清晰接口的工作优先派给 subagent；按需启用角色，不为凑齐角色制造无价值任务。
- 派发使用 `.unity-game/templates/task-package.md`：任务 ID、冻结输入、依赖、写入路径、共享只读路径、验收、交付和资源预算齐全后启动。
- 并发数量服从宿主限制。宿主没有原生 subagent 时，主代理按角色契约串行执行，记录实际执行方式；不虚构代理、模型或独立审查。
- 一个路径/共享 Unity 对象只分配一个写入者。Scene、Prefab、Animator、材质、包清单、项目设置及对应 `.meta` 必须明确所有权。
- 同一 Unity 工程的 Editor 操作串行。并行代码任务不得同时启动导入、编辑场景、测试和构建；主代理统一排队。
- 子代理按 `.unity-game/templates/handoff.md` 返回实际变更、测试命令和输出路径、风险与下一步；主代理核对后更新共享状态。
- 实现者与最终 `game-reviewer` 使用不同上下文；审查发现由责任角色修复后复验，再进入下游。

## Skill 与 Subskill 调度

各阶段使用 `.unity-game/references/skills.md` 的映射：总入口为 `.agents/skills/unity-game-development/SKILL.md`，包含9个阶段入口、29个原有专项、模型链6个技能、实际游戏测试8个、9个执行skill，以及reviewer的5个技能，共67个技能。只加载当前任务相关技能，角色的双端定义已列出对应文件。派发任务同时指定 skill/subskills、冻结输入与产物，而非只指定专家角色。技能包缺失时说明依赖，由主代理通过 `vibe add skill unity-game-development` 安装。独立专项可单独安装并按实际路径读取；不以“调用 skill”虚构代理或工具执行。

## 执行、Reviewer 与推进契约

每个阶段由目录中对应的 `*-execute` skill 组织实际操作，任务包必须记录执行 skill、专项 skill、原 owner 和固定 revision；计划或角色派发本身不是阶段执行完成。`game-reviewer` 在不同上下文实际读取 `unity-game-review`，以当前阶段 ID 为 profile，按需执行设计/代码/资产/证据审查子技能。

- 审查状态 `pending / completed / not_run` 与运行验证 `passed / failed / not_run` 分开。已执行审查的 verdict 为 `passed / changes_requested / blocked`。
- 仅在必需交付和运行证据齐全、独立审查 passed 且报告绑定当前 revision/哈希、所需用户确认完成后推进。审查后输入变化重新审查。
- `changes_requested` 记录 finding ID，交回原执行 skill/owner 修复，新 revision 再独立复审；reviewer 只读审查，不直接修改实现再自批。
- 缺必需证据记 `blocked`；没有独立 reviewer 记 `review_status: not_run`，保持阶段待验。避免无新证据的无限返工，升级明确依赖或决策。

规范图位于 `.unity-game/references/workflow.svg`，对应实际技能映射生成，不代表已执行状态。

## 阶段与确认

按 `discovery → design → prototype → vertical-slice → production → alpha → beta → release-ready → live` 执行。各阶段产物与退出条件以生命周期文档为准。

必须获得用户明确确认的门：
1. `direction`：GDD、TDD、范围与里程碑已审查，进入原型前确认。
2. `vertical-slice`：代表性可玩内容、视听链路和构建证据审查后，进入批量制作前确认。
3. `release`：候选包、回归、商店素材、许可和回退方案审查后，外部发布前确认。

审批写入 decisions，含用户原话或消息引用、日期、产物路径和版本、接受的风险。方向、平台、商业模式或已批准基线实质变化时重新确认相应门。付费采购、使用凭据、上传或外部发布还须针对该操作确认，不以模板安装等同发布批准。

## 模型设计与外部软件

3D任务由model-artist使用unity-game-modeling及design/build/surface/rig-export等subskills操作源场景；technical-artist负责Unity导入，独立game-reviewer用model-review再汇总production。接入说明与可选MCP配置在 `.unity-game/references/external-tools.md`；安装模板不会安装软件或启动服务器。

先确认真实软件/版本、已连接实例与工具schema，或实际软件skill路径；CLI通过dcc_cli.py在新目录操作副本，--new必须使用实际建模脚本，默认export模板只导出静态网格。源文件/导出/纹理/预览/操作证据/哈希齐备后再审查。相对依赖、绑定和Unity导入按项目实测，缺软件或连接为not_run；MCP多客户端不允许同场景并发写入。

## 工程与证据纪律

- Unity 版本从 `ProjectSettings/ProjectVersion.txt` 读取，依赖从 `Packages/manifest.json` 核对；版本升级先单独提案。
- 不手写伪造 `.meta` GUID、不删除未知 `.meta`、不复制造成 GUID 冲突；移动资源和 `.meta` 成对进行并核对引用。
- 优先纯 C# 逻辑 EditMode 测试；PlayMode 验证场景、输入、生命周期和存档；目标平台构建另行验收。
- 测试与构建通过 `.unity-game/scripts/unity_cli.py` 留档，附源码版本、Editor/平台、原样命令、退出码、日志和实际产物。
- 验证结果仅用 `passed`、`failed`、`not_run`；零测试、缺日志/XML、缺 Editor、缺平台模块或超时都单独说明，不归入通过。
- 静态代码审查不替代试玩；Editor 内通过不等于目标设备性能通过；有构建文件不等于已上架。
- 隐私、资源许可、商店规则与平台技术要求使用对应平台的现行官方材料核对，保存来源与核对日期。

## 完成标准

实际交付物已归档、验收证据可复查、独立审查意见已处置、共享状态已更新、下一阶段依赖已明确。停在等待确认/环境依赖时，保留具体待办和复现命令，不填造通过记录。

## 实际游戏测试

用户要求测试/玩游戏时，qa-engineer先读取unity-game-testing及相关子技能，按references/game-testing.md核对真实构建、输入与隔离数据并执行。测试代码、Unity对象检查、状态注入、AI推演都不自动等于普通输入游玩；缺窗口/工具/构建即not_run。QA记录缺陷交原owner修复，新revision复测后由独立game-reviewer执行unity-game-test-review。game_test_cli.py仅校验已有会话/证据/哈希和review，不是控制器；人类体验、音频与设备性能分项验收。
