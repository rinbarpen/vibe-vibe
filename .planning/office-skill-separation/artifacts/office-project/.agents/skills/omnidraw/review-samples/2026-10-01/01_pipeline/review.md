# Review

- Route: Omnidraw 科研图 → pipeline → Happy Figure 式 Brief/Visual Schema → deterministic SVG/PNG。
- 逐区检查：五模块、四条向前箭头；传感器光路、预处理波形、分类分支、告警图标可辨。
- 图中文字均为白名单；无小灰字、伪文字、灰色占位横线。
- 局限：传感器示意是概念图，不代表特定光学设计；无实测阈值或性能。


验证：`figure.svg` 可被 CairoSVG 渲染为 `figure.png`；PNG 1600×900，RGB/RGBA=RGB。
