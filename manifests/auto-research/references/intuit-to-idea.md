# 直觉成题：intuit-to-idea 接入

## 入口与职责

- 用户希望“围绕这个方向问我问题”“沿我的直觉形成课题”，或希望互动细化已有假设时，调用 `$intuit-to-idea`。宽泛方向即可开始，AI 提供具体情境，不要求用户先交出创新点。
- 一次聚焦一个会改变机制或判断的问题，等待用户真实回答；用户说“不知道”时提供可比较的例子；已有判断直接延续。用户要求检索、总结或给出方案时，执行该请求，不为了保持问答而继续追问。
- 用户要求自主发现、批量候选或已有明确执行任务时，沿用 `aris/idea-discovery` 及现有流水线，不强制进入互动模式。
- `grill-me` 负责既有计划前的目标/约束压力测试；`intuit-to-idea` 负责想法形成，二者不互相冒充。已确认的计划不重复审问。

## 与现有生命周期交接

该 skill 不增加生命周期阶段、不替代科研模型绑定、审批门或 checkpoint 工具：

1. 在 `idea/hypotheses/candidates` 形成竞争解释、可测预测、反证条件和最小验证。AI 建议、用户直觉、已核验文献和估计分别标注；相关文献按机制比较，不因关键词相似就淘汰方向，也不把未检出等同于首创。
2. 与 `aris/research-lit` / `aris/novelty-check` 衔接证据核验；缺来源或无法确认的比较保留未验证状态。证据不足回到 `literature/position`；可行性涉及资源取舍时回到 `startup/roadmap`，不静默降低 baseline 或扩展预算。
3. 用户要求书面总结或正式阶段交接时，读取 skill 的 `references/idea-card.md`，将核心内容合并到既有 `refine-logs/contracts/HYPOTHESES.md`；无需另建一套账本。保留未验证假设，不默认保存逐轮对话或公开未发表机制。
4. 在原有 `idea/hypotheses/comparison` 形成 `refine-logs/contracts/IDEA_DECISION.md`，沿用其 `human_confirmation` 门。用户同意后进入 `idea/method/mechanism`；调整则返回候选；未答复保持等待。直觉问答中的普通回答不是方案审批。
5. 方法阶段继续交付既有 METHOD_SPEC、组件与 claims。按原 checkpoint 规则登记正式产物；“机制清楚”“相关工作差异已核验”“收益已实验验证”是三个不同状态。

## 资源位置与安装

上游仓库：[ShawnL1N/intuit-to-idea](https://github.com/ShawnL1N/intuit-to-idea)。本仓库以 `skills/intuit-to-idea` 子模块保留完整来源，不改写上游指令。

`vibe init/add manifest auto-research` 通过 `skills.txt` 安装完整 skill 到目标项目 `.agents/skills/intuit-to-idea/`，包括 `SKILL.md`、`references/` 和 `agents/openai.yaml`；按需在此目录读取支持材料，不只复制单个入口。单独安装用 `vibe add skill intuit-to-idea <target>`，无需全局安装。

新安装包含 [Idea 工作流 SVG](idea-workflow.svg)、[可编辑源](idea-workflow.json) 和 `scripts/render_idea_workflow.py`。生成与只读检查命令见项目 README；源文件变化时重新生成，不手工改 SVG。图只描述候选生成及其交接，不取代 `lifecycle/defaults.json` 的完整阶段树。

既有项目请注意：`vibe update manifest auto-research` 只更新已经安装的必需 skills，不自动补装新增依赖；先执行 `vibe add skill intuit-to-idea <target>`，再更新 manifest。更新也保留项目 README，因此生成命令同时在随包文档中列出：

```bash
python3 scripts/render_idea_workflow.py --source references/idea-workflow.json --output references/idea-workflow.svg
python3 scripts/render_idea_workflow.py --source references/idea-workflow.json --output references/idea-workflow.svg --check
```

初始化只安装资源，不自动启动问答、训练、付费任务或投稿。skill 本身无额外运行依赖；完成实时文献核验需要宿主提供检索能力。
