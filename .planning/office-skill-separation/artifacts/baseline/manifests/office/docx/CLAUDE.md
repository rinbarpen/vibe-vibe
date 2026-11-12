# DOCX：可编辑 Word 文档

图片/绘图先读 `.agents/skills/omnidraw/SKILL.md`，任何表格的数据/模型/布局先读 `.agents/skills/omnisheet/SKILL.md`，再进入 DOCX 文件工程。先读 `office/rules/quality.md`、`office/rules/file-safety.md`、`office/rules/docx.md` 和 `.agents/skills/anthropics-skills-docx/SKILL.md`。本指南路径相对安装后的项目根目录；源文件存放于 manifest 的 `docx/` 中。正文写作或润色再加载 `.agents/skills/ai-vibe-writing/SKILL.md`；该层不替代 DOCX 文件工程。

## 正文写作层

正文能力来自 [AI Vibe Writing Skills](https://github.com/donghuixin/AI-Vibe-Writing-Skills)。先按用户本次范围进入，而非启动全部 18 个写作角色：

- 新建正文、实质润色：需要结构时用 Outline Manager / Workflow Coordinator，章节起草用 Content Writer，现有句段精炼用 Writer；Content Review 核对内容与证据，句间推理或衔接存在问题时再用 Sentence Flow。
- 仅语法、拼写和标点：只走 Grammar Checker 最小纠错，保留原意、语气和格式，不自动扩成通篇重写、学术预审或投稿流程。
- 文风迁移不是仅保留原语气：使用上游 `1_style_extractor.md` 主动学习用户指定样文/参考，提炼语气、语域、节奏、词汇、论证顺序、意象和体裁，在当前项目 `.ai_context/style_profile.md` 留来源与正反例；Writer 与审阅者据此对照修订。区分用户确认偏好与样本推断，事实、术语、数字和引用仍按来源核对。
- skill 内的 `.ai_context/` 存放上游提示词/模板；本任务的规范、大纲、样文分析、错误与记忆实例位于用户项目 `.ai_context/` 或项目已有位置。保持已安装 skill 只读，不向其写稿件或任务记忆。

图文共同规划：`office-writer` 负责文字与主张，`office-visuals` 经 Omnidraw 准备真实图片/绘图及编辑源，经 Omnisheet 准备表格数据/模型/布局，按“主张 → 数据/来源 → 视觉类型 → 题注/替代文本/交叉引用”交接；真正的 Word 表格、原生或嵌入图表由 DOCX 工程师依目标应用写入，表格不转图片，不为普通文档表格强制另建 XLSX；不按某个库的限制统一转图，也不强制装饰。完整流程见 [voice-and-visuals.md](references/voice-and-visuals.md)，任务模板见 [content-brief.md](templates/content-brief.md)。

正文与视觉素材就绪后由唯一 DOCX 写入者装配/编辑文件，并继续全部结构、内容、全页渲染和独立 QA 门禁。文本审阅不等于版面通过，写作层内部审查不替代最终文件的 `office-qa`。

## 图题、表题与同页

默认图的小标题/题注在图下且图题同页，表题在表上且整表与表题同页；这里“小标题”是题注，不是文档 Heading。按 [native-formatting.md](references/native-formatting.md) 落实段落/行约束并实际渲染核验，超页不静默拆表、裁切或缩成难读内容；跨页表仅按用户/模板明确约定采用。

## 公式、编号与引用

涉及公式或图/表/公式引用时读 [equations-and-fields.md](references/equations-and-fields.md)：保留 LaTeX/Markdown 数学源和稳定 ID，交付可编辑 OMML；用独立 SEQ 序列及书签/REF/PAGEREF 管理动态编号，公式编号位于右侧。插入/删除/移动后按“先 SEQ、再 REF/分页域”的两轮依赖顺序实际更新，复用现有标签/章编号并保护第三方文献域；缺转换或应用更新证据时保持 `pending`。

## 制作与保护

- 明确文档用途、读者、语言、页数、模板、目录与引用要求；优先复用已有模板的样式和节设置。普通文档不继承专利规范。
- 先按需求选 Word/VBA/模板、LibreOffice UNO、OOXML 或格式库的实际能力，允许使用原生样式/主题、多级编号、节、TOC/SEQ/REF、书签、题注、内容控件、批注/修订、OLE/SmartArt 和宏。库接口缺口不是禁用原生功能的理由，详见 [native-formatting.md](references/native-formatting.md)。新建时按上游 skill 选择合适的原生文档引擎。编辑先记录输入哈希并制作副本，盘点页眉页脚、目录、编号、批注、修订、域、图片关系和嵌入对象；选用能保留所需特性的编辑方式。
- 将适用要求落实为原生约束并审计：标题字体/KeepWithNext 用样式，多级编号用列表定义，图题/表题整表同页用段落链和行属性，题注与引用用域；续页表头仅在已明确采用跨页表时设置；固定模板标题或用户指定编辑区可用内容控件锁定/限制编辑。仅按用户范围启用保护，不默认锁整篇或设密码，不将保护视为加密保证。
- 使用真正的标题样式、列表编号、表格与分页，不用空格/反复换行模拟布局。保持中文字体、东亚字体映射、段前后距及行距一致。
- 只改需求范围内的内容；若库的重新保存可能移除原有特性，先选择保留该特性的路径，或明确待解决项。不要把多页内容变成整页图片。

## 验收与交接

1. 用 `python3 office/docx/scripts/feature_audit.py FILE --output REPORT.json` 取得只读原生特性清单；有明确约束时加 `--expect CONSTRAINTS.json` 核对原生属性，结合需求矩阵检查实际对象/行为；它不执行宏，也不替代实际目标应用验证。重新打开输出，核对章节、段落/表格、标题层级、编号连续性、页眉页脚、节/页码、目录/域和链接。对编辑任务比较未修改内容及需保留的文档特性。
2. 用 `python3 office/scripts/verify.py FILE --output REPORT.json` 取得结构记录，再用 `python3 office/scripts/render.py FILE --out-dir PREVIEW_DIR` 生成全页 PDF/PNG；每个修订用新的或空的预览目录，保留 `render.json`。命令中的路径须换成本任务实际文件并保留原始输出/退出码。
3. 阅读全部页面：标题不孤立，表格不截断，图片/文字无溢出，目录和页码对应，中文无缺字/替换，图表与正文对应、题注/替代文本/交叉引用准确，引用与数据有来源。导出时需要更新的目录/域，先更新再渲染核对。
4. 将最终 DOCX、内容及结构记录、全页预览、输入/最终哈希交给独立 `office-qa`。修复后重新验证；尚无全页或独立审查证据时保持 `pending`。

细化清单见 `office-quality` 的 `references/docx.md`，交接与交付使用其 `references/delivery.md`。

## 原生排版入口

```bash
# 输入为已留源哈希的工作副本，另存输出；Linux 运行 LibreOffice UNO，不运行 Word VBA
python3 office/docx/scripts/native_format.py --engine libreoffice \
  --input "working/report.docx" --output "deliverables/report.docx" \
  --report "evidence/report-native-format.json"
```

该入口只在需要统一排版时运行，已有模板保留任务不强制使用；可选 `--profile PROFILE.json` 依据 brief 覆盖排版示例设置。输出/报告均用新的路径；若往返保真检查发现 Word 特性损失，保留工作副本与失败证据，转由能保留该特性的引擎处理。Word 可显式导入 `office/docx/macros/OfficeLayout.bas`，也可由 `.dotm` 模板中的宏排版 `.docx`。需在交付件保留宏时使用 `.docm` / `.dotm` 并记录宏内容；文档带宏不代表自动运行。分别记录本机 UNO 实际执行、VBA 静态检查与目标 Word 中的真实测试，按引擎保真能力核对字段/控件/嵌入对象。

## 按需路径

用户明确请求专利时再读 `office/docx/rules/patent.md`，核对当前适用规则与资料来源。`docx-polar` 仅在用户明确选择且当前项目已配置时按其实际技能操作；不依赖个人目录或预设 `office-cli` 命令。
