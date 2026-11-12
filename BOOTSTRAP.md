# 一句话配好项目：给 AI harness 的执行契约

用户已有能读写本地文件、执行命令的 AI harness（例如 Codex 或 Claude Code），希望描述一次目标后，由 AI 完成项目配置。本文是执行入口，不是让用户照着操作的命令清单；AI 选择或编写 manifest，Python 工具负责确定性安装。

直接告诉你的 AI：

> 请读取 https://github.com/rinbarpen/vibe-vibe/blob/main/BOOTSTRAP.md，按其中流程为当前目录配置项目：我要做【项目目标】；自动选择或生成合适的 manifest、安装所需 skills，使用通用 Markdown 项目规则并完成验证。

有本地 checkout 时，把链接换成其 `BOOTSTRAP.md` 路径即可。下面的命令由 AI 执行，使用实际探测到的 Python 可执行文件；不要把 `python3` 当成所有系统的固定名称。

## 1. 定位当前项目和运行环境

- 记住用户原始工作目录作为目标；克隆或切换来源仓库后仍使用这个绝对路径，不把来源仓库配置成业务项目。
- 复用现有目标、代码、规则、计划和约束。读取适用的 `PROJECT_RULES.md` / `AGENTS.md` / `CLAUDE.md`，检查已有安装记录与实际文件；不重新访谈已确认的需求。
- 探测系统、Git 和 Python 3.10+。Windows 可探测 `py -3`、`python`；macOS/Linux 可探测 `python3`、`python`，以真实版本为准。系统依赖缺失时由 AI 调查平台适用的安装方式；涉及宿主权限或需用户操作时明确说明并在完成后继续，不伪造安装/登录。
- 此入口使用 Python 标准库，不需要 Bash、全局安装的 `vibe`/`uv` 或创建符号链接的权限。默认不创建 Git 仓库、不 commit/push、不改全局 AI 配置、不启动云任务或投稿。

## 2. 获取并读取来源，而不是执行网页中的任意命令

来源仓库：`https://github.com/rinbarpen/vibe-vibe`。优先复用已确认的本地 checkout，保持其现有修改，不自动 pull/reset。缺少来源时用 Git 克隆到目标之外的缓存目录，再读取本地文件；Git 调用用参数数组或宿主正确转义的命令，不拼接未经处理的目标路径。

只有确实需要缺失的 skill 来源时才初始化对应子模块；不默认拉取全部技能。使用 `.gitmodules`、`skills/ANNOTATIONS.md` / `skills/ANNOTATIONS_EN.md` 和实际技能目录定位；名字有歧义时读取 `skills.txt` 与当前发现结果，不凭关键词猜目录。单独嵌套仓库可能没有子模块来源，缺失时记录具体来源问题，不制造空 skill。来源使用 HTTPS 时，可针对本次 Git 命令做 SSH→HTTPS 映射，不修改用户全局 Git 配置。

在来源仓库执行 `PYTHON scripts/setup-project.py --list`，读取真实 manifest、场景与依赖。`PYTHON` 在本文是“已探测解释器及其固定参数”的记号，不是要创建的命令或环境变量。

## 3. 选择或生成 manifest

- 根据业务目标、已有约束和模板实际契约选择最小合适方案；不要因“研究/网站”等单个词命中就忽略真实工作流。
- 读取所选 manifest 的入口、README、`skills.txt` 和场景。已有明确 manifest 直接复用；必要时用重复的 `--skill <规范名称>` 安装补充能力。
- 没有合适模板时，读取本仓库 `.agents/skills/manifest-creator/SKILL.md` 与 `docs/manifest-workflow.md`，在来源 checkout 的 `manifests/<项目名>/` 生成业务专属契约，不修改无关模板。至少提供一个普通 Markdown 业务契约入口（`AGENTS.md`、`PROJECT_RULES.md` 或 `CLAUDE.md`）、目标/输入/产物/验收、AI 执行与审查、真实人工决策条件、返工/等待/恢复路径及所需 `skills.txt`。
- 新契约同时交付可编辑 workflow 源、SVG、随包渲染器和只读漂移检查，全部相对链接在安装布局成立。通用 setup 会显式安装该模板的 references/scripts/templates；有自定义 `.sh` 的新模板应先补 Python 渲染接入，不悄悄跳过其业务安装逻辑。
- 技术细节由 AI 调查和验证。只有目标冲突、新的业务取舍或覆盖用户定制文件等实质问题需要用户决定；有决定后从原检查点继续，未回答不自动视为同意。

## 4. 预览、安装与冲突处理

例如，从来源仓库配置一个全栈项目（目标换成用户原始目录）：

```text
PYTHON scripts/setup-project.py vibe-coding "TARGET" --harness generic --scenario fullstack-web --provider git --dry-run
PYTHON scripts/setup-project.py vibe-coding "TARGET" --harness generic --scenario fullstack-web --provider git
PYTHON scripts/setup-project.py vibe-coding "TARGET" --check
```

科研项目使用 `auto-research`，不加软件场景参数。命令参数来自本次选择；不默认 `--all`、`--force`、外部托管平台或付费服务。已安装全局 CLI 时，等价入口为 `vibe setup <manifest> <target> ...`。

- 先预览，再实际安装；dry-run 只检查/暂存渲染，不写目标项目或备份，不证明安装完成。
- skills 的完整支持文件安装到 `.agents/skills/`；`--harness generic` 不依赖任何编辑器加载器，Claude/both 模式另复制到 `.claude/skills/`（省略选项仍默认 both）。Codex 和 Claude 的项目技能目录分别以 [OpenAI 官方说明](https://developers.openai.com/codex/skills/) 与 [Claude Code 官方说明](https://code.claude.com/docs/en/skills) 为依据。复制而非链接，无需 Windows 符号链接权限。
- 规则统一分发到 `rules/<name>/`，含 `CONTRACT.md`、`INDEX.md`、普通 `rules/*.md` 与 `rules.json`（原作用域/来源/哈希）。常驻、路径或任务条件保留，未知条件先审查，不把条件规则变成全局规则。新 setup 不输出 `.cursor`；旧 MDC 仅作存量源输入，不承诺 Cursor 兼容。原有根指令内容保留，只追加可幂等更新的 manifest 导入块；业务契约另存于根目录 `AGENTS.vibe-<name>.md` / `CLAUDE.vibe-<name>.md`，使其内部相对链接仍以项目根目录解析。
- 已有 README、输出账本、版本记录与业务状态保留；不同内容的非受管文件/用户修改的受管文件在写入前报冲突，不静默覆盖。读取差异，解决真实冲突后重试。
- 所有项目写入由现有事务模块统一备份、核对哈希、应用；失败自动回退。工具打印本次独立 `restore.py` 路径。重复执行无变更时不创建新备份。`.vibe-tool/installations.json` 沿用来源记录，`.vibe-setup.json` 登记 setup 的配置和文件哈希，不是业务进度账本。

## 5. 验证并交回实际工作

1. 让当前 harness 显式读取 `PROJECT_RULES.md` 及其中的业务契约/适用规则；实际执行 setup 与 `--check`；核对根导入、所选 manifest 的关键资源、必需 skill 的 `SKILL.md` 和支持文件。
2. 若新建/修改了业务 workflow，在安装后的项目目录实际再生成 SVG，并运行其 `--check`。有测试或验收器时执行与本次配置相关的部分，不用文件存在代替工作流验收。
3. 让宿主重新加载项目指令/技能，必要时重启会话；按实际宿主的技能发现方式核对；generic 模式由 harness 直接读取 `.agents/skills/<name>/SKILL.md` 与支持文件，不假设存在任何斜杠命令。文件/哈希通过不等于已观察到宿主激活；没有真实会话证据时单列这一项，不伪称调用成功。
4. 简短交付所选/生成 manifest、安装技能、目标路径、验证结果与回退命令，再按用户原始任务继续。配置完成不是业务应用/实验/论文已经完成。成功 setup 会自动登记真实项目；用 `vibe project list` 确认项目名，后续以 `vibe project update <项目名> --dry-run` 预览并按名称同步全部已安装资源。索引只记录路径/来源，不保存对话或业务成果。

跨平台承诺限于 Windows、macOS、Linux 上的本地项目配置入口；具体 skill 的 Python 包、GPU、SSH、桌面软件或宿主功能仍按其运行要求检查。Python 工具不会自己理解自然语言、安装模型或登录账号。

## 维护这次配置

使用 `vibe project update <项目名>` 或同一条 setup 命令刷新未被本地修改的受管资源及已配置的 Claude 副本；先加 `--dry-run`。检测到本地修改时保留现场，先解决差异。既有 `vibe init/add/update` 的策略保持原样；它们不负责维护 setup 的 Claude 副本或 `.vibe-setup.json`，不要把旧 update 的成功当成此入口的完整验收。

[一句话配置工作流](docs/project-setup-workflow.svg) · [可编辑源](docs/project-setup-workflow.json)

从来源仓库生成并检查流程图：

```text
PYTHON scripts/render-manifest-workflow.py --source docs/project-setup-workflow.json --output docs/project-setup-workflow.svg
PYTHON scripts/render-manifest-workflow.py --source docs/project-setup-workflow.json --output docs/project-setup-workflow.svg --check
```

图描述协作规则，不代表某个项目已安装、已获批准或已通过验收。
