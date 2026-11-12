# 发现

- 用户确认：已装好 AI 工具后，一句自然语言配好项目，不含 AI 工具安装/登录。
- 现有 CLI 所有 custom init 经 .sh 执行；Tutor/Office/Unity/Game-design 已有 Python 实现。
- 现有 skills 仅安装到 .agents/skills；Claude Code 需其对应项目级技能入口。
- 自动配置可用 Python 3.10+ 标准库，不必全局安装 uv/CLI；本任务不修改上一轮研究契约。
- 仓库有已有未提交更改，必须保全其当前状态；通用 init/update 原覆盖策略保持不变。
- 已核对官方技能目录：Codex .agents/skills；Claude Code .claude/skills。Firecrawl 未暴露工具，外部核对用官方网页。
- 新入口独立于旧 init/add：复用四个原生 Python 安装器；其余 legacy 资源布局显式渲染并对照 shell 产物，不依赖 Git Bash。
- 事务复用既有 transaction/rollback；新入口以 setup 记录维护双端副本，旧 update 不维护该记录，文档明确区分。
