# 独立审查记录

- 任务/阶段 / 审查人 / 实际独立上下文 / 输入版本：待填写
- 实现责任人 / 原执行skill / 审查范围 / 验收依据版本：待填写
- reviewer skill / profile / 审查subskills与实际路径：待填写
- reviewed_revision / source_hashes / artifact_hashes：待填写
- review_status：not_run；审查实际完成后为completed，排队为pending
- verdict：留空（完成审查后为passed / changes_requested / blocked）
- approved_revision：留空；仅passed时绑定当前revision
- report_path / previous_report / 报告自身SHA-256：待填写

| 发现 ID | 严重性/是否阻断 | 文件/需求/证据哈希 | 预期/实际/复现 | 原owner/执行skill | 修复revision | 复审报告/证据 |
|---|---|---|---|---|---|---|

## 核对
- 需求与实际行为一致；接口、错误/边界、存档兼容符合基线。
- 资源/`.meta` 配对和引用完整；并行修改所有权无冲突。
- 测试命令、日志、XML、构建与源码版本一致，not_run 项没有写成通过。
- 玩法/性能/目标设备覆盖缺口明确；许可证、隐私与发行材料按需核对。
- 结论：独立审查未执行保留review_status=not_run；已审但缺必需证据为blocked，需修复为changes_requested，证据齐全且无阻断项为passed。运行测试状态另记passed / failed / not_run。
- 只有当前版本审查通过且必需交付/证据及用户确认齐全才推进；输入改变重新审查，修改由原skill/owner处理。
- 发布或阶段用户确认与代码审查分开，不以审查通过代替用户批准。
