# 阶段 Skill 与 Subskill 路由

技能包位于源仓库 `mine/unity-game-development/`，由 manifest 的 `skills.txt` 自动安装到 `.agents/skills/unity-game-development/`。总入口、9个阶段入口、29个原有专项、模型链6个、实际游戏测试8个、9个执行skill，以及reviewer的5个技能，共67个真实 `SKILL.md`，名称均可被 `vibe list skills` 递归发现。

## 选择方式

- 主代理从当前阶段或用户明确的专项请求选择最小入口，再把技能文件路径加入任务包。
- 阶段 skill 路由子技能；角色负责执行，二者分开。输入已冻结且路径不重叠时，几个子技能交给不同 subagent 并行完成。
- 父入口只需读相关子 skill。完整目录与角色映射在 `.agents/skills/unity-game-development/references/skill-map.json`；源仓库同文件位于技能包的 `references/`。
- 下表路径相对完整技能包根。子技能也可单独安装；单独安装后位于 `.agents/skills/技能名/SKILL.md`，无需父包支持即可完成专项。宿主不递归注册子技能时，由代理直接读取对应文件。

## 九阶段路由

| 阶段 | 执行 skill | 独立审查 | 专项方法 |
|---|---|---|---|
| `discovery` | `unity-game-discovery-execute` | `unity-game-review` / `discovery` | `unity-game-brief`、`unity-game-market-research`、`unity-game-scope-risk` |
| `design` | `unity-game-design-execute` | `unity-game-review` / `design` | `unity-game-core-loop`、`unity-game-systems-balance`、`unity-game-level-narrative`、`unity-game-art-direction`、`unity-game-ui-ux`、`unity-game-technical-design` |
| `prototype` | `unity-game-prototype-execute` | `unity-game-review` / `prototype` | `unity-game-project-setup`、`unity-game-playable-prototype`、`unity-game-prototype-playtest` |
| `vertical-slice` | `unity-game-vertical-slice-execute` | `unity-game-review` / `vertical-slice` | `unity-game-slice-integration`、`unity-game-slice-review` |
| `production` | `unity-game-production-execute` | `unity-game-review` / `production` | `unity-game-feature-delivery`、`unity-game-asset-production`、`unity-game-animation-vfx`、`unity-game-audio`、`unity-game-modeling`（含5子技能） |
| `alpha` | `unity-game-alpha-execute` | `unity-game-review` / `alpha` | `unity-game-test-automation`、`unity-game-flow-regression`、`unity-game-testing`（含7子技能） |
| `beta` | `unity-game-beta-execute` | `unity-game-review` / `beta` | `unity-game-balance-playtest`、`unity-game-performance`、`unity-game-compatibility` |
| `release-ready` | `unity-game-release-execute` | `unity-game-review` / `release-ready` | `unity-game-build-release`、`unity-game-store-publishing`、`unity-game-release-readiness` |
| `live` | `unity-game-liveops-execute` | `unity-game-review` / `live` | `unity-game-feedback-triage`、`unity-game-hotfix`、`unity-game-operations-review` |

## 模型设计与外部软件 Skill链

`unity-game-modeling` 下分 `unity-game-model-design` → `unity-game-model-build` → `unity-game-model-surface` → `unity-game-model-rig-export` → `unity-game-model-review`。MCP/实际软件skill/CLI/API选择由模型skill按真实能力完成，不把配置样例当已连接。模型源owner为model-artist，Unity接力为technical-artist。

```bash
vibe add skill unity-game-modeling ./my-game
vibe add skill unity-game-model-build ./my-game
```

[外部软件接入与MCP示例](external-tools.md) 包含Blender与Unity的已核验固定版本示例、可执行Blender helper，以及软件缺失/源工程副本/依赖和验收边界。整包安装会递归带上模型链，单项skill也独立可用。

## 实际游戏测试 Skill链

`unity-game-testing`包含计划→实际游玩→按需探索/视觉→最短复现→修复复验→独立测试审查，7个子技能均独立安装。跨阶段调用不要求先到Alpha。QA执行，game-reviewer只读独立审查；原owner修复。详见 [游戏测试与证据协议](game-testing.md)。

```bash
vibe add skill unity-game-testing ./my-game
vibe add skill unity-game-fix-verification ./my-game
```

## Reviewer 与闭环

每个阶段执行都进入独立审查，而非仅在发布前审查。`unity-game-review` 根据9阶段标准，按需加载设计审查 `unity-game-design-review`、代码审查 `unity-game-code-review`、资产审查 `unity-game-asset-review`、证据审查 `unity-game-evidence-review`。

审查通过只批准固定 revision/产物哈希；`changes_requested` 返回原执行skill/owner，修复后新版本复审；缺必需证据为 `blocked`，独立审查缺席为 `review_status: not_run`，均不推进。三个用户确认门独立保留。阶段中的 slice-review/release-readiness 可作为专项检查或评审准备，不代替最终独立上下文结论。

[查看 workflow SVG](workflow.svg)。它由技能目录生成，表达执行→审查→返工/等待/推进规范，不是实际运行状态。

```bash
# 源仓库生成与检查图
python3 manifests/unity-game/scripts/render_workflow.py
python3 manifests/unity-game/scripts/render_workflow.py --check
# 安装后从项目根检查/再生成
python3 .unity-game/scripts/render_workflow.py --check
python3 .unity-game/scripts/render_workflow.py
```

## 调用与安装

```bash
# 整包（包括全部阶段与子技能），manifest 安装自动执行此项
vibe add skill unity-game-development ./my-game
# 只安装一个阶段及其子技能
vibe add skill unity-game-design ./my-game
# 只安装一个专项技能
vibe add skill unity-game-performance ./my-game
# 独立阶段执行 / reviewer包（含4个审查子技能）
vibe add skill unity-game-production-execute ./my-game
vibe add skill unity-game-review ./my-game
```

例如性能任务只需读取 `unity-game-beta/unity-game-performance/SKILL.md` 并交给 performance-engineer；原型任务可并行使用 playable-prototype 和 prototype-playtest，但试玩执行依赖可玩的实际版本。每个角色的原生定义已有对应技能路径。

## 复用已安装的通用 Skills

| 通用技能 | 对应环节 | 组合边界 |
|---|---|---|
| `version-management` | 立项排期、依赖拆分、制作与版本迭代 | 复用任务分层；本工作流仍由主代理单写共享状态，每批次先集成再放行下游 |
| `git-manager` | 功能交付、构建发布、热修复 | 分支、差异与版本追踪；push、凭据和外部发布按实际操作范围确认 |
| `omnidraw` | 核心循环、技术设计、关卡草图、UI 与美术方向 | 绘图与概念参考；图稿不等同 Unity 已导入资产或可玩内容 |
| `state-machine-reasoning` | 核心玩法、流程/存档回归、异常恢复 | 推导状态、转移和不变量，再转成实现与测试；状态图不是运行证据 |

这些通用技能由 manifest 一起安装；单独使用专项 subskill 时，仅在已安装且确有需要时组合使用，不作为隐含依赖。

## 更新已有工程

```bash
# 刷新本模板已管理的入口、角色和参考资料，同时安装此前缺失的技能包
vibe add manifest unity-game ./my-game --force
# 已经安装过此包且明确需要更新技能内容时，再单独刷新
vibe add skill unity-game-development ./my-game --force
```

第一条保留现有技能，并校验当前源包实际分发的必需文件及catalog最低schema4；旧包缺文件/目录映射过旧会报告needs_migration并退出非零，保留用户文件。先备份并合并缺少内容或明确更新包，然后重跑校验；第二条会替换该技能目录，先保留自己修改的技能文件。运行状态、已填交付物和实际游戏资源继续保留。直接运行 manifest init 脚本仅安装工作流，技能仍通过 vibe add skill 安装。
