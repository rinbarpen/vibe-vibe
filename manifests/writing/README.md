# Writing：标书与专利写作场景

将真实材料、正文、图表、审阅和版本组织成可持续修改的写作项目。选择体裁后沿用其专属契约，不把专利保护范围与投标条款混为同一套验收。

## 配置标书项目

需要 Python 3.10+、本地 writing 基础技能来源，以及 z-writing 的随包引擎。在来源仓库根目录执行，目标放在仓库之外：

```bash
python3 scripts/setup-project.py writing "../标书项目" --harness generic --scenario bid --skill z-writing --dry-run
python3 scripts/setup-project.py writing "../标书项目" --harness generic --scenario bid --skill z-writing
python3 scripts/setup-project.py writing "../标书项目" --check
```

预期得到项目入口、bid 规则、写作技能和完整支持文件。然后让 AI 读取 PROJECT_RULES.md，先登记招标材料、条款与证据，再分章编写。支持 100 页以上长任务、检查点恢复、材料/图文提醒、用户真实资料归档、引用追踪与多轮修订；配置不代表已生成实际标书。

[标书首次使用](references/bid-start.md) · [标书契约](references/bid-contract.md) · [长任务](references/long-bid.md) · [修订与参考资料](references/revisions-and-sources.md)

## 配置专利项目

```bash
python3 scripts/setup-project.py writing "../专利项目" --harness generic --scenario patent --dry-run
python3 scripts/setup-project.py writing "../专利项目" --harness generic --scenario patent
python3 scripts/setup-project.py writing "../专利项目" --check
```

专利场景保留已有 chinese-patent 和 omnidraw 整包、交底/支持矩阵模板、附图、审阅及 DOCX 导出流程，不要求 z-writing。实际导出软件条件按技能核对。

[专利首次使用](references/patent-start.md) · [专利执行指南](references/patent-guide.md)

未指定场景时先沿用当前任务和项目简报，不自动启用体裁专属规则。两个场景共享 setup 安装入口和版本/来源原则，保留各自有效的图源与渲染器。历史 init/add 不作为完整支持资源的等价入口。

## 工作流与恢复

[标书 SVG](references/workflow.svg) · [标书图源](references/workflow.json) · [专利 SVG](references/patent-workflow.svg) · [专利图源](references/patent-workflow.json)

在配置项目根目录或模板源码目录，分别执行：

```bash
python3 scripts/render_workflow.py --source references/workflow.json --output references/workflow.svg --check
python3 scripts/render_patent_workflow.py --source references/patent-workflow.json --output references/patent-workflow.svg --check
```

去掉 --check 可重新生成对应图；图描述规则而非执行状态。配置回滚使用 setup 打印的 restore.py；文稿版本按对应项目记录恢复，不把两者混用。宿主重新加载、原生格式制作和全量页面审查均以实际执行为准。
