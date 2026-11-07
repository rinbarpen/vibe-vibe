# Game Design — 多引擎游戏设计与制作契约

先读取 `.game-design/README.md`、`.game-design/references/lifecycle.md` 与 `.game-design/state/` 中的 project.json、status.md、decisions.md、evidence.md。恢复已有工作，从首个未满足的验收继续；不要重建已有工程。若当前是模板源码目录，资源位于同级 README.md、references/、templates/，安装到项目后才使用 `.game-design/` 路径。

## 默认目标
先设计可验证的游戏，再按用户约定进入实现。默认 `design-only`：交付设计包，不自动建工程、安装引擎、下载付费资源或发布。用户明确要求开发后，记录 mode=implementation 并沿用同一设计、测试、制作、发布流程。主流适配器以 references/engine-matrix.md 和 engines.json 为准。

## 第一次会话
1. 读取状态、已有代码/设计/构建证据；运行 `python3 .game-design/scripts/game_design.py detect --project .` 取得只读引擎线索。复合仓库对用户指定的游戏子目录执行，不扫描所有资产或缓存。
2. 整理受众、体验支柱、核心循环、类型/视角、目标平台、输入、联网、商业模式、预算/工期、团队和成功标准。缺省可提出显式假设；影响方向的选项给人决定，技术实现疑问由 AI 调研/实验解决。
3. 有工程则保持其引擎与版本；新项目比较 2–3 个合适引擎及成本，以人确认的引擎/版本/平台填写 state/project.json 和 engine-decision.md。检测不等于选择，空工程不默认 Unity。多个候选不自动择一。
4. 只加载所选适配器（references/adapters/<id>.md）及 references/adapter-contract.md。先检查本机工具、插件/SDK 和命令帮助，再将其示例绑定到实际工程；不运行未解析占位命令。
5. 读取 references/genres.md 的可组合类型档案，用 production_tools.py 按领域/任务按需加载工作包；类型、2D/3D、联网、平台和资产生产方式分别配置。为本项目选择适用任务，不适用写理由与依赖影响，登记 state/work.md。
6. 读取 references/modeling.md、version-management.md、tool-routing.md：先确定版本/资产锁/源与生成物策略；需要3D时执行真实DCC链，再按所选引擎导入复验；2D/无模型项目明确跳过3D理由而非强行建模。
7. 设计 GDD、系统数值、关卡叙事、视听/UI、技术映射和测试计划。每个玩法需求分配 REQ-ID，连接实现、用例与证据。方向确认后才启动约定内原型；设计模式到设计包审查/确认即停。

## 执行与验收
- 以 references/lifecycle.md 为唯一阶段规则；workflow.svg 是规范图，不是项目当前进度。
- 角色是职责而非自动创建的多个代理：设计负责人、引擎实现者、QA/审查者可由同一会话分轮承担；用户明确需要时再安排多人。作者自检与独立审查分别记录；没有独立人员时标记 self-review，不冒称独立。
- Scene/World/Prefab、事件数据库和云项目共享资源采用单写者；源与生成物分离，保留 GUID/UID/资源 ID。二进制资源使用对应 Editor/工具，不用文本替换伪造。
- 数据表校验、静态检查、单测、真实启动/操作、目标设备、真人试玩互不替代。记录命令、版本、输入、stdout/stderr、exit code、截图/日志和产物哈希；缺环境记 not_run/blocked_dependency，不报告通过。
- “编译成功”不是“好玩”；原型必须验证最小玩法闭环和关键体验假设，真人反馈与 AI 操作证据分开。
- 每次实现修改先保留可回退基线，在工作分支/副本操作，验证后再纳入；失败由原 owner 修复并重跑原用例。改引擎/版本/付费依赖、改变目标/预算、切片放行、对外发布需要明确决策记录。未回复保持 waiting_human，确认后由 AI 从记录的 resume 节点继续。
- Unity 需要深化制作时可接已有 unity-game / unity-game-development；复用其目录和技能，不将 Unity API 套到其他引擎。不自动安装无关技能或改写宿主 MCP。
- 实际发布必须人工确认目标包哈希、平台/受众、存档迁移与回退计划；模板安装和检查不构成发布批准。

## 粗细工作与工具契约
- references/production.json 是工作包事实源，每包绑定输入、实际操作、交付、可观察验收、前置任务和返工点。阶段规则仍由 lifecycle.md 定义；在 state/work.md 追踪本项目选择与职责。按用户范围执行，不把整个目录机械排成任务。
- references/genres.json 是类型专项事实源。主/辅类型组合先解决循环/数值/镜头/输入/联网冲突；类型覆盖不是成品承诺，渲染维度和平台不是游戏类型。
- 建模需走规格→DCC实际制作→拓扑/UV/PBR→可选绑定/动画→LOD/碰撞→导出→引擎导入→审查。源文件、生成物、工具日志、包hash和审查证据分开。export_model.py 是导出模板，创建新模型必须另有按规格编写的真实建模操作。
- 版本职责贯穿所有阶段：规划/分支/审查、代码与资产单写者/LFS或P4锁、引擎/工具链版本、游戏/内容/build/存档schema/网络协议版本、tag/包hash/迁移/更新与回退。version_check.py只读检查，不代替团队策略，也不自动初始化/提交/推送。
- canonical DCC helper由安装器从仓库原源分发，install.json 的 canonical_sources 记录原源路径/hash；安装后的工具自包含。工具doctor通过、文件hash通过、模型质量审查、真实引擎验收是四种不同证据。
