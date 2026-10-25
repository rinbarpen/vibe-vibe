# 文风迁移与图文一体内容

需要写正文、学习指定文风或配图配表时使用。所有运行路径相对安装后的项目根目录。先加载 `.agents/skills/ai-vibe-writing/SKILL.md`，按范围读提示词；文件装配和原生版式另见 [native-formatting.md](native-formatting.md)。

## 主动学习和迁移文风

1. 将用户指定的样文、参考文章和明确偏好纳入样本清单。记录样本 ID、来源路径/URL、作者归属、版本、语言、体裁、章节和实际读取范围；作者自写、合著、编辑稿与外部参考分开，不将外部样文误称为用户习惯。
2. 调用上游 `.ai_context/prompts/1_style_extractor.md`，在用户项目的 `.ai_context/style_profile.md` 中提炼会影响本次写作的模式：语气与情绪、语域/正式度、句长与节奏、词汇与术语、论证顺序、意象/比喻、叙述视角、段落和体裁结构。区分 `author_confirmed`、`sample_inferred`、`editorial_default`，每项带来源位置、适用条件与样本支持程度。
3. 每个关键模式保留短正例、反例或“无需修改”的对照：说明为什么像、哪里不像、如何迁移；不把一次用词变成禁词或句式配额。样本冲突按体裁或语境分组；没有样本时采用用户确认的风格目标，记录尚未学习个人文风。
4. Writer / Content Writer 根据该档案写局部试段或直接修改约定范围，主动迁移有效模式，而不只是纠错。需要结构时组合 Outline Manager，衔接问题用 Sentence Flow；仅语法请求仍采用 Grammar Checker 最小修改。
5. 审阅者对照样文、档案和候选段落，按相同维度检查可定位的匹配/偏差，兼顾任务目的、事实和可读性，再由写作者修订。以例句和位置说明差异，不用 AI 检测器、作者身份概率或虚构风格分数验收。正文事实、数字和引用不从文风模仿中生成。

档案、样本摘录、任务记忆放当前用户项目，保留来源和隐私边界；上游已安装 skill 中的 `.ai_context/` 只提供提示词/模板，不写入本任务资料。完整能力与角色来源见 [AI Vibe Writing Skills](https://github.com/donghuixin/AI-Vibe-Writing-Skills)。

## 正文与图表共同规划

Brief / 大纲同时列出主张与支持它的视觉，不在全文写完后再随意补装饰。可从 [content-brief.md](../templates/content-brief.md) 复制本任务所需字段。

| 内容定位 / 主张 | 数据或素材来源 / 单位 / 版本 | 视觉目的与形式 | 制作与编辑源 | 题注 / 替代文本 / 正文交叉引用 |
|---|---|---|---|---|
| 章节与待支持结论 | 已核对表格、原图、资料页或待补来源 | 趋势图、对比表、流程图、结构图、照片或无需视觉 | 数据、脚本、图形源、嵌入对象路径与责任人 | 图表 ID、要点、来源、限制及引用位置 |

- 让图表解释关系、比较、过程或证据；无需图表的段落保持文字，不强制每页配图、固定密度或装饰元素。
- `office-writer` 负责主张、文字、题注、替代文本和引用语境；`office-visuals` 先用 `.agents/skills/omnidraw/SKILL.md` 路由图片/绘图（含 matplotlib），先用 `.agents/skills/omnisheet/SKILL.md` 路由所有表格数据/模型/布局，保留真实来源和编辑源。两者各写自己的中间文件，由唯一 `office-docx` 写入者整合文档。
- 素材必须实际存在且可定位。记录原始资源链接/本地路径、署名/使用条件和数据快照；检索到链接不等于已取得图片。生成或重绘的图注明来源方法，不冒充实测图/原始照片。
- Omnisheet 准备的表格由 DOCX 工程师插入真正的 Word 表格，不以图片代替，也不为简单表格额外生成未请求的工作簿；表头、单位、注释与数据源明确。Word 的 [Tables.Add](https://learn.microsoft.com/en-us/office/vba/api/word.tables.add) 可创建原生表对象。
- 图表需要继续编辑时，按接收应用能力使用原生图表或嵌入工作簿，并保留核对后的数据源。Word 提供 [AddChart2](https://learn.microsoft.com/en-us/office/vba/api/word.inlineshapes.addchart2) 与 [AddOLEObject](https://learn.microsoft.com/en-us/office/vba/api/word.inlineshapes.addoleobject)；不是因为某个 Python 库缺少接口就统一转成图片。流程/结构图可用原生形状或 [SmartArt](https://learn.microsoft.com/en-us/office/vba/api/word.shapes.addsmartart)，也可按交付约定使用 SVG/位图并随附可编辑图源。
- 每幅图/表使用稳定 ID、说明性题注、准确替代文本与正文引用，说明单位、统计口径和限制；题注及交叉引用优先使用原生域/书签，插入/删除图表后更新并核验编号。

图/表稳定 ID、SEQ 编号和 REF/PAGEREF 交接按 [equations-and-fields.md](equations-and-fields.md)，不由 writer/visuals 手填最终显示号。

## 验收

对照内容计划检查没有缺图、空白占位、孤立图表或无依据数据；核对图表与正文数值/结论一致、来源可追溯、图源实际可编辑。逐页检查图文关系、题注邻接、默认整表同页（明确允许跨页表时再查续页表头）、清晰度、中文字体和替代文本；独立 `office-qa` 读取样文/档案、内容计划及最终文档，不仅检查图片是否存在。
