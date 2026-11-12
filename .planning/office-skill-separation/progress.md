# 进度

- 已保存 86 个原有文件的 SHA-256 与字节快照；保留原有 Git index 和原路径已有缓存。
- 基线安装/运行/图示回归：31 passed、4 skipped。
- 通用 Office 指南、脚本、宏与角色已迁入 mine/office；项目 Manifest 仅保留业务协作、简报、规则与工作流。
- 实际源码独立 Skill 安装与十项依赖的 Manifest 安装成功；未用第三方占位 Skill 冒充这两项实际安装。
- init/add、便携 setup/check、update 与独立 restore 回归通过；旧项目入口、README、账本和 legacy 用户文件保持。
- 工作流源、SVG、随包 renderer 与只读漂移检查有效，已查看两张真实 PNG。修复 CairoSVG 字体回退和 SVG 1.1 描边兼容后中文/分支标签可读。
- 最终相关回归：217 passed、3 skipped、1025 subtests passed；没有把打包验证声称为 Microsoft Office 宏执行。
- 对 136 个变更路径生成可重放补丁，在基线副本实际应用并核对修改版哈希，执行独立 rollback 后恢复原 SHA-256，额外用户文件保留。
- 已重新打开验证 office.skill、verification.json、补丁与回滚脚本；工作区仅运行 rollback dry-run，未回退已完成改动。

## 已处理的问题
- 安装测试夹具的 scripts 目录依赖旧布局：显式建立项目脚本目录，更新夹具和预期路径。
- 新测试导入缺少 PYTHONPATH：使用当前源码入口；完整回归采用已缓存的隔离 uv 环境。
- SVG 预览中文缺字、描边覆盖：两份随包 renderer 优先 CJK 字体，标签分层描边后重生成和查看。
- renderer 首次编辑缩进错误：修正循环缩进，重新生成成功后才刷新预览。
- 补丁缺少原 SVG 文件末尾无换行标记：补齐标准 EOF 标记并保留原换行字节，git apply 与回滚实际通过。
