---
name: omnippt-storyboard
description: "Make a plain slide-planning draft that fixes content hierarchy, placement and object intent before visual styling. Use after outline or for restructuring selected slides; preserve existing-template boundaries."
---

# 朴素策划稿 / Storyboard

接收有稳定 slide ID 的大纲、来源事实、目标画幅、模板与 edit_scope。先解决信息的位置、顺序和对象类型；可以用线框、结构化合同或简洁草图，不强制先生成一套临时 PPTX。

## 逐页策划

- 为本页结论、主要证据、解释/注释、来源和必要图示划定区域；标记阅读顺序及焦点，避免所有信息等重。内容过多先删重复/分层或在允许范围拆页，不靠不可读的小字硬塞。
- 对象用稳定 element ID、kind、绝对 box 坐标/单位、native 目标、fact IDs 和父子关系表示；同一画布坐标系贯穿构建。明确故意包含/叠放，不把意外遮挡称作层级。
- 区分原生文本/形状/表格/图表与插图素材，真实表格仍是表格，数据图只有 chart yes 才进入新增制作；图片形式图表同样受确认约束。既有对象保留与新增分开记录。
- 沿模板占位符/版式设置放置内容，保留备注、主题和母版关系；一页小改只策划选定区域，不重建整个 deck。

## 输出与更新

输出每页的结论、内容区域、元素清单/坐标、来源映射、原生/图片意图、备注及未决项；暂不以阴影、装饰或复杂色彩掩盖内容缺口。视觉阶段可以按内容调整构图，但须同步合同/修订及原因；不要求用户逐阶段批准，除非用户指定审稿节点或变化影响原需求。
