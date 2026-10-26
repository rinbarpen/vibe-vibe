# Knowledge-Learning Manifest

上传教材后，助手先分析目录、章节与知识依赖，再结合学习目标和已有基础，生成**有教材依据的章节学习路线**。支持既有 PPT、PDF、视频、网页、音频和图片处理能力；实际提取依赖当前助手可用的读取/OCR/转录工具，不自带解析服务。

## 快速开始

```bash
# 初始化新项目（四选一的可选场景）
vibe init knowledge-learning my-learning-project --scenario course-learning
# 或给已有项目加入模板
vibe add manifest knowledge-learning existing-project
# 预览；默认保留已有文件，--force 只覆盖模板对应文件
vibe init knowledge-learning my-learning-project --dry-run
```

在目标项目启动助手后，上传教材附件或给出可访问的材料路径。助手会自动：

1. 轻量索引目录、章节边界和必要抽样，先展示教材地图及解析缺口。
2. 复用已知信息，仅补问缺失的目标、已有基础和已学章节。
3. 生成章节路线，列出学习顺序、章节定位、重点问题、教材练习和完成标准。

也可显式使用助手指令：

```text
/import path/to/textbook.pdf
/learn --plan --material path/to/textbook.pdf
/learn 线性代数 --plan
```

`--plan` 是助手的 `/learn` 指令参数，不是 `vibe init` 或 `vibe add` 参数。自然语言“根据上传的教材规划学习”进入同一流程。普通 `/learn <topic>` 仍然开启学习会话。

## 规划产物

```text
projects/<教材或主题>/
├── MATERIAL_INDEX.md    # 材料清单、章节地图、页码体系、解析完整度
└── LEARNING_PATH.md     # 学习目标、已有基础、章节路线、重点与完成标准
```

- 未限定范围时覆盖所选教材；基础未知标为未确认，不假定已掌握。
- “前置准备 → 基础 → 核心 → 进阶与综合”是可选规划分组，不是新增教材章节。
- 路线基于真实章节；教材明确的依赖与助手推荐顺序分别标明。
- PDF 页序与印刷页码分列；未知页码用已确认章节标题，不编造定位或习题编号。
- 扫描件/目录缺失时只记录已识别范围与待补资料，多份教材先分别索引再验证映射。
- 默认只规划章节路线，不安排每日课表、固定周期或持续陪学。不要求上传后先生成整本笔记和闪卡。
- 原有 `COURSE_PLAN.md.example` 日历模板仍保留，供明确要求时间安排的独立任务使用。

选定章节后，可继续使用 `/learn`、`/study`、`/flashcard`、`/review`、`/exam`、`/mindmap`、`/diagram`、`/track`，共 9 个指令。

## 安装布局

| 资源 | 目标项目位置 |
|------|--------------|
| 项目指令与配置 | 根目录 `CLAUDE.md`、`AGENTS.md`、`README.md`、`.cursorrules` |
| 指令索引和全部具体指令 | `.cursor/commands/` |
| 核心规则、可选场景规则 | `.cursor/rules/`；场景说明 `.cursor/scenario.md` |
| 内置技能、参考和角色说明 | 根目录 `skills/`、`references/`、`agents/` |
| 索引、路线、笔记等模板 | `.cursor/templates/` |

内置技能入口为 `skills/SKILL.md`，由入口指令按任务读取；不是 `vibe add skill` 的全局技能注册，也不新增原生子 Agent。默认安装保留已有文件，`--force` 逐文件替换模板对应内容，额外自建文件及已有 `notes/_index.md` 保留。

可选场景：`self-study`、`exam-prep`、`course-learning`、`research-reading`。`--scenario` 用于 `vibe init`；已有项目的 `vibe add manifest` 维持原接口。

## 环境设置

默认 `STRICT_SOURCE_MODE=true`、`NOTEBOOKLM_ENGINE=false`；章节索引与规划不需要开启增强引擎。在启动助手的 shell 中可设置：

```bash
export STRICT_SOURCE_MODE=true
export NOTEBOOKLM_ENGINE=true  # 可选增强功能
```

初始化不持久化环境变量、不创建或自动加载 `.env`，也不接受 `--strict` / `--notebooklm` 初始化选项。助手指令 `/import --strict` 保留原语义。

## 验收

开发者可使用 `evaluations/README.md` 的教材样例检查上传、问询与路线质量。安装和资源契约由 CLI 单元/集成测试验证；静态检查不等于实际模型端到端验收。

## License

MIT
