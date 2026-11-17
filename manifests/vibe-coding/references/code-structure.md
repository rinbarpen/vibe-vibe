# 持续管理代码结构

目标是让模块职责、文件归属、公开接口和依赖方向随代码保持一致，而不是强推某种目录树或把每个大文件机械拆开。适用于单语言、多语言与 monorepo；本地即可完成，PR / Issue 仍是可选交付路径。

## 第一次使用

把“为当前项目建立代码结构契约并检查”交给 AI。它先调查真实代码、语言原生配置和已有架构说明，参考 [示例](code-structure.example.json) 编写项目自己的 `architecture/structure.json` 和模块文档。示例仅展示格式，不在安装/更新时写入该项目数据路径；不强制使用示例的 Python 布局。

在安装后的项目根目录运行：

```bash
python scripts/check_structure.py check --root .
```

源码模板仓库中相应入口为 `python manifests/vibe-coding/scripts/check_structure.py check --root <目标项目>`。工具仅用 Python 3.10+ 标准库，无 Git、网络、CodeGraph 或平台账号前提；普通 Markdown 宿主读取相同规则即可。

初次检查通常返回 `1`（缺少已审查的拓扑快照），而不是假称首次通过。先核对 JSON 中的 `blockers`、`new_findings` 和 `topology`，解决缺口，再生成候选：

```bash
python scripts/check_structure.py snapshot --root .
python scripts/check_structure.py baseline --root .
```

这两个命令只把候选 JSON 写到 stdout，不改任何项目文件，也不代表已接受。AI/维护者检查命令退出为 `0`、比对当前版本及候选、更新架构文档后，用临时文件和 `os.replace` 原子保存 `snapshot` 候选到契约的 `snapshot` 路径。只有明确采用既有债务时才保存 `baseline` 候选到 `architecture/structure-baseline.json`，并在正常变更记录中说明理由、范围与后续处理。不需为了现有约定内的技术整理逐次请求人批准；新的业务取舍和风险接受需真实决定。

采用已审查债务的后续检查：

```bash
python scripts/check_structure.py check --root . --baseline architecture/structure-baseline.json
```

没有债务不传 `--baseline`；传入的文件缺失/损坏不会被忽略。检查退出 `0`：无新问题、无未解决覆盖缺口、无拓扑漂移；`1`：新增/恶化问题或拓扑漂移；`2`：配置、输入、归属、解析或依赖证据缺口。`status: pass` 只代表该结构检查的声明范围，不是编译/测试通过或人工批准。

## 项目契约：一个事实来源

`schema_version` 当前为整数 `1`；未知字段/版本报错，避免拼写错误被悄悄忽略。

| 字段 | 含义 |
|---|---|
| `source_roots` | 项目相对的源码目录列表；支持 `.`，不规定必须有 `src/` |
| `exclude` | 可选、大小写敏感的项目相对 glob；匹配完整路径。显式记录生成目录，勿隐藏有意义的源码 |
| `external_prefixes` | 明确排除在本地模块图外的依赖前缀，如 `typing`、`react`、`std`、`java`。不检查这些依赖内部结构或安全性 |
| `extensions` | 可选源码后缀列表；默认覆盖常见 Python/JS/TS/Go/Rust/Java 以及 C#/Dart/C/C++/Swift/Kotlin 后缀，后几类需要原生证据 |
| `max_lines` | 可选正整数，项目文件行数预算；模块可覆盖。不设统一 800 行门槛，不度量认知复杂度 |
| `snapshot` | 必需、已审查拓扑 JSON 的项目相对路径；应跟随代码纳入版本管理 |
| `dependency_evidence` | 可选原生依赖归一化报告路径，见下文 |
| `modules` | 非空模块列表；模块 `name` 唯一，`paths` 为不重叠目录或单文件，`responsibility` 为真实职责 |
| 模块 `allowed_dependencies` | 允许的模块名列表，不是声称已存在的依赖；跨模块实际引用必须在其中 |
| 模块 `import_prefixes` | 从构建配置核实的本地导入前缀/别名，如 `myapp.domain`、`@app/domain`、`example/app/domain`、`crate::domain`、`org.app.domain`。有前缀时该模块使用一个路径根；多根模块可用原生文件边 |
| 模块 `public_paths` | 允许外部模块引用的文件/接口目录；目录覆盖其文件，但目录导入（如 Go 包）只匹配该目录，不自动暴露嵌套子包；空列表即不公开 |
| 模块 `entrypoints` / `docs` | 实际存在的入口路径列表、非空架构文档路径列表；职责、接口与依赖变化后由 AI 核对语义，不只验证文件存在 |

路径用项目相对 POSIX 格式，拒绝绝对路径、越界和符号链接。源码范围内每个文件必须有唯一模块归属。默认剪枝 `.git`、`.vibe-tool`、`__pycache__`、`node_modules`、`.venv`/`venv`、`.next`、`.nuxt`、`.gradle`、`.dart_tool`；实际跳过项在报告中可见。其他生成目录通过 `exclude` 声明；不会把 Rust 的 `src/bin` 当缓存。文件按 UTF-8 读取，其他编码先用原生流程核实后有意调整。

### 自动检查的内容

- 源码唯一归属、必要目录/入口/文档/公开路径存在；缺口不可用债务基线掩盖。
- 文件行数是否超过项目约定；超限是调查与有边界重构的信号，不是任意拆分的理由。
- 实际直接依赖是否越过 `allowed_dependencies` 或目标模块 `public_paths`。
- 从实际跨模块边计算循环，而非从“允许依赖”列表推断循环。
- 当前文件归属、直接依赖、入口/公开路径/文档声明与已审查快照是否一致。新增一个合法文件/依赖也会提示拓扑变化；纯函数体修改不强制更新快照。文档内容是否准确仍需 AI 结合变更审查。

### 多语言分析边界

| 内置提取 | 覆盖的静态声明 |
|---|---|
| Python | AST `import` / `from` 与相对导入；非语法执行 |
| JS / TS | 字面量静态 import/export-from、require、import()；相对路径、配置中列明的别名 |
| Go | 单个/分组 import，映射已声明的 module/package 前缀 |
| Rust | `use` 路径/嵌套组、`mod name;`；映射 `crate`、`self`、`super` 路径 |
| Java | import / static import / 通配包声明，映射已声明的包前缀 |

除 Python 外使用有限词法声明提取，不是完整语法解析。各编译器的名称解析、Rust 宏/条件编译与重导出、Java 全限定内联类型、JS 复杂语法/动态别名、Python 反射等不由该工具证明。未映射的 import、发现的计算式导入、Rust path/include 或未支持后缀显式阻塞并列出覆盖缺口；其他未出现 import 声明的动态关系仍需原生工具和测试。注释/字符串中的伪声明应通过测试排除，但仍应核对实际报告，不把提取成功当作完整依赖覆盖。

外部包前缀只显式列为 external 后才跳过；本地前缀优先，勿用宽泛 external 前缀掩盖本地别名。继续跑项目自己的 linter、编译器、架构测试、集成测试。已有 CodeGraph 仍可辅助查影响，不作为准入前提，也不代替原生证据。

### 原生工具证据：适配其他语言或复杂语法

检查器不自动安装或执行工具。由项目现有编译器/分析器导出真实依赖，再以适合该项目的适配器归一化为以下 JSON；`producer` 记录实际命令或来源，执行日志另存项目已有验证记录。不是让 AI 编造一个空图。

```json
{
  "schema_version": 1,
  "producer": "实际执行的原生依赖导出及适配命令",
  "source_sha256": {"src/App.cs": "所有当前受管源码文件的 SHA256，非占位值"},
  "covered_files": ["src/App.cs"],
  "edges": [{"from": "src/App.cs", "to": "src/Core.cs"}]
}
```

`source_sha256` 必须恰好覆盖当前源码清单，`covered_files` 指明由原生工具替代内置提取的文件；所有来自这些文件的本地直接依赖都应列在 `edges`，目标必须存在且受管。任何源码增删/修改使旧报告失效。C#/Dart/C/C++ 等使用相同文件边协议，不伪称已有各语言编译器适配器。工具验证报告来源标签、结构、端点与哈希新鲜度，不认证生产者身份，也不证明导出器的语义完整性；AI 核对真实命令输出、目标平台和构建条件。

## 存量采用、日常维护与回退

1. **采用**：AI 调查既有目录和构建别名，声明边界并处理归属/解析缺口。基线保存可见现有违规，不要求先重写整个项目。
2. **不恶化**：超大文件基线允许缩短或保持，继续增长即新增问题；其余旧违规绑定当时源码哈希，修改违规文件需重审，不沿用宽泛豁免。消失的旧问题列为可清理记录，不重新制造。契约变化使旧基线失效；不能自动批量接受全部问题。
3. **变更**：在约定内实现和测试；越层、循环或私有接口引用先修实现。合法新增模块/文件/边也核对职责与文档，再审查/保存新快照。快照更新只消除漂移，不消除违规。
4. **人机协作**：AI 调查、实现、验证和维护文档；新的业务边界、不可兼容 API 或接受新增风险才交由人决定，提供契约与候选版本/哈希、证据和影响。未答复只等待依赖该决定的动作，答复后核对版本并从调查/契约继续；小修改不强制新建计划、Issue 或 PR。
5. **交付**：本地检查/原生测试证据和新增/存量问题可见。CI 只运行 check，保留真实退出状态，不在检查前生成基线/快照。模板提供的可选 POSIX quality helper 在发现契约时调用本检查，非零即失败；未配置时明确说明未启用，跨平台直接运行 Python 命令。
6. **回退**：保存本次修改的源码/契约/文档/快照/基线原件与哈希；取消时只恢复拥有的改动，保留后来编辑，重跑相关测试与结构检查。检查器自身只读；候选不是批准，图也不是运行状态。模板更新只刷新工具/参考资源，保留整个 `architecture/` 项目数据目录。

[流程图](code-structure-workflow.svg) · [可编辑图源](code-structure-workflow.json)。从模板目录或安装后的项目根目录重生成并只读检查：

```bash
python scripts/render_codegraph_workflow.py --source references/code-structure-workflow.json --output references/code-structure-workflow.svg
python scripts/render_codegraph_workflow.py --source references/code-structure-workflow.json --output references/code-structure-workflow.svg --check
```
