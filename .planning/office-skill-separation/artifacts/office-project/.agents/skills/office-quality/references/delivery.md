# 交接、证据与交付报告

此模板为工作记录，按任务填写实际值；不伪造命令输出、退出码、审查覆盖或代理身份。独立审查需是另一代理/审查者，而非制作人把自己改称 QA。只读提取免独立 QA，仍需来源定位。

## 角色交接

```markdown
# Office Handoff
- Task / audience / purpose:
- Producer / receiving role:
- Inputs: path, source/version, SHA-256 recorded before editing
- Output: path, format, current SHA-256
- Allowed changes / features to preserve:
- Shared data snapshot / units / key expected values:
- Graphics via Omnidraw / tables-model-layout via Omnisheet: actual source, route, handoff and native-format owner:
- Voice samples / provenance / project style_profile / writer-review comparisons (if requested):
- Claim-to-visual plan / actual assets / editable sources / captions / alt text / cross-references:
- Native requirements -> objects/properties -> allowed edit scope -> actual audit evidence:
- Word math (if used): LaTeX/Markdown source/version/hash, OMML conversion evidence, stable IDs/bookmarks/sequence mapping, actual two-pass updates and displayed-result checks; bibliography field preservation:
- Excel decisions: chart yes/no/pending + confirmation source/scope, metrics/type/location/source range, existing-chart preservation; macro yes/no/pending + selected modes:
- Excel macros (if selected): purpose/entry/arguments, workbook/sheets/ranges/trigger/output, source vs compiled-project paths/hashes, static/preservation/actual Excel compilation-execution evidence:
- PPT design (if used): audience/outcome/mode/template/edit_scope, source/fact IDs, stable-slide-ID outline, plain storyboard element kind/box/native intent, tokens/stage revisions; Omnippt native-build and data/asset handoffs:
- PPT decisions: separate data-chart/macro yes/no/pending, real answer/scope, chart specs and existing-chart preservation; macro source vs pptm/potm/ppsm package vs actual PowerPoint compilation/invocation, entry/arguments/target/trigger/results:
- Acceptance criteria / declared print views:
- Evidence: structural/content/recalculation/preview paths and coverage
- Checks actually run: command, inputs, literal output, exit status
- Open issues / compatibility / next action:
```

QA 的独立结论可使用 `pass` / `pending` / `fail`：`fail` 或 `pending` 均映射为交付状态 `pending`；仅当前最终版本的全部适用门禁和独立 QA 均满足时，交付状态才能为 `passed`。

QA 基于最终文件和以上原始证据复核，不只读制作人的通过摘要。问题定位到页码、幻灯片、工作表/单元格、字段或对象；返回严重程度、实际现象、预期和复验要求，不直接修改产物。

## 最终交付报告

```markdown
# Office Delivery
- Status: draft | pending | passed
- Task / acceptance criteria:
- Deliverables: native editable file(s), optional exported PDF/CSV
- Inputs: source path, initial SHA-256, final source SHA-256 (unchanged?)
- Final artifacts: path, SHA-256, change summary, preserved features

## Verification record
| Gate | Actual command / method | Inputs | Evidence / literal output | Exit status / result |
|---|---|---|---|---|
| Reopen / structure | | | | |
| Content / source / key values | | | | |
| Recalculation (if applicable) | | | | |
| Excel chart decision / chart scope and preservation (if applicable) | | | | |
| Excel macro decision / source, preservation or actual execution (as selected) | | | | |
| PPT design lineage / final native objects / chart and macro decisions (if applicable) | | | | |
| Voice / claim-to-visual consistency (if applicable) | | | | |
| Native features / constraints / target-application behavior (if applicable) | | | | |
| Rendering / visual review | | | | |

## Coverage and independent QA
- Preview files and final artifact SHA-256 they describe:
- DOCX/PPTX/PDF: total pages, pages reviewed, issue locations
- XLSX: all sheets checked, formula/error results, declared print views reviewed
- Reviewer identity / independent session or review reference:
- QA conclusion, evidence, unresolved items:
- Repair and recheck history for final artifact:

## Delivery and restoration
- What changed / what stayed unchanged:
- Engine/version, macros present or executed, native protection/editable-area scope:
- Actual LibreOffice/Word/Excel/PowerPoint runs vs static VBA/OOXML checks; source/static, macro-package preservation and actual compilation/execution stated separately; SVG embedded vs target-application converted shape evidence:
- Remaining limits and next acceptance action:
- Backup and restore instructions if original was explicitly replaced:
```

不适用的门禁写明理由，不留空冒充通过。自动工具与视觉/内容审阅分开记录：重新打开仅说明可读，渲染仅说明生成预览，公式缓存仅说明存在结果；关键值需要对照预期，全部视觉页需要实际查看。

## 状态决策

- `draft`：仍在制作，尚未提交验收。
- `pending`：已具产物但有失败、未覆盖页面、缺依赖/字体/重算或独立 QA 证据，列出具体下一步。Excel/PPT 新增数据图表或宏采用尚待用户答复，或本次要求的宏执行/保真尚未实测时，分别列出未决范围；已明确 no 的能力按未选用记录，不当作失败。
- `passed`：当前最终哈希对应的全部适用门禁均有证据，独立 QA 确认且没有阻断项。不得因为工具退出 0、抽样成功或交付时间到了而升级。

原文件默认未变，恢复只需继续使用原文件。用户明确要求覆盖时，报告提供备份绝对路径和恢复到原路径的实际命令；记录原始与恢复哈希，不自动提交 Git 或替用户删除备份。
