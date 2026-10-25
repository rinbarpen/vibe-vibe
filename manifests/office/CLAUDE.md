# Office：质量优先的办公文档工作区

处理 DOCX、XLSX、PPTX、PDF；CSV 用于表格交换。支持按样文主动学习/迁移文风、正文与图表共同创作，以及 Word 原生排版、模板和宏。默认交付原生可编辑文件及可审阅的验证证据，按需求选择能力而非以某个库的限制替代应用能力。

## 开始前加载

本入口安装在项目根目录；下述路径均相对项目根目录。若已有入口被保留，请从 `office/README.md` 接入本工作流。

1. 读取 `office/rules/quality.md`、`office/rules/file-safety.md`。
2. 图片/配图/示意图/数据绘图先加载 `.agents/skills/omnidraw/SKILL.md`（matplotlib 也从该入口路由）；所有表格/工作簿的数据、模型与布局先加载 `.agents/skills/omnisheet/SKILL.md`，再进入底层格式引擎。原生表格/图表仍由最终格式工程师写入，不转成图片。
3. 加载 `.agents/skills/office-quality/SKILL.md`；按本次格式加载对应指南、共享规则与文档 skill：

| 格式 | 指南 | 规则 | Skill |
|---|---|---|---|
| DOCX | `office/docx/CLAUDE.md` | `office/rules/docx.md` | `.agents/skills/anthropics-skills-docx/SKILL.md` |
| XLSX / CSV | `office/xlsx/CLAUDE.md` | `office/rules/xlsx.md` | `omnisheet` → `.agents/skills/anthropics-skills-xlsx/SKILL.md` |
| PPTX / 按需宏演示 | `office/pptx/CLAUDE.md` | `office/rules/pptx.md` | `omnippt` → `.agents/skills/anthropics-skills-pptx/SKILL.md` |
| PDF | `office/pdf/CLAUDE.md` | `office/rules/pdf.md` | `.agents/skills/anthropics-skills-pdf/SKILL.md` |

DOCX 的正文/文风任务另加载 `.agents/skills/ai-vibe-writing/SKILL.md` 与 `office/docx/references/voice-and-visuals.md`；原生排版或约束实现读 `office/docx/references/native-formatting.md`。

Word 公式或图/表/公式动态引用读 `office/docx/references/equations-and-fields.md`，由 LaTeX 源转可编辑 OMML、原生域管理编号/引用，并以实际应用更新结果验收。

Word 默认图下题注且图题同页、表上题注且题注与整表同页；按 `office/docx/references/native-formatting.md` 实现并渲染验收，超页不得静默拆分，跨页表仅依明确约定。

Excel 分别交互确认新增图表与宏使用，已有明确答复直接复用；未答继续非图表/非宏工作且未决范围 pending，宏按需制作/保留/明确调用，见 `office/xlsx/references/charts-and-macros.md`。

PPT 先加载 `.agents/skills/omnippt/SKILL.md`，按需经过 brief/研究 → 可调整大纲 → 朴素分镜 → 视觉语言 → 原生构建 → 独立逐页审查；已有模板的小改复用现有结构，不强制重做研究或六阶段。图片经 Omnidraw、表格/数据经 Omnisheet，最终演示仅 `office-pptx` 写入。新增数据图表与宏使用分别 yes/no/pending，复用本次明确答复；未答不擅加图或执行宏。具体原生/SVG与宏格式边界见 `office/pptx/CLAUDE.md`。

缺少 skill 时报告缺失项，先核对安装结果，不假定存在外部工具或仓库路径。

## 执行与交付

确认受众、用途、输出格式、模板、文风样本、图文计划与数据来源 → 只读检查依赖和输入 → 副本制作 → 结构与内容校验 → 重算及全页渲染 → 独立 QA → 交付文件、预览与报告。复杂或跨格式任务使用 `office/planning/CLAUDE.md` 的持久化规划；简单任务直接执行，但保留质量门禁。

- 主 agent 负责需求、调度和最终交付，八个角色见根目录 `AGENTS.md`；正文由 `office-writer`、图表/素材由 `office-visuals` 按各自中间文件协作，格式角色整合；同一文件只有一位制作角色写入。
- 新建或编辑文件必须由 `office-qa` 独立审查。只读提取免除此步骤，但注明来源、页码/单元格和提取限制。
- 原生能力用于实现适用要求：样式/主题、多级编号、分节、目录/题注/交叉引用域、内容控件、修订批注、图表/OLE/SmartArt、VBA/UNO 均可按需求选用。把“要求 → 原生对象/属性 → 审计与版面证据”落到产物；限制编辑只按用户指定范围启用，不默认锁定整篇。
- `verify.py` 仅提供结构证据；成功退出不等于内容、视觉或独立 QA 通过。渲染生成预览也不等于已看过每页。
- 缺少重算、渲染、字体或独立审查条件时保留 `pending` 待验收产物，明确未完成项；修复后重新验证最终文件。
- 编辑基于副本并记录源哈希；仅在用户要求时覆盖原件，并保留备份。不自动建分支、提交、安装系统依赖或修改全局配置。

## 本地辅助命令

以下命令从已安装的项目根目录执行；先检查依赖，再选择本次任务需要的命令。

```bash
python3 office/scripts/doctor.py
python3 office/scripts/verify.py "deliverables/report.docx" --output "evidence/report-structure.json"
python3 office/scripts/render.py "deliverables/report.docx" --out-dir "evidence/report-preview"
```

`doctor.py` 是依赖清单；只把本次选定路径实际需要的缺失项当作前置阻断。`render.py` 的输出目录须为新建或空目录，每次修订用独立目录保留证据。结构记录、业务核对和人工/独立视觉审阅共同组成验收证据；格式转换存在语义和版式损失风险，转换后重新验收。
