# 按场景选择可视化

**简体中文** | [English](visualization-scenarios_EN.md)

本页是 Omnidraw 的场景入口。先看用户要表达什么、真实输入是什么、交付到哪里，再选择能力；不是把每个任务转成 HTML，也不是把所有数据都画成流程图。用户指定的工具、格式与现有项目栈优先。

## 选择制作路线

| 场景与判据 | 采用的能力 / 规范 Skill id_path | 交付与检查 |
| --- | --- | --- |
| 架构讲解、代码差异、方案对比、项目回顾，读者需要浏览完整说明 | `visual-explainer/plugins/visual-explainer` | HTML 源稿与页面；核对图中箭头、标签和源码事实，按需用其 kit 渲染器检查 |
| 趋势、柱状、散点、误差线等确定性数据图 | `omnidraw/matplotlib`；更深入定制可用 `claude-scientific-skills/skills/matplotlib` | 绘图代码、来源数据、SVG/PDF/PNG；核对单位、坐标、样本与不确定性 |
| 分布、分组比较、相关性、探索性统计 | `claude-scientific-skills/skills/seaborn` | 保留聚合方法、缺失值和原始观测；探索结果与已验证结论分开 |
| 悬停、缩放、图例切换等交互式数据图，不需要完整应用 | `claude-scientific-skills/skills/scientific-visualization` 的 Plotly 路线 | HTML、生成代码、可访问数据表；静态备份单独导出，检查离线资产与导出依赖 |
| KPI、多视图联动、筛选与刷新等完整仪表盘 | `ai-design-components/skills/creating-dashboards`；图表另选合适后端 | 可运行页面/项目与数据接入说明；测试筛选、加载、空值、错误和刷新状态，不把原型说成已部署系统 |
| Markdown 中的流程、时序、ER、状态机、思维导图、少量概念关系 | `omnidraw/mermaid`；复杂 UML 按现有 PlantUML 路线 | Mermaid/PlantUML 图源及需要的预览；核对分支、关系和阅读顺序，不强制包进 HTML |
| 知识图谱、引用/社交/生物网络，需要属性、规模或图算法 | `claude-scientific-skills/skills/networkx` | 节点/边数据、图模型、布局与分析代码；区分方向、多重边、权重和来源。纯概念关系仍用 Mermaid 即可 |
| 论文统计图、多面板、误差和期刊输出 | `claude-scientific-skills/skills/scientific-visualization` | 保留数据和变换，检查物理尺寸、字体、图例与不确定性；按实际投稿阶段核验期刊要求，不套固定 DPI 当验收结论 |
| 科研方法架构、机制、实验装置、图形摘要 | `CCFA-Skills/ccf-visual-composer`；已安装科学示意图路线可补充 | 先核对科学对象、箭头语义和证据边界，再选矢量或图像路线；与数据统计图分工，不生成虚构实验数值 |
| 地理分布、行政区、轨迹或空间关系 | `claude-scientific-skills/skills/geopandas` | 核对坐标参考、空间连接、边界和数据许可；输出地图及可复现代码，不从图片猜地理数据 |

表中是能力来源，而不是要求安装全部依赖。当前仓库没有独立 `plotly` Skill；Plotly 是 `scientific-visualization` 覆盖的绘图后端。`creating-dashboards` 负责应用层，`visual-explainer` 负责说明层，两者都不能代替指标定义或真实数据分析。

## 安装与已安装项目的解析

仅安装本次任务需要的路线。统一入口与 Mermaid/Matplotlib 子技能可一起安装：

```bash
vibe add skill omnidraw ../my-project
```

额外能力按需选择；以下完整 id_path 在同名技能并存时也指向明确来源：

```bash
vibe add skill visual-explainer/plugins/visual-explainer ../my-project
vibe add skill claude-scientific-skills/skills/matplotlib ../my-project
vibe add skill claude-scientific-skills/skills/seaborn ../my-project
vibe add skill claude-scientific-skills/skills/scientific-visualization ../my-project
vibe add skill ai-design-components/skills/creating-dashboards ../my-project
vibe add skill claude-scientific-skills/skills/networkx ../my-project
vibe add skill CCFA-Skills/ccf-visual-composer ../my-project
vibe add skill claude-scientific-skills/skills/geopandas ../my-project
```

完整 id_path 安装时目录名由路径连字符化；例如 scientific-visualization 会安装为 `.agents/skills/claude-scientific-skills-skills-scientific-visualization/`。已经用短名安装的目录不需要改名。路由时先读取目标项目已有的 `SKILL.md` 与 `.vibe-tool/installations.json`，用记录的 `source` 确认来源，再读取实际安装路径；不要照搬仓库根的相对链接到目标项目。`omnidraw/matplotlib` 和 `omnidraw/mermaid` 是随主入口一起分发的本地子技能，无需再次单独安装。

缺少所选能力时，说明缺口与准确安装方式，或在不丢失需求的前提下使用已有能力；避免把静态截图当作交互图、把示意图当作真实数据图，或因为一条路线缺依赖就阻塞其他路线。新增依赖、数据外发、后台刷新、部署、付费图像生成等都仍按本次约定执行，不因安装 Skill 自动启动。

## 组合与验收

- **科研报告**：Matplotlib/Seaborn/Plotly 产出真实数据图，scientific-visualization 检查出版与可访问性，Visual Explainer 可把核验过的图组织成网页说明；HTML 页面不替代投稿用的 PDF/SVG。
- **业务仪表盘**：先明确指标口径、粒度、时间范围、来源和缺失值，再用 creating-dashboards 组织筛选与多视图；不默认增加实时服务、额外部署或全新框架。
- **系统/知识说明**：流程和小关系图用 Mermaid；有边表与图计算时用 NetworkX；需要交互讲解或对比评审时再组合 Visual Explainer。不存在的边、因果与权重保持未知，不补造。
- **办公交付**：保留代码、图源、数据及静态/交互预览。需要 PPTX 或原生可编辑图时走相应制作路线，不把 HTML 或截图声称为可编辑办公对象。
- **依赖与验证**：只检查所选路线实际用到的运行时。HTML kit 使用 Node.js；统计绘图使用项目的 Python 环境；Plotly 静态导出与浏览器检查、地图和图算法各有额外依赖。安装成功不等于这些运行时已装好。

交付时说明实际生成和实际执行过的检查；仅做语法/结构检查时不要写成浏览器视觉验收。保留用户语言和指定格式；缺数据时区分待补数据与明确标注的演示数据。

## 维护工作流示意图

`assets/workflow.mmd` 是随包分发的可编辑图源，SVG 描述路由规则而非运行状态。从本聚合仓库根目录可复用已有 Pretty Mermaid 渲染器；仅编辑此图时才准备该渲染器的锁定依赖：

```bash
node skills/Pretty-mermaid-skills/scripts/render.mjs \
  --input mine/omnidraw/assets/workflow.mmd \
  --output mine/omnidraw/assets/workflow.svg --format svg \
  --theme github-light --font 'Noto Sans CJK SC' --bg '#ffffff' --fg '#173B47'
```

只读漂移检查可将相同命令的 `--output` 指向临时目录，再用 `cmp` 与仓库 SVG 比较；这不改图源或已安装项目。图源使用纯 Mermaid，无渲染器不支持的 YAML 头。
