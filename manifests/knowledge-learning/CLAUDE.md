# Knowledge-Learning Manifest

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

面向多种知识载体格式的系统化学习 manifest。提供从材料导入到复习巩固的全流程管理：
**导入各种学习材料 → Source-grounded 提取知识 → 结构化笔记 → 间隔重复复习巩固**。

采用类似 NotebookLM 的严格源引用模式，学习材料与知识输出一一可追溯。

## Mode Settings

| 设置 | 默认 | 作用 |
|------|------|------|
| `STRICT_SOURCE_MODE=true` | 开启 | 所有输出必须引用原始材料，禁止 AI 自由发挥 |
| `NOTEBOOKLM_ENGINE=false` | 关闭 | NotebookLM 增强功能（音频概述等），与严格模式正交 |

## Commands

| Command | Description |
|---------|-------------|
| `/import <path/url>` | 导入学习材料，自动识别载体类型并提取知识 |
| `/learn <topic>` | 基于已有材料启动结构化学习会话 |
| `/review [topic]` | SM-2 间隔重复复习 |
| `/flashcard <topic>` | 从学习材料生成闪卡 |
| `/mindmap <topic>` | 基于学习材料生成知识图谱 |
| `/study <material>` | 针对特定材料(PPT/课本/视频)的专项学习 |
| `/exam <topic>` | 生成试卷/习题，支持难度和知识点配置 |
| `/diagram <concept>` | 生成概念图表（流程图/思维导图/对比图等） |
| `/track [scope]` | 学习进度追踪与报告 |

## Architecture

```
<root>/
  materials/              # 原始学习材料（按载体类型组织）
    slides/               # PPT/幻灯片 (.ppt, .pptx, .key)
    pdf/                  # PDF 课本/论文/报告
    video/                # 视频课程 (.mp4, .mov) + 字幕
    web/                  # 网页文章/在线文档 (URLs, HTML)
    audio/                # 音频课程/播客 (.mp3, .wav)
    exercises/            # 习题/试卷/测试题
    images/               # 图片/图表/截图
  notes/                  # Source-grounded 结构化笔记
    atoms/                # 原子笔记（一个概念一条）
    summaries/            # 跨概念的提炼与总结
  flashcards/             # 间隔重复闪卡 (SM-2)
    decks/                # 按主题/材料分组的卡片组
    reviews/              # 复习日志与 SM-2 参数
  projects/               # 知识应用项目
```

## Key Files

| File | Purpose |
|------|---------|
| `references/carrier-types.md` | 支持的载体格式与提取策略 |
| `references/source-grounding.md` | 源引用规范与置信度标注 |
| `references/learning-methodologies.md` | 学习科学方法论参考 |
| `agents/knowledge-agents.md` | 子智能体角色定义 |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STRICT_SOURCE_MODE` | `true` | 开启严格源引用模式 |
| `NOTEBOOKLM_ENGINE` | `false` | 开启 NotebookLM 增强功能 |
| `KNOWLEDGE_ROOT` | `./` | 知识库根目录 |
| `REVIEW_LIMIT` | `20` | 每次复习最大卡片数 |

## Gotchas

- **引用可追溯**: 所有知识声明必须标注来源。格式 `[Source: 材料名, 页码/P#/时间戳]`
- **不可验证的断言必须标记**: 无源材料支撑的内容必须标注 `[unverified]`
- **NFE（NotebookLM Engine）默认关闭**: 开启后启用音频概述等重量级功能，不影响严格模式
- **原子笔记原则**: 一个概念一条笔记，通过 `[[wiki-link]]` 连接
- **复习至上**: 不复习的学习等于没学。定期运行 `/review`
- **源材料优先路由**: 先查已导入材料，找不到再降级询问用户
- **渐进式提炼**: 从 capture → organize → synthesize 逐层精炼
- **SM-2 算法**: 闪卡默认使用 SM-2 间隔重复算法
- **试卷可配置**: `/exam` 支持 `--difficulty`(easy/medium/hard/mixed) 和 `--format`(choice/fill/short/essay/mixed)
- **图表自动生成**: `/diagram` 自动生成 Mermaid 图表嵌入笔记，思维导图等图像可自动输出
- **习题答案标注来源**: 试卷中的每道题答案均标注 `[Source: ...]` 可追溯

## Workflow (5-Stage Learning Pipeline)

1. **Import (导入)** — 使用 `/import` 将各格式材料导入并自动提取
2. **Extract (提取)** — 自动拆解为 source-grounded 原子笔记
3. **Organize (组织)** — 归类、打标签、建立 `[[wiki-link]]` 连接，生成图表辅助理解（`/diagram`）
4. **Review (复习)** — 通过 `/review`、`/flashcard`、`/exam` 巩固记忆和检验掌握度
5. **Apply (应用)** — 将知识转化为项目产出，使用 `/track` 记录进度
