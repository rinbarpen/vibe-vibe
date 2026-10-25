---
name: omnippt-native-build
description: "Assemble or edit native PowerPoint files from a deck contract using an available presentation engine. Preserves templates, themes, masters and notes, routes data/assets to sibling skills, and separates macro preservation from actual target-PowerPoint execution."
---

# 原生 PowerPoint 装配

接收 brief、源/模板哈希、稳定大纲、storyboard/设计 token、真实素材/数据、变更范围及图表/宏确认。该技能是工程交接层，不重复实现 PPTX 引擎。轻量局部编辑可直接使用已有引擎，只加载所需内容；不强制生成机器合同或重走研究。

## 选引擎与保护文件

按当前环境发现 `anthropics/skills/pptx` 或适合本次能力的等效引擎；Office 稳定入口为 `.agents/skills/anthropics-skills-pptx/SKILL.md`。图片/图源需要时先 Omnidraw，表格/数据模型先 Omnisheet；单独安装按名称定位，缺某个选定依赖只将该分支 pending，不要求加载全部外部工具或 ppt-master。

- 记录源 SHA-256，在副本上制作，一个最终文件仅一个写入者。覆盖原件只按用户明确要求且留备份/恢复命令；中间合同和图源放在用户项目。
- 模板/既有文件优先保留母版、布局、主题、备注、隐藏页、内部链接与未选对象。选择能保留本次特性的工具，先盘点再保存；只改一页不重建整套演示或把所有页扁平化。
- 默认原生文本、形状、表格、图表与适用分组。合同 `native:true` 是要求不是验收证据；实际重开/对象清单及目标应用行为证明其可编辑性。SVG/图片只是插图或计划源，不自动成为原生形状/文本。
- box/字体/token 按实际画幅映射，检查文本溢出、形状遮挡、图表数据引用、单位、表格合计、主题字体与备注。复杂对象遇库接口缺口时选适合引擎，不以库限制变成应用功能禁令。

## 图表与宏

图表/宏有独立 yes/no/pending 及本次确认来源；未明确主动问，已有答复复用。chart yes 后按指标/类型/位置/源范围制作原生图表，图片图由 Omnidraw；no/pending 不新增/重建（含图片、宏绕道），保留既有图表及已约定数据引用维护。

宏支持可审阅 `.bas` / `.cls` 源和 `.pptm` / `.potm` / `.ppsm` 的制作/保留/明确调用；`.pptx` / `.potx` / `.ppsx` 不承载 VBA。调用需本次明确用途、入口、目标演示/页面/对象、触发及输出，已有明确范围不反复批准。打开输入不自动跑宏，不改全局信任；原样保留不要求运行。源码、真实编译项目/关系保留、目标 PowerPoint 编译/执行分别留证；没有相应引擎就将本次所需执行项 pending，不声称已有通用脚本执行或保真转换宏。模板宏与最终输出格式分别注明。

## 输出

交最终文件/格式/哈希、保留/变更对象清单、模板/备注/图表数据与宏证据、真实构建命令/输入/输出/退出状态、结构重开、全页渲染和未决项。合同 checker 只为静态策划证据，不创建或验收 PPTX。制作人完成自检后交另一代理/审查者独立 deck-review；修复改变最终文件须重跑检查/预览并复验。
