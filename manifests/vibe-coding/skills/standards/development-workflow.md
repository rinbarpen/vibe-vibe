# 开发流程 (Development Workflow)

按任务范围选择最轻量且足够可靠的路径；不要让每项工作都触发规划或额外 skills。

## 工作流路由

- **简单需求**：直接 vibe coding；检查相关实现、完成最小改动、运行针对性验证，不创建计划文件。
- **Bug 修复**：使用 `grilling` 梳理复现、根因和预期行为，再交给 `implement` 修复与验证。
- **复杂 Feature**：依次使用 `grill-with-docs` → `to-spec` → `to-tickets` → `implement`。
- **中大型任务跟踪**：中文任务使用 `planning-with-files-zh`，英文任务使用 `planning-with-files`；不把它们扩展到简单改动。

## Implement 与 Review

1. `implement` 根据任务和项目约定选择针对性测试、lint、类型检查与构建验证；适合时采用 RED → GREEN → IMPROVE。
2. `implement` 内隐调用 subagent 完成双轴 review：
   - 正确性轴：需求符合度、行为边界、测试覆盖。
   - 代码质量轴：设计、可读性、可维护性。
3. 不手工额外发起 code-review。安全敏感变更仍根据规则追加安全评审。
4. 汇总验证结果、评审发现及处理情况后交付；仅按任务需要创建 commit/PR 并更新文档。
