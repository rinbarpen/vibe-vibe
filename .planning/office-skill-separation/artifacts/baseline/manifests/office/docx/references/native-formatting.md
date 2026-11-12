# Word 原生排版、约束与宏

以需求选择能力：先判断 Word/LibreOffice 的原生对象能否表达要求，再选择 VBA、UNO、OOXML 或格式库。库接口缺口不是文档能力上限；不要先设固定图表、字体或版式禁令。下文路径相对已安装项目根目录。

## 需求 → 原生实现 → 审计证据

每个实际要求记录“目标、实现对象/属性、约束范围、实际状态、渲染结果”。原生约束应落到最终文件，不只写在提示词中；不是每个文档都必须启用所有功能。

| 需求 | 原生实现候选 | 实际验收 |
|---|---|---|
| 字体、段落层级、标题不与后文分离 | 样式/主题，标题样式的字体、段距、[KeepWithNext](https://learn.microsoft.com/en-us/office/vba/api/word.paragraphformat.keepwithnext) 等属性 | 样式及段落引用、实际属性与逐页效果 |
| 多级标题编号连续 | 标题样式关联多级列表，不手打序号 | 列表定义/层级、重启设置及显示编号 |
| 横向附表、分节页码与页眉页脚 | 节、页面设置、页眉页脚连接关系和页码域 | 节边界/方向/链接及导出页码 |
| 目录、图表编号和正文引用随编辑更新 | TOC、SEQ、REF 域、书签、题注和交叉引用 | 域代码/目标、更新结果，无失效引用 |
| 图下题注、表上题注与对象同页 | 图片段/表题 KeepWithNext、表内段落/行相邻链及 cantSplit，末端断链 | 实际渲染图题同页、表题与整表同页；仅显式跨页表使用续页表头 |
| 标题或固定条款保持，指定区域可填 | 内容控件的 [LockContents](https://learn.microsoft.com/en-us/office/vba/api/word.contentcontrol.lockcontents) / [LockContentControl](https://learn.microsoft.com/en-us/office/vba/api/word.contentcontrol.lockcontentcontrol)；需要时限定可编辑范围或 [Protect](https://learn.microsoft.com/en-us/office/vba/api/word.document.protect) | 控件 Tag/类型、锁定状态、允许区域及用户是否能完成约定编辑 |
| 审阅可追踪 | 批注、修订模式及现有修订 | 对象/作者与范围、修订状态和显示/导出要求 |
| 图表、流程和附件保持可编辑 | 原生图表/嵌入工作簿、形状/SmartArt、OLE 与内容控件 | 对象类型、数据与链接、打开/编辑能力和展示结果 |

Word 官方对象入口包括 [Styles](https://learn.microsoft.com/en-us/office/vba/api/word.document.styles)、[ListTemplate](https://learn.microsoft.com/en-us/office/vba/api/word.listtemplate) 和 [Sections](https://learn.microsoft.com/en-us/office/vba/api/word.sections)；目录由 [TablesOfContents.Add](https://learn.microsoft.com/en-us/office/vba/api/word.tablesofcontents.add) 建立，题注与引用分别可用 [InsertCaption](https://learn.microsoft.com/en-us/office/vba/api/word.range.insertcaption)、[InsertCrossReference](https://learn.microsoft.com/en-us/office/vba/api/word.range.insertcrossreference)。

- 需要收集/固定模板内容时使用 [ContentControls](https://learn.microsoft.com/en-us/office/vba/api/word.document.contentcontrols)；仅在用户要求时锁定指定内容/删除行为或启用限制编辑，不默认锁定整篇、不擅自设置密码。编辑保护是工作流约束，不是加密或防篡改保证。
- 使用 [TrackRevisions](https://learn.microsoft.com/en-us/office/vba/api/word.document.trackrevisions) 与 [Comments.Add](https://learn.microsoft.com/en-us/office/vba/api/word.comments.add) 支持实际审阅；不擅自接受/删除已有修订或批注。
- 更新目录/域后重新分页和渲染，检查正文、页眉页脚及其他适用区域，而不是只更新正文域就宣称全部完成。[Fields.Update](https://learn.microsoft.com/en-us/office/vba/api/word.fields.update) 可更新域结果，但成功返回仍需检查引用、页码和版面。

公式源、可编辑 OMML、独立 SEQ 及 REF/PAGEREF 更新的集中约定见 [equations-and-fields.md](equations-and-fields.md)。编号/书签结构存在不代表应用已更新显示结果。

## 图题、表题与同页约束

默认**图下题注、表上题注**，题注与对应对象紧邻；“图的小标题”按 Caption / 模板题注样式处理，不当作章节 Heading，也不自动纳入文档目录。原有 SEQ、书签、REF/PAGEREF 编号/引用能力保持。

- **图与下方题注：** 图片所在段落设置 KeepWithNext，连到紧随其后的题注；题注自身使用 [KeepTogether](https://learn.microsoft.com/en-us/office/vba/api/word.paragraphformat.keeptogether) 保持整段，题注末段关闭 KeepWithNext，不再把下一正文一起拖走。优先按模板选择可控的图片锚定/内嵌布局，浮动图还需核对实际锚点、环绕与显示页，属性存在不证明图片真的同页。
- **表题与整张表：** 表题段 KeepWithNext 连表，表内建立跨行/段落相邻链，所有行设置 `cantSplit`（对应 Word [AllowBreakAcrossPages=False](https://learn.microsoft.com/en-us/office/vba/api/word.row.allowbreakacrosspages)），表末端关闭相邻链以免牵连后文。`cantSplit` 只防一行拆页，不独自保证整表同页；需同时检查全表链与实际排版。
- **复用 helper：** 已安装 `office/docx/scripts/equations.py` 的 `apply_caption_layout(document, *, allow_multipage_tables=False)` 可处理真实 SEQ Figure/Table 与正文紧邻对象；`add_caption` 的结果也附带 layout 记录，表格建好后需显式调用布局 helper。Equation 和公式三列版式表不受其处理。浮图、隔段、分页或 SDT 等未可靠绑定的对象保持 `pending`，不自动移动内容；返回的 `caption_layout_applied` / `pending` 都只代表结构处理，`quality_status` 仍为 `pending`。默认不允许跨页；只有本次绑定表均明确采用跨页方案时才启用 `allow_multipage_tables=True`，部分表的例外由格式工程师按对象处理，不把整文档跨页模式套到其他表。
- **UNO 属性对应：** [ParagraphProperties](https://api.libreoffice.org/docs/idl/ref/servicecom_1_1sun_1_1star_1_1style_1_1ParagraphProperties.html) 的 `ParaKeepTogether=true` 是连到下一段，`ParaSplit=false` 才防段内拆页；[TextTable](https://api.libreoffice.org/docs/idl/ref/servicecom_1_1sun_1_1star_1_1text_1_1TextTable.html) 的 `Split=false` 用于整表防拆，`KeepTogether=true` 却是把表连到后文，不可混用。仍需按实际应用版本核对导出和排版结果。
- **实际同页验收：** 渲染最终 DOCX 全部页面，逐一记录图 ID/图片页/题注页，表 ID/表题页/首末行页，确认默认图题同页、表题与完整表格同页。只看 KeepWithNext / cantSplit 的结构结果不算通过。
- **超过单页可用区：** 先评估含题注的图/表整体高度、可用页宽/页高；在模板/本次范围允许时选择横向页、合理列宽/间距或其他可读调整，更新后重新渲染。仍超页或需拆表时保持 `pending`，列明具体选项；不静默拆页、裁切数据或压缩到不可读，也不靠省略内容“满足”同页。
- **明确的跨页例外：** 只有用户或模板明确约定跨页表时，才采用跨页布局和 [HeadingFormat 续页表头](https://learn.microsoft.com/en-us/office/vba/api/word.row.headingformat)，记录该表的例外、题注与首段/续表要求并验收。启用跨页表不再声称“整表同页”，更不自动改变其他表的默认约束。

## 运行路径与文件格式

### Word VBA / 模板

`office/docx/macros/OfficeLayout.bas` 是供 Word 导入的原生排版模块。先审阅过程和目标范围，在文档工作副本上显式调用相关过程；记录实际 Word 版本、入口和输出。该源文件在 Linux 上静态检查不等于已经在 Word 执行。

宏可以驻留 `.dotm` 模板，由它排版目标 `.docx`；目标为 `.docx` 不代表排版过程必须放弃 VBA。需要把宏保留在文档/模板中时选 `.docm` / `.dotm`，并明确交付中的宏内容。Word 的 [WdSaveFormat](https://learn.microsoft.com/en-us/office/vba/api/word.wdsaveformat) 区分普通文档、宏文档与宏模板。文件或模板包含宏不构成执行指令；打开/渲染不得顺带运行输入携带的宏，也不为自动化而调整全局宏信任设置。

### LibreOffice UNO

Linux 环境可在确需统一排版时显式选择项目提供的 UNO 工作副本入口；保留既有模板原样的任务不必运行该步骤。默认排版 profile 只是示例起点，按 brief 用可选 `--profile PROFILE.json` 指定字体/字号、表头和短行跨页设置，不把脚本默认值当成所有文档的规则：

```bash
python3 office/docx/scripts/native_format.py --engine libreoffice \
  --input "working/report.docx" --output "deliverables/report.docx" \
  --report "evidence/report-native-format.json"
python3 office/docx/scripts/feature_audit.py "deliverables/report.docx" \
  --output "evidence/report-features.json"
```

`--input` 使用已记录源哈希的工作副本，输出与报告均使用新的路径，不复用已有结果；每次修订保留独立证据。该路径操作 LibreOffice 的原生对象，不执行 Word VBA，也不自动执行输入宏。逐项确认所需样式、字段、控件、OLE/SmartArt 等特性的保留和目标 Word 兼容性；不要把 LibreOffice 成功写入解释成所有 Word 特性已验证。往返保真检查如发现 Word 专属对象、控件/字段或修订等损失，会返回失败而保留输入和证据；选择能保留该特性的实际引擎，不通过删对象绕过检查。

`feature_audit.py` 可用 `--expect CONSTRAINTS.json` 将明确要求变成可失败的验收。例如本任务确认“标题控件 Tag 为 `report-title`、内容和删除都锁定，Heading1 与后文同页，不启用全篇保护”时，约束文件可写：

```json
{
  "styles": {"Heading1": {"keep_with_next": true}},
  "content_controls": {"report-title": {"lock": "sdtContentLocked"}},
  "document_protection": {"enforced": false}
}
```

```bash
python3 office/docx/scripts/feature_audit.py "deliverables/report.docx" \
  --expect "working/native-constraints.json" --output "evidence/report-constraints.json"
```

样式 ID / 控件 Tag 以实际模板为准，只填本次约定的约束。`native_constraints_pass` 仅说明这份 JSON 声明的包内属性匹配，仍需在接收应用检查正文可编辑、控件行为、字段结果和全页显示；未声明的功能不因此被验证。

`feature_audit.py` 是只读特性清单，不更改文件、不执行宏；按需求矩阵检查样式/编号、表格约束、域/书签、内容控件与宏部件等实际状态。它与通用 `verify.py`、全页 `render.py` 及目标应用打开/编辑测试互补，不替代独立 QA。

## 原生约束验收

交付记录实际引擎/版本、修改范围、原生对象和属性、前后哈希、特性审计及渲染证据。纯 Python/OOXML 仅写了域代码时应注明未由应用更新；Linux UNO 已执行与 Word VBA 未执行分别记录。用户要求 Word 专属功能时保留原生对象并待目标 Word 验证，不为通过当前工具检查而静默扁平化、移除控件或接受所有修订。
