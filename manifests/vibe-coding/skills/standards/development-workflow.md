# 开发流程 (Development Workflow)

本流程旨在通过 Vibe Coding 的方式，结合 Cursor 的强大能力，实现高效、正规的软件开发。

## 阶段 1：需求分析与探索
1.  **意图确认**: 与用户确认最终目标。
2.  **技术调研**: 
    - 使用 `SemanticSearch` 探索现有代码。
    - 使用 `skill-seekers` 摄取第三方库文档。
    - 使用 `WebSearch` 查找最佳实践。

## 阶段 2：方案设计 (Plan Mode)
1.  **架构设计**: 调用 `code-architect` subagent。
2.  **编写 Plan**: 创建 `.plan.md`，明确步骤、涉及文件和验证方法。
3.  **评审**: 确认方案符合开源标准。

## 阶段 3：迭代实现 (Agent Mode)
1.  **环境准备**: `uv sync` 或 `proxy_on`。
2.  **小步快跑**: 每次修改 1-3 个文件，保持逻辑独立。
3.  **即时验证**: 每次 substantive 修改后运行 `ReadLints`。

## 阶段 4：质量把关 (Review)
1.  **自我审查**: 检查是否引入了 AI 产生的冗余代码 (Deslop)。
2.  **Subagent 评审**: `implement` 内含双轴 subagent review，不单独发起通用 code-review。
3.  **测试运行**: 确保所有测试通过。

## 阶段 5：交付与归档
1.  **提交代码**: 编写符合规范的 Git Commit。
2.  **创建 PR**: 包含详细的测试计划。
3.  **文档更新**: 同步更新 README 和 API 文档。
