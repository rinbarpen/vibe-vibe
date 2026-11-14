# Writing：专利编写场景

将技术交底、已有方案或专利草稿组织成可持续修订的写作项目。首个场景 `patent` 覆盖规划、附图、说明书与权利要求起草、审阅和 DOCX 导出；具体制作复用仓库已有的 `chinese-patent` 与 `omnidraw` 技能。

## 配好项目并开始写

需要 Python 3.10+ 和本仓库的两项技能来源；配置本身只用 Python 标准库。**从来源仓库根目录**执行，目标放在仓库之外；已有项目可使用相同入口：

```bash
python3 scripts/setup-project.py writing ../patent-project --harness generic --scenario patent --dry-run
python3 scripts/setup-project.py writing ../patent-project --harness generic --scenario patent
python3 scripts/setup-project.py writing ../patent-project --check
```

预期出现 `PROJECT_RULES.md`、`AGENTS.md` 导入、`rules/writing/`、完整技能包与下方的工作流/模板。配置只准备工作约定，不生成虚构的专利成稿。Windows 使用探测到的 Python 3.10+ 命令；已安装 CLI 时可使用等价的 `vibe setup writing <目标目录> --harness generic --scenario patent`。

随后在目标目录让助手读取 `PROJECT_RULES.md`，给它实际技术交底，例如：

> 按 patent 场景继续。先读取我的技术交底和已有文稿，梳理技术问题、必要技术特征与待补材料；输出专利规划和权利要求支持矩阵，不编造实验数据。已有明确决定直接复用。

需要简报时复制 [交底模板](templates/patent-brief.md) 到项目的 `brief.md` 并填写；已有材料直接引用，不重新抄录。以项目的 `MANIFEST.md` 为唯一产物账本；开始制作时沿用已有账本，或复制 [账本模板](templates/patent-ledger.md) 后记录工作路径。配置阶段不创建业务账本，避免将可变状态当作受管资源。阶段验收、人工决定与返工路径见 [执行指南](references/patent-guide.md)。

## 安装内容与运行条件

- `chinese-patent` 整包保留规划、绘图、撰写、审阅子技能、规则、HTML 模板及导出脚本；不把子技能拆开安装，避免共享相对路径失效。
- `omnidraw` 提供专利绘图技能引用的路由；按任务选择已有 Draw.io 或数据图能力，不默认联网生成图。
- 技能放在 `.agents/skills/`；选择 `--harness claude` 或 `both` 时另有 `.claude/skills/` 完整副本，具体宿主是否已加载需在真实会话核对。
- HTML→DOCX 需要本地 Pandoc；PDF 导出、数据图和 Draw.io 的运行条件按技能逐项检测。安装技能不等于安装这些软件。配置与工作流检查不依赖 Pandoc。
- 当前场景面向中国发明/实用新型起草；外观设计、其他辖区或仅有不完整构思时记录分支与待决项。此模板没有申报平台接入，也不以文档生成或静态检查保证授权结果。实际办理前另核对官方当期要求和专业审阅。

本模板的完整场景入口是 **setup**。历史 `init/add manifest` 的通用复制布局不分发这里承诺的场景与完整支持资源，维护时沿用 setup 或项目级 update，不把旧入口的成功当作场景验收。

## 工作流与只读检查

[查看专利工作流 SVG](references/patent-workflow.svg) · [编辑 JSON 源](references/patent-workflow.json) · [随包渲染器](scripts/render_patent_workflow.py)

在**已配置项目根目录**生成并检查（Python 标准库，无图形服务依赖）：

```bash
python3 scripts/render_patent_workflow.py --source references/patent-workflow.json --output references/patent-workflow.svg
python3 scripts/render_patent_workflow.py --source references/patent-workflow.json --output references/patent-workflow.svg --check
```

在**来源仓库根目录**维护时使用：

```bash
python3 manifests/writing/scripts/render_patent_workflow.py --source manifests/writing/references/patent-workflow.json --output manifests/writing/references/patent-workflow.svg
python3 manifests/writing/scripts/render_patent_workflow.py --source manifests/writing/references/patent-workflow.json --output manifests/writing/references/patent-workflow.svg --check
```

`--check` 只读；缺图/漂移返回 1，无效节点或引用返回 2。图中区分 AI 制作、AI 审阅与人工决定；缺技术材料的等待、保护范围决定、取消和文稿回退均有恢复位置。图不记录任务进度。

## 维护与恢复

更新前保留文稿与账本，先预览同一 setup 命令，或使用自动登记的真实项目名运行 `vibe project update <项目名> --dry-run`。更新保留已有业务文件，用户改过的受管资源会报冲突，先核对差异再继续。不要直接修改 `rules/writing/` 中作为来源副本的模板来存放正文。

安装/更新工具打印本次备份的 `restore.py` 绝对路径；需要撤回配置时执行 `python3 <本次备份目录>/restore.py`。文稿修订则依据账本恢复具体版本，两者不混用。
