# 首次使用及响应矩阵说明

## 建立工作副本

setup 只安装配置，不捏造业务材料。业务项目根目录保存 `brief.md`、`bid.json`、`MANIFEST.md`，输入放 `sources/`，章节放 `draft/`，审查与决定放 `review/`，候选交付放 `delivery/`，前版放 `archives/`。已有目录则沿用，并在简报说明对应关系。

从模板目录复制缺少的文件，创建目录并登记初始状态。无需联网、数据库或后台服务。先从全部有效材料提取要求，再建立矩阵；审查者对照原文件复核，不只检查 AI 已提取出的行。

## bid.json 字段

UTF-8 JSON，`schema_version` 为整数 1。校验器只读，退出码：0 为当前模式通过，1 为检查问题，2 为输入/结构错误。未知字段、重复键、重复 ID、非法值和未知来源引用均为结构错误。

`project` 必须包含 `name`、`lot`、`tender_revision`、`deadline` 四个字符串。截止时间用带时区的 ISO 8601 值，例如 `2030-01-02T09:00:00+08:00`（仅语法示例，不是项目事实）。不自动判定是否逾期；各平台时间以实际来源核对。

`sources` 为数组，每个来源包含：

| 字段 | 含义 |
| --- | --- |
| id | 项目内唯一来源 ID，如 T-001、E-001；字母开头，仅字母/数字/短横线/下划线 |
| kind | tender、clarification、bidder、reference 四选一 |
| path | 相对 bid.json 所在目录的真实文件路径；不接受绝对路径、反斜杠、上级跳转或符号链接 |
| sha256 | 原文件的 64 位 SHA-256 十六进制值；变化后重新核对有效版本 |

`requirements` 为数组，每个条款包含：

| 字段 | 含义 |
| --- | --- |
| id | 唯一条款 ID；正文需包含精确标记 `<!-- REQ:该ID -->` |
| source_id、locator | 原招标文件/澄清来源 ID，以及原页码/条款/表格定位 |
| text | 保留范围、条件、否定和单位的要求摘要；必要时拆分复合要求 |
| category | qualification（资格）、mandatory（否决/实质）、scored（评分）、general（一般响应）、submission（提交） |
| status | pending（待编）、gap（缺口）、covered（已响应）三选一 |
| response_path | 对应 UTF-8 章节文件的相对路径；不能用大纲冒充响应 |
| requires_evidence | 布尔值；按原要求判断是否需要附件证明，不统一强制或免除 |
| evidence | 数组，元素仅含 source_id 与 locator；实际证明材料通常来自 bidder 或 clarification |
| note | 缺口、处理方案、偏离决定或复核说明；没有内容时使用空字符串 |

以下仅演示**记录结构**，占位字段须从真实材料填入；不是已满足某项要求的证明：

```json
{
  "id": "R-001",
  "source_id": "T-001",
  "locator": "原文件页码及条款号",
  "text": "从真实招标材料提取的单项要求",
  "category": "qualification",
  "status": "pending",
  "response_path": "draft/01-qualification.md",
  "requires_evidence": true,
  "evidence": [],
  "note": "等待对应企业证明材料"
}
```

条款 source_id 必须指向 tender 或 clarification，不以样文或企业自述代替招标依据。证明附件使用 reference 来源不计为 release 就绪，须换成有依据的真实材料。每包独立维护矩阵，不按章节重复定义同一条款。

## draft 与 release 检查

```bash
python scripts/check_bid.py bid.json --mode draft
python scripts/check_bid.py bid.json --mode release
```

两种模式均校验 schema、枚举、引用、路径范围和已存在输入文件的哈希；schema 有误退出 2，文件哈希变化退出 1。draft 对空项目字段、缺文件/哈希、空矩阵、待编/缺口项及缺章节/证据发出 WARN；release 将这些待补转为 ERROR。release 至少需要一个 tender 来源和一个条款，所有条款 covered，所有被引用证据可定位且章节包含其 ID 标记。

本工具不读取 PDF 语义、不验证 OCR 准确性、不判断证照真伪/有效期、不评估方案实质合规，也不计算报价或预计得分。标记存在并不证明正文满足原要求，locator 存在并不证明原页支持该主张。AI 内容审查、业务责任人复核、原生格式/全量页面 QA 和真实定稿决定各自留证。release 不执行签署、上传或提交。

SHA-256 可用 Python 标准库计算；大文件分块读取，不把工具输出的其他文字贴进 sha256 字段。新补遗或来源变化先复核影响，再登记新哈希、返工和复验；不为让脚本通过而盲目更新哈希。

## 依赖准备

在**来源仓库**检查 `mine/z-writing/references/ai-vibe-writing/SKILL.md`、`mine/z-writing/references/z-humanizer/SKILL.md` 及普通中文润色使用的 `mine/z-humanizer/references/unslop/SKILL.md`。其中 AI Vibe 与 unslop 来自子模块；仅缺这两项时：

```bash
git submodule update --init --depth 1 -- skills/ai-vibe-writing skills/unslop
```

然后重跑 setup 的预览、应用与检查。setup 安装的写作包会物化支持文件；不要求业务项目保留来源仓库符号链接。安装后核对 `.agents/skills/z-writing/references/ai-vibe-writing/SKILL.md` 和所需提示词，并让宿主实际读取技能。其他学术润色分支不是本标书场景必经路线，不默认初始化其全部来源。
