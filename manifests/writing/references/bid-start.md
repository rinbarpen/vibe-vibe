# Writing：标书编写场景

把招标要求、企业证据和逐章稿件串成可追溯的投标响应项目。支持 100 页以上标书的分批编写、检查点恢复、反复修改、用户资料接收、引用追踪及材料/图文补充提醒；具体目录、表单、签章和提交要求始终以项目材料为准。

## 创建一个标书项目

前提：Python 3.10+，本地 vibe-coding 来源可用；`z-writing` 及其随包引擎已就绪。在仓库根目录执行，目标路径换成自己的业务项目：

```bash
python scripts/setup-project.py writing "../标书项目" --harness generic --scenario bid --skill z-writing --dry-run
python scripts/setup-project.py writing "../标书项目" --harness generic --scenario bid --skill z-writing
python scripts/setup-project.py writing "../标书项目" --check
```

预期得到 `PROJECT_RULES.md`、`AGENTS.md` 导入、`rules/writing/` 规则包、写作技能以及 `templates/`、`references/`、`scripts/`。已有项目内容受 setup 冲突检查和备份事务保护。本模板以跨平台 **setup** 为完整安装入口；旧 `init/add` 的通用复制布局不分发本场景全部支持资源，不作为等价入口。

在新项目中告诉 AI：

> 读取 PROJECT_RULES.md，按 writing 契约开始这份标书。招标文件在 sources/；先登记版本和哈希，提取否决项、资格项、评分项和提交要求，建立 bid.json 响应矩阵与待补清单，再依据真实材料逐章编写。资料缺口先标出，不补造事实。

还没有材料时也可以初始化工作副本：将 [简报](../templates/brief.md) 保存为 `brief.md`，[矩阵](../templates/project.json) 保存为 `bid.json`，[目录](../templates/outline.md) 保存到 `draft/outline.md`，把 [审查清单](../templates/review-checklist.md) 和 [决定记录](../templates/decisions.md) 保存到 `review/`。只创建缺少的文件，不覆盖现有稿件。默认目录和字段详见 [首次使用及矩阵说明](bid-guide.md)。

## 编写和验收的边界

`z-writing` 负责大纲、正文与保真润色；本场景负责投标条款、证据、人工业务决定和版本闭环。标书命令用 --skill z-writing 显式追加正文能力；writing 基础包保留 patent 已有的 chinese-patent 与 omnidraw 依赖。Word/PDF 等最终格式按实际可用的 Office/格式技能组合，另行完成原生文件与全量页面 QA；配置完成不等于已产出标书或完成投标。

在项目根目录检查矩阵：

```bash
python scripts/check_bid.py bid.json --mode draft
python scripts/check_bid.py bid.json --mode release
```

空模板的 draft 会提示待补，release 会失败。结构就绪不代表已经通过业务复核、获得评分或取得签署/提交许可。[协作契约](bid-contract.md) 说明返工、等待、业务决定与恢复规则。

## 编写 100 页以上的标书

按 [长标书执行说明](long-bid.md)，将 [长任务模板](../templates/long-task.json) 保存为 `long-task.json`，为当前章节建立 [任务包](../templates/chapter-brief.md)。模板的 101/120 页与八章预算是可调整的规划示例；实际篇幅由招标规则与最终排版计数确定。

```bash
python scripts/long_task.py status long-task.json
python scripts/long_task.py next long-task.json
python scripts/long_task.py report long-task.json --output review/supplements.md
```

AI 分章/分小节持续写作，保存正文位置和下一动作；章节审查后登记哈希检查点。中断后从当前章节恢复，不重写输入未变的已验收章节。补充报告列出缺什么、影响哪章、需要谁提供什么，以及架构/流程图、进度/人员表、真实照片和附件的具体需求；每批工作后向用户提示新增重要缺口。

脚本管理状态而非后台运行模型；宿主停止后保留可恢复状态。最终仍需完成原生文件、实际页数统计、全页 QA 与定稿决定，不把页数预算或完成标记当成已经写完 100 页。

## 多轮修改与用户参考资料

按 [修订与来源说明](revisions-and-sources.md)，保留用户上传原件及版本，核对正文中的事实/引用与实际原页位置；文风参考和投标事实分开。新上传材料不自动替换旧来源，也不覆盖用户手改。

修改前/后可保存 REV-001、REV-002 等快照，用只读 diff 查看直接影响和依赖章节。恢复版本前先预览，实际恢复自动保留恢复前状态；新上传原件和未纳入目标版本的新文件继续保留。命令、引用结构及 [修订记录模板](../templates/revision-request.md) 见上述说明。

## 工作流与维护

[工作流 SVG](workflow.svg) · [可编辑 JSON](workflow.json) · [标准库渲染器](../scripts/render_workflow.py)。在模板源码目录或安装项目根目录重建并检查：

```bash
python scripts/render_workflow.py --source references/workflow.json --output references/workflow.svg
python scripts/render_workflow.py --source references/workflow.json --output references/workflow.svg --check
```

图描述规则，不代表实时进度。setup 输出当前事务的 `restore.py` 路径；需要撤销配置时使用该次实际打印的恢复命令。业务稿件按协作契约保存前版再回退，不用配置回滚覆盖业务成果。

若本地 `z-writing` 引擎尚未检出，仅初始化其实际需要的来源；不要拉取全部技能。源码路径与检查步骤见 [依赖准备](bid-guide.md#依赖准备)。宿主需重新加载项目指令与技能；文件检查不冒称已观察到宿主激活。
