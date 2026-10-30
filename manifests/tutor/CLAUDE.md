# Tutor Manifest

根据对话配合你的学习导师：有教材按材料学，没有教材也能直接学；自动保存图文笔记与真实学习记录，按需导出 PDF。

## Start with a Conversation

- “为什么平均数不适合概括颜色？” → 直接解释，不先要求上传教材。
- “我想系统学统计，只有算术基础。” → 简短导学后开始一个单元。
- 上传教材并说“讲第二章” → 定位相关章节后辅导，不先生成全书路线。
- “提示一下”“完整讲一遍”“先别问我”“继续上次” → 根据当前任务自动处理，不要求切换模式。

只上传教材时轻量索引并简要展示 `MATERIAL_INDEX.md`，再问一个方向问题；明确要求规划才生成 `LEARNING_PATH.md` 并停止。详见 `references/tutor-interaction.md` 和 `AGENTS.md`。

## Nine Optional Commands

| Command | Description |
|---------|-------------|
| `/import <path/url>` | 索引材料并简要展示已验证结构，不强制规划 |
| `/learn <topic> [--export pdf]` | 有/无教材主题辅导，自动图文 Markdown |
| `/learn [topic] --plan [--material <path>]` | 只规划：有教材真实章节，无教材建议主题单元 |
| `/study <material>` / `/study --next` | 深入当前材料或恢复待答任务与确认位置；可 `--export pdf` |
| `/review [topic]` | 有卡片 SM-2，无卡片按记录、笔记和问题复习 |
| `/flashcard <topic>` | 按需创建闪卡，不作为学习必经步骤 |
| `/mindmap <topic>` | 整理真实或明确标注的概念关系 |
| `/exam [topic] [--paper]` | 默认逐题；试卷模式题面与答案分开 |
| `/diagram <concept>` | 生成实际可见的图解 |
| `/track [scope]` | 只读查看记录、证据、问题和续学状态 |

上表 `/learn` 两行是同一个指令，共九个。`--plan`、`--paper`、`--export pdf` 均为助手指令参数，不是 vibe CLI 参数。

## Files and Persistence

- `projects/<教材或主题>/`：有材料才需要 `MATERIAL_INDEX.md`；规划时有 `LEARNING_PATH.md`；`LEARNING_RECORD.md` 保存原文、条件、实际活动及当前辅导状态。
- `notes/summaries/<主题>/`：自动单元 Markdown；`notes/atoms/`：按需概念笔记；`notes/assets/<主题>/`：真实 SVG/PNG 与图源。
- `exports/<主题>/`：按需 PDF，调用 `scripts/export-notes.py`；原 MD/图源保留，个人日志不默认并入。
- `skills/`：内置技能，入口 `skills/SKILL.md`；`references/`：工作规范；`agents/tutor-agents.md`：职责说明，非原生子 Agent。
- `.cursor/commands/`、`.cursor/rules/`、`.cursor/templates/`：指令、规则与模板，保留原课程日历模板供独立需求使用。

学习增量在本轮回复结束前保存；首次建档、阶段总结、明确记录及导出时才提示路径，失败立即说明。继续先读记录，待答题不自答、不当作掌握；`/track` 和纯导出只读。

## References and Defaults

- `references/tutor-interaction.md`：意图路由、教学粒度及低打扰交互。
- `references/learning-path-design.md`：章节/主题路线。
- `references/learning-records.md`：原文、证据、当前辅导状态与恢复。
- `references/illustrated-notes.md`：自动图文笔记和 PDF。
- `references/source-grounding.md`：材料事实、通用讲解、自拟题与待核实信息。

`STRICT_SOURCE_MODE=true` 约束真实教材引用，不要求通用讲解伪造出处；`NOTEBOOKLM_ENGINE=false` 不影响基础能力。沿用 `KNOWLEDGE_ROOT=./`、`REVIEW_LIMIT=20`，环境由启动进程提供，不自动加载 `.env`。默认无每日课表或后台持续排程。
