---
name: material-processor
description: 上传学习资料后建立轻量教材地图；具体章节学习时按需提取 PPT/PDF/视频/网页/音频/图片内容，所有教材事实保留真实来源。
dependencies: []
---

# 材料处理器 (Material Processor)

## 先选择处理模式

- **上传、导入或教材规划**：默认索引模式，不全量提取笔记、转录或闪卡。
- **当前章节学习或明确要求精读/详细提取**：只深入选定范围，产出 source-grounded 原子笔记。

## 索引模式

1. 识别载体并保留原件到 `materials/<type>/`；同名不同内容保持独立路径。
2. 读取元数据、目录/书签、章节标题、概览及核实结构必要的代表性页面。PPT 先目录/标题，PDF/EPUB 先目录/章标题，音视频先大纲/已有字幕，图片只对必要页 OCR；策略见 `references/carrier-types.md`。
3. 用 `.cursor/templates/MATERIAL_INDEX.md.example` 保存 `projects/<教材或主题>/MATERIAL_INDEX.md`，记录材料路径、真实章节、已核验定位、检查范围和待补项。PDF 页序与印刷页码分开，目录标注位置与已查正文位置分开。
4. 多份资料各自索引，核验后才建立章节对应。无目录或扫描件识别不全时只输出部分教材地图，不从主题名称补写章名、页码或题号。
5. 先读项目已有 `LEARNING_RECORD.md` 并按 `references/tutor-interaction.md` 路由：只上传时简要地图加一个方向问题；上传并指定任务时定位必要范围直接辅导，索引可标 partial；明确规划才按 `references/learning-path-design.md` 生成路线，归档完成即停止。不强制先做整书地图/路线。
6. 学习条件与个人记录遵循 `references/learning-records.md`，使用 `.cursor/templates/LEARNING_RECORD.md.example`。导入与索引只代表材料已处理，不标为用户已读/已练习/已掌握；重新导入和新增材料不覆盖旧日志、用户原文或确认位置。

用户只要求归档时，交付索引后停止。重复导入复用已验证结果，仅补查变化部分。

## 按需详细提取

| 载体 | 当前单元的提取内容 | 来源 |
|------|----------------------|------|
| PPT | 相关页标题、要点、speaker notes、图表/公式 | `[Source: 文件名, P#]` |
| PDF/EPUB | 选定章/节定义、推导、示例、已核验练习 | 已核验页序/印刷页码或章/节标题 |
| Video/Audio | 所选片段字幕/转录，话题分段，必要画面 | `[Source: 文件名, HH:MM:SS]` |
| Web | 相关正文、标题层级、代码块和表格 | 原 URL 与已核验标题/段落 |
| Image | 相关文字 OCR 和图表内容 | 文件名，OCR 存疑单独标注 |

原件保留在 `materials/`；具体学习自动整理 `notes/summaries/<主题>/` 的章节主笔记，必要的独立概念才写 `notes/atoms/`，每条原子笔记只含一个核心概念，不机械地把每页变成一条笔记。教材事实、用户提供的信息与助手建议分别标识，详见 `references/source-grounding.md`。用户明确提供的原文笔记/要求记住的内容与助手整理分别写入学习记录，不把材料全文提取或助手生成笔记当用户已学的证据。
