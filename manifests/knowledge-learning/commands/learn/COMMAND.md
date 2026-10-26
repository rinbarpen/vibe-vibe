---
description: 基于材料开展学习会话；--plan 根据上传教材生成有章节依据的学习路线
globs: ["materials/**/*", "notes/**/*", "projects/**/*"]
---

# /learn

## Purpose

`--plan` 只规划章节路线；省略此参数则保留主动学习会话。它是助手指令参数，不是 `vibe` CLI 参数。

## Usage

```text
/learn <topic>                                  # 学习某个主题
/learn <topic> --mode deep                      # 深度学习会话
/learn <topic> --mode overview                  # 概览会话
/learn <topic> --material <path>                 # 从指定材料学习
/learn [topic] --plan [--material <path>]        # 按教材规划章节路线
```

Examples:
```text
/learn 决策树
/learn 神经网络 --mode deep
/learn 微积分 --mode overview
/learn Python基础 --material materials/slides/Python基础.pptx
/learn --plan --material materials/pdf/统计学习方法.pdf
/learn 线性代数 --plan
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `topic` | 规划时可省略 | 学习主题；规划时从当前上传或选定的教材确定 |
| `--plan` | false | 生成教材地图和章节路线，不启动学习会话 |
| `--mode` | `deep` | 学习会话模式：deep/quick/overview；不改变规划粒度 |
| `--material` | — | 指定材料路径；规划时优先于当前上传材料 |

## 规划模式 (`--plan`)

收到“根据这份教材规划学习”等自然语言，或上传教材后的规划引导，也进入此模式，不要求重发命令。

1. **确定材料**：优先使用 `--material`，否则使用本次上传/对话已选材料。仅在存在多组无从判定的候选时请用户选择；尚无材料时引导上传，不用通用知识树假装教材内容。
2. **轻量索引**：交给 material-processor 读取元数据、目录/书签、章节标题、概览及必要代表性页面。复用已核验索引，只补充缺失或变更部分。先不逐章全文提取、不批量生成笔记或闪卡。
3. **展示教材地图**：先保存并展示 `projects/<教材或主题>/MATERIAL_INDEX.md` 的章节结构、定位、覆盖状态及待补内容；多材料分开列明。
4. **集中补问**：复用对话和项目中已知的学习目标、已有基础、已学章节，只问尚缺项。每天时长、截止日期不作为规划前提；基础未知记为“待确认”，不据此跳过前置章节。
5. **设计章节路线**：按 `references/learning-path-design.md`，由 curriculum-designer 将实际章节编入“前置准备 → 基础章节 → 核心章节 → 进阶与综合”。阶段是规划标签，不是教材真实章名。未指定范围时覆盖所选教材；已学范围只有用户明确同意后才标为跳过或仅复核。
6. **保存并核对**：参考 `.cursor/templates/MATERIAL_INDEX.md.example` 和 `.cursor/templates/LEARNING_PATH.md.example`，保存 `projects/<教材或主题>/LEARNING_PATH.md`。每个单元写明目标、真实章节/定位、重点问题、已确认的教材练习、完成标准和顺序依据。教材依赖、助手推荐顺序分别标注；用户目标/基础与教材事实分开记录。
7. **交付后停止**：输出路线文件、材料覆盖与待补清单。不生成每日/每周课表，不自动开始首章学习，不创建持续陪学或动态排程。日历模板继续供原有按需使用。

扫描件识别不全、无目录或习题尚未核实时，保留已验证部分并标“待补”；未知章节、页码、习题编号不补造。PDF 页序与印刷页码分别标注，详见 `references/source-grounding.md`。

## 学习会话（无 `--plan`）

1. 在 `materials/`、`notes/` 和已有教材地图中匹配主题；按已知基础确认当前学习目标。
2. 在当前范围内安排 prerequisites → core → advanced，引用真实来源，不重做整本教材规划。
3. 进入主动学习循环：约每 20 分钟插入主动回忆检查点；按当前单元提取必要内容，产出原子笔记到 `notes/atoms/`。
4. 会话结束生成有来源的闪卡并记录进度，保留 deep/quick/overview 行为。

## Source-Grounding 与增强引擎

- 教材事实、概念和依赖引用实际材料；多来源分别标注。助手建议用 `[规划建议]`，推断顺序用 `[推荐顺序：推断]`，用户信息标“用户提供”，不伪造教材出处。
- 无源材料的知识性补充用 `[unverified]`；置信度标记不代替核验。
- `NOTEBOOKLM_ENGINE=true` 时可在学习会话中增加综合学习指南和 grounded Q&A；教材索引与 `--plan` 在开关关闭时同样可用，开启也不扩大导入/规划范围。
