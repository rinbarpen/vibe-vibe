# CLAUDE.md

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

针对小说创作的项目上下文管理。

## 创作命令

| 命令 | 描述 |
|---------|-------------|
| `vibe-outline` | 查看/更新小说大纲 |
| `vibe-characters` | 查看角色设定卡 |
| `vibe-world` | 查看世界观设定 |
| `vibe-progress` | 统计章节字数与进度 |
| `vibe-check-logic` | 检查剧情逻辑一致性 |

## 快速上手（新项目初始化）

```bash
# 1. 创建项目目录结构
mkdir -p chapters outline characters world research drafts
mkdir -p outline/arcs

# 2. 创建大纲和角色模板
cp templates/outline-template.md outline/main.md
cp templates/character-card-template.md characters/list.md

# 3. 初始化伏笔追踪
touch .vibe-foreshadow.json
echo '{"foreshadows": []}' > .vibe-foreshadow.json

# 4. 开始创作
# 使用 vibe-outline 规划 → chapters/ 写作 → vibe-check-logic 验证
```

## 项目结构

```
<root>/
  chapters/    # 章节正文 (Markdown, 命名: CH001_标题.md)
  outline/     # 大纲与剧情线
    main.md         # 主线剧情大纲
    arcs/           # 支线剧情弧
    timeline.md     # 时间线
  characters/  # 角色设定文件
    list.md         # 核心角色索引
  world/       # 世界观、地理、力量体系
    setting.md      # 核心世界观说明
    geography.md    # 地理设定
    magic-system.md # 力量体系
  research/    # 资料收集与参考（项目特定资料）
  references/  # 通用知识域参考（神秘学、神话等）
  templates/   # 创作模板
    chapter-template.md       # 章节模板
    character-card-template.md # 角色卡模板
    outline-template.md       # 大纲模板
  rules/       # AI 行为规则文件
    vibe-novel-character.mdc   # 角色一致性
    vibe-novel-narrative.mdc   # 叙事规范
    vibe-novel-plot.mdc        # 剧情逻辑
    vibe-novel-quality-gate.mdc # 质量门禁
  scripts/     # 辅助脚本
    foreshadow-tracker.sh     # 伏笔追踪
    word-count.sh             # 字数统计
  drafts/      # 废弃稿件与灵感碎片
```

## 知识参考 (Knowledge References)

创作涉及特定题材时，AI 应优先查阅以下参考以保持术语与典故的准确性：

| 领域 | 文件 |
|------|------|
| 神秘学 | `references/occult-knowledge.md` |
| 希腊神话 | `references/greek-mythology.md` |
| 北欧神话 | `references/norse-mythology.md` |
| 中式神话 | `references/chinese-mythology.md` |
| 日式神话 | `references/japanese-mythology.md` |
| 克苏鲁神话 | `references/cthulhu-mythos.md` |
| 修仙 | `references/cultivation-knowledge.md` |
| 异世界 | `references/isekai-knowledge.md` |
| 科幻 | `references/sci-fi-knowledge.md` |
| SCP 基金会 | `references/scp-foundation.md` |
| 灵能 | `references/psionic-knowledge.md` |

- `references/` 为通用知识域，`research/` 为项目特定资料。

## 关键文件

- `outline/main.md` - 主线剧情大纲
- `characters/list.md` - 核心角色索引
- `world/setting.md` - 核心世界观说明
- `templates/` - 章节/角色卡/大纲模板
- `.vibe-foreshadow.json` - 伏笔追踪数据（自动管理）

## 创作风格指南

- **视角控制**：明确每一章的 POV (Point of View)
- **描写偏好**：侧重动作与心理，避免过度形容词堆砌
- **对话风格**：符合角色身份背景，避免 OOC (Out Of Character)
- **展示而非叙述**：Show, Don't Tell

## 创作流程（Vibe Writing）

1. **灵感 (Ideate)**: 在 `drafts/` 记录灵感碎片，调用 `muse` 扩展
2. **大纲 (Outline)**: 在 `outline/` 维护主线与支线，由 `editor` 审核结构
3. **草拟 (Draft)**: 在 `chapters/` 编写初稿，保持流畅度
4. **逻辑校验 (Verify)**: 运行 `vibe-check-logic --full` 扫描一致性
5. **伏笔记录 (Track)**: 使用 `scripts/foreshadow-tracker.sh add` 记录新伏笔
6. **润色 (Polish)**: 调用 `stylist` 对重点段落进行风格化处理
7. **进度更新 (Progress)**: 运行 `scripts/word-count.sh --target <目标字数>` 更新进度

## 验证流程（质量门禁）

每一章完成前必须通过以下检查：

- [ ] 逻辑自洽：新章节是否与之前的设定冲突？
- [ ] 伏笔检查：使用 `scripts/foreshadow-tracker.sh report` 检查未回收伏笔
- [ ] 人设校验：角色是否 OOC？
- [ ] 语气校验：是否符合小说整体基调？
- [ ] 字数达标：使用 `scripts/word-count.sh` 检查各章节分布

## 量化指标

| 指标 | 参考标准 |
|------|----------|
| 每章字数 | 3000-5000 字 |
| 总字数目标 | 由作者设定（参考: 网文30-100万字，轻小说8-15万字） |
| 伏笔回收率 | >80%（完本时） |
| 质量门禁通过率 | 100%（每章必须全通过） |

## 协作流

- **灵感阶段**：在 `drafts/` 记录碎片
- **细化阶段**：将灵感转化为 `outline/` 中的具体情节
- **创作阶段**：在 `chapters/` 编写正文
- **校验阶段**：运行 `vibe-check-logic --full`
- **润色阶段**：调用 AI 进行遣词造句的优化