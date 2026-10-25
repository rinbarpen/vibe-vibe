# Unity Game Manifest 实施

## 已批准目标
Unity 2D/3D 全流程 manifest，20 个双端原生角色，subagent 优先并行，方向/切片/发布确认，Editor CLI 辅助，无新增外部依赖。

## 阶段
- [complete] 流程、参考资料与交付物模板（unity_docs）
- [complete] 20 个角色与双端定义（unity_roles）
- [complete] Unity CLI 与伪 Editor 验证（unity_cli）
- [complete] 初始化、安装回归与中英文索引（root）
- [complete] 集成审查、回归、验证及回滚证据

## 固定接口
安装辅助资源到 .unity-game/{agents,references,templates,scripts}，共享状态 .unity-game/state/{status,tasks,decisions,artifacts}.md，交付 .unity-game/deliverables/。
辅助 CLI doctor/test/build --project PATH [--editor PATH]；test --mode editmode|playmode；build --target TARGET --execute-method METHOD --output PATH。

## 修改边界
新增 manifests/unity-game 和本规划目录；更新两份 README；为保留必需技能新增核心安装器的可选 force 策略读取。保留实施前已有的 Python 缓存变动。

## 追加：全流程 Skills 与 Subskills
- [complete] 新建 unity-game-development 总入口、9 个阶段 skill、29 个专项 subskill（三级渐进加载）。
- [complete] 接入 manifest 自动安装、九阶段路由、20 个角色及任务包。
- [complete] 单项/阶段/整包安装、引用、双端一致性、升级保留与完整回归。
- [complete] 独立样例前向验证、增量补丁与回滚验证。

新增技能放 mine/，按仓库真实递归发现规则独立安装。子技能独立可用，不依赖包外相对路径。已有产物保留并增量更新。

## 追加：执行 Skills、Reviewer 与 workflow SVG
- [complete] 9 个阶段执行 skill 与独立 reviewer skill（含4个审查 subskills）。
- [complete] 九阶段执行→独立审查→返工/等待/通过→用户门禁映射与任务/报告契约。
- [complete] 根据机器可读目录生成真实SVG，安装、再生成与可视化检查。
- [complete] 技能闭包、全流程图一致性、回归、前向评审和增量回滚证据。

## 追加：模型设计与外部软件操作
- [complete] 模型设计/建模/UV材质/绑定导出/审查的层级skills及model-artist角色。
- [complete] 可选Blender CLI/Python执行器、MCP/外部skill接入配置与操作契约。
- [complete] Unity导入/角色/模板/目录与workflow SVG联动。
- [complete] 递归安装、伪DCC与独立审查、回归、补丁及回滚验证。

## 追加：实际游戏测试与可靠性
- [complete] unity-game-testing及7个子技能，真实输入/探索/视觉/复现/修复复测/独立审查闭环。
- [complete] 安装事务恢复、旧包升级兼容检测、输入产物证据与格式完整性。
- [complete] 测试证据校验、模板/角色/目录/SVG集成。
- [complete] 独立评审、前向样例、全部回归、增量补丁/回滚验证。
