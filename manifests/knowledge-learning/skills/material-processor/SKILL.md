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
5. 向用户展示教材地图，再按 `references/learning-path-design.md` 进入 `/learn --plan`：仅补问缺失的目标、基础、已学章节，交给 curriculum-designer 生成章节路线，不排日课表。

用户只要求归档时，交付索引后停止。重复导入复用已验证结果，仅补查变化部分。

## 按需详细提取

| 载体 | 当前单元的提取内容 | 来源 |
|------|----------------------|------|
| PPT | 相关页标题、要点、speaker notes、图表/公式 | `[Source: 文件名, P#]` |
| PDF/EPUB | 选定章/节定义、推导、示例、已核验练习 | 已核验页序/印刷页码或章/节标题 |
| Video/Audio | 所选片段字幕/转录，话题分段，必要画面 | `[Source: 文件名, HH:MM:SS]` |
| Web | 相关正文、标题层级、代码块和表格 | 原 URL 与已核验标题/段落 |
| Image | 相关文字 OCR 和图表内容 | 文件名，OCR 存疑单独标注 |

一条笔记只含一个核心概念；按概念组织，不机械地把每页变成一条笔记。原件保留在 `materials/`，笔记写入 `notes/atoms/`。教材事实、用户提供的信息与助手建议分别标识，详见 `references/source-grounding.md`。
