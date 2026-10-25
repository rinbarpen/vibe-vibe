---
name: unity-game-design-execute
description: 实际完成 Unity GDD/TDD、系统内容与视听交互契约，集成设计证据后进行独立设计审查和方向确认。
---

# Unity 策划与技术设计执行

## 执行边界与状态

这是执行 skill，不是角色说明：宿主实际读取本文件后，用可用工具完成下面的产物与验证。skill 名不是工具，文字“调用”不代表已执行；只有真正读入技能、委派成功或工具结果才记为执行。先识别用户请求的是完整阶段还是局部任务，只完成本次承诺，不自动跑整条生命周期。

复用既有工程版本、包、平台与已批准决策，不硬编码 Unity 版本或擅自升级。存在 `.unity-game/` 时，产物放 `.unity-game/deliverables/`，主代理单写共享 state/tasks/decisions；子代理仅写被分配的产物和证据。独立安装默认 `docs/unity-game/` 或用户指定目录；本文件含独立执行方法，不依赖其他技能或模板已安装。文档先写临时文件再原子替换。

任务单必须有任务 ID、输入修订、原执行 skill、owner、可写路径、依赖、验收与回传证据。真正具备 subagent 工具时才委派下表角色，按宿主并发上限分配不重叠文件；没有时由主代理按同一契约串行实现并如实记录。Scene、Prefab、序列化资源、项目配置及 `.meta` 单写，同工程 Editor 导入/测试/构建串行；资源与 `.meta` 成对保留。

## 输入与就绪

已确认或本次冻结的简报、范围预算、现有工程事实、目标平台/受众与已知风险。完整流程读取 discovery 结论；局部系统请求只冻结对应输入，不补跑立项。

## 专项方法与任务所有权

若阶段/整包同时安装，按当前缺口读取本执行技能父目录中的 `<下表 skill>/SKILL.md`，每个都是可选专项方法；只装本 skill 时直接执行下一节等价方法。不要求无关技能或不存在的相对链接。多角色任务拆成明确单一 owner 的子任务，不能共同抢写。

| 原执行 skill（安装时实际读取） | 建议 subagent | 本轮交付 |
|---|---|---|
| `unity-game-core-loop` | `game-designer` | core-loop.md；动作、状态、反馈、胜负与重试规则 |
| `unity-game-systems-balance` | `systems-designer` | systems-balance.md；单位、公式、边界与样本计算 |
| `unity-game-level-narrative` | `level-designer / narrative-designer` | level-narrative.md；灰盒路线、节奏、触发与验收 |
| `unity-game-art-direction` | `art-director` | art-direction.md；风格、资源规格与预算 |
| `unity-game-ui-ux` | `ui-ux-designer` | ui-ux.md；用户路径、输入与可访问性 |
| `unity-game-technical-design` | `unity-architect` | technical-design.md；组件、数据、存档、测试和版本依赖 |

未安装专项 skill 时，任务单原执行 skill 记 `unity-game-design-execute`，由对应角色按本文件方法执行；不能把未读取的专项记成已调用。

## 实际执行

1. 先实际写出核心循环和共享数据术语：状态、事件、数值单位、进入/退出、失败重试。对已有玩法只补所请求规则，不平行设计另一套系统。
2. 冻结最小接口后并行分派数值、关卡叙事、美术、UI 和技术设计，分配独立文档所有权。单人/无叙事项目不硬开叙事任务；多人项目才展开网络权威与协议边界。
3. 运行公式或状态表的小样推演：至少检查可达胜负、暂停重试、资源守恒、无效输入和进度恢复。输出实际输入与计算结果，不把策划文档当运行测试。
4. 主代理集成 GDD/TDD 索引，逐条追踪体验支柱→规则/内容→代码/资源接口→验收场景，解决数值单位、存档、UI、内容预算冲突；留下被否决方案及理由。

## 本阶段交付与推进

GDD/TDD 索引、相关领域设计、规则推演记录、资源清单与里程碑；审查规则可实现/可测试、跨领域接口一致、内容成本在范围内。未明确平台或预算的项保留待决状态。

完整 design 审查通过后，主代理展示固定修订的 GDD/TDD、范围和风险并取得用户 `direction` 明确确认，才进入 prototype。局部设计交付后停止，不强制新建方向门。

## 独立 reviewer 与返工闭环

1. 冻结本次提交/文件哈希、任务单及证据，生成 `design-execution-rN.md`：范围、任务→原执行 skill/owner、实际产物、命令/输入/字面结果/退出码、未运行项、风险、版本与回退。仅使用真实执行得到的 `passed` / `failed` / `not_run`，静态检查不替代运行。
2. 若已安装 `unity-game-review`，实际读取该技能，再由独立 `game-reviewer` 以 profile `design` 审查本次范围和固定修订。该 skill 不存在时，在新独立 reviewer 上下文执行同样的任务验收：检查输入→产物→证据、独立复现关键检查、给 finding ID/严重度/文件与复现/原执行 skill 和 owner/验收条件，并给 `passed`、`changes_requested` 或 `blocked`。新 reviewer 不承担实现；实现者自检不冒充独立审查。宿主没有独立上下文能力时输出待审查包、注明独立审查未执行，保持阶段不推进。
3. `changes_requested` 必须携 finding ID 回到任务单记录的**原执行 skill + 原 owner**修复；不要重派 reviewer 实现或换技能掩盖问题。生成新修订，重跑受影响验证，独立 reviewer 针对新修订复审；重复返工无新证据时记录原因和待决事项，避免无界重试。
4. `blocked` 或必需运行证据 `not_run` 时，交付已完成部分和具体恢复步骤，阶段原地保持。只有独立审查 `passed` 后由主代理写阶段完成/下一步建议；完整流程还须遵守本阶段用户门。局部任务只验收本次范围，不据此宣称整个阶段通过。
