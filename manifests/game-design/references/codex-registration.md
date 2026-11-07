# Codex 原生角色：发现、配置与执行证据

核验日期：2026-11-06。不要把“生成了 TOML”与“当前宿主已加载并派生了该角色”合并为一个结论。

## 当前 Codex 的发现方式

当前官方 [Subagents 文档](https://developers.openai.com/codex/subagents/) 规定：项目角色使用 `.codex/agents/*.toml`，个人角色使用 `~/.codex/agents/*.toml`；每个独立文件必需 `name`、`description`、`developer_instructions`。角色以 `name` 识别。本模板采用该独立文件形式，不需要额外生成逐角色 `[agents.<name>]` 注册表。

全局 `[agents]` 可设置启用、并发上限与默认模型等；配置字段另见 [官方配置参考](https://developers.openai.com/codex/config-reference/)。模板不写用户/项目 `config.toml`，不设置模型、不扩大宿主权限或并发额度。旧客户端或组织包装器如使用 `config_file` 注册方式，应按其对应版本另行核验，不把两种格式机械混用。

## 安装与使用

1. 完成 manifest 安装，确认角色落在**游戏项目根** `.codex/agents/`，不是 `.game-design/.codex/agents/`。
2. 运行 `python3 .game-design/scripts/render_agents.py --check` 检查源与角色文件一致；这仅验证生成资料。
3. 从目标游戏项目开启适用的 Codex 会话，确认宿主实际提供子代理能力、配额和工具。明确要求使用角色，例如：

   > 请让 game-design-designer 处理已领取的设计任务；使用 game-design-qa 验证产物，由 game-design-reviewer 独立审查。按任务依赖、写入范围和资源认领并行，返回实际运行 ID 与证据。

4. 主代理通过当前宿主的真实创建/消息/等待工具执行，并把实际 agent/thread ID 绑定到调度任务。已有会话是否动态重新发现角色取决于客户端；没有发现记录时，不预设文件已加载。

## 本机观察与证据边界

- 本机 `codex --version` 的字面输出为 `codex-cli 0.153.4`。安装包本地 README 只指向官方配置文档，未给出更详细的独立角色发现说明，因此以上发现规则由官方文档核验。
- 只读检查显示现有用户配置启用了 `features.multi_agent`，没有 `[agents]` 表；本次未修改用户配置或其他 manifest。
- 在临时目录和隔离 `CODEX_HOME` 中运行 `codex --enable multi_agent debug prompt-input`，命令退出 0，但它只给出 model-visible messages，没有完整工具定义/角色清单。其输出未出现探针角色名，既不证明发现失败，也不证明已经发现或执行。
- 当前可用 collaboration 宿主可以显式把生成角色 prompt 随任务交给真实子代理，记录实际工具结果/运行 ID。这证明的是“当前宿主使用该 prompt 执行”，不是“另一个 Codex CLI 会话已按原生角色自动派生”。

证据应分别记为：**格式/生成检查通过**、**宿主发现状态**、**真实代理执行结果**。后两项缺少对应记录时保留 `not_run/unknown`；Python 调度状态、角色文件数和模拟测试不代替真实代理调用。
