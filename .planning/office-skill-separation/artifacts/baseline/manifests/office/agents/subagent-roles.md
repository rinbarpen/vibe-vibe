# Office Subagent 角色与交接协议

主agent保持需求、调度及最终交付责任。以下八个角色在 `.claude/agents/` 和 `.codex/agents/` 提供原生定义，两套提示词一致。复杂写作、素材、装配和QA按实际任务分工；仅排版不启动完整写作，缺独立subagent时QA标pending。

## 共享交接

- **输入**：brief、来源/模板/作者样文、源哈希、允许改写范围、正文/风格profile/具体对比、素材计划/实际素材及数据、原生功能约束、输出路径与证据。
- **输出**：源及产物路径/哈希、真实命令/输入/字面输出/退出状态、语气与事实对比、素材/数据/题注/替代文本/插入位置、原生状态和执行证据、渲染/覆盖、QA记录及限制。
- **所有权**：writer只写文本源/风格/计划，visuals只写实际素材及源/数据，office-docx独占最终Word文件；其他格式各一个最终写入者。QA不兼任本次文本/素材/文件作者，只写审查证据。
- **状态**：交付draft/pending/passed，QA verdict独立为pass/pending/fail；只有全部门禁及QA pass才交付passed，QA pending/fail均交付pending。验收只绑定当前最终哈希。
- **覆盖**：DOCX/PPTX/PDF全部页面；XLSX全部工作表数据/公式和所有交付打印视图。检查用户实际选择的原生功能/宏/引擎，不将未选择工具的缺失泛化为限制。样式/域/内容控件/编辑范围以实际XML或应用状态证明，不默认加锁/密码。

- **入口与所有权**：图片/绘图（含 matplotlib）先走 `.agents/skills/omnidraw/SKILL.md`；所有表格数据/模型/布局及工作簿先走 `.agents/skills/omnisheet/SKILL.md`，再用底层格式 skill。保留真实来源/单位/版本，格式工程师仍拥有最终原生表格/图表与文件，不将表格转图或额外生成未请求工作簿。

- **Excel 决策**：新增图表/宏使用各自 yes/no/pending，记录本次用户确认来源；未答主动问但继续非图表/非宏工作，原图表/宏默认保留。图表规格与宏用途/入口/目标簿表范围/触发/输出按 `office/xlsx/references/charts-and-macros.md` 交接；宏源/项目保留与实际 Excel 运行分开。

## office-planner

PPT 先用 Omnippt 按需建立受众/结果、来源、稳定 ID 大纲与朴素分镜，再视觉 tokens；小改复用有效上下文。新增数据图表/宏分别确认，office-pptx 是唯一演示文件写入者。

整理受众、作者语气、内容配图、原生约束机制、制作分工和可检验验收条件。

接收需求/样文/模板/来源，输出brief、角色/路径、图文需求、约束→原生机制→验收方法，交主agent调度。

## office-writer

按作者样文形成真实语气/风格对比，起草润色正文并规划有来源的配图表，仅交付文本和源。

加载ai-vibe-writing必要上游提示词，提炼作者语气profile并交付正文源、具体风格对比、来源和带题注/引用/位置的图表计划；不写最终Word。

## office-visuals

依据正文与数据制作实际图表、示意图和表格资产，交付可编辑源、数据、题注及替代文本。

按内容用途先经 Omnidraw 准备图片/绘图，先经 Omnisheet 准备表格数据/模型/布局，交付实际来源、编辑源、数据、预览、题注/替代文本与放置说明，交对应格式唯一写入者；PPT 依据 Omnippt 分镜/tokens 交 office-pptx，不先画整页替代原生装配。新增数据图表需本次 yes，no/pending 不绕图片；不以占位或装饰数量替代真实素材。

## office-docx

装配作者正文和有来源的图表素材，使用原生 Word 功能/宏与自动化排版并验证最终文档。

加载anthropics-skills-docx，唯一装配最终Word；接收正文/语气与实际素材，使用选定原生功能、已审阅宏或应用自动化，核对编号/域/内容控件/编辑范围及全页排版后交独立QA。

## office-xlsx

制作或编辑 Excel 数据、公式、已确认图表及宏，执行适用的真实重算与关键数值核对。

先加载 Omnisheet 再加载 anthropics-skills-xlsx，完成数据/公式/原生图表、真实重算、关键数值和全部工作表/打印视图检查，交独立QA。

## office-pptx

制作原生可编辑 PPTX，处理叙事、模板与数据图表，并逐页审查全部幻灯片。

先加载 `.agents/skills/omnippt/SKILL.md`，按需六子技能，从 brief/来源到可移动大纲、朴素分镜、视觉 tokens，再由 native-build 接 anthropics-skills-pptx。独占最终演示、保留原模板/母版/主题/备注；图表/宏各自 yes/no/pending，源/包/真实 PowerPoint 执行分开。SVG 嵌入不等于逐元素编辑能力，全部最终幻灯片检查后交独立 QA。

## office-pdf

处理 PDF 读取提取、合并拆分、表单及导出验收，保留页码映射与 OCR 限制。

加载anthropics-skills-pdf，完成提取/合并拆分/表单或导出验收，记录来源页映射/OCR限制，创建修改后全页检查并交独立QA；纯只读提取例外。

## office-qa

独立核验语气、图文来源、原生功能和约束实际状态及全部页面，只写审查证据。

核对 Omnidraw 素材及 Omnisheet 表格/模型/布局的真实来源和版本；独立读取最终文件和全部预览，比较作者语气、图表来源/题注/引用、实际原生约束/执行证据及全部门禁，仅写pass/pending/fail证据；问题交原制作角色。

Word 公式/动态域按 `office/docx/references/equations-and-fields.md`：writer 交 LaTeX 源与稳定 ID，visuals 交图表 ID/题注，DOCX 唯一写入者转 OMML、管理 SEQ/书签/REF/PAGEREF 并两轮应用更新，QA 对照源与实际显示及编辑后自增；文献管理保持原体系。

PPT 按 Omnippt `deck-review` 独立检查来源/阶段版本与最终原生对象、全部页预览、数据图表/宏两个决定及实际 PowerPoint 证据；合同结构/对象计数不证明内容、视觉或执行，缺证据为 pending。

## 调度与修复

1. 主agent直接记录简单需求，复杂任务交office-planner明确语气/图文/原生约束和验收。
2. 需要写作时office-writer先产正文/风格/图表计划，office-visuals制作必要实际素材；不同源文件可并行，数据和事实统一。
3. office-docx独占最终Word装配/原生排版，其他格式由对应角色制作；完成结构、内容/语气、数值、原生状态及全部页面验证后交独立office-qa。
4. QA定位问题交writer/visuals/最终工程师修对应源，最终工程师重新装配、更新哈希和相关证据后再交审；主agent按当前哈希的QA结论交付。
