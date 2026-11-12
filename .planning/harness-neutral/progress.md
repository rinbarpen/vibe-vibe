# 进度

- 已读取 manifest-creator、旧任务记录、规则清单、installer 和 update 资源边界。
- 已实现普通 Markdown 规则包、PROJECT_RULES 通用入口、generic harness 模式与既有安装/更新贯通；源 MDC 的作用域作为数据保留，无客户端解释器依赖。
- 发现器支持 AGENTS.md / PROJECT_RULES.md 单入口，不再以 CLAUDE.md 为硬前提；补齐仅单入口时的 named-host 交接。
- 12 项 harness 专项（含全部现有 manifest/场景）初次通过。首次兼容回归揭示符号链接被文本重写物化、初次发布备份语义和旧场景路径断言；修复链接节点保真，保留原 init 的纯新增行为，并改为验收中立输出而非 Cursor 路径。

- 确认无需扩展历史 init/add：补发中立文件会绕开其原生回退事务，已撤回该路径，保留原入口语义；通用配置使用 setup，集中更新使用 project update。未通过测试保持完整恢复断言，而非放宽回退要求。
- 修复正文路径二次替换导致的链接嵌套；为普通规则相互引用、支持目录 INDEX、单 PROJECT_RULES 入口刷新、多 manifest 合并与旧 tracking 退役增加测试。
- 基线真实 CLI 生成旧项目；新 CLI 完成 generic 安装、显式读规则、scope 核验、安装后图再生、旧项目升级与逐文件哈希回退。
- 文档只读结构检查 7 文件无错误；两张图漂移检查通过，配置图已实际查看。Chromium 的 /tmp 截图未产生文件，已纠正到工作区并核实实图。

- 最终冻结源码后重新运行全套：503 passed, 2 skipped, 1353 subtests passed；15 项 harness 专项通过。24 文件差异已在独立基线实际应用并核对哈希，选择性回退、重复回退和新修改保护均通过；verification.json 已重开校验。未 commit/push。
