# PPTX：先内容与分镜，再视觉与原生交付

先加载 `.agents/skills/omnippt/SKILL.md`，按本次阶段读取其六子技能；再加载 `office/rules/quality.md`、`office/rules/file-safety.md`、`office/rules/pptx.md` 和 `.agents/skills/anthropics-skills-pptx/SKILL.md`。下文路径相对安装后的项目根目录。Omnippt 负责设计决策，不替代原生格式引擎与独立 QA。纯只读提取按格式 skill 读取并注明来源，不强制重建设计阶段或独立 QA，不修改输入。

## 内容与设计分层

1. **Brief / 研究**：明确受众、要促成的决定/行动、场景与时长、语言/画幅、页数范围、模板/品牌和来源。只补本任务必要的事实缺口，记录 source ID 与事实/数据依据；不为已有完整材料强做外部研究。
2. **可移动大纲**：先确定叙事、每页结论与前后关系，为页面分配不随顺序变化的 slide ID，再按反馈调整顺序；事实、证据和删减依据可追溯。
3. **朴素分镜**：在视觉风格之前描述每页信息层级、元素 kind/ID/box、数据或素材及原生编辑意图；先验证内容和版面逻辑，不以漂亮截图替代分镜。
4. **视觉语言**：根据内容选择字体、颜色、间距、图像和布局 tokens。Bento/卡片按信息关系灵活使用；不要求每页固定格子、装饰图或统一内容密度。
5. **原生构建与审查**：读 `.agents/skills/omnippt/native-build/SKILL.md` 接可用 PPTX 引擎，再按 `deck-review/SKILL.md` 交独立审查。阶段修订要同步大纲/分镜/构建与证据，旧版本记录不证明新最终文件。

已有模板先检查母版、主题、版式、占位符、备注和对象；仅改一页、格式或现有内容时复用有效的 brief/大纲/设计约定，只处理本次范围，不强制重新调研或走完整六阶段。复杂项目持久化计划，简单任务保持轻量。

## 新增数据图表与宏分别确认

记录独立的 `chart_decision` / `macro_decision`（yes/no/pending），附真实用户答复来源、目标演示与范围；复用本次已明确的要/不要，不重复询问，不以沉默或模板推荐当 yes。未明确时主动问，可一次问完，继续不依赖这些决定的内容/排版工作。

- **新增数据图表**：yes 后明确指标/单位、类型、所在页/位置、实际数据范围和版本；no/pending 不新增或重建数据图表，不改用图片或制图宏绕过。原图表默认保留；按已确认编辑范围维护其数据引用与兼容性，不把 no 当作删除许可。普通内容布局/非数据概念图按本次 brief 制作，不为其机械套用新增数据图表确认。
- **宏**：区分制作/保留/修改/调用，记录用途、源码/编译项目来源和哈希、入口/参数、目标演示/幻灯片/对象范围、手动/按钮/明确指定事件触发、预期修改与输出。本次调用范围已明确则复用，不反复批准。原宏默认保留，打开、提取或预览不自动执行；无本次确认不运行未知宏，不降低全局信任设置。
- `.bas` / `.cls` 是源码；含 VBA 的演示/模板/放映分别使用 `.pptm` / `.potm` / `.ppsm`，普通 `.pptx` / `.potx` / `.ppsx` 不承载 VBA，改后缀不等于保存正确格式。保存事实见 [Microsoft 宏格式说明](https://support.microsoft.com/en-us/powerpoint/save-a-presentation-that-contains-vba-macros) 与 [PpSaveAsFileType](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.ppsaveasfiletype)。
- 选用真实 PowerPoint 路径导入/编译或显式调用时，分别留源码静态、项目/关系保留、真实编译/执行、结果和范围验证证据。源码或包存在不证明运行成功；只要求保留不额外强迫执行。缺本次要求的 PowerPoint 条件时仅对应项 pending，不把宏未选用变成所有 PPT 失败。

## 文件工程与素材交接

- `office-pptx` 是最终演示文件唯一写入者。图片/插图/示意图及图源先经 `.agents/skills/omnidraw/SKILL.md`（含 matplotlib），所有表格数据/模型/布局先经 `.agents/skills/omnisheet/SKILL.md`；共用同一数据快照，交付实际来源、单位、编辑源与预览。最终工程师插入真正原生表格/已确认图表，不把表格转图或另建未请求的工作簿。
- 默认正文、形状、表格、数据图表原生可编辑；复杂插图按用途选择原生组合、图片或 SVG，保留图源。整页概念图可按明确用途作为素材，但不以整页截图/SVG 替代需编辑的正文与页面对象。
- SVG 嵌入是图形，不等于逐个原生形状/文字可编辑。PowerPoint 的 Convert to Shape 是单独的应用步骤，支持和结果依实际平台/版本；需要时逐对象检查文字、组、线条与效果，未转换/未验收就如实记录。参见 [Microsoft SVG 编辑与转换说明](https://support.microsoft.com/en-au/office/graphics-visuals/edit-svg-images-in-microsoft-365)。
- 使用能保留需求特性的 PptxGenJS 或其他可用原生路径；保持模板母版、主题、布局、备注、未修改页与链接/嵌入对象。某个库缺口不是全局禁用原生能力的理由。不默认 `ppt-master`，也不新增固定 SVG 处理流水线。

## 逐页验收与交付

以下通用命令仅覆盖 `.pptx`；不证明 `.pptm` / `.potm` / `.ppsm` 宏项目保真或执行，不将宏文件转普通后缀绕过验收。宏格式按选定 PowerPoint 路径核验和预览。

```bash
python3 office/scripts/verify.py "deliverables/deck.pptx" --output "evidence/deck-structure.json"
python3 office/scripts/render.py "deliverables/deck.pptx" --out-dir "evidence/deck-preview"
```

- 重新打开最终演示，核对页数/顺序、文本、原生对象、数据、主题/母版、备注、关系和需保留特性；对照 baseline 检查本次范围，不以扩展名或对象计数代替编辑能力。
- Omnippt 合同检查只验证其覆盖的设计结构；不是内容正确、渲染或 PowerPoint 运行的证明。每页实际看 PNG/PDF，检查溢出、遮挡、对齐、留白、可读性、字体替换、图像与数据一致性。
- 制作角色提交 brief/来源、稳定 ID 大纲、分镜、tokens/阶段版本、图表/宏决定、构建记录、源/最终哈希、全页预览与限制，独立 `office-qa` 读取文件和证据。修复后重新构建、校验和全页审阅，旧缩略图不证明新文件。

缺适用证据保持 `pending`。细化清单见 `office-quality` 的 `references/pptx.md`；仅用户明确选用 `ppt-master` 时接入其真实已安装配置。
