# 调研发现

## 本地基线
- 工作区初始 git status 干净，无 .codegraph，跳过 CodeGraph。
- 现有 .planning/auto-research-writing 已完成，保持原文件。
- 现有 manifests/unity-game 含技能目录、专用脚本及 workflow；新模板应兼容而非替代。
- docs/manifest-workflow.md 要求真实 SVG、可编辑源、渲染器、只读漂移检查与安装后资源完整性测试。
- manifest 发现以 CLAUDE.md 为准；任意 references 不会自动由通用安装器分发，需检查并提供专用初始化器。

## 外部资料
待核验官方资料；外部内容仅作为研究数据。

## 安装与设计决策
- vibe 自动发现 scripts/*init*.sh，未知模板可使用默认 -f/-n 约定；CLI 对未知脚本 dry-run 只展示命令，不执行。
- 新模板命名 game-design，以引擎无关 GDD 为核心；单独提供全套只读适配查询工具与专用资源安装器，不改 CLI 及 unity-game。
- 不将引擎选项伪装成 scenario（公共 CLI 未映射新模板的 scenario）；安装后显式选择引擎，已有工程只读检测。
- 不创建空壳的多个重复 manifest；统一协议下登记引擎/框架的场景、脚本、资源、验证、构建、版本和平台限制。

## 官方资料初查（2026-11-03）
- Unity 官方测试框架文档提供 -runTests/-testResults，Editor 运行与测试结果必须分开验证：https://docs.unity.com/en-us/engine/6000.5/manual/scripting/test-framework-introduction/running-tests/run-tests-from-command-line
- Unreal 官方构建说明将 BuildCookRun 归于 UAT，不等同于测试和实际游玩：https://dev.epicgames.com/documentation/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine
- Godot 命令行导出需要 editor binary、匹配版本 export templates 和 export_presets.cfg：https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html
- 搜索出现 Cocos 2.x 和 3.x 两种参数，需按已装版本区分，继续核验 3.8 文档。

## 官方资料覆盖与适配范围
- 已核验官方入口：Cocos Creator 3.8、Phaser、PixiJS、Babylon.js、PlayCanvas、GameMaker、Construct 3、GDevelop、Defold、MonoGame、libGDX、Bevy、Ren'Py、RPG Maker MZ、Roblox Studio、O3DE、Stride、raylib。具体链接写入各适配器目录。
- Three.js 旧 creating-a-scene.html 返回 404；转官方 manual fundamentals。LÖVE wiki 返回 403；转官方 GitHub。Bevy 旧域名跳转 bevy.org，额外核验官方仓库。
- Cocos 3.8 使用 --project；适配器明确区别 2.x，不复制 --path 的旧用法。
- 覆盖 23 项：4 通用编辑器，5 Web 运行时/渲染库，5 低代码/叙事/平台工具，6 代码优先引擎/框架，Roblox/O3DE/Stride（按目录类别细分）。渲染库明确缺少完整玩法/物理/存档系统。
- 覆盖表示设计与工程映射协议齐全，不表示在当前机器安装或构建过全部运行时。

## 适配协议与验证边界
- 每个适配器包含定位、识别特征、版本锁定、场景/实体、脚本/数据、资源导入、坐标与输入、存档/联网、测试、构建、限制及官方资料。
- 原型/垂直切片之后继续制作、QA、发布/运营；设计模式可停在已确认的设计包，不默认进入开发或发布。
- 工具只读检测根工程与显式子项目，不扫描缓存、不运行引擎。多命中返回 ambiguous，通用 Cargo.toml/package.json 不足以直接认定引擎。
- 初始状态 engine=null、运行时 not_run；版本、平台、工具缺失应列待决，绝不以目录存在推断运行通过。
- Cocos 3.8 官方构建成功码是 36，而不是通常的 0；Ren'Py lint 用 --error-code；Defold Bob 的 JDK 要求依版本核验。

## 实现与首轮验证
- 新增 23 项 adapter 的格式正例及无特征文件/多引擎/显式子项目/符号链接等反例；所有检测均为只读线索。
- 首轮标准库 unittest：48 tests，OK；包括实际 vibe list/init/add --force、安装后链接、图/适配文档只读漂移、幂等、已有入口/状态/交付物保护、独立回滚和故障注入回滚。
- 图的 renderer 是仓库 canonical renderer 的逐字节副本，图源独立表达跨引擎业务，不复制 Unity 的 skill-map。
- 当前机器未运行任何游戏 Editor；证据按设计/安装/格式检查保存，运行时状态保持 not_run。

## 图形验收
- ego-browser 在此 Linux 环境未安装，其技能安装器仅支持 macOS；未要求用户为可选预览安装桌面应用。
- 使用本机已有 librsvg + cairo 从真实 SVG 渲染 /tmp/game-design-workflow.png 并实际查看：1910×3670 SVG，三泳道、阶段文字/人工条件/恢复节点、返工/等待/回退箭头可读且未裁切。
- 该渲染只用于视觉验证，不修改 SVG，不增加项目依赖。回环预览 HTTP 服务已停止。

## 最终回归归因
- 专项测试：50 tests，OK。
- 联合回归：382 passed、9 failed、9 skipped、1227 subtests passed。
- 在 git archive HEAD 的独立副本复跑两个失败文件（仅复用未改的外部技能检出）：同样 9 failed、2 passed；失败节点集合完全相同。属于 CCFA/MattPocock/anthropics/wxa 技能资源与旧文案基线问题，不是 game-design 回归。
- 本次没有修改 tools/vibe_tool/src、manifests/unity-game、mine/unity-game-development，git diff --exit-code 验证为空。
- bash -n、git diff --check、真实安装后链接/再生成/回滚均通过。

## 可复验交付
- 修改归档和补丁包含 README 与 53 个新 manifest 文件（共 54）；逐字节验证归档与补丁应用结果一致。
- 运行 rollback.py --target <验证副本> 后 README 恢复原 hash，新增 source 文件全部删除；再次运行是 0 操作。真实工作区保留交付。
- verification.json 绑定三类 artifact SHA256、记录原始输出、失败基线和 14 条命令；baseline-context.json 留存 HEAD/隔离副本来源。


## 本轮缺口审计
- 已有引擎适配与高层阶段，但缺少可组合类型专项、可查询的细工作包、独立资产生产链和版本策略模板。
- canonical manifests/unity-game/scripts/dcc_cli.py 为标准库Blender copy-and-run适配器，具备 doctor/run、源文件保留、副本、job/result、产物hash、退出/超时与锁语义；除临时前缀外基本引擎无关，适合源级复用安装分发。
- 本机 PATH 无 blender；真实DCC运行将记 not_run，契约/缺软件/模拟进程与引擎游玩分开验证。
- 现有 version-management 是需求规划/分支/worktree执行技能；git-manager负责托管平台管理；游戏仍需补LFS/文件锁、源与缓存、游戏/内容/存档版本和发布包回退的专项契约。

## 扩展内容集成
- 类型档案按玩法循环而非引擎绑定；专业工作包DAG与生命周期返工循环分开，便于按需加载与明确不适用理由。
- 建模文档覆盖12个实际环节，资产登记CSV区分DCC执行/文件/技术/视觉/引擎/设备验收；静态export模板明确不负责新建模型与完整绑定动画。
- 版本文档覆盖Git/LFS/P4、ignore正确边界、锁、分支/CI、8个独立版本轴、补丁/存档迁移与回退；已核验Git/LFS/P4/SemVer官方说明。
- canonical导出协议确实包含mesh/triangles/material/texture/bounds/units及源/导出hash；安装分发从原始文件取字节并记录来源，不维护分叉。
- 独立审查发现canonical来源记录需区分实际已安装字节和可用上游字节：已补 installed_sha256 / available_source_sha256 / provenance_verified / current|refresh_pending|customized|unmanaged，避免KEEP旧版或用户文件却声称新源已装。
- 新修改归档必须显式包含两个canonical依赖，并在解包布局实际运行init验证，不仅做catalog检查。

## 扩展验证结果
- 32类型/19领域/94细工作包已校验，JSON单源生成查询文档，无环依赖序有效。
- 专项+canonical DCC+图测试首轮103 passed、85 subtests passed；完整回归425 passed、9 failed、9 skipped、1253 subtests passed，仍为前轮已确认的同9基线失败。
- 新增上一版真实安装→本版force升级用例，保留旧project.json与源资产，新增状态/工具按种子补齐。
- 新图2066×4930已用本机librsvg/cairo渲染并查看：类型、版本基线、DCC/非DCC分支、导出审查/引擎复验、依赖等待/回退齐全，文字未裁切。

## 本轮最终交付
- 32类型 × 19领域94工作包 × 23引擎；新增资产/版本只读检查，安装后canonical DCC自包含且来源可信状态明确。
- 专项最终104 passed、85 subtests；全量最终426 passed、9 failed、9 skipped、1253 subtests，原有9失败集合与前轮HEAD基线相同。
- revision-02归档80文件payload（含两个未修改的canonical依赖）、35处源差异；分离源码目录真实init和安装后查询通过。补丁副本与归档字节一致，回滚恢复上一版源字节，计划/证据保留。
- 独立审查发现的来源记录、未提交HEAD、缓存路径误判均有针对性修复和回归；真实Blender/游戏Editor未执行。

## 原生并行编排设计
- 任务调度由主代理调用真实host subagent工具，Python只持久化队列、事务、运行ID、预留与证据，不执行LLM。
- 新parallel.py采用单JSON原子事务与OS进程锁（POSIX flock/Windows byte lock），状态读/next只读。pending→running→submitted→integrated→validated→done，失败blocked保持资源。
- claim冻结输入hash、分配attempt/token/租约；绑定真实host运行ID后收集结果；作者/集成/QA/审查上下文区分，done后才解锁依赖。
- 资源预留检查字面写入路径（含父子/大小写）与外部资源键；不假装是OS沙箱。worktree由宿主准备，集成需主目录字节一致。
- 租约过期仍保留预留，恢复必须先停止原worker、提供证据并显式recover，旧token作废；技术等待、人决策与返工不自动变通过。
- 独立测试指出done依赖的审查证据及领取后的隐式依赖也需复核：已将依赖产物/门/审查证据纳入就绪与收件/验收，防止未列inputs的父产物变更滑过。
- 正常修改已有源文件时输入可与写入范围重叠；只读输入冻结，受领范围内的原输入hash保留为baseline，新版本在提交后绑定产物hash，避免一律拒绝in-place修改。
- 字面写入路径拒绝glob/越界/symlink、Windows保留名与末尾点/空格，并做大小写及父子范围冲突检查。

## 当前验证与宿主分层
- 当前官方Codex文档确认项目.codex/agents/*.toml的独立角色发现约定，localCLI=0.153.4；没有把debug prompt-input当作角色发现或执行证明，详见codex-registration.md。
- 147专项测试通过；全量469通过、9失败、9跳过、1274 subtests，通过范围包含38调度黑盒与5原生分发/保护/回滚测试；9失败仍为既有基线。
- 真host作者 /root/parallel_docs 与 /root/demo_level_author完成两个独立文档任务；/root/native_roles独立集成，/root/parallel_tests独立QA。QA为文档/规则模拟，遍历787状态和3148方向转换，非游戏运行。
- 演示队列在两个任务仅submitted/integrated/validated时均未解锁第三依赖，等待最终独立review后验证。

## 原生并行扩展最终交付
- 12角色与24原生配置；DAG/单写者资源/真实run绑定/心跳/token/收件/集成/QA/独立审查/显式停止后恢复/计划扩展与有门的模式晋级均已实现。
- 真host闭环：两个不同作者→不同integrator→不同QA→新的reviewer，审查前无就绪后继，审查后design-package唯一ready。模拟范围为文档与Python规则，不是游戏/引擎/设备。
- revision-03归档含115文件（含canonical依赖）、45处源改动；源码包解开真实安装、角色和状态功能通过。补丁应用后逐字节对归档一致，回滚恢复revision-02源文件且再次执行无操作。
- 独立proof、原位新版本baseline、未列inputs的依赖失效等新增问题已由38黑盒用例覆盖；另外5项原生安装保护/回滚测试通过。
