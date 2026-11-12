# Excel：数据、图表与宏一起验收

先读 `.agents/skills/omnisheet/SKILL.md`，按场景确认数据口径、模型、公式与布局，再读 `office/rules/quality.md`、`office/rules/file-safety.md`、`office/rules/xlsx.md` 和 `.agents/skills/anthropics-skills-xlsx/SKILL.md`。命令均从安装后的项目根目录执行。

## 图表与宏先交互确认

分别记录 `chart_decision` / `macro_decision`（`yes` / `no` / `pending`）及本次范围的用户确认来源；未明确时主动询问，可一次问完。用户已明确要/不要就复用，不重复问，也不把沉默或场景推荐当同意。未答先完成非图表/非宏工作，未决范围保持 `pending`；既有图表和宏默认保留，存在不等于新增/执行许可。图表 yes 后记录指标、类型、位置及源范围，原生图表由 XLSX 工程师维护，图片图经 Omnidraw；no/pending 不用图片绕过确认。

宏是可选的一等能力，支持 `.bas` / `.cls` 源、`.xlsm` 工作簿与 `.xltm` 模板的制作、保留、明确调用和验证。调用前确认用途、入口、目标簿/表/范围、触发及输出；已明确的本次任务范围直接复用。打开输入不自动运行宏，不改全局信任；`.xlsx` 不承载 VBA，`keep_vba=True` 仅保留而非执行或全面保真。详见 `office/xlsx/references/charts-and-macros.md`，可复制 `office/xlsx/templates/workbook-brief.md`。

## 制作选择

表格/工作簿统一由 Omnisheet 路由至适用场景，底层 XLSX skill 负责实际文件读写、公式、重算与验收。若需要输出图片形式的数据图，由 Omnidraw 路由（含 matplotlib）；工作簿原生图表仍由 XLSX 工程师维护，同一数据版本共享。

- 新建复杂格式/图表可用 XlsxWriter；编辑可用 openpyxl；分析可用 pandas。已有透视表、外部连接、宏、嵌入对象或特殊图表时先验证工具保真能力，避免常规加载保存丢失特性。
- 区分原始数据、假设和计算结果：原始输入保留值、来源和单位；派生计算使用公式，不把公式输出硬编码为最终值。CSV 不保留公式、样式或多工作表，作为交换件单独说明损失。
- 基于副本操作并记录输入哈希。公式编辑使用 `data_only=False`；`data_only=True` 仅用于读重算缓存，绝不保存该工作簿。
- 确认全部工作表、隐藏数据、命名区域、引用、图表源、日期/货币/百分比格式、打印区域和分页设置。中文或带空格的工作表引用需要正确引用名称，如 `'销售 数据'!A1`。

## 重算与验证

下列重算及通用渲染命令仅用于非宏 `.xlsx`。`.xlsm` / `.xltm` 不走 LibreOffice 转 `.xlsx` 的路径，选择实际 Excel 保真重算、运行与预览；缺所需环境时保留宏副本和 `pending`，不宣称当前脚本已经执行宏。

```bash
# 以下 FILE 为工作副本；保存制作前的输入哈希
bash office/xlsx/scripts/recalc.sh "deliverables/model.xlsx" 60
# 可选：保存至另一路径，并保留独立的重算报告
python3 office/xlsx/scripts/recalc.py "deliverables/model.xlsx" 60 --output "deliverables/model-recalculated.xlsx" --report "evidence/model-recalc.json"
python3 office/scripts/verify.py "deliverables/model.xlsx" --output "evidence/model-structure.json"
python3 office/scripts/render.py "deliverables/model.xlsx" --out-dir "evidence/model-preview"
```

- 上述两种重算入口二选一；默认更新工作副本，指定 `--output` 时后续校验/渲染须指向实际重算输出，而非旧文件。按所选环境也可用 `uv run --script office/xlsx/scripts/recalc.py` 自动准备脚本声明的依赖。
- 含公式的工作簿保存后执行重算，检查工具确实生成新文件，公式仍存在、缓存可读且无错误。重算脚本隔离输入、输出和 LibreOffice profile；失败保留现有副本，不将旧文件误认作成功输出。
- 检查全部工作表的公式和数据，定位 `#REF!`、`#DIV/0!`、`#VALUE!`、`#NAME?`、`#N/A` 等错误；按业务口径核对总计、跨表关联、单位、舍入、空值、零分母和边界条件。公式缓存非空不等于结果正确，关键值与独立计算的预期值比较。
- LibreOffice 与 Excel 的函数/图表支持可能不同。若公式受支持程度、外部数据或兼容性影响结果，保持 `pending`，明确尚需哪一引擎复核；不为了通过检查而删除公式或静默冻结值。
- 全表结构/数值检查后渲染所有约定交付视图的打印区域，审阅图表、分页、列宽、换行、数值显示和中文字体。每次修订使用新建或空的预览目录并保留 `render.json`。数据表无需逐个单元格截图，并确认没有遗漏约定的交付视图。
- 把最终文件、业务预期与实际值、重算记录、全表检查和打印预览交给独立 `office-qa`；仅结构校验或抽样检查不构成质量通过。

## 已有轻量辅助脚本

`uv run office/xlsx/scripts/create.py DATA.json OUTPUT.xlsx` 用于简单数据表，`uv run office/xlsx/scripts/analyze.py INPUT.xlsx` 用于只读概览；它们不替代专业 skill、重算或验收。分析依赖按任务安装，不强制改变项目依赖配置。

细化清单见 `office-quality` 的 `references/xlsx.md`；没有重算/视觉/独立 QA 条件时保留 `pending` 并交付限制说明。
