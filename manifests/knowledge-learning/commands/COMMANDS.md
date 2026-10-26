# Knowledge-Learning Commands

Complete command index for the knowledge-learning manifest.

## Commands

| Command | Description | Subagent | Strict Mode |
|---------|-------------|----------|-------------|
| `/import <path/url>` | 轻量索引教材，展示章节地图并引导规划 | material-processor + curriculum-designer | 教材结构和定位必须可追溯 |
| `/learn <topic>` / `/learn [topic] --plan [--material <path>]` | 原有学习会话；--plan 生成章节路线 | curriculum-designer + note-architect | 教材事实附来源，规划建议单列 |
| `/review [topic]` | SM-2 间隔重复复习 | review-master | 复习时标注原始出处 |
| `/flashcard <topic>` | 从学习材料生成闪卡 | review-master | 每卡标注 `[Source: 材料名, 页码]` |
| `/mindmap <topic>` | 基于学习材料生成知识图谱 | note-architect | 节点标注材料来源 |
| `/study <material>` | 针对特定材料的专项学习 | material-processor | 严格绑定到单个材料 |
| `/exam <topic>` | 生成试卷/习题，支持难度和知识点配置 | exam-generator | 每道题标注 `[Source: ...]` |
| `/diagram <concept>` | 生成图表（流程图/思维导图/对比图等） | note-architect | 图表内容基于源材料 |
| `/track [scope]` | 学习进度追踪与报告 | curriculum-designer | — |

## Subagent Dispatch

| Agent | Trigger | Effect |
|-------|---------|--------|
| material-processor | 上传附件、`/import`, `/study` | 上传先轻量索引；选定学习范围后详细提取 |
| note-architect | 普通 `/learn`, `/mindmap`, `/diagram` | 笔记结构化、图表生成与连接 |
| review-master | `/review`, `/flashcard` | SM-2 调度与复习管理 |
| exam-generator | `/exam` | 试卷生成、难度配置、知识点覆盖率检查 |
| curriculum-designer | 上传后引导、`/learn --plan`、普通 `/learn`, `/track` | 教材章节路线；保留原有学习与进度职责 |

## Execution Priority

Command dispatch follows this order:
0. 上传附件或自然语言“根据教材规划学习”自动进入索引与规划流程；无需额外指令。复用已有索引，仅补问缺失的目标、基础、已学范围。
1. Parse the command and identify topic/material
2. Check `STRICT_SOURCE_MODE` and `NOTEBOOKLM_ENGINE` settings
3. Detect domain/carrier type of the topic
4. Activate the appropriate subagent
5. Execute command logic with source-grounding rules

规划模式输出 `projects/<教材或主题>/MATERIAL_INDEX.md` 与 `LEARNING_PATH.md`，不生成每日课表或全书笔记。`--plan` 是 `/learn` 助手指令参数，不是 vibe CLI 参数；未带该参数的 `/learn` 保持原学习会话。
