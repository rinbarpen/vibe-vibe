# Omnidraw 科研图型 Review 样例

同一虚构研究主题：便携式河水浊度监测。所有数值均为模拟或明确标注 illustrative；图像草稿不代表实验结果。

[打开可视化索引](index.html)

| 编号 | 图型 | 样例 | 来源/代码 | Review |
|---|---|---|---|---|
| 01 | 技术路线 / Pipeline | [查看](01_pipeline/figure.png) | [来源](01_pipeline/figure.svg) | [记录](01_pipeline/review.md) |
| 02 | 实验系统 / Apparatus | [查看](02_apparatus/figure.png) | [来源](02_apparatus/prompt.txt) | [记录](02_apparatus/review.md) |
| 03 | 机制解释 / Mechanism | [查看](03_mechanism/figure.png) | [来源](03_mechanism/prompt.txt) | [记录](03_mechanism/review.md) |
| 04 | 模型架构 / Architecture | [查看](04_architecture/figure.png) | [来源](04_architecture/figure.svg) | [记录](04_architecture/review.md) |
| 05 | 多面板定性比较 / Comparison | [查看](05_comparison/comparison.png) | [来源](05_comparison/render.py) | [记录](05_comparison/review.md) |
| 06 | 图形摘要 / Graphical Abstract | [查看](06_graphical_abstract/figure.png) | [来源](06_graphical_abstract/prompt.txt) | [记录](06_graphical_abstract/review.md) |
| 07 | 汇报总览 / Roadmap | [查看](07_roadmap/figure.png) | [来源](07_roadmap/figure.svg) | [记录](07_roadmap/review.md) |
| 08 | 封面主视觉 / Cover Art | [查看](08_cover_art/figure.png) | [来源](08_cover_art/prompt.txt) | [记录](08_cover_art/review.md) |
| 09 | 单面板统计 / Single Panel | [查看](09_stat_single/stat_single.png) | [来源](09_stat_single/render.py) | [记录](09_stat_single/review.md) |
| 10 | 多面板统计 / Multi-panel | [查看](10_stat_multi/stat_multi.png) | [来源](10_stat_multi/render.py) | [记录](10_stat_multi/review.md) |

## 执行说明

- 科研流程、架构、汇报总览：Omnidraw 分型 → Happy Figure 式 Brief/视觉契约 → 确定性 SVG → PNG。
- 装置、机制、图形摘要、封面：Omnidraw 分型 → Happy Figure 式提示词 → image_gen → 目视审查。
- 统计图：明确模拟数据 → Matplotlib/Python → PNG/PDF；NaturePanelForge 的已有图复现路线不适用于这些新数据样例。
- 本次尚未执行 figure2pptx 可编辑重建；生成稿用于先审内容、图型与视觉方向。

## 共性 Review 发现

- 小灰字/灰色伪文字：最终样例未发现；有意义的灰色副标题和说明仍存在于部分代码图。
- 流程、架构和路线总览清楚，但视觉风格偏模板化，尚未达到高水平论文 Figure 1 的信息设计水准。
- 位图机制图首稿把探测器画在错误方向，已通过编辑纠正为 90° 侧向探测。
- 统计图有可执行源码与模拟数据；图形摘要/封面不应被解读为测量结果。
