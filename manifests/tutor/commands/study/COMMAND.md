---
description: 深入当前材料或恢复主题辅导，自动保存图文笔记与真实记录，PDF 按需导出
globs: ["materials/**/*", "notes/**/*", "projects/**/*"]
---

# /study

```text
/study <path> [--mode skim|deep] [--export pdf]
/study --next
/study notes/summaries/统计/U01-变量.md --export pdf
```

`path` 为选定材料，`--mode` 为可选浏览/深读方式；`--next` 也支持恢复无教材主题。`--export pdf` 为助手参数，不是 vibe CLI 参数。

## Execution

1. 按 `references/tutor-interaction.md` 判断当前意图；纯导出已有笔记直接执行转换，不教学、不补问基础、不改记录。
2. 先读当前项目 `LEARNING_RECORD.md`，存在时再读 `MATERIAL_INDEX.md`、`LEARNING_PATH.md`，复用条件、偏好和问题，不重复问已知项。
3. `--next` 或自然语言“继续”先恢复**当前辅导状态**的待答原题/提示，不自答推进；已作答则按真实反馈后的下一步处理。旧记录没有状态区时使用最后确认位置与实际日志，不重置历史、不从笔记时间猜已学范围。多项目或起点真正不明确才确认。
4. 显式材料/章节优先，只读取相关章/页/片段；用户已给出问题则直接处理，不强制先完成全书索引和路线。无教材续学按稳定主题单元处理，不伪造教材定位。
5. 按用户回答选择提示、例子、重述邀请或完整讲解，不强制每次作答；换题保留暂停任务。用户直接要求答案时给解答但不记成用户已答。
6. 本轮知识增量在**本轮回复结束前**自动写 `notes/summaries/<主题>/<单元ID>-<章节或主题名>.md`，短内容文字、复杂关系真实 SVG/PNG，资源入 `notes/assets/<主题>/`，相对链接与图注检查见 `references/illustrated-notes.md`。只有 Mermaid 代码不算成图。先读再合并，保留用户原文和手改。
7. 按 `references/learning-records.md` 保存个人原文、真实作答与反馈及待答任务；未作答/未评估不填成绩。已读/练习/掌握分开，定位与页码只写已知范围，PDF 页序和印刷页码分开。不等待退出口令，不重复记录同一事件。
8. 核验写入与图链。普通教学不重复列路径；首次建档、阶段总结、明确记录请求及导出时提示，保存失败立即说明。
9. 按需执行 `python scripts/export-notes.py INPUT.md --output OUTPUT.pdf`；纯转换不追加学习事件。保留 MD/图源/已有 PDF，明确同意覆盖才加 `--force`；检查实际 PDF 中文、图像和版面后交付，不默认包含个人日志。
