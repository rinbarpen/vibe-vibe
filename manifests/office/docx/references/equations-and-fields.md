# DOCX：LaTeX 公式源、原生数学与动态域

适用于带数学公式、图/表/公式编号或交叉引用的 Word 文档。LaTeX 负责管理数学源，OMML 负责最终 Word 可编辑数学；SEQ/REF/PAGEREF 负责显示编号与引用。这三者分工独立，不把公式截图、手填编号或写入旧缓存当作完成。

## 1. 保留源与稳定 ID

- 在用户项目保留可编辑 `.tex` 或 Markdown 数学源及版本/哈希，记录每条公式的内容、符号/单位、行内/展示方式和来源。不要只把 LaTeX 文本塞进 Word 普通段落而声称已转换。
- 使用与显示编号无关的稳定 ID，例如 `eq_energy`、`fig_trend`、`tbl_summary`；保留“逻辑 ID → 源位置 → Word 书签 → 序列/显示位置 → 引用位置”的映射。插入、移动后 ID 不随新显示号改变。
- Word 书签名遵循应用限制并保持唯一；复杂外部 ID 映射为合法书签名，不擅改现有模板/插件生成的书签。复制对象需生成新 ID，移动对象保留原 ID。

## 2. LaTeX → 可编辑 OMML

从有证据支持的转换器或 Word 数学输入路径产生原生数学对象，保留源与转换记录。交付件检查 `m:oMath` / `m:oMathPara` 的实际结构，并在应用中核验公式仍可编辑、分式/根号/上下标/矩阵/积分等语义与源一致。原生 OMML 的 `m:oMath` 对象见 [Microsoft Open XML OfficeMath](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.math.officemath?view=openxml-3.0.1)。

Word 提供 [LaTeX / UnicodeMath 线性输入](https://support.microsoft.com/en-us/office/linear-format-equations-using-unicodemath-and-latex-in-word-2e00618d-b1fd-49d8-8cb4-8d17f25754f8)；具体命令支持随输入模式/版本而异，不假定完整 TeX 宏包都被支持。[OMaths.Add](https://learn.microsoft.com/en-us/office/vba/api/word.omaths.add) 与 [OMath.BuildUp](https://learn.microsoft.com/en-us/office/vba/api/word.omath.buildup) 可建立/排版数学对象，但单独调用 BuildUp 不是任意 LaTeX 已正确解析的证明。

本项目的 Python helper 选用 Pandoc 转换数学；[Pandoc 数学输出文档](https://pandoc.org/MANUAL.html#math) 明确 DOCX 使用 OMML。该路径将警告视为失败并检查数学结构，仍需逐式比对语义和渲染；Pandoc 缺失只影响选用这条路径，不泛化为 Word 数学输入路线也不可用。

- 保留数学含义、符号、运算次序、对齐与文字注释；不为了某个转换器成功而静默改写表达式。
- 遇到不支持语法/宏或转换条件缺失，保留源并列出具体待转换项，状态 `pending`。不静默栅格化为 PNG/SVG，不以普通文本或图片冒充 Word 原生数学。
- 展示公式居中或沿用模板对齐，编号在公式右侧，使用原生制表位/模板布局定位，不用空格凑位置。编号为域结果，不写死 `(1)`、`(2)`；跨行公式的括号、编号归属和分页按模板核对。

**已知本机兼容性：** 在 LibreOffice 7.3.7.2 的本轮往返实测中，`\bar{x}` 的横线 `‾` 被改为 `´`，嵌套求和 `σ² = (1/n) Σ(xᵢ−μ)²` 丢失子表达式；数学保真 guard 均已拦截，保留输入及原生 OMML 草稿。同一路径的基础式 `E=mc²` 和 `μ=(1/n)Σxᵢ` 已实测成功。上述限制仅针对该版本和已测表达式，不据此禁用 UNO 或所有公式；受影响公式应交由能保留其结构的 Word 或其他实际验证的引擎处理，保持 `pending` 直至通过验收，不为通过检查静默改公式。本机结果不表示已在 Word 执行。

## 3. 图、表、公式独立自动序列

新文档分别使用 `SEQ Figure`、`SEQ Table`、`SEQ Equation`，三个序列独立递增；复用模板现有中文标签、序列名和章编号方案，不混用“图”/“Figure”等名字产生平行计数，也不默认每章或每节重置。`\r` / `\s` 等重启仅在模板/用户已要求时沿用。SEQ 的更新与重启开关见 [Microsoft SEQ 字段](https://support.microsoft.com/en-us/office/field-codes-seq-sequence-field-062a387b-dfc9-4ef8-8235-29ee113d59be)。

下面仅展示**域代码语义**；花括号必须是真正的 Word 域，不是正文手打的字符：

```text
图 { SEQ Figure \* ARABIC }：说明性题注
表 { SEQ Table \* ARABIC }：说明性题注
公式右侧：({ SEQ Equation \* ARABIC })
正文引用：式 ({ REF eq_energy \h })，见第 { PAGEREF eq_energy \h } 页
```

`eq_energy` 等书签包住要引用的动态编号范围，而不是整条公式或整段题注；有章前缀时覆盖约定的完整编号。图/表书签同理。显示标签、括号与引用文字沿用模板；源中的稳定 ID 不等于显示号。序列域按文档实际顺序计算，不以插入时算一次再硬填的数值替代动态结果。

## 4. 交叉引用与书签生命周期

[REF](https://support.microsoft.com/en-us/office/field-codes-ref-field-b2531c23-05d6-4e3b-b54f-aee24447ceb2) 引用书签内容，[PAGEREF](https://support.microsoft.com/en-us/office/field-codes-pageref-field-bbda448f-7233-4aaa-b061-55ca4664c4d7) 引用书签所在页；二者须指向当前文档存在且范围正确的目标，按需启用超链接。

- 新增对象：创建唯一稳定 ID/书签、对应 SEQ 与引用映射；正文可在对象之前引用，但编号缓存不是最终结果。
- 移动对象：连同域和书签一起移动，保留 ID 并重新计算显示号/页码；避免复制后留下重复书签或引用指向旧位置。
- 编辑书签边界后检查其范围，防止新增内容被意外纳入引用；此类边界变化见 [Microsoft 交叉引用说明](https://support.microsoft.com/en-us/office/create-a-cross-reference-300b208c-e45a-487a-880b-a02767d9774b)。
- 删除对象：先查其所有引用，按需求删引用、改指正确目标或明确待修复；不留下失效 REF/PAGEREF，不把失效提示替换成旧硬编码号掩盖问题。

## 5. 两轮应用更新与核验

对本次管理的图/表/公式编号、交叉引用和分页域执行依赖顺序更新，特别覆盖“正文先引用、目标在后”的情形：

1. **第一轮：编号目标。** 在实际应用中更新 SEQ 及适用的章前缀/题注编号，确认目标书签仍覆盖正确的新编号。
2. **第二轮：引用与分页。** 再更新 REF，重新分页后更新 PAGEREF/PAGE/目录等受影响域；如引用长度改变分页，再分页并更新至显示稳定，记录实际轮次/范围。
3. 插入、删除或移动任何图/表/公式后重复以上过程，保存并重新打开最终文件，核对三个序列及所有受影响引用的**显示结果**，再渲染全部页面检查公式、右侧编号、题注和跳转目标。

只写域代码、设置 `updateFields` / dirty 标志、手填缓存或调用一次“更新全部域”都不证明上述结果已核验。`Document.Fields` 的更新范围不自动涵盖所有页眉页脚/文本框等故事区；按本任务实际使用范围核对。Microsoft 的 [Fields.Update](https://learn.microsoft.com/en-us/office/vba/api/word.fields.update) 文档说明更新域结果，API 成功仍需结果与版面证据。缺少实际应用更新或可编辑数学转换时保持 `pending`。

## 6. 不混淆交叉引用与文献引用

图/表/公式的 SEQ + REF/PAGEREF 不是文献管理。Word [CITATION](https://support.microsoft.com/en-us/office/field-codes-citation-field-18b0c6a3-c0e6-4f76-a541-478f389b287d) / [BIBLIOGRAPHY](https://support.microsoft.com/en-us/office/field-codes-bibliography-field-cbb17838-05d7-4533-8066-4791aeddb9de) 以及现有 Zotero 等第三方字段沿用其原管理器、来源键和更新方式；不擅自改写、解链或将其替换为 SEQ。编号更新限定本次管理的域，不顺带接管第三方文献字段；用户要求修改文献时再走对应管理流程。

## 7. 已安装的复用 API

从项目的 `office/docx/scripts/equations.py` 导入，处理格式工程师持有的 python-docx `Document` 工作副本。LaTeX 源由调用者留存，不由转换函数替代源管理。`latex` 参数是单个数学片段，不带文档前导/文件命令或外层数学定界符；示例 `.tex` 文件只存该公式片段。

| API | 用途与结果 |
|---|---|
| `latex_to_omml(latex, display=True, *, pandoc=None, timeout=30)` | 返回 `m:oMathPara` / `m:oMath`，不修改源文本 |
| `add_seq_field(paragraph, sequence, bookmark=None, *, cached_text=None)` | 创建真实 SEQ，返回书签名；新 helper 支持 Figure/Table/Equation，既有模板字段沿用原体系 |
| `add_ref_field(paragraph, bookmark, *, cached_text=None, allow_missing=False)` | 创建 REF；前置引用暂用 `allow_missing=True`，装配结束必须检查全部目标 |
| `add_caption(document, sequence, text, *, bookmark=None, label=None)` | 题注段与书签；中文显示标签与序列 ID 分开 |
| `add_numbered_equation(document, latex, *, bookmark=None, pandoc=None, timeout=30)` | 原生 OMML + 右侧 SEQ Equation，返回版式表/书签/源及 `pending` 状态 |
| `validate_references(document)` | 校验目标/引用结构，`quality_status` 仍为 `pending`，不模拟应用显示更新 |

示例只演示工作副本装配；实际源和输出路径按本任务填写，新建 ID 不与已有目标重复：

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path("office/docx/scripts").resolve()))
from docx import Document
from equations import add_numbered_equation, add_ref_field, validate_references

document = Document("working/report.docx")
latex_source = Path("sources/eq_energy.tex").read_text(encoding="utf-8")
add_ref_field(document.add_paragraph("见式 "), "eq_energy", allow_missing=True)
result = add_numbered_equation(document, latex_source, bookmark="eq_energy")
reference_checks = validate_references(document)
if reference_checks["errors"]:
    raise ValueError(reference_checks["errors"])
# 结构无缺失目标后仍只保存待应用更新的工作稿。
document.save("working/report-with-equations-unupdated.docx")
```

编号 helper 的三列无边框表只是“居中公式 + 右侧编号”的排版容器，不是新增业务数据表，不为它另建 Omnisheet 工作簿。若模板需其他编号/布局方案则按原模板由格式工程师实现；helper 不自动迁移已有字段。新域默认 `?` 缓存并始终标记 dirty；保留既有全局 `w:updateFields` 原值，仅在缺少该标志、全部现存域都是 SEQ/REF/PAGEREF 且无锁定域或坏结构时新增 true 请求。存在第三方、文献、外部等其他域时不新增全局更新请求，改用显式受管应用更新。这些标志、缓存及结构校验均不代表已实际更新；`cached_text` 也仅是暂存结果。装配后继续第 5 节的实际应用更新与全页独立验收。

## 交接与 QA

writer 交付 LaTeX/Markdown 源、符号含义、稳定 ID 和引用位置；visuals/表格准备者交付图表 ID、真实数据/来源与题注；唯一 `office-docx` 写入者负责 OMML、动态编号/书签/引用及实际应用更新。QA 独立比较数学源与 OMML、序列/书签映射和更新前后显示结果，覆盖前置引用、插入/删除/移动后的自增、右侧编号、章编号和第三方字段保留。证据绑定源与最终文件哈希，包含实际转换/更新命令、输出/退出码和全页预览；结构清单不是最终质量通过。
