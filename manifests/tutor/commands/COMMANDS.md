# Tutor 指令索引

共 9 个可选助手指令；自然语言与命令共用 `references/tutor-interaction.md`，无需先选择场景或教学模式。

| 指令 | 行为 |
|------|------|
| `/import <path/url>` | 轻量索引材料，展示简要结构；有任务直接辅导，归档请求不强制规划 |
| `/learn <topic>` | 有/无教材主题辅导，自动增量 Markdown；`--plan` 仅规划并停止 |
| `/study <material>` | 深入相关范围；`--next` 恢复待答任务或确认位置 |
| `/review [topic]` | 有卡片 SM-2，无卡片基于笔记/问题/记录复习 |
| `/flashcard <topic>` | 按需生成带真实来源或通用知识标识的卡片 |
| `/mindmap <topic>` | 生成概念关系图，不假装未读教材结论 |
| `/exam [topic]` | 默认逐题，`--paper` 才批量生成独立题面与答案 |
| `/diagram <concept>` | 生成真实可见图像，保留可编辑源 |
| `/track [scope]` | 只读查看 LEARNING_RECORD.md、学习证据与可用复习数据 |

`--plan`、`--paper`、`--export pdf` 是助手参数，不是 vibe CLI 参数。规划见 `references/learning-path-design.md`；个人原文、当前辅导状态与历史见 `references/learning-records.md`；图文 MD 和 PDF 见 `references/illustrated-notes.md`。默认低打扰保存，明确记录和导出时反馈路径，失败立即说明。
