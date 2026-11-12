---
name: omnippt-deck-review
description: "Independently review a final PowerPoint deck against its brief, evidence, editable-object requirements and every-slide previews. Distinguishes static contract checks, actual file inspection and target-application macro execution; returns located issues without editing the deck."
---

# 独立演示审查

接收用户 brief、制作者身份、源/模板与最终哈希、大纲/事实来源、合同修订、实际图表/素材、构建/结构/渲染记录和验收条件。审查者独立于本次正文、素材和最终文件制作；作者自审不冒充独立 QA，只写审查证据，问题退回原制作阶段。

## 审查门禁

- 重算最终哈希，与合同/构建/预览记录匹配，实际重开文件。对照需求核实只改了范围内页面/对象，母版、布局、主题、备注及无关特性保留；来源和建议/假设不混淆。
- 从事实来源逐页核对结论与数据，包括单位、时间区间、比例/总计、表格和图表引用；不是只读制作者“通过”摘要。大纲/策划/设计修订一致，已改结论不复用过期图表。
- 图表/宏的 yes/no/pending 与真实本次答复一致，未答确有主动询问。no/pending 未新增/重建数据图（含图片、宏绕道），原图表保留和数据引用维护分开验证；yes 核对指标/类型/位置/源范围。
- 宏源码、编译项目保留、真实 PowerPoint 编译/执行各有独立记录；打开输入不自动执行/更改全局信任。用户只要求保留不额外要求运行，要求运行却无真实引擎证据则 pending，不能用静态源码或不相关示例二进制代替。
- 检查原生文本/形状/表格/图表及实际编辑能力，SVG 嵌入不是自动可编辑对象。合同 `native:true` 和静态 checker 结果不是文件对象或质量证明。
- 实际渲染并查看全部幻灯片，逐页记录裁切/溢出、遮挡、对齐、字体、对比、图片质量、来源/备注和数据一致性。含隐藏页时说明清单及其实际渲染/检查范围，不把默认导出遗漏页称作已审。预览生成成功或抽样前两页不等于全量视觉通过。

## 结论与修复

返回审查身份/独立性、源/最终哈希、实际命令/方法/输出、每页覆盖与观察、问题位置（slide/element ID 与页码）、预期/实际和修复验收方式。QA verdict 为 pass/pending/fail；证据缺失 pending、确认缺陷 fail，全部适用门禁有证据才 pass。问题回到来源/outline/storyboard/design/build 对应阶段修复，最终哈希变化后重新核对相关内容并全页渲染/复审。

最终交付状态 draft/pending/passed 与 QA verdict 分开：仅当前版本全部适用门禁且独立 QA pass 才 passed；选定宏执行或渲染环境缺失只列具体待验收项，不扩大为未采用引擎失败。只读提取说明来源定位，不强制独立 QA。
