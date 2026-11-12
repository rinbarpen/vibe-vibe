# 进度

- 已读取现有入口、初始化器、安装记录与事务/回退 API，核对 root 指令与 manifest-creator。
- 新增 setup/portable Python 模块、免全局安装脚本、CLI setup 子命令和双端导入/skills 安装。
- 新增 BOOTSTRAP 一句话契约及 workflow，保持 README 双语入口和既有参考页。
- 初次 14 项测试的四个 provider 对照因多复制命令目录根索引失败，修正为既有命令分发布局后全通过。
- 新增 Windows/macOS/Linux × Python 3.10/3.12 CI 矩阵；当前会话仅实测 Linux，不标称远端 CI 已运行。
- 扩大全量工具测试时收集缺 lxml，已改用隔离 uv 补齐 Office 测试依赖，不更改全局 Python。
- 真实 CLI 预览暴露来源参数 repo 与生成参数 --repo 的命名冲突；已将来源参数改为 source_root 并补实际 dispatch 回归，不只测试 --list。
- 最终专项 16 项通过；现有工具回归 470 passed、2 skipped、1313 subtests passed；共用 renderer 10 项通过。
- 真实 vibe-coding fullstack 项目：39 个 skills 双端完整副本、490 个文件哈希验证、重复执行无新备份；独立恢复脚本恢复原始指令/README/数据哈希。
- 文档五页只读结构检查 0 错误；workflow 已再生、漂移检查和 Chromium 图面检查通过。
- 基线 CLI 无 setup（exit 2），修改后入口存在（exit 0）；15 文件补丁实际应用、选择性回退及幂等回退均验证，工作区改动保持原样。
- 尚未提交/推送；Windows/macOS 原生 CI 与独立宿主激活不在本地执行结果中冒充通过。
