---
description: 默认逐题交互测验，明确试卷请求或 --paper 才批量输出独立题面与答案
globs: ["materials/exercises/**/*", "notes/**/*", "projects/**/*"]
---

# /exam

```text
/exam [topic] [--difficulty easy|medium|hard|mixed] [--count 10]
/exam <topic> --format choice|fill|short|essay|mixed
/exam <topic> --knowledge "概念A,概念B"
/exam --final --count 50
/exam <topic> --paper --count 20
```

以上是助手指令参数，不是 vibe CLI 参数。`--difficulty` 默认 mixed，`--format` 默认 mixed，`--count` 默认 10 且只控制题数；`--knowledge` 限定知识点，`--final` 扩展到当前已选学习范围，不偷偷纳入全部私人项目。混合难度可参考 easy/medium/hard=3:4:3，小样本不强行百分比。

## 默认：逐题交互

先按 `references/tutor-interaction.md` 读取当前目标、笔记和 `LEARNING_RECORD.md` 实际证据，未给 topic 可沿用当前主题。无材料也可生成通用知识自拟题，不先要求上传或创建闪卡。

1. 一次只展示一道题及必要选项；作答前不展示标准答案、正确标记、解析或暗示正确项的引用，来源可以在反馈后显示。
2. 将原题、必要条件/选项、题号/总数和“待作答”保存为当前辅导状态；不预填用户答案或得分。
3. 用户实际回答后先反馈正确部分与具体差异，附可核验依据。请求提示时先给提示，请求直接答案时可以给，但记录为助手解答/用户未作答。
4. 依据真实反馈调整后续题目；答错或未答不自动记通过、跳章节。“继续”遇未答题应恢复该题而非自答后推进。明确暂停/换题保留任务引用。
5. 完成/结束时只总结实际尝试范围；已出题不算完成题数，不虚构整章掌握率。

## 试卷模式

只有明确自然语言“生成试卷/习题集并附答案”或 `--paper` 才批量写 `materials/exercises/<主题>-试卷-<已知日期>.md` 与独立答案文件。题面不含正确选项标记或解析；答案卷单独给标准答案、过程和真实来源/自拟标签。保留既有同名文件，重复生成采用不冲突文件名，用户同意才覆盖。

题型保持 choice（四选一）、fill、short、essay、mixed。覆盖检查必须有明确知识点范围和实际分母；可说明在已知范围内的覆盖情况，不硬填 ≥80% 或示例百分比。试卷生成不算用户实际练习，不预填成绩；题面和答案文件写入成功后才交付。

## 来源和记录

教材原题、依据教材自拟题、通用知识自拟题分开标识；真实教材题号/页码必须核验，不虚构干扰项出处。自拟题的干扰项可围绕合理混淆设计，不冒充教材原文。见 `references/source-grounding.md` 和 `skills/exam-generator/SKILL.md`。

实际作答/反馈与可见待答任务按 `references/learning-records.md` 保存；新讲解按 `references/illustrated-notes.md` 自动合并 Markdown，普通轮次不反复报告路径。纯查看试卷/答案不新增学习事件。
