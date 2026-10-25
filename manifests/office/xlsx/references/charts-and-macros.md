# Excel 图表确认与宏工作流

用于新建/编辑工作簿时的交互、原生图表与 VBA 交接；安装后从项目根目录读取本文件。数据/模型/表格布局先走 Omnisheet，最终工作簿由 `office-xlsx` 唯一写入。可复制 `office/xlsx/templates/workbook-brief.md` 记录约定。

## 两个独立决策，先问再制作

新增图表与宏使用分别记录 `chart_decision`、`macro_decision`，值为 `yes` / `no` / `pending`，附用户原话或会话定位、目标文件、任务范围和日期。先复用本次范围内已明确的要/不要；不得重复询问已确认决定，也不把“数据适合画图”、场景模板推荐或用户沉默当作同意。范围实质变化才补充确认变化部分。

尚未明确时主动询问，可一次问完，例如：

> 这次 Excel 是否需要新增图表？是否需要宏自动化？可分别回答要/不要；若要图表，请说明希望展示的指标，若要宏，请说明自动化用途。

- **图表 yes**：记录指标/单位、图表类型、目标工作表及位置、实际源范围/数据版本；已有明确要求直接复用。原生 Excel 图表由 `office-xlsx` 创建，图片形式的图由 Omnidraw 制作，均使用 Omnisheet 核对的数据。不为了通过确认绕道生成图片图表。
- **图表 no**：本次不新增/重建图表，覆盖场景子技能的默认推荐制图步骤；继续完成数据、公式、格式和打印视图。
- **图表 pending**：先问用户，同时继续非图表工作；新增图表范围保持待确认，不擅加图，也不以交付期限默认 yes。
- **宏 yes**：明确本次是制作、保留、修改还是调用宏，按下节确认用途与作用范围；已有明确任务约定直接记录，不反复请求同一批准。
- **宏 no / pending**：不制作、修改或调用未确认的宏；pending 时询问并继续非宏工作，不把宏是否采用的未决项阻塞整个表格任务。

原工作簿已有图表和宏默认保留；只读清单与原样保留不需要为执行再确认，它们的存在也不是新增/执行许可。按用户范围维护既有图表的数据引用与兼容性，不凭 no 删除原图表，也不把仅保留图表说成新增。新增图表的宏入口同样需要图表 yes。纯只读检查不执行宏，也不需要为“是否新增”制造变更。

## 宏是一等原生能力

按任务支持 `.bas` 标准模块、`.cls` 类模块、含宏的 `.xlsm` 工作簿及 `.xltm` 模板。`.xlsx` / `.xltx` 不承载 VBA，不能仅改后缀假装宏已嵌入；保存格式及真实包部件/关系必须一致。[Excel 文件格式枚举](https://learn.microsoft.com/en-us/office/vba/api/excel.xlfileformat)

1. **约定**：记录宏用途、源码/已编译项目来源及哈希、入口过程及参数、目标工作簿/工作表/单元格范围、触发方式（手动/按钮/明确指定的事件）、预期修改及输出。把“保留宏”与“运行宏”分开；用户已明确给出本次调用和作用范围即视为已确认，不要求重复批准。范围缺口只询问缺失部分。
2. **制作或保留**：在副本上编辑/导入已审阅源码，保留原宏项目、控件绑定、工作簿/工作表 VBA codenames、关系及适用签名。新源码需在真实 Excel/VBA 环境导入、编译和验证；源码文件存在不证明已编译进交付文件。已有项目修改可能影响签名，记录实际状态，不虚报签名保留。
3. **显式调用**：只有本次调用范围明确后才在目标应用调用指定入口，核对实际工作簿/工作表/范围而非依赖活动窗口；事件宏仅按明确约定设置/触发。打开输入、读取清单或预览不自动运行宏，不更改全局信任设置。`Application.Run` 可调用指定过程及参数，但调用代码本身不证明运行成功。[Excel 宏调用 API](https://learn.microsoft.com/en-us/office/vba/api/excel.application.run)
4. **验证**：分别记录源码静态审查、宏包保留/嵌入、真实 Excel 编译/执行、公式重算和结果核对。实际运行证据包含 Excel 版本、入口/参数、输入输出哈希、实际变化范围、日志/返回值、关键预期与实际值；无关数据保持不变。仅保留既有宏的任务不额外要求运行它，要求调用却未实际执行的项为 `pending`。

自动化打开 Excel 文件时不要依赖默认行为；根据所选真实引擎显式控制宏与链接更新，局部状态在结束时恢复。`EnableEvents=False` 只控制事件，不是所有宏的总开关；`UserControl` 不是用户确认标志。不通过降低 Trust Center 或修改全局配置来完成任务。本 manifest 本轮不新增 Windows 自动执行器。[Workbooks.Open](https://learn.microsoft.com/en-us/office/vba/api/excel.workbooks.open)、[AutomationSecurity](https://learn.microsoft.com/en-us/office/vba/api/excel.application.automationsecurity)、[EnableEvents](https://learn.microsoft.com/en-us/office/vba/api/excel.application.enableevents)

## 引擎能力与宏保真

- `openpyxl.load_workbook(..., keep_vba=True, data_only=False)` 可用于适配文件的 VBA 保留，不执行或编译宏，也不保证所有图形/控件保真；复杂特性先对副本验证，保留前后清单和哈希。不得保存 `data_only=True` 实例。[openpyxl 读取参数](https://openpyxl.readthedocs.io/en/3.1/api/openpyxl.reader.excel.html)、[保留限制](https://openpyxl.readthedocs.io/en/3.1/tutorial.html)
- XlsxWriter `add_vba_project()` 嵌入已有 `vbaProject.bin`，不是将新 `.bas` / `.cls` 编译成项目。已编译二进制、源码和按钮入口必须对应；第三方 `say_hello` 示例项目只可作保留测试，不是本次新宏源码已经编译或执行的证据。[XlsxWriter VBA 工作方式](https://xlsxwriter.readthedocs.io/working_with_macros.html)、[嵌入 API](https://xlsxwriter.readthedocs.io/workbook.html#workbook-add-vba-project)
- 当前 `office/xlsx/scripts/recalc.py` / `recalc.sh` 与通用 `render.py` 的表格路径仅支持非宏 `.xlsx`；含宏交付不得借改后缀或 LibreOffice→`.xlsx` 转换丢弃宏。保留 `.xlsm` / `.xltm` 副本，选择经实际保真验证的 Excel 重算/预览/运行路径；环境欠缺时列出待验收项，不宣称现有脚本已保真执行宏。
- 宏包字节/关系核对、源码静态检查和结构重开都不是宏业务效果或 UI/控件保真的证明。保留检查可以有独立结论，整体状态仍依本次全部适用门禁和独立 QA 决定。

## 已安装辅助 API 与 VBA 入口

`office/xlsx/scripts/workbook_features.py` 是可导入模块，不是新 CLI，不打开 Excel、不执行宏。实际接口：

| API | 用途与边界 |
|---|---|
| `chart_decision(answer=None, *, source=None, scope="new_charts")` | 记录 yes/no/pending；yes/no 必须有真实确认来源；记录本身不认证用户答复 |
| `require_chart_confirmation(decision=None, *, creating_new_charts=True, scope="new_charts")` | 新增前检查；yes 返回 True，no 返回 False（跳过），pending/范围不匹配抛 `ChartConfirmationRequired`；仅保留既有图表不需新确认 |
| `macro_decision(answer=None, *, source=None, scope="macro_work", requested_modes=("preserve",))` | 分开记录宏决定与 preserve/create/modify/invoke 模式 |
| `require_macro_confirmation(decision=None, *, mode, scope="macro_work")` | 原样保留返回 True；制作/修改/调用须匹配已确认范围与模式，no 跳过，pending 抛 `MacroConfirmationRequired` |
| `inspect_workbook(path)` | 只读检查 `.xlsx` / `.xlsm` / `.xltx` / `.xltm` 真实包格式、图表、宏/控件关系及部件；不提取或审查二进制内的 VBA 源 |
| `verify_macro_preservation(source, output)` | 不同源/输出文件的受管宏相关部件字节、关系、内容类型、codenames 与控件绑定对比；`quality_status=pending` / `macro_execution_status=not_run` |

调用方将 pending 异常转为用户问题，继续无关数据/格式工作；False 必须跳过对应新增/调用，不能只调用检查却忽略结果。确认记录必须来自真实本次对话；测试模拟选择须注明 simulated，不能当作用户批准。保留检查只证明报告列出的图谱范围，不证明全部单元格、图形、签名有效性或宏业务结果；审阅 `errors` 和限制后再交 QA。

`office/xlsx/macros/OfficeWorkbook.bas` 可审阅后在真实 Excel 手动导入，提供：

- `CalculateOfficeRange(wb, target, macroConfirmed=False)`：指定工作副本和范围重算；仍需跨表依赖与关键值核对。
- `ConfigureOfficePrintArea(wb, view, macroConfirmed=False)`：设置明确的连续交付打印区域；不等于已打印或审阅。
- `AddOfficeNativeChart(wb, data, host, chartName, title, chartConfirmed, macroConfirmed=False, ...)`：按明确数据范围、目标表、名称和类型/尺寸创建原生图表，既有同名图表不覆盖；需要图表与本次宏调用两个独立确认。

这些参数是调用方契约，不替代真实用户决定；模块不自动保存、不自动启动、不设置全局信任。`.bas` 本身是源码，不是已编译 `vbaProject.bin`，本环境的静态检查不冒称 Excel 执行。用户选定宏路径时，在目标 Excel 导入/编译并按约定显式调用、保存正确格式和核验输出；尚缺该引擎则对应执行项待验收。

## 验收与交接

交付包含两项决策及确认来源、图表规格/保留清单、宏用途/入口/范围/触发/输出、实际采用格式/引擎及源码和编译项目各自的路径/哈希。检查全部工作表的数据/公式和关键业务值、全部声明交付视图；新增图表检查实际源范围、类型、位置与可编辑性，宏检查本次实际承诺的保留或执行效果。修订后更新最终哈希并由独立 `office-qa` 复验。未答的范围、缺 Excel 执行或宏兼容性证据具体标 `pending`；用户明确不要的能力记为未选用，不虚列为失败。
