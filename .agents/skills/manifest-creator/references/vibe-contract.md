# vibe Manifest 安装与维护契约

仅在编写初始化脚本、场景、依赖安装或更新支持时读取。这里记录非直觉约束；目标仓库的当前源码与测试是最终依据。以下路径均相对于目标仓库根目录，不依赖本 skill 的安装位置。

## 发现与最小结构

`tools/vibe_tool/src/vibe_tool/discovery.py`：

- `discover_manifests` 扫描 `manifests/` 的非隐藏直接子目录，并要求 `CLAUDE.md`；仅有 `AGENTS.md` 或 `SKILL.md` 不构成可发现的 manifest。注意当前黑名单约束。
- `scripts/*init*.sh` 按名称排序后只取第一个作为入口，避免多个候选产生歧义；shell 入口应有 shebang 和可执行权限。
- `scenarios/` 的非隐藏子目录用于场景发现；“列出场景”不等于安装器已经实现了场景选择与合并。
- `skills.txt` 支持空行与 `#` 注释。依赖由 `skills/` 和 `mine/` 共同解析，名字冲突可能由相对路径消歧。

不要复制文档中旧的模板数量或固定 skill 清单。用 `vibe list manifests --json`、`vibe list skills --json` 查询当前状态。

## 安装器的真实边界

检查 `tools/vibe_tool/src/vibe_tool/manifest.py` 以及该模板自己的安装脚本：

- 无自定义脚本时走通用复制：约定的根文件、Cursor 规则/命令，以及原生 `.claude/agents/`、`.codex/agents/` 等特定资源。它不是模板整目录镜像。
- 通用复制不会自动分发任意 `references/`、`scripts/` 或场景目录。若 README 的链接将在项目中使用，必须有显式安装路径，或明确那些链接只在模板仓库内使用。
- 若承诺目标项目拥有 workflow 图和再生成能力，显式分发 SVG、可编辑源、渲染入口及其真实依赖；测试目标项目内的命令，不只测试仓库里的副本。
- 有自定义脚本时，CLI 把解析后的目标目录作为首个位置参数，并提供 `VIBE_MANIFEST` 环境变量。脚本仍应根据自身位置可靠定位源文件，避免依赖调用者的当前目录。
- 自定义选项透传由 `_SCRIPT_FLAG_MAP` 控制。新脚本自己接受 `--scenario`，不代表 `vibe init --scenario` 会自动传入；需要检查映射和端到端测试。不要为未请求的选项扩展公共 CLI。
- `--force` 和 `--dry-run` 有各自的透传默认值。对未知初始化器，CLI 的 dry-run 可能只打印命令，并未执行脚本，所以它不证明脚本自身具备只读预览。
- init/add 完成后才继续处理必需 skills，并记录 `.vibe-tool/installations.json`。依赖失败可能出现在模板文件已写入之后；自定义脚本的成功不等于整次安装成功。

若需安装脚本，按任务约定处理已有文件，确保路径含空格时有效、错误正确退出、测试性覆盖可恢复。普通初始化不应顺带联网拉仓库、安装软件或写全局配置，除非用户请求包含这些动作。

若当前通用安装器满足不了分发承诺，优先使用模板自己的窄范围入口；确需更改公共安装器时，明确变更范围并增加回归测试，不把新增任意目录复制当作默认行为。

## 推荐验证方式

从目标仓库运行以下命令，把变量换成真实值；所有测试写入独立临时目录：

```bash
NAME=your-manifest
TMP=$(mktemp -d)
vibe list manifests --json
vibe init "$NAME" "$TMP/new-project" --dry-run
vibe init "$NAME" "$TMP/new-project"
mkdir -p "$TMP/existing-project"
vibe add manifest "$NAME" "$TMP/existing-project"
```

逐条检查退出状态，再核对实际文件和链接；dry-run 前后比较目录状态。测试已有项目时加入与模板同名的用户文件，验证既定的保留/冲突策略。按承诺的布局在目标项目重新生成 workflow SVG，并运行漂移检查。

- 通用工作流工具：`tests/test_manifest_workflow.py` 与 `scripts/render-manifest-workflow.py`。
- 通用安装相关测试：`tools/vibe_tool/tests/test_manifest_installation.py`；其他测试按本次改动选择，不默认跑所有业务模板的重型测试。
- 双端 agent：检查 Claude Markdown 与 Codex TOML 的当前字段和语义，再运行 `python3 scripts/validate-agent-compat.py`。这是执行式验证脚本，先读入口再运行，不假定它实现 `--help` 参数。

没有安装好的 `vibe` 时，先检查 `tools/vibe_tool/pyproject.toml` 的本地运行方式；可以用 `PYTHONPATH=tools/vibe_tool/src python3 -m vibe_tool ...`，前提是当前解释器具备声明的依赖。别为了验证静默安装工具或改全局配置。

## 支持更新时才检查

阅读 `manifest_update.py`、`project_update.py`、`installations.py` 及适用测试。新模板拥有 init 脚本，不代表它自动具备完整 update 语义；检查资源选择、渲染和安装选项恢复是否覆盖它。

当前契约要点：

- `vibe update manifest <name> [target]` 从本地源同步受管配置/工具资源，不拉取 Git。保留项目 README、VERSION、CHANGELOG、数据与产物账本；`vibe-coding` 的 `MANIFEST.md` 有专门例外。不要把该例外推广到其他模板。
- 必需 skills 只更新已安装项，缺失依赖和无关 skills 保留原状；这一行为与 init/add 的依赖安装不同。
- 生成选项来自 `.vibe-tool/installations.json` 与显式覆盖。旧项目可能需要补齐适用选项，省略与显式空字符串语义不同。
- 有变更时生成 `.vibe-tool/backups/<id>/changes.json`、原文件和独立 `restore.py`；只读预览和无变更更新不应创建备份。恢复命令使用本次实际打印的路径。

只在临时安装副本测试更新与恢复，分别记录更新前、更新后、恢复后的文件或哈希；不要声称新模板享有尚未验证的通用回滚保障。
