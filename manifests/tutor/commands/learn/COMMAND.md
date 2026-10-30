---
description: 有或无教材的对话辅导与自动图文 Markdown；--plan 只规划，--export pdf 按需转换
globs: ["materials/**/*", "notes/**/*", "projects/**/*"]
---

# /learn

## Usage and Parameters

```text
/learn <topic> [--mode deep|quick|overview] [--material <path>]
/learn [topic] --plan [--material <path>]
/learn <topic> --export pdf
/learn --material notes/summaries/统计/U01-变量.md --export pdf
```

`--plan` 默认 false，表示只规划并停止；普通会话的 `--mode` 默认根据对话自动选择，显式值优先。`--material` 指定真实材料或待导出笔记；`--export pdf` 按需导出。均为助手指令参数，不是 vibe CLI 参数。

## Shared Interaction

先按 `references/tutor-interaction.md` 判断意图。具体问题直接辅导，不先要求教材/路线/全套学习条件；系统学习只问影响起点的关键信息。未提供材料时使用通用知识解释，不要求上传。

读取已有 `projects/<教材或主题>/LEARNING_RECORD.md` 和当前辅导状态；有教材再关联 `MATERIAL_INDEX.md`，有路线再读 `LEARNING_PATH.md`。多项目真正歧义时询问一次，不跨项目混写。回答待答题时先反馈，不当作新主题；提示、完整讲解、直接答案按用户意图处理，不固定检查间隔。

## Planning Only: --plan

1. 有材料时优先 `--material`，否则当前已选材料；轻量索引、先展示已验证地图与待补。复用已有核验，扫描/OCR 不全标 partial，不造章节、页码、题号；PDF 页序和印刷页码分开。
2. 无材料时按主题单元规划，不创建虚假 `MATERIAL_INDEX.md`；不用通用知识树冒充教材目录。
3. 复用目标/基础/已学范围，仅补问影响本次规划的缺项；基础未知标待确认，用户要求草案时直接注明默认值。每天时长、截止日期不是前提。
4. 按 `references/learning-path-design.md` 和 `.cursor/templates/LEARNING_PATH.md.example` 写 `LEARNING_PATH.md`。有教材每单元关联真实章节、重点问题、已核验练习或待核说明、完成标准、依赖证据；无教材明确标主题建议、自拟检查任务和推荐顺序。
5. 保存用户已提供的条件，保留个人原文、历史和已确认位置；不预填学习/练习记录。交付路线及必要路径后停止，不自动开课、生成全书笔记/PDF或排日历。

## Tutoring and Automatic Notes

- 围绕当前任务使用必要材料，或直接通用辅导。概览/完整讲解不强制缩成一道题；用户要提示时先给提示，未作答不当作失败或通过。
- 实际知识增量在**本轮回复结束前**自动保存 `notes/summaries/<教材或主题>/<稳定单元ID>-<章节或主题名>.md`。无教材用稳定主题 ID，不伪造章号。先读原文件，保留用户原文和手改；图文组织见 `references/illustrated-notes.md`，参考 `.cursor/templates/CHAPTER_NOTE.md.example`。
- 短内容文字表达，复杂结构用真实 `notes/assets/<主题>/` SVG/PNG 与可编辑源、相对图链、标题、alt、图注及来源/示意说明；只有 Mermaid 代码不算可见成图。
- 按 `references/learning-records.md` 保存 `LEARNING_RECORD.md` 原文、实际活动、待答题、真实作答/反馈和下一步；助手摘要链接主笔记。未作答/未评估保持原状，不把讲解当掌握，不猜时长。
- 普通教学静默保存并核验，不逐轮列路径；首次建档、阶段总结、明确记录及导出时反馈。失败立即说明；同一增量不重复写。闪卡仅按需，不在每次结束自动生成。

## PDF Export

只转换已有笔记时直接运行 `python scripts/export-notes.py INPUT.md --output OUTPUT.pdf`，跳过教学、条件补问和记录写入。按 `references/illustrated-notes.md` 检查图链、实际 PDF 中文/图片/版面，保留 MD/图源，个人 `LEARNING_RECORD.md` 不默认导出。已有 PDF 默认保留，明确同意才加导出器 `--force`，字体可用 `--font FONT_PATH`。

`--plan --export pdf` 不触发全书笔记；说明当前只规划，待选择已有学习笔记后转换。材料事实、通用讲解、自拟例子与真正待核实内容遵循 `references/source-grounding.md`；NOTEBOOKLM_ENGINE 关闭仍可完整使用基础流程。
