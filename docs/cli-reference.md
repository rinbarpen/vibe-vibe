# CLI 与维护参考

**简体中文** | [English](cli-reference_EN.md)

需要查参数、更新条件、备份或维护命令时再读本页。初次使用从 [项目首页](../README.md) 开始；以下命令默认在仓库根目录执行。

## `vibe` CLI

仓库定位优先级为 `$VIBE_HOME` 环境变量 → 从当前目录向上查找同时包含 `manifests/` 和 `skills/` 的目录 → `~/.config/vibe-tool/config.json`。在仓库外使用时，可以先通过 `vibe config set-repo /path/to/vibe-vibe` 固定仓库路径。

项目安装与直接更新命令支持 `-n/--dry-run` 预览；`init/add` 使用 `-f/--force` 显式覆盖已有文件，`update skill/manifest` 则覆盖选定资源并自动备份。`target` 默认为当前目录；场景与 `--provider`、`--owner`、`--org`、`--repo`、`--email` 等生成参数按模板适用，详情见相应命令的 `--help`。

| 命令 | 用途 |
| --- | --- |
| `vibe list manifests` | 列出可用项目模板 |
| `vibe list skills` | 递归列出可用 Skills |
| `vibe list --json` | 输出机器可读的清单 |
| `vibe init <manifest> [target]` | 从模板初始化新项目 |
| `vibe add manifest <name> [target]` | 向已有项目加入 Manifest |
| `vibe add skill <name> [target]` | 向已有项目加入单个 Skill |
| `vibe add skill --all [target] --yes` | 批量安装全部 Skills |
| `vibe update` | 更新受管理的 Skill 子模块 |
| `vibe update skill <name> [target]` | 从本地仓库同步项目中已安装的 Skill，自动备份 |
| `vibe update manifest <name> [target]` | 从本地仓库同步 Manifest 配置及已安装的必需 Skills，自动备份 |
| `vibe config set-repo <path>` | 设置仓库路径 |
| `vibe config show` | 查看当前配置 |
| `vibe mcp list` | 列出可用 MCP 服务 |
| `vibe mcp add <name> [target]` | 合并安装 MCP 服务配置 |
| `vibe mcp add --all [target]` | 安装全部 MCP 服务配置 |
| `vibe hook list` | 列出可用 Hook 集合 |
| `vibe hook add <name> [target]` | 向项目安装 Hook 集合 |
| `vibe hook add --all [target]` | 安装全部 Hook 集合 |
| `vibe stats show` | 查看 Skill 使用统计 |

常用选项（下列 `add/hook` 示例假设 `demo` 已存在；`--dry-run` 本身不会创建目标目录）：

```bash
vibe init vibe-coding demo --dry-run
vibe add manifest office demo --force
vibe add skill --all demo --yes --dry-run
vibe mcp list
vibe hook add ralph-loop demo
```

## 跨平台项目配置：`vibe setup`

一句自然语言入口见 [BOOTSTRAP.md](../BOOTSTRAP.md)。AI 负责按需求选择/生成 manifest；安装器不对自然语言做关键词路由。无需全局 CLI 时，在来源仓库用实际探测的 Python 3.10+ 执行 `scripts/setup-project.py`，参数与下列命令一致。

```text
vibe setup --list
vibe setup vibe-coding ../my-project --harness both --scenario fullstack-web --provider git --dry-run
vibe setup vibe-coding ../my-project --harness both --scenario fullstack-web --provider git
vibe setup vibe-coding ../my-project --check
```

- `--harness generic|codex|claude|both`（`--agent` 为别名）默认 both；所有模式保留 `.agents/skills` 规范副本，Claude/both 另有 `.claude/skills` 完整副本。`--skill <规范名称>` 可重复补充能力，不默认全装。
- 默认 provider=git；不初始化 Git、不提交、不启用云。所有当前模板都有不经 Bash 的资源渲染路径；已有 Python 初始化器直接复用，旧 shell 安装器的 `init/add` 行为保持原样。
- 根指令保留用户内容，以导入块引用根目录的 `AGENTS.vibe-<name>.md` / `CLAUDE.vibe-<name>.md`；已有 README、输出账本、版本记录和业务状态保留。其他本地冲突在写入前停止，不提供隐式强制覆盖。
- setup 在一次现有备份事务中应用文件、双端技能和安装记录；失败自动回退，输出独立恢复脚本。`.vibe-setup.json` 保存配置与哈希，`--check` 是只读结构验收，不模拟宿主技能激活。
- 同一 setup 命令可刷新未被本地修改的受管资源；先预览。也可用 `vibe project update <项目名>` 统一更新；不要混用旧 update 来维护 Claude 副本与 setup 记录。Windows/macOS/Linux 的具体 skill 运行依赖仍按各 skill 检查。

## Harness 无关的规则

Manifest 是业务协作契约，不是某个编辑器的规则插件。新模板只需 `AGENTS.md`、`PROJECT_RULES.md`、`CLAUDE.md` 中至少一个入口，不要求 Claude 或 Cursor 文件。规则推荐普通 `rules/*.md`；可用可选头字段 `always: true|false`、`paths`、`when` 声明范围。

```text
vibe setup vibe-coding ../project --harness generic --provider git --dry-run
vibe setup vibe-coding ../project --harness generic --provider git
vibe setup vibe-coding ../project --check
```

生成 `PROJECT_RULES.md`、`rules/<name>/CONTRACT.md`、`INDEX.md`、`rules/*.md` 和 `rules.json`，支持资源随包放在 references/commands/templates/scripts。规则正文、场景选择、路径/任务条件及来源哈希保留；旧 MDC 头作为数据迁入索引，未知范围标为人工/AI 审查，绝不静默全局启用。支持脚本是普通文件，不代表注册了宿主插件；依赖仍按各自要求验证。

任何具有文件读取能力的 harness 可显式读取 `PROJECT_RULES.md`，再读取契约和适用规则。generic 另提供普通 `AGENTS.md` 导入与 `.agents/skills`，不要求 Codex 软件；命名模式只增加宿主入口/技能副本，不改变业务门。文件/哈希检查与真实宿主发现、工具运行分开报告，不模拟工具或批准。

新 setup 不分发 `.cursor` / `.cursorrules`，无需维护 Cursor 兼容。旧源 `.mdc` 仅作迁移输入；已有项目中的旧目录原样保留，更新后不再作为该 setup 的受管输出。历史 init/add 脚本尚有旧目录写入，使用本节 setup 取得无 Cursor 的布局。项目更新维护共享入口、已安装规则/技能与备份回退，不改业务成果和用户独立规则。

[配置工作流](project-setup-workflow.svg) · [可编辑源](project-setup-workflow.json)。生成和只读检查命令见 [配置契约](../BOOTSTRAP.md)。

## 管理多个项目

`vibe setup`、`vibe init`、`vibe add manifest/skill` 成功后会自动登记真实目标项目；dry-run、失败安装和内部暂存目录不登记。项目名默认取目录名，同名目录自动加路径摘要；显式同名绑定到不同路径时报告冲突。

### 登记与查找

```text
vibe project list
vibe project list --json
vibe project show paper
vibe project add ../old-project --name paper --source /path/to/vibe-vibe
```

`project` 也可写作 `projects`。list/show 在任意目录可运行，不要求当前目录是来源仓库；它们回读项目内 `.vibe-tool/installations.json` 与 setup 配置，展示真实登记资源，而不是全局复制一套技能清单。没有安装记录的目录可以登记，但更新前需先 setup/init/add，工具不会猜测其 manifest。

- `vibe project rename paper thesis` 只改显示/查询名。
- 项目已被用户移动后，运行 `vibe project relocate thesis /path/to/moved-project` 重新绑定已存在的路径；此命令不移动文件。
- `vibe project remove thesis` 只移除登记，不删除项目、技能或备份。路径失联时 list 标记 missing，保留记录供重新绑定。

### 按项目更新与回退

```text
vibe project update paper --dry-run
vibe project update paper
vibe project update paper --manifest auto-research --dry-run
vibe project update paper --skill intuit-to-idea
vibe project update --all --dry-run
vibe project update --all
```

指定一个项目时，默认更新其中全部已安装 manifest 与 skills；`--manifest` / `--skill` 可重复指定以限定范围。manifest 选择会包含其**已安装**依赖；新依赖、已移除的技能目录不自动补装。每个项目使用登记的来源仓库及项目内记录的生成参数，不要求先切目录。默认只读本地来源，不自动 fetch/pull；来源更新与项目同步是两个步骤。

每个项目先准备全部选定资源，再通过原事务模块一次应用；配置、skills、安装记录和 setup 哈希共享一份备份。失败自动回退，成功打印独立 `restore.py` 命令；无变化不创建备份。全项目更新逐项目处理，一个失败仍检查其他项目，最后汇总并返回非零；这是每项目原子性，不是跨项目的整体事务。

setup 项目维护导入侧车与完整 `.agents/skills` / `.claude/skills` 副本，整目录刷新会清理旧版本残留，并同步 `.vibe-setup.json`。原根指令的用户内容、README、业务状态、成果账本、VERSION/CHANGELOG 保留；已修改的受管资源或技能中的额外本地文件先报冲突，不直接覆盖。后续 `vibe add skill` 对 setup 项目也采用双端/记录的同一备份事务；显式 `--force` 才覆盖已有技能。

未使用 setup 的项目通过 project update 获得通用规则入口和规则包；其其他根资源沿用原覆盖语义。原 `vibe update manifest/skill` 命令保持原样；对 setup 项目优先使用这里的项目更新入口，避免只刷新规范技能而漏掉 Claude 副本。新增 setup manifest 仍用 `vibe setup`，不把登记当成已安装。

### 索引位置与异常

索引默认在 `~/.config/vibe-tool/projects.json`，仅保存项目名、绝对路径和来源仓库。可用 `VIBE_PROJECTS_FILE` 指向另一个文件（例如测试、便携环境或不同工作集）。并发写入使用跨平台文件锁和临时文件原子替换；读取、预览不改索引或项目。

旧项目可用 add 显式登记，不扫描整盘。索引损坏时保留原文件并报告；自动登记失败会警告，项目内安装记录仍然有效，修复后重新 add。索引不是业务进度，也不代表文件一定未被修改；先 dry-run 查看当前差异。各项目的回退只恢复项目内容，不删除其全局登记。

[项目管理工作流](project-management-workflow.svg) / [可编辑源](project-management-workflow.json)。从来源仓库运行：

```text
python scripts/render-manifest-workflow.py --source docs/project-management-workflow.json --output docs/project-management-workflow.svg
python scripts/render-manifest-workflow.py --source docs/project-management-workflow.json --output docs/project-management-workflow.svg --check
```

## 更新与维护

### 同步项目中已安装的 Skill / Manifest

已初始化项目支持**原地更新，无需重新运行 `vibe init`**。安装到项目的资源是副本，源仓库更新后需要显式同步目标项目；暂不更新时，项目继续使用已安装的版本。

更新前准备：

- 本地源仓库已包含所需版本；需要远程新版时，先同步主仓库或对应的 Skill 来源。
- 目标项目目录已存在，并确定要更新的 Skill / Manifest 名称。
- 对应资源已经安装；安装记录用于复用来源及生成参数，旧项目的接入条件见下文。

直接更新使用当前本地仓库内容，**不隐式拉取远程**。`target` 默认为当前目录；每次指定一个名称，不支持 `--all`。

```bash
# 先预览，再同步整个已安装 Skill 目录（包括清理旧版本残留）
vibe update skill taste-skill ../my-project --dry-run
vibe update skill taste-skill ../my-project

# 先预览，再同步配置；默认复用安装时记录的生成参数
vibe update manifest vibe-coding ../my-project --dry-run
vibe update manifest vibe-coding ../my-project

# 需要时显式覆盖参数；add manifest 同样支持 --scenario
vibe update manifest ui-testing ../my-project --scenario=web-e2e
vibe add manifest ui-testing ../my-project --scenario=component
```

Skill 更新会替换整个已安装目录，自定义文件也包含在更新前的备份中。尚未安装时先运行 `vibe add skill <name> [target]`。

Manifest 更新只覆盖模板生成的指令、规则、commands、agents、平台配置和工具资源；保留业务文件、研究成果、README、CONTRIBUTING、VERSION、CHANGELOG、运行记录及初始化大纲/笔记索引。仅 `vibe-coding` 的 `MANIFEST.md` 是更新资源，其他模板的同名产出账本保持原样。不删除新模板已移除的旧配置，也不整体替换项目资源目录。必需 Skills 中只同步已经安装的条目，缺失依赖仅提示，无关 Skills 不变。

`init/add` 会在目标项目的 `.vibe-tool/installations.json` 记录来源及适用的生成参数。之后更新默认复用记录，显式选项优先。没有记录的旧项目，需已有至少一项模板资源，首次更新还需明确所有适用参数（命令会列出缺项）；全新项目先使用 `vibe init` 或 `vibe add manifest`。空字符串表示模板默认值或无场景，例如：

```bash
vibe update manifest vibe-coding ../legacy-project \
  --provider=git --scenario='' --owner='' --org='' --repo='' --email=''
```

`--dry-run` 仅输出将新增、覆盖及跳过的路径，不写项目、安装记录或备份。实际变更前自动备份到 `.vibe-tool/backups/<唯一ID>/`，包含原始内容、校验值与变更清单；成功后打印恢复命令：

```bash
python /path/to/project/.vibe-tool/backups/BACKUP_ID/restore.py
```

将 `BACKUP_ID` 替换为本次备份目录名，或直接使用更新命令打印的恢复命令。恢复脚本独立运行，无需安装 `vibe`。配置、依赖 Skill 与安装记录在同一事务中更新，应用失败自动恢复已触及内容；内容及记录均未变化时不创建备份。

### 无需安装 CLI 即可更新

只需 Python 3.10+ 和本地源仓库，无需安装 `uv`、全局 `vibe` 或第三方 Python 依赖。按上述条件准备资源与已有项目，然后直接运行仓库内的 Python 入口：

```bash
REPO=/path/to/vibe-vibe
PROJECT=/path/to/existing-project

# 临时函数，仅在当前终端会话中生效
vibe_local() {
  VIBE_HOME="$REPO" \
  PYTHONPATH="$REPO/tools/vibe_tool/src" \
  python3 -B -m vibe_tool "$@"
}

# 先预览需要的更新
vibe_local update skill taste-skill "$PROJECT" --dry-run
vibe_local update manifest ui-testing "$PROJECT" --dry-run

# 确认预览后，按需运行对应更新
vibe_local update skill taste-skill "$PROJECT"
vibe_local update manifest ui-testing "$PROJECT"
```

将路径与资源名称替换为实际值。以上命令沿用相同的更新条件、覆盖范围、自动备份与独立回滚规则。

### 更新仓库中的 Skill 来源

裸 `vibe update` 只更新受管理的 Skill 源子模块。主仓库中的 Manifest 变更需先同步主仓库；已有项目仍需使用上面的 `update skill/manifest` 命令显式同步：

```bash
vibe update
```

也可以使用仓库脚本：

```bash
./scripts/skills-git-pull.sh
```

`agent-skills` 和 `ai-investment-advisor` 默认不参与批量更新，需要单独执行：

```bash
git submodule update --remote --merge -- skills/agent-skills
git submodule update --remote --merge -- skills/ai-investment-advisor
```

部分 Skill 仓库（例如 `aris`、`ppt-master`）是独立嵌套仓库，不在 `.gitmodules` 中，按其自身仓库方式更新。

## 开发与验证

修改 CLI 或 Manifest 后，建议运行：

```bash
# 验证 Claude Code 与 Codex agent 文件兼容性
python scripts/validate-agent-compat.py

# 运行 vibe-tool 测试
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/vibe_tool/src python -m pytest tools/vibe_tool/tests -v
```

新增 Manifest 至少需要包含 `CLAUDE.md`，这样才能被 `vibe list manifests` 发现。新增 Skill 则应在 Skill 目录中提供 `SKILL.md`。

新建 Manifest 或修改其工作流时，还需同步交付 **workflow SVG、可编辑源、可复现生成命令和只读一致性检查**，并从 README/主指令链接。图上区分 AI 自主执行、AI 验证与人工决策，标注分支、返工及人工确认后的恢复路径。详见 [Manifest 工作流图交付规范](../docs/manifest-workflow.md) 与 [真实 SVG 示例](../docs/examples/manifest-workflow/workflow.svg)。现有 Unity 图源与渲染器继续复用；本约定不改变模板安装策略。

```bash
# 检查通用示例图是否与可编辑源一致
python3 scripts/render-manifest-workflow.py \
  --source docs/examples/manifest-workflow/workflow.json \
  --output docs/examples/manifest-workflow/workflow.svg --check

# 验证渲染、分支结构和只读漂移检查
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_manifest_workflow.py' -v
```

