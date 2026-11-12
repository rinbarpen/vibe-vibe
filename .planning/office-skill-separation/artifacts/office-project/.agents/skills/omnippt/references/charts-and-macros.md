# PPT 数据图表与宏交接

## 独立确认，不重复询问

记录 `chart` 与 `macro` 各自的 yes/no/pending、真实用户原话/会话定位与本次 scope。已有明确要求直接复用；缺项主动询问，可合为一问，不把沉默、文章风格或“数据适合画图”当同意。测试示例的 simulated 记录只验证分支，不是真实批准。

- chart yes：指标/单位、类型、目标页/位置、源范围/数据版本；原生图表由最终引擎写入，图片图走 Omnidraw。Omnisheet 准备/核对数据及表格规格。
- chart no/pending：不新增/重建数据图，包括图片、SVG 图表及制图宏绕道；继续文字、表格和已请求的非数据插图。原图表默认保留，用户范围内维护数据引用与新增分开核验。
- macro yes：指定 preserve/create/modify/invoke 的实际模式，明确用途、入口/参数、目标演示/页/对象、触发及输出；已有明确本次范围不反复批准。macro no/pending 不制作、修改或调用未确认宏，继续非宏工作。

## 原生宏能力与证据

支持 `.bas` / `.cls` 可审阅源、宏演示 `.pptm`、宏模板 `.potm` 和宏放映 `.ppsm`；`.pptx` / `.potx` / `.ppsx` 不承载 VBA。格式、真实 VBA 项目及关系一致，不靠重命名后缀宣称宏已保留。[Microsoft 保存含宏演示说明](https://support.microsoft.com/en-us/powerpoint/save-a-presentation-that-contains-vba-macros)、[PowerPoint 文件格式枚举](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.ppsaveasfiletype)

原有宏默认保留而不自动执行，打开输入、只读盘点或预览不构成调用许可；不改变全局信任。不把某个库不支持宏说成 PowerPoint 禁用宏：选择能保留本次特性的真实引擎，先在副本核验；不走会丢项目的非宏转换。

分别交接源码/来源/hash、编译项目/包关系的保留或修改证据、目标 PowerPoint 的实际导入/编译/入口调用/输出检查。提供新源码、保留二进制或静态合同不证明实际运行；只保留任务不强迫运行，要求调用而缺真实引擎则对应项 pending。本技能不附新宏执行器或声称通用渲染脚本执行过宏。

最终 QA 核对当前哈希、图表/宏实际范围与全部所需证据；chart/macro未答的范围继续 pending，明确 no 记录为未采用而非失败。
