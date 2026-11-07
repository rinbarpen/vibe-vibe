# 工具、技能与职责路由

本文件说明如何把工作包交给真实工具，而不是假设“有一条技能名称就已经执行”。先看当前项目约定、工具/连接、文件/未保存状态和允许修改范围；按适用性读取所选技能的真实 `SKILL.md`。

## 1. 路由优先级

1. **已经连接且适用的 MCP/API**：发现当前工具名、参数 schema、应用实例与文件；做一个可回退小样并重读/重开确认，记录真实调用与输出。不要编造 `create_model` 等不存在的方法。
2. **实际已安装的软件/专项 skill**：核对路径、版本、插件、可操作对象与产物要求，再执行。提示中出现名称不等于宿主注册了工具。
3. **本地 CLI/脚本**：绑定已安装二进制和版本，记录 cwd/env/输入/退出码；使用经审查脚本、工作副本和新输出目录。CLI 参数以当前软件帮助/版本资料为准。
4. **GUI**：仅当当前操作需要可见窗口且上述路径覆盖不足时，使用可用的 GUI 技能/工具；先确认未保存场景和单写者，截图/保存重开核对。不争用用户正在编辑的唯一场景。
5. **缺依赖**：标 `waiting_dependency` 与 `not_run`，继续不受阻的规格/数据工作，保留所需工具、输入、恢复用例；不产出伪模型或假冒运行日志。

付费、下载新依赖、插件安装、对外上传/云生成、生产数据写入与发布按已有决策门处理。模板安装不自动合并 MCP 配置、不启动桌面软件、不默认接管远端。

## 2. 可复用资源与边界

| 工作 | 已有资源 / 接入方式 | 适用边界与验收 |
|---|---|---|
| 3D 模型规格、实际建模、UV/PBR、绑定导出、独立审查 | 可选 `unity-game-development` 中真实 `unity-game-model-design/build/surface/rig-export/review` 子技能；从安装位置读取，不复制整份目录 | 方法可复用；原子技能末端 Unity 导入/路径/owner 由本项目 adapter/TDD 替换，不能直接宣称其他引擎通过 |
| Blender doctor/副本执行/导出 | 本包 `.game-design/scripts/dcc_cli.py`、`templates/Blender/export_model.py`，从 canonical 源显式分发并登记来源 hash | 本地协议通过不代表艺术质量、绑定/动画、保存重开或引擎验收；新模型必须有实际 creation 脚本 |
| Maya/3ds Max/其他 DCC | 项目已有软件 skill、实际 MCP/CLI/API 或 GUI | 本包没有虚构一套通用命令；需绑定软件、插件、真实源/导出、版本、参数和日志 |
| 项目计划、分支/任务依赖、replan | 可选 `version-management`；按实际安装根读取 `version-plan/replan/execute` | 不改变已有仓库策略；其并行 worktree 方法不取消 DCC/Editor 单写者；需要委派时遵循当前宿主协作规则 |
| 托管平台 PR/issue/CI/release | 可选 `git-manager` 的 GitHub/Gitee/custom-git 子技能 | 核对当前平台/登录状态；源、本地配置与远端动作分开，凭据只确认存在，不写入文档或日志 |
| 游戏真实输入/探索/缺陷复现/修复复测 | Unity 项目可接既有游戏测试子技能；其他引擎沿用相同用例证据原则，并接实际运行窗口/设备/harness | EditMode/静态检查不是实际游玩；输入操作、视觉/音频、性能、设备与真人反馈分别记账 |
| 引擎导入/构建/运行 | 只读所选 [engine adapter](engine-matrix.md)，然后实际 Editor/命令/harness | 23 项是设计映射覆盖，不表示本机已装全部软件；每项成功码/构建路径和目标不同 |

这些是**可选资源**。`game-design` 本体不把 Unity、版本管理或托管平台技能全部设成必装依赖，避免非 Unity/离线设计项目被迫安装无关资源。安装命令可在项目有明确需求时执行，例如 `vibe add skill version-management ./my-game`；实际可用名称以 `vibe list skills` 为准。

## 3. canonical 分发约定

维护者只修改 canonical `dcc_cli.py` 和静态网格导出模板；本 manifest 的安装器显式分发所需文件并记录来源与内容哈希。已安装 `.game-design` 包应自包含运行，不依赖用户机器保留本仓库或另装 `.unity-game`。修改 canonical 实现时跑其既有测试与 game-design 的分发/契约测试，不维护分叉实现。

源码中的 canonical 路径仅供维护者定位，不作为安装后 Markdown 链接：`manifests/unity-game/scripts/dcc_cli.py`、`manifests/unity-game/templates/Blender/export_model.py`。Unity 的 `skill-map.json` 与生命周期仍由其原包维护，本 manifest 不另复制同一目录充当第二事实源。

## 4. 每次交接最小包

- WORK-ID/REQ-ID/ASSET-ID、设计 revision、选定类型/引擎/平台和 owner。
- 已冻结输入与哈希、允许修改路径、工具/插件版本、状态与单写者锁。
- 实际执行步骤/命令/工具 schema，预期输出/预算/阈值，失败时的返工 owner。
- 源文件、交换文件/依赖、引擎资源 ID/引用、原始日志/截图/播放/设备记录与真实 hash。
- 每项 `pass/fail/not_run/not_applicable`、不适用理由、reviewer 独立性、缺口与恢复用例。
- 修改前快照与回退步骤；确认只覆盖本次 revision/输入/目标，不替整个项目或发布审批。
