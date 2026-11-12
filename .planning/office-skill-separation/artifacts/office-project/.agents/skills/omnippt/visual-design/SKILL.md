---
name: omnippt-visual-design
description: "Apply content-led visual hierarchy to a slide storyboard, using flexible Bento/card layouts only where they serve the content. Routes images and drawing sources to Omnidraw and tabular models to Omnisheet while retaining native Office object intent."
---

# 内容驱动的视觉设计

接收 storyboard、品牌/模板、实际数据/来源、目标显示尺寸和可编辑性要求。策划确定要表达什么与位置，视觉设计决定如何让其重点被看见；不以固定卡片数或整页图像取代信息设计。

## 设计决策

- 先明确焦点、主次、阅读路径与对齐，再选字体、字号层级、色彩、留白和图片处理。可用灵活 Bento/卡片把相关信息分组，重要内容获得更大或更明确的区域；需要单一论点、全幅原生图表或简洁标题时不强行塞卡片。
- 沿既有模板的字体/主题/布局扩展；新设计用一套可复用 token，记录字体/字色/背景/强调色/标题与正文尺度。合同示例的颜色/尺寸是示范，不是所有演示的固定规格。
- 图片、插画、示意图、SVG 设计源及图片形式的数据绘图经可用 Omnidraw；表格内容/模型/布局经可用 Omnisheet。只在确有视觉用途且该路线可用时取用，不强制外部图像服务或每页装饰。
- 数据图表新增前查 chart yes/no/pending 与本次来源；no/pending 不做原生或图片数据图，也不借制图宏绕过，继续文字/表格和非数据插图。原生图表/表格构建规格交最终 PPT 工程师，不用截图替代原生表格。
- SVG 可作草图或单幅艺术/说明素材；SVG 内文字可改源不等于最终 PowerPoint 文字可逐项编辑。用户需要原生编辑时由引擎重建合适对象或在真实应用转换/验证，保留图源，不把整页 SVG 当作默认交付管线。

## 输出与检查

交设计 token、逐页布局修订、实际素材/预览/可编辑源及哈希、数据/来源/单位、替代文本、图表规格和插入位置。检查实际目标尺寸的可读性、对比、标签和一致性；图源预览不代替完整幻灯片渲染。素材欠缺只标所选素材分支 pending，原生内容可继续制作。
