from pathlib import Path
import json, os, re, shutil, hashlib
ROOT=Path.cwd(); M=ROOT/'manifests/office'; S=ROOT/'mine/office'; A=ROOT/'.planning/office-skill-separation/artifacts'
def put(p,text):
    p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name(p.name+'.tmp'); t.write_text(text,encoding='utf-8'); os.replace(t,p)
# Preserve the one narrow update-selector change before editing user work.
baseline=json.loads((A/'baseline.json').read_text())
extra='tools/vibe_tool/src/vibe_tool/manifest_update.py'
p=ROOT/extra; q=A/'baseline'/extra; q.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,q)
baseline['scopes'].append(extra); baseline['files'][extra]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':p.stat().st_mode&0o777}
put(A/'baseline.json',json.dumps(baseline,ensure_ascii=False,indent=2)+'\n')
S.mkdir()
for name in ('docx','xlsx','pptx','pdf','planning','agents','assets'):
    shutil.move(str(M/name),str(S/name))
(S/'rules').mkdir(); (S/'scripts').mkdir()
for p in list((M/'rules').iterdir()):
    if p.suffix=='.md': shutil.move(str(p),str(S/'rules'/p.name))
    elif p.suffix=='.mdc': p.unlink()
for p in list((M/'scripts').iterdir()):
    if p.is_file() and p.name not in {'install_office.py','init-office.sh'}: shutil.move(str(p),str(S/'scripts'/p.name))
for host in ('claude','codex'):
    shutil.move(str(M/f'.{host}/agents'),str(S/'agents'/host))
    (M/f'.{host}').rmdir()
# Runtime examples use the standard skill installation layout. The entrypoint
# explicitly resolves other installations rather than assuming this layout.
pattern=r'(?<![\w./-])office/(?=(?:scripts|rules|docx|xlsx|pptx|pdf|planning|agents|README))'
for p in S.rglob('*'):
    if p.is_file() and p.suffix in {'.md','.mdc','.toml','.py','.sh'}:
        text=p.read_text(encoding='utf-8')
        text=re.sub(pattern,'.agents/skills/office/',text)
        text=text.replace('.agents/skills/office/README.md','.agents/skills/office/SKILL.md')
        text=text.replace('Office manifest','Office skill').replace('Office Manifest','Office Skill')
        put(p,text)
for p in (ROOT/'mine/office-quality').rglob('*.md'):
    text=p.read_text(encoding='utf-8'); text=re.sub(pattern,'.agents/skills/office/',text)
    text=text.replace('.agents/skills/office/README.md','.agents/skills/office/SKILL.md')
    text=text.replace('Office manifest 安装时','办公项目 Manifest 安装时')
    text=text.replace('辅助脚本只在 Office manifest 已安装时可用，缺脚本则用可用引擎执行同等检查并记录命令。','通用指南与辅助脚本由 `office` Skill 分发；先发现其实际路径，按需读取或执行。缺脚本则用可用引擎执行同等检查并记录命令。')
    put(p,text)
# Canonical workflow source is JSON with a shipped deterministic stdlib renderer.
(S/'assets/workflow.mmd').unlink()
shutil.copy2(ROOT/'scripts/render-manifest-workflow.py', S/'scripts/render_workflow.py')
shutil.copy2(ROOT/'scripts/render-manifest-workflow.py', M/'scripts/render_workflow.py')
def graph(title,description,nodes,edges):
    return json.dumps({'schema_version':1,'title':title,'description':description,'nodes':[dict(id=i,label=l,kind=k,row=r,detail=d,**kw) for i,l,k,r,d,kw in nodes],'edges':[dict(zip(('from','to','label','kind'),e)) for e in edges]},ensure_ascii=False,indent=2)+'\n'
runtime_nodes=[
 ('start','办公文件任务','terminal',0,'复用本次目标、原稿与已确认约束。',{}),
 ('plan','Office：选择实际能力','ai',1,'按需路由写作、Omnidraw、Omnisheet、Omnippt及格式引擎；同一文件唯一写入者。',{}),
 ('decision','用户决定变化部分','human',2,'仅当目标变化、宏或图表选择等约定门尚未确认时等待；独立工作继续。',{'trigger':'缺少会改变产物的业务选择；复用已有有效决定。','resume':'继续返回制作；调整回计划；取消本项保留原件与记录。'}),
 ('build','制作或局部修复','ai',3,'正文、素材、原生表格与格式工程按已确认来源装配；保留工作副本与编辑源。',{}),
 ('check','结构、原生功能与全量视觉','check',4,'核对内容、数值、宏实际状态、页面/工作表覆盖和输入/最终哈希。',{}),
 ('qa','独立 Office QA','check',5,'另一审查者读取最终文件与证据；缺条件保持 pending，问题回制作人。',{}),
 ('done','成品与证据交付','terminal',6,'仅当前版本全部适用验收有证据时 passed；否则明确未决项，不伪造验证。',{})]
runtime_edges=[('start','plan','复用已知输入','normal'),('plan','decision','本次必要决定待确认','normal'),('plan','build','条件齐备','normal'),('decision','build','继续：有效决定','normal'),('decision','plan','调整约束','rework'),('decision','done','取消本项：保留记录','normal'),('build','check','真实产物与执行记录','normal'),('check','qa','检查与覆盖证据齐备','normal'),('check','build','检查失败：原制作人修复','rework'),('qa','build','发现问题：修复并复验','rework'),('qa','done','通过或明确 pending','normal')]
put(S/'assets/workflow.json',graph('Office Skill：可复用办公能力','能力工作流，不表示某次任务已经运行或获得用户决定。',runtime_nodes,runtime_edges))
project_nodes=[('start','办公项目需求','terminal',0,'报告、会议材料、方案或跨格式交付；保留既有项目内容。',{}),('brief','项目目标与材料版本','ai',1,'整理受众、交付清单、来源、模板/样文、负责人及验收范围；复用已有简报。',{}),('decision','业务决策与范围确认','human',2,'仅处理新目标、约束冲突、对外发布等已约定门；不接管常规实现。',{'trigger':'新业务取舍或约定的高影响门；已确认范围直接进入制作。','resume':'继续交 Office；调整返回简报；取消保留原件并归档本次状态。'}),('office','调用 Office 技能制作','ai',3,'通用写作、图表、格式、宏与检查由 office 及配套 Skills 实现；项目不复制实现。',{}),('review','项目验收与版本核对','check',4,'复用 Office 独立 QA，核对跨格式口径、交付清单和当前版本哈希。',{}),('archive','归档与交付登记','ai',5,'在既有 MANIFEST.md 登记成品、证据、未决项与用户反馈；修订另存版本。',{}),('done','项目阶段交付','terminal',6,'仅按任务范围宣告完成；对外发送另按已有业务决定执行。',{})]
project_edges=[('start','brief','接收或恢复任务','normal'),('brief','decision','需要新业务决定','normal'),('brief','office','范围已确认','normal'),('decision','office','继续','normal'),('decision','brief','调整','rework'),('decision','archive','取消：保留原件与记录','normal'),('office','review','成品与独立 QA 证据','normal'),('review','office','问题清单：局部修复','rework'),('review','archive','通过或明确 pending','normal'),('archive','done','登记版本与状态','normal')]
put(M/'assets/workflow.json',graph('办公项目 Manifest：业务协作契约','项目工作方式与通用 Office 能力分层；图只描述规则，不代表实际进度。',project_nodes,project_edges))
put(S/'SKILL.md','''---
name: office
description: "制作、编辑与验收 Word、Excel、PowerPoint、PDF 办公文件；按需协调正文与样本文风、图表素材、原生格式、公式/动态域、宏与全量视觉检查。用于单次文件任务和跨格式交付，不要求初始化办公项目；项目组织由办公 Manifest 负责。"
---

# Office

办公文件的可复用能力入口。按实际任务选择写作、图表与格式引擎，保留原件、原生可编辑内容和真实验收证据；无需先安装某个 Manifest。

![Office 能力工作流](assets/workflow.svg)

## 开始与路径

本技能根目录是包含当前 `SKILL.md` 的目录，记作 `OFFICE_SKILL_ROOT`。先读 [质量规则](rules/quality.md)、[文件保护](rules/file-safety.md)，再只读本次格式指南。正文/数据/产物与记录留在用户项目，不写回技能目录。

指南里的 `.agents/skills/office/…` 是 vibe 默认安装布局示例；技能位于其他目录时按实际根目录替换。不要依赖源码仓库的 `manifests/office`、项目根 `office/` 或创作者机器路径。其他技能同样通过宿主发现实际入口，默认安装名不是路径存在的证明。

## 按任务路由

| 任务 | 本包指南 | 配套能力（实际存在时按需加载） |
| --- | --- | --- |
| 正文起草、润色与参考样本文风 | [图文与文风交接](docx/references/voice-and-visuals.md) | `ai-vibe-writing`；仅纠错不扩大为重写 |
| 图片、示意图和数据绘图 | [素材交接](agents/subagent-roles.md) | `omnidraw`，使用随包 UI 约束及真实来源 |
| 表格数据、模型和布局 | [XLSX 指南](xlsx/CLAUDE.md) | `omnisheet`，原生表格仍交最终格式工程师插入 |
| Word 文件工程 | [DOCX 指南](docx/CLAUDE.md)、[规则](rules/docx.md) | 精确来源 `anthropics/skills/docx` |
| 工作簿 | [XLSX 指南](xlsx/CLAUDE.md)、[规则](rules/xlsx.md) | 精确来源 `anthropics/skills/xlsx` |
| 演示文稿 | [PPTX 指南](pptx/CLAUDE.md)、[规则](rules/pptx.md) | `omnippt` → `anthropics/skills/pptx` |
| PDF 操作 | [PDF 指南](pdf/CLAUDE.md)、[规则](rules/pdf.md) | 精确来源 `anthropics/skills/pdf` |
| 复杂或跨格式任务 | [规划指南](planning/CLAUDE.md) | 复用已确认目标、材料、来源与口径 |
| 最终验收 | [质量规则](rules/quality.md)、[角色与交接](agents/subagent-roles.md) | `office-quality` 与当前格式能力 |

配套技能缺失时只检查本次所选能力，并明确相应未决项；不启动无关外部服务、不安装全套系统依赖。本包提供通用指南与工具，格式引擎是可组合依赖，不把第三方 Skill 复制进本包。

## 制作、检查与交付

- 编辑前记录源 SHA-256，使用工作副本；同一最终文件只有一个写入者。保留未选内容、模板、样式、公式、批注、修订、关系和宏。
- 样文、正文主张、来源/数据、图表类型、编辑源、题注、替代文本和交叉引用共同规划；已知输入直接沿用，无信息价值时不加装饰。
- Word 公式交付可编辑 OMML，动态编号/引用实际更新后核验；[公式与域](docx/references/equations-and-fields.md) 和 [原生排版/宏](docx/references/native-formatting.md) 按需加载。
- 宏源码、项目保留与实际应用编译/执行分别验收。宏或新增图表的决定沿用已有明确范围；未决时继续独立工作，不把文件存在当成运行成功。详见 [Excel](xlsx/references/charts-and-macros.md) 与 [PPTX](pptx/CLAUDE.md)。
- 重新打开最终文件，核对内容、数据与原生特性，再实际查看全部页面；XLSX 核对全部表的数据/公式和约定打印视图。修订后更新哈希、检查和预览。
- 创建/修改交付文件后取得独立 QA；可用角色源为 [Claude](agents/claude/) / [Codex](agents/codex/)，只选择本次角色。独立上下文不可用时记录该门 pending，不把制作人自检冒充独立 QA。只读提取使用轻量来源核对。
- 输出 `draft` / `pending` / `passed`、路径/哈希、实际命令与退出状态、检查与覆盖证据和剩余项。只依据当前最终版本；项目已有 `MANIFEST.md` 时追加登记，不另造重复账本。

## 随包工具

先将环境变量 `OFFICE_SKILL_ROOT` 指向实际发现的技能根目录，然后按需运行：

```bash
python "$OFFICE_SKILL_ROOT/scripts/doctor.py"
python "$OFFICE_SKILL_ROOT/scripts/verify.py" FILE --output REPORT.json
python "$OFFICE_SKILL_ROOT/scripts/render.py" FILE --out-dir PREVIEWS
```

Word 原生检查/排版工具位于 `docx/scripts/`，VBA 源位于 `docx/macros/`；Excel 分析/重算及宏保留工具位于 `xlsx/scripts/`，VBA 源位于 `xlsx/macros/`。工具覆盖范围和所选应用执行状态分别报告；不降低全局信任设置或自动运行未知输入宏。

## 安装与项目边界

`vibe add skill office <target>` 只安装本技能，不生成项目根指令、不注册宿主角色、不自动安装其他 Skills。已有文档、科研、基金等项目可以按需复用本能力。完整办公工作区使用 `vibe init office <target>`：业务 Manifest 负责项目简报、来源/版本、交付决策和归档，并显式安装本技能及配套 Skills。

[工作流源](assets/workflow.json)；从本技能根目录再生成及只读检查：

```bash
python scripts/render_workflow.py --source assets/workflow.json --output assets/workflow.svg
python scripts/render_workflow.py --source assets/workflow.json --output assets/workflow.svg --check
```
''')
contract='''# 办公项目协作契约

本模板面向报告、会议材料、方案和跨格式办公交付项目。它管理项目目标、来源/版本、协作与归档；通用文件制作能力由已安装的 [Office Skill](.agents/skills/office/SKILL.md) 提供，不在项目模板中重复实现。

## 从当前任务开始

先读取项目已有简报与材料，明确受众、用途、交付清单、模板/样文、真实来源、允许修改范围和验收要求。简单任务在对话中简要约定；复杂或跨会话任务在项目中保存简报、版本与证据。复用已有明确决定，不为进入工作流重新访谈。

办公任务加载 `.agents/skills/office/SKILL.md`，由它按需选择写作、Omnidraw、Omnisheet、Omnippt、格式引擎和独立 QA。项目安装的原生角色只提供宿主入口，通用角色源由 Office Skill 维护。宿主不支持角色时按该技能的交接规则记录实际审查方式与缺项。

## 项目执行与验证

1. **接收/恢复**：核对目标、当前材料版本与未决项；输入、工作副本、交付和证据分别存放，沿用现有目录。
2. **组织材料**：记录事实/数据/文献/图片来源、日期与版本；同一批多格式交付共用已核对口径和术语。样文风格与事实来源分开。
3. **委托制作**：把具体文件与验收条件交给 Office Skill；技能负责正文、图表、原生对象、宏、格式与检查，项目契约不复制这些实现。
4. **项目验收**：核对交付清单、跨格式内容/数值一致性及当前哈希，复用 Office 的全量预览与独立 QA，不再追加一套重复格式审查。
5. **反馈与归档**：问题定位到具体文件/版本，交原制作人局部修订并复验。保留前版、来源和证据，项目根 [MANIFEST.md](MANIFEST.md) 是唯一产物账本。

## 人工决策与恢复

- 人决定新目标、重要内容/品牌取舍、约定预算或对外发送/发布；AI 负责实现调查、制作、测试与常规返工。
- 缺必要决定时列明对象、版本、选项与影响，仅等待相关动作；独立任务继续。已有有效决定复用，沉默不记为同意。
- 继续后从当前确认版本进入制作；调整则更新简报与受影响要求；取消本项保留原件、已完成成果与记录。覆盖/回退使用实际备份，核对恢复结果。

## 交付与项目状态

在 MANIFEST.md 追加成品与证据路径、版本/哈希、实际覆盖、QA、决定及未决项。使用 Office 的 draft/pending/passed 状态，不把生成文件或结构检查成功当作完整验收。对外发送不是制作任务的默认附带动作。

稳定接入说明为 `office/README.md`；需要简报时复用 `office/templates/task-brief.md`。工作流、可编辑源和复现命令见该说明，图描述规则而非真实任务状态。
'''
put(M/'AGENTS.md',contract); put(M/'CLAUDE.md',contract.replace('# 办公项目协作契约','# 办公项目协作契约（Claude Code）',1))
put(M/'README.md','''# 办公项目 Manifest

把报告、会议材料、方案等办公交付组织成可追溯项目：管理目标、材料来源、样文/模板、跨格式版本、验收与归档。Word/Excel/PowerPoint/PDF 的通用能力由 **Office Skill** 提供；单次文件任务直接安装 Skill，无需建立办公项目。

## 开始使用

前提：本地技能来源已就绪，已配置 vibe 仓库。新项目：

```bash
vibe init office "./office project"
```

预期得到项目协作入口、`office/` 项目说明与工作流、`.agents/skills/office/` 及配套技能；实际文件任务由 Office Skill 按需执行。初始化不运行宏、不启动模型服务、不改全局配置。

已有项目先预览再安装；既有入口和文件默认保留：

```bash
vibe add manifest office "./existing project" --dry-run
vibe add manifest office "./existing project"
```

若根指令被保留，在其中加入：**办公项目任务先读 `office/README.md`，文件制作加载 `.agents/skills/office/SKILL.md`。**

只需要办公能力，而不是项目模板：

```bash
vibe add skill office "./existing project"
```

该命令只复制 Office Skill；配套写作、绘图和格式技能通过现有环境发现或按需另装，不隐式递归安装。

## 两层职责与安装布局

| 层 | 负责内容 | 唯一来源 |
| --- | --- | --- |
| 办公项目 Manifest | 目标、来源/版本、业务决定、交付清单、反馈与归档 | 本模板 |
| Office Skill | 通用办公路由、格式指南、原生功能/宏、工具、角色源和验收 | `mine/office/`（仓库位置） |
| 配套 Skills | 正文/样文、图片、表格、演示设计、格式引擎与质量审查 | 各技能自己的包 |

项目中 `office/` 仅含项目说明、简报模板、业务规则与工作流再生成资源；通用指南/工具位于 `.agents/skills/office/`。`skills.txt` 显式声明 Office 和九项配套依赖，缺来源会返回非零。原生 Claude/Codex 角色从 Office Skill 的同一份源安装到宿主目录，单独安装 Skill 不注册这些角色。

[项目简报模板](templates/task-brief.md)。产物仍追加至项目根 MANIFEST.md；不写进已安装技能。

## 项目工作流

![办公项目工作流](assets/workflow.svg)

[可编辑 JSON 源](assets/workflow.json) · [标准库渲染器](scripts/render_workflow.py)。安装后从项目根目录执行：

```bash
python office/scripts/render_workflow.py --source office/assets/workflow.json --output office/assets/workflow.svg
python office/scripts/render_workflow.py --source office/assets/workflow.json --output office/assets/workflow.svg --check
```

在本模板源码目录中运行时，将命令中的 `office/` 前缀去掉。图描述规则，不表示实际制作、用户决定或 QA 已完成。

## 已有 Office 项目的更新

旧版项目先安装新能力，再更新契约：

```bash
vibe add skill office "./existing project"
vibe update manifest office "./existing project" --dry-run
vibe update manifest office "./existing project"
```

更新保留项目数据、README 和产物账本；未安装的其他依赖仍按现有 update 语义跳过。旧 `office/docx` 等目录不会被自动删除，也不覆盖其中的用户内容；新任务读取 Skill 内的新路径。旧项目若自行定制了入口，应同步调整其读取位置。资源更新生成备份与独立恢复命令，按实际打印路径回退。

宏源码、宏包保留、真实应用编译/执行分别验收；安装 Office Skill 不代表当前环境已有 Microsoft Office。具体能力、限制和调用入口以已安装 Office Skill 为准。
''')
put(M/'templates/task-brief.md','''# 办公项目任务简报

- 目标、读者与使用场景：
- 本次交付清单、格式与目标版本：
- 输入材料、来源/日期/版本与模板：
- 样文、品牌及已确认偏好：
- 允许修改范围与需保留内容：
- 多格式共享事实/数据与单位：
- 项目验收条件与证据位置：
- 必要业务决定、原话来源与有效范围：
- 当前状态、未决项与下一步：

文件制作、图表与宏的具体约定交 Office Skill，不在此重复技术清单。成果在既有 MANIFEST.md 追加登记。
''')
put(M/'rules/office-project.md','''---
always: true
---

# 办公项目规则

项目先复用既有目标、来源/版本、模板/样文和交付清单。文件制作读取 `.agents/skills/office/SKILL.md`；格式、宏与验收工具由该技能维护，不从旧 `office/docx` 等目录加载实现。

跨格式共用已核对的数据与术语；用户项目数据不写回已安装 Skill。新目标、约束冲突及对外动作按本次真实决定处理，等待仅限相关动作；常规制作和返工由 AI 继续。保留原件与前版，复用 Office 的当前版本 QA 证据，在根 MANIFEST.md 追加交付记录。
''')
old=(M/'skills.txt').read_text(); put(M/'skills.txt','# Project dependencies; format implementations live in their own Skills.\noffice\n'+old)
# Update descriptions without reformatting existing bilingual catalogs.
for rel,old,new,section in [
 ('docs/catalog.md','| `office` | DOCX / XLSX / PPTX / PDF：正文写作、原生可编辑交付、全量视觉验收与独立 QA |','| `office` | 办公交付项目：目标、来源与版本、跨格式协作、验收与归档；包含 Office Skills |','### 项目模板（Manifests）'),
 ('docs/catalog_EN.md','| `office` | DOCX / XLSX / PPTX / PDF: substantive writing, native editable delivery, full visual acceptance, and independent QA |','| `office` | Office-delivery projects: goals, sources and versions, cross-format coordination, acceptance and archiving; includes Office Skills |','### Manifests')]:
 p=ROOT/rel; text=p.read_text(); text=text.replace(old,new)
 paragraph=('### Office：能力与项目分层\n\n`vibe add skill office <target>` 安装通用办公能力；`vibe init office <target>` 创建办公项目并安装 Office 与配套技能。格式指南、宏和验证工具的唯一来源为 [Office Skill](../mine/office/SKILL.md)，项目协作契约见 [办公 Manifest](../manifests/office/README.md)。\n\n' if rel.endswith('catalog.md') else '### Office: capability and project layers\n\n`vibe add skill office <target>` installs reusable office capabilities. `vibe init office <target>` creates an office-delivery project and installs Office plus companion Skills. Format guides, macros and verification tools live in the [Office Skill](../mine/office/SKILL.md); project coordination belongs to the [office Manifest](../manifests/office/README.md).\n\n')
 text=text.replace(section,paragraph+section); put(p,text)
for rel,entry in [('skills/ANNOTATIONS.md','\n### office\n- **路径**: `mine/office`\n- **简介**: 可复用办公能力：正文/样本文风、图表、原生格式/宏和可追溯验收；与办公项目 Manifest 分层。\n- **使用场景**: 单次文件任务使用 `vibe add skill office <target>`；项目级协作使用包含该能力的 `vibe init office <target>`。\n'),('skills/ANNOTATIONS_EN.md','\n### office\n- **Path**: `mine/office`\n- **Description**: Reusable office capability for writing/voice, visuals, native formats/macros and traceable acceptance, separate from project coordination.\n- **Usage**: Use `vibe add skill office <target>` for file tasks; use `vibe init office <target>` for an office project with companion Skills.\n')]:
 p=ROOT/rel; put(p,p.read_text()+entry)
# Narrowly include the business project's managed resources in legacy update.
p=ROOT/'tools/vibe_tool/src/vibe_tool/manifest_update.py'; text=p.read_text(); marker='    if name == "auto-research":\n'
insert='    if name == "office":\n        return any(_under(relative, Path(root)) for root in (\n            "office/rules", "office/scripts", "office/assets", "office/templates",\n        ))\n'
assert marker in text; put(p,text.replace(marker,insert+marker,1))
print('Moved runtime resources into',S)
