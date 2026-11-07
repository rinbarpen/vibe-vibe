# 游戏项目的版本管理与协作

版本管理覆盖代码、设计、数值、资产、工具链、存档和线上内容，不只是添加 Git 分支。先用 [版本策略模板](../templates/version-policy.md) 写明当前仓库事实和方案；模板安装不初始化/重写用户仓库，不自动改 remote、LFS/typemap，不默认提交、推送或上传资产。

## 1. 先调查，再选版本控制方案

| 方案 | 适用条件 | 需要验证的条件 |
|---|---|---|
| 现有 Git | 代码/文本占主、团队已有成熟 Git 习惯 | 资产大小/增长、clone 与构建时间、备份、分支规则、源文件可达性 |
| Git + LFS | 需保留较大二进制资产，且托管/CI 能提供对应对象 | 存储/带宽/成本、客户端/CI 安装、真实对象下载、LFS 锁服务支持及推送校验 |
| Perforce / P4 | 大量二进制、集中资产协作、已有 P4 运维或明确需求 | 服务器/备份/许可、workspace/stream/typemap、权限与 exclusive-open、CI 内容同步 |
| 外部资产库 + Git 清单 | 资产仓库已有稳定不可变版本与访问机制 | 清单含版本/hash/许可，离线/CI可取回，源可恢复；只有共享网盘路径不算可复建 |

已有工程优先延续方案。切换仓库/重写历史/迁移大文件是独立变更：先完整备份、估算成本、确认协作窗口并在副本演练。按 [Git LFS 官方说明](https://git-lfs.com/)，添加 tracking 规则本身不会转换旧历史；不要声称执行 `git lfs track` 已完成历史迁移。

## 2. 源、生成物、缓存与证据分层

| 分类 | 通常应保留 | 单独定义策略 |
|---|---|---|
| 权威源 | 游戏代码、GDD/数值/关卡、`.blend/.psd` 等 DCC 源、实际纹理/音频源、脚本与导出 preset、工具配置/锁文件 | 大二进制用已选 LFS/P4/资产库，不用 ignore 丢弃唯一源 |
| 引擎源与引用 | Unity `Assets/`、`.meta`、`Packages/`、`ProjectSettings/`；Unreal `Content/Config/Source`、`.uproject`；Godot `project.godot`、`.tscn/.tres` 与 `.uid`；其他引擎真实工程/事件数据库 | 成对 ID 与资源迁移一起提交；文本序列化的 Scene/Prefab 仍可有语义冲突 |
| 可重建生成物 | 编译代码、烘焙/导出结果、打包资源、生成代码 | 写明生成源/工具/参数/版本；游戏发布依赖的必要导出物可需入库或不可变制品库，不一概丢弃 |
| 缓存/临时 | Engine import cache、编译中间目录、IDE 临时物 | 按实际引擎/版本与路径审批 ignore；清理前确认不是唯一恢复副本 |
| 证据/构建制品 | 原始日志、测试报告、包哈希、截图/录屏、release manifest | 归档到 Git 或制品存储，策略记录保留期与访问；CI workspace 缓存不是发布归档 |
| 敏感/个人态 | 私人凭据、签名私钥、生产数据、未脱敏试玩数据 | 通过已配置的密钥/数据管理；公共提交只保留无秘密的配置 schema/例子 |

以下仅是**项目根路径片段**，选定引擎并审查目录内容后再合并，不由安装器自动写 `.gitignore`：

```gitignore
# Unity cache — keep Assets/, .meta, Packages/, ProjectSettings/
/Library/
/Temp/
/Logs/

# Unreal generated cache — keep Content/, Config/, Source/, .uproject
/Binaries/
/DerivedDataCache/
/Intermediate/
# Saved/ may contain recovery data; archive needed autosaves before choosing an ignore rule.

# Godot 4 import/editor cache — keep .uid and engine source assets
/.godot/

# JS / .NET generated dependencies only when those paths are genuinely generated
/node_modules/
/obj/
/bin/
```

禁止用 `Assets/`、`Content/`、`*.meta`、`*.uid`、`*.blend`、`*.fbx` 这类源/资源规则“缩小仓库”。构建目录也需明确路径：项目自有名为 build 的源目录不因名字就被忽略。Git 官方说明 `.gitignore` 影响未跟踪文件，已跟踪文件不会因此退出版本库；已被忽略的父目录也不能靠内部否定规则轻易救回，见 [gitignore](https://git-scm.com/docs/gitignore)。

## 3. 大文件与单写者锁

经项目确认后，Git LFS 可按类型/目录管理不可文本合并的源文件；下面是待审查 `.gitattributes` 片段，而非已经启用的配置：

```gitattributes
*.blend filter=lfs diff=lfs merge=lfs -text lockable
*.psd filter=lfs diff=lfs merge=lfs -text lockable
*.fbx filter=lfs diff=lfs merge=lfs -text lockable
*.glb filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.uasset filter=lfs diff=lfs merge=lfs -text lockable
*.umap filter=lfs diff=lfs merge=lfs -text lockable
```

`.meta/.uid`、代码、配置及文本场景不默认送入 LFS。`.gltf` 文件和其 buffers/images 必须一起保留，不能只保留文本 JSON。压缩交换文件是否入 LFS 按项目预算决定，规则不是“所有媒体同一种处理”。

Git LFS 的远端锁依赖服务端和客户端的校验配置；`lockable` 或本地 owner 表不是普遍强制互斥。先验证 [LFS lock 的真实行为](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-lock.adoc)，无可靠锁服务时使用团队明确的单写者认领+审查门。P4 的 `+l` exclusive-open 与普通 `p4 lock` 不同，使用 [官方 exclusive-open 规则](https://help.perforce.com/helix-core/server-apps/p4guide/current/Content/P4Guide/resolve.lock.exclusive.html) 配置并演练；不要声称仅加普通锁就阻止所有人打开。

二进制 DCC 场景、World/Level、Prefab/数据库、骨架/动画工程、云 Editor 场景采用路径/资源 ID 单写者。其他人修改独立文件或提交建议；文本能合并也不代表引擎引用/场景语义正确。

## 4. 日常版本闭环

1. **恢复与基线**：检查当前分支、dirty files、未保存 DCC/Editor 场景、remote 与上一个已验证 revision；先保留修改，不替用户清理工作树。
2. **拆分与认领**：工作包绑定 REQ-ID/BUG-ID、分支、owner、单写者路径/锁、验收与回退。团队可用短 feature/fix 分支或既定 trunk-based；不要为每个小动作强制长期分支。
3. **在隔离单元执行**：代码可用独立工作目录/worktree；同一引擎工程/场景的 GUI 写入仍串行。worktree 不是共享云资产或外部 DCC 文件的隔离。
4. **提交前自检**：显式暂存相关文件；核对源+ID配对、二进制/大文件、数据 schema、许可/依赖、锁文件与可重建命令；不把无关用户修改一起提交。
5. **审查**：代码 diff、设计/数值变化、资产前后视图/统计、测试原始证据与 save/network 兼容分别审查；review 绑定 revision/hash，变更后必要项重跑。
6. **合并与 CI**：沿用已有保护分支。CI 在干净 checkout 中取得真实 LFS 对象/资产库版本，安装锁定工具，做设计数据校验、逻辑/引擎测试、资源/依赖检查、实际构建与包 hash；图形/设备/真人试玩分别保留状态。
7. **交付与清理**：发布后记录 revision/制品与风险；仅在确认合并、产物与后续恢复可用后清理临时目录或解锁，不擅自删除原场景/源资产。

已有 `version-management` 可负责 ROADMAP/TODO、依赖分层、replan 与验证；`git-manager` 负责对应托管平台的 PR/CI/release。它们按 [工具路由](tool-routing.md) 可选接入，不自动创建远程仓库、提交或推送。

## 5. 游戏需要多个独立版本轴

| 版本字段 | 用途 | 变更与兼容条件 |
|---|---|---|
| `client_version` | 对玩家/商店可见的软件版本 | 项目可采用 `MAJOR.MINOR.PATCH[-prerelease]`，明确“兼容”的公开契约；不是只看功能数量 |
| `build_id` | 每个 CI/本机构建的唯一标识 | 同 client_version 的不同产物有不同 build_id、commit、工具链与包 hash |
| `content_version` | 关卡/数值/资源/配置内容版本 | 与客户端接受范围、资源清单和缓存失效/回退策略绑定 |
| `save_schema` | 存档数据结构版本 | 有迁移函数、旧档样本、备份、向后/向前兼容范围与失败恢复 |
| `network_protocol` | 客户端/服务器消息契约版本 | 明确兼容矩阵、混版本连接规则、服务端/客户端发布顺序 |
| `toolchain_revision` | 引擎/SDK/插件/DCC/exporter/脚本 | 锁文件与 source manifest，可重新构建同一包，升级是有证据的变更 |
| `design_revision` | 已批准的设计/需求与数值基线 | 哪些设计对应本构建、试玩与人工决定，避免“文档最新”与发布包脱节 |

[SemVer 2.0](https://semver.org/) 为公开兼容契约定义版本语义；游戏是否采用、存档/协议是否兼容需要项目自己的规则。不能从 `1.2.3` 字符串推导旧档可读或在线混版本可连。推荐 release manifest 同时保存上述字段、source commit、依赖与完整文件哈希。

## 6. 发布、补丁、迁移与回退

- 候选包/资源清单/hash 一旦进入审批就冻结；任何内容变更产生新 build_id/hash 并补足受影响测试，不在原 tag 下悄悄替换文件。
- 发布 tag 指向审查的源码 commit，附带构建/内容 manifest 与 changelog；签名/保护策略沿用仓库约定。源码 tag 不等于商店已经上线，也不包含自动 LFS/云资产备份保证。
- 补丁记录基础版本范围、差异内容、校验、下载中断/断电恢复、缓存与空间预算；完整旧包与清单保留。客户端、内容、服务端和配置可独立回退，需兼容矩阵。
- 存档迁移先复制旧档样本，在隔离目录验证成功/失败/重复迁移/断电场景；有不可逆字段或生产数据变更时先过人工门。不把旧客户端恢复等同于旧存档恢复。
- 共享分支上撤销已合并修改优先使用项目约定的反向提交流程，审查冲突后再推进；[git revert](https://git-scm.com/docs/git-revert) 创建反向提交，代码层面的撤销仍需资产、存档和实际包复验。不得用 destructive reset/force-push 作为默认回退。
- 发布异常按生产计划停止扩大影响，恢复已验证客户端/内容/配置/服务；复跑原始问题、存档/联网兼容与代表场景。恢复证据齐备才标回退完成；重新发布另绑定新候选 hash。

## 7. 只读检查与缺依赖状态

安装后运行：

```bash
python3 .game-design/scripts/version_check.py --project . --large-mb 10
```

该工具只读报告 Git 仓库/分支/dirty、已跟踪缓存、大二进制/LFS 覆盖、锁建议和版本元数据待决；`--large-mb` 是报告阈值，不是自动配置/迁移上限。它不写 `.git*`、不初始化仓库、不运行 migrate/提交/推送、不据此批准发布。未装 Git/LFS/P4 或缺远端状态时记录 `not_run/unknown` 与恢复步骤；只读本地报告不能证明远端锁、完整资产备份或云数据恢复有效。
