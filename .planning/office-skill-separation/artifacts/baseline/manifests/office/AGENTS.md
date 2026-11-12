# Office Agents

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

本文件用于 Codex 和 Claude Code 的办公任务。开始时显式读取 `office/rules/quality.md`、`office/rules/file-safety.md`，再读当前格式的 `office/rules/{docx,xlsx,pptx,pdf}.md` 与指南。`office/README.md` 是已有项目入口未覆盖时的稳定接入点。

## 角色与路由

| 角色 | 输入 / 职责 | 输出与技能路由 |
|---|---|---|
| `office-planner` | 受众、用途、输入、模板、文风样本、图文计划与原生约束；整理验收条件与分工 | 简单任务简明约定；复杂任务持久化计划；`office-quality` |
| `office-writer` | 样文/风格目标、来源、大纲；主动学习与迁移文风，起草/精炼正文、题注和替代文本 | 正文、用户项目风格档案、图文计划与来源；`ai-vibe-writing` + `office-quality` |
| `office-visuals` | 内容主张、数据和素材计划；图片/绘图先 Omnidraw，表格数据/模型/布局先 Omnisheet | 实际素材或结构化表格数据、编辑源、题注/替代文本与来源；`omnidraw` / `omnisheet` → 按需格式 skill |
| `office-docx` | 已确认图文、模板和原生约束；使用适合的 Word/VBA/UNO/OOXML 能力整合 | 可编辑 DOCX、原生特性/约束审计、结构/全页预览；`anthropics/skills/docx` + `office-quality` |
| `office-xlsx` | 已核对的数据、业务公式、工作簿；先 Omnisheet 确认场景/模型/布局再执行 | XLSX、关键值核对、全表公式检查和打印视图；`omnisheet` → `anthropics/skills/xlsx` + `office-quality` |
| `office-pptx` | 先 Omnippt 明确受众/目标、叙事与朴素分镜，复用模板并管理图表/宏决策 | 原生演示、构建与逐页证据；`omnippt` → `anthropics/skills/pptx` + `office-quality` |
| `office-pdf` | PDF 与操作约定；读取、提取、合并拆分、表单、导出检查 | PDF 或提取结果、页数/字段与全页预览；`anthropics/skills/pdf` + `office-quality` |
| `office-qa` | 最终产物、验收条件、输入/哈希、全部检查与预览 | 独立审查结论、问题定位和复验记录；`office-quality` + 当前格式 skill |

八个角色按任务选择，不要求每次全部启动。PPT 制作先读 `.agents/skills/omnippt/SKILL.md`，按需使用六子技能，不增加六个运行时角色。图片/数据绘图先用 `.agents/skills/omnidraw/SKILL.md`；所有表格/工作簿先用 `.agents/skills/omnisheet/SKILL.md`，再用底层格式 skill。写作层入口为 `.agents/skills/ai-vibe-writing/SKILL.md`；其他安装后的 skill 入口为 `.agents/skills/office-quality/SKILL.md` 和 `.agents/skills/anthropics-skills-{docx,xlsx,pptx,pdf}/SKILL.md`。Claude Code 角色来自 `.claude/agents/`，Codex 角色来自 `.codex/agents/`；具体运行时须支持并启用 subagents。若运行时未加载角色，使用 `office/agents/` 中对应角色说明发起独立审查；未取得独立审查证据时保持 `pending`。

## 调度契约

- 主 agent 保留需求解释、任务调度和最终交付责任；复杂或跨格式任务先读 `office/planning/CLAUDE.md`。
- Brief / 大纲把主张映射到数据/素材来源、图表形式、实际资产/可编辑源、题注/替代文本及交叉引用；无视觉必要时保留文字。原生约束记录要求、对象/属性、允许编辑范围与实际审计，不把提示词限制当成已实现的格式约束。
- 文风迁移由样本来源和当前项目 `.ai_context/style_profile.md` 驱动；写作/审阅按语气、语域、句子节奏、用词、论证顺序、意象与体裁对照，不使用检测器分数。
- 图片/绘图由 Omnidraw 路由，表格/数据模型/布局由 Omnisheet 路由。writer/planner 在计划中标明素材或表格来源、单位、版本与交接角色；QA 对照这些真实来源核验。原生 Word/PPT 表格仍由对应格式工程师插入，不转成图片，不为简单表格额外生成未请求工作簿。
- Excel 的新增图表/宏使用各有 yes/no/pending 和确认来源，未答主动询问且继续非图表/非宏工作；原图表/宏保留不等于新增/执行同意。按 `office/xlsx/references/charts-and-macros.md` 交接图表范围、宏入口/目标/触发/输出、源码/编译项目与真实 Excel 证据。
- PPT 经 Omnippt 保留 brief、来源、稳定 slide ID 大纲、朴素分镜、设计 tokens 与阶段版本；office-pptx 独占最终演示。图片/图源走 Omnidraw，表格/数据走 Omnisheet；新增数据图表与宏分别 yes/no/pending，复用本次答复，原对象/宏保留不等于新增/执行许可。PPT 宏格式、实际 PowerPoint 证据及逐页验收按 `office/pptx/CLAUDE.md`。
- Word 数学源与动态编号按 `office/docx/references/equations-and-fields.md` 交接：writer 保留 LaTeX/Markdown 和稳定 ID，visuals 提供图表 ID，docx 写入 OMML、SEQ/REF/PAGEREF 并实际更新，QA 核对显示结果；文献引用另由既有管理器维护。
- 一个文件只有一个写入者。可并行处理不同文件；跨格式内容引用同一份核对过的数据和版本，不凭各角色记忆重新估算数值。
- 交接包括输入与输出路径、源/最终哈希、保留特性、变更范围、验收条件、命令及其实际输出/退出码、预览范围与未决项。使用 `office-quality` 内的交接和交付模板。
- 每次创建或修改结束后派发独立 `office-qa`。QA 不兼任该产物制作人，不在检查中直接改文件；返回页码、工作表/单元格、幻灯片或字段定位，由制作人修复后重新提交最终版本。
- DOCX/PPTX/PDF 审阅全部页面；XLSX 检查全部工作表的数据与公式、所有约定的交付打印视图。记录实际覆盖范围，抽样结果不代表全量通过。
- `draft` 表示尚在制作；`pending` 表示验证未完成或仍有问题；仅全部适用门禁和独立审查均有证据时使用 `passed`。工具返回成功不是最终质量状态。
- 只读提取任务不要求独立 QA；说明提取边界和 OCR 不确定项，不修改输入。

## 文件与操作边界

基于副本编辑，记录源哈希并验证输入未变；覆盖仅按用户要求且留备份。保留无关样式、公式、批注、关系和内容；原生字段、内容控件、OLE/SmartArt 与宏按需使用，遇库接口缺口选择适合引擎并验证保真。宏存在不表示应执行；Word 保留宏使用 `.docm` / `.dotm`，模板宏也可处理普通 `.docx`；Excel 保留宏使用 `.xlsm` / `.xltm`；PowerPoint 保留宏使用 `.pptm` / `.potm` / `.ppsm`，普通 `.pptx` 不承载 VBA；源码、项目保留与实际编译/执行分别验收。编辑保护只按用户要求启用，不默认加锁或设置密码。发现工具可能丢失特性时在保存前说明。避免自动分支/提交、全局配置变更或系统级依赖安装。专利、`docx-polar` 和 `ppt-master` 仅在用户明确要求并确认可用时接入，不作为默认路径。
