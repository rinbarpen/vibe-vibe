# Knowledge-Learning Manifest

教材驱动的知识学习 manifest：**上传教材 → 轻量索引与章节地图 → 确认目标和基础 → 章节学习路线 → 按需学习与复习**。

采用 NotebookLM 风格的严格源引用模式。教材事实可追溯，用户信息与规划建议分别标明依据；基础规划不依赖 NotebookLM 增强功能。

## Commands

共 9 个学习指令，`--plan` 是 `/learn` 的规划模式，不是新的 vibe CLI 参数。

| Command | Description |
|---------|-------------|
| `/import <path/url>` | 轻量索引材料、展示章节地图，并引导规划 |
| `/learn <topic>` | 保留原有结构化学习会话 |
| `/learn [topic] --plan [--material <path>]` | 根据教材生成章节路线 |
| `/review [topic]` | SM-2 间隔重复复习 |
| `/flashcard <topic>` | 从学习材料生成闪卡 |
| `/mindmap <topic>` | 基于材料生成知识图谱 |
| `/study <material>` | 针对特定材料的专项学习 |
| `/exam <topic>` | 生成试卷/习题，支持难度和题型配置 |
| `/diagram <concept>` | 生成概念图表 |
| `/track [scope]` | 学习进度追踪与报告 |

## Upload and Planning Workflow

1. 用户上传附件、给出本地路径或调用 `/import` 时，自动识别材料并保护原件。
2. 先读元信息、目录、章节边界、概览及必要抽样，保存材料索引并展示教材地图；不全量生成笔记或闪卡。
3. 复用对话信息，仅补问缺失的学习目标、已有基础、已学范围；不询问每日时长或截止日期。
4. 使用 `/learn --plan` 对应流程生成章节路线，每个单元有目标、真实章节定位、重点问题、教材练习及完成标准。
5. 用户选择章节后再详细提取、讲解、记笔记；保留原有复习、自测和应用能力。

未指定范围时默认覆盖所选教材；基础未知则标待确认，不默认已掌握。前置准备、基础、核心、进阶与综合是规划分组，不是虚构的教材章节。默认不生成日历课表或持续陪学排程。

## Architecture

```text
<root>/
  materials/              # 原件按载体类型组织
    slides/ pdf/ video/ web/ audio/ exercises/ images/ epub/
  projects/
    <教材或主题>/
      MATERIAL_INDEX.md   # 材料清单、章节地图、解析完整度
      LEARNING_PATH.md    # 目标、基础、章节顺序、完成标准
  notes/atoms/            # 详细学习阶段才按需创建原子笔记
  notes/summaries/
  flashcards/decks/
  flashcards/reviews/
  skills/                 # 随 manifest 安装的内置技能资源
  references/             # 材料处理和来源规范
  agents/                 # 角色说明，非原生子 Agent 注册
  .cursor/commands/       # 完整指令索引与各 COMMAND.md
  .cursor/rules/
  .cursor/templates/      # 索引、章节路线和既有课程日历模板
```

## Key Resources

- `references/learning-path-design.md`：教材索引、规划问询和章节路线流程。
- `references/carrier-types.md`、`references/source-grounding.md`：支持格式与真实定位规范。
- `references/learning-methodologies.md`：学习方法参考。
- `agents/knowledge-agents.md`：角色职责。
- `skills/SKILL.md`：内置技能入口；按任务读取 `skills/<name>/SKILL.md`。
- 初始化后使用 `.cursor/templates/MATERIAL_INDEX.md.example` 和 `.cursor/templates/LEARNING_PATH.md.example`；源模板位于本 manifest 的 `templates/`。

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STRICT_SOURCE_MODE` | `true` | 教材事实和定位必须可追溯 |
| `NOTEBOOKLM_ENGINE` | `false` | 既有增强功能，与严格模式独立 |
| `KNOWLEDGE_ROOT` | `./` | 知识库根目录 |
| `REVIEW_LIMIT` | `20` | 每次复习最大卡片数 |

变量由启动助手的环境提供；初始化不保存环境变量，也不自动加载 `.env`。

## Quality Rules

- 教材内容引用 `[Source: 材料名, 位置]`；用户目标标“用户提供”，建议顺序标“规划建议”或“推荐顺序（推断）”。
- PDF 页序与印刷页码分别记录；未知页码使用已确认的章节标题，不编造章节或习题编号。
- 扫描件、缺少目录或附件尚未可读时，只索引已验证范围，展示待补内容；不假称完成全书解析。
- 多份资料分别索引，验证后才建立章节映射；同名不等于同一知识点。
- 原子笔记一个概念一条，保留 source 与 wiki-link；导入成功不等于学习完成或掌握。
- 原有 `/exam --difficulty/--format`、`/diagram`、SM-2 复习等能力保持不变。
