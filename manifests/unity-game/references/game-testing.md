# 实际游戏测试与缺陷闭环

## 何时选择

“帮我测试游戏”“运行并玩一遍”“看看有没有bug”首先读取 `unity-game-testing`，再按任务选择7个subskills：测试计划、启动游玩、探索异常、视觉/交互、缺陷复现、修复复测、独立测试审查。它位于Alpha目录以便整包安装，但跨原型、切片、制作、Beta、候选包和热修复使用。

它补充而不是替代既有 `unity-game-test-automation`（EditMode/PlayMode）、`unity-game-flow-regression`（流程/存档）、performance/compatibility（实测）和prototype/balance-playtest（真人观察/分析）。测试计划和试玩反馈不是实际操作证据；能发现Unity对象不等于能控制游戏输入。

## 实际执行通道

1. **项目现有harness**：确认提供普通输入和可观察断言；直接改内部状态只能证明单独标注的调试/注入场景。
2. **已连接MCP**：先发现真实工具/schema、目标实例/运行模式与输入能力，在测试副本做小样；不预编造方法名。
3. **桌面游戏**：有可见窗口且需要GUI时，定位并读取实际已安装的computer-use/设备控制skill；核对目标窗口、焦点、坐标与输入支持，避免操作用户其他窗口。缺窗口或输入工具即not_run。
4. **WebGL**：读取宿主已有浏览器skill，测试实际URL和canvas，通过真实输入观察帧；DOM文本为空不代表画面为空。调试JS直接修改状态与普通鼠标/键盘分开记录。
5. **移动/其他设备**：使用实际设备工具，记录设备、包、输入和采集能力；Editor结果不代替目标设备。

不在模板中自动安装软件/插件、连接服务或使用账号。确认测试数据副本，有限时间/动作/重试预算，失败释放所有按键/指针，保存现场后退出；联网、支付和外部写入另行确认。音频、Profiler帧时间和人类主观反馈需要各自真实观察条件。

## QA与reviewer

QA加载计划→普通输入游玩→按需探索/画面→缺陷最短复现。代码修复返回原owner/执行skill；QA用修复后的明确revision重跑原case和相邻回归，不仅观察“这次没遇到”。独立game-reviewer加载 `unity-game-test-review` 审查实际报告与原始证据，再汇总当前阶段profile。QA、原实现和reviewer身份/上下文分别记录；用户确认门不由测试通过代替。

缺环境/未执行用not_run；真实失败用failed；有真实步骤与断言证据才passed。缺独立reviewer或必需用例未执行不推进；审查绑定session哈希和构建revision，输入变化复审。

## 会话模板与只读校验

复制需要的模板到每个任务的独占目录，不修改模板充当实际交付：
- [game-test-session.md](../templates/game-test-session.md)：操作、断言、设备和缺陷记录。
- [game-test-session.json](../templates/game-test-session.json)：机器可校验的执行记录。
- [bug-report.md](../templates/bug-report.md)：复现、修复与回归。
- [game-test-review.json](../templates/game-test-review.json)：独立审查侧车。

安装后：
```bash
python3 .unity-game/scripts/game_test_cli.py check --session Evidence/run-001/session.json
python3 .unity-game/scripts/game_test_cli.py check --session Evidence/run-001/session.json --review Evidence/run-001/review.json --require-review
```

该命令**只读核验记录，不启动游戏、不采集截图、不操作输入**。`validation_status`是结构/哈希检查，`status`是记录的本轮必需用例结论；两者不是物理执行真实性的证明。退出0表示记录满足通过条件，1为失败/证据无效，2为未执行/待审。模板直接检查为not_run/2。

JSON字段：
- `schema_version:1`、`run_id`；`game.revision`与`game.build:{path,sha256}`，真实执行需要实际非空构建文件，默认kind:file只绑定该文件；整个包使用kind:manifest声明schema1的JSON（files数组，每项path/sha256，相对清单目录，不越界、不重复、不包含清单本身），并核验实际包文件；path相对session目录或绝对路径。
- `execution.kind:planned|simulation|real_game`；真实执行还记录channel（project-harness/mcp/desktop-skill/browser-skill/device-tool）、tool真实名称/skill路径、environment与tester上下文。可另记implementation_actor。模拟/计划只保持真实游戏用例not_run。
- `cases`中每项有唯一id、required布尔、expected、status；not_run附reason；执行过的项附actual、真实顺序steps、evidence数组。至少一个required用例；任何真实失败保持failed，必需项not_run不算全通过。
- `scope`可选startup/gameplay/visual，默认gameplay。后两者要求normal_input:true；启动崩溃可用startup记录实际启动步骤及日志，不伪造输入。测试范围由用例决定，通过启动测试不等于全游戏通过。
- `evidence:[{path,kind,sha256}]`必须位于会话目录、实际非空且哈希匹配。截图/视频/日志/状态断言各自说明证明内容；校验器不自动判断图像、声音或“好玩”。
- 可选`input_events:[{kind,code,t_ms}]`记录实际标准化轨迹；接受key/pointer/touch/gamepad的_down/_up、pointer_move/touch_move、scroll、text与gamepad_axis；离散按下/释放须配对，axis携带code/value[-1,1]且最终回零，text携带实际text；时间有限、非负递增，未知事件拒绝。实际工具的原样输入输出另外保存；未提供轨迹不冒称已验输入释放。
- review侧车填写review_status、独立reviewer、independent_context、reviewed_revision、最终session字节的reviewed_session_sha256、verdict、approved_revision。passed只批准同revision且所有必需用例有证据；reviewer与tester/原实现上下文不同。更新session后重新计算并复审。提供了已完成的负面审查即阻止通过，--require-review只决定未审时是否阻止；上下文身份比较去除首尾空白。

独立child skill安装不附带此helper；没有helper仍按同一实际证据契约执行并交接。原始日志、截图和失败尝试不覆盖；状态仍由producer单写。
