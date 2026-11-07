# 游戏版本、资产协作与发布策略

状态：proposed；DEC-ID/WORK-ID：；owner：；适用工程根：；批准 revision：

## 1. 已有事实与决策

- 当前 Git/P4/资产库、分支/dirty、remote、LFS/P4 客户端/服务端、CI、工具版本、资产大小/增长：
- 继续已有方案或拟变更方案；备选、成本/带宽/备份/许可、维护人、迁移/停写窗口：
- 明确允许的本地修改、提交、远端动作；未批准动作不自动执行：
- 版本控制/分支/上传/历史迁移变更的决定人、日期、风险与 resume：

## 2. 目录与所有权

| 路径/资源类型 | 源/生成/缓存/证据 | Git/LFS/P4/制品库 | 单写者/锁/owner | ignore/属性规则及理由 | 恢复/保留期 |
|---|---|---|---|---|---|

保持引擎资源 ID 与源成对；Unity `.meta`、Godot `.uid`、场景/事件数据库、DCC 源与必要纹理/音频不被粗粒度 ignore 丢弃。应用规则前用实际源文件样本核验。

## 3. 分支、工作包、审查与 CI

- 主干/feature/fix/release/hotfix 规则、命名、合并门/保护分支、owner：
- WORK-ID/REQ-ID/BUG-ID → 分支/路径/锁 → 输入/产物/测试 → review revision → 合并：
- DCC/Editor/云场景单写者；文字/数值/代码并行的隔离范围：
- CI checkout/真实 LFS 或资产内容、锁定 Editor/SDK/DCC/插件、单测/引擎/资源/构建任务：
- 目标设备、性能、真人试玩与未测项如何记录；缺图形/设备不报告通过：
- 提交前凭据/许可证/引用/大文件/无关修改检查、资产前后对照：

## 4. 独立版本轴与兼容矩阵

| 字段 | 当前值 | 决定规则 | 兼容/迁移/回退范围 |
|---|---|---|---|
| client_version | | | |
| build_id | | | |
| source_commit | | | |
| content_version | | | |
| save_schema | | | |
| network_protocol | | | |
| toolchain_revision | | | |
| design_revision | | | |

SemVer 的公开契约是什么；旧档/旧内容/在线混版本分别有哪些支持组合；未知组合保持待测。

## 5. 候选包、发布与回退

- release tag/commit、候选包/完整资源清单/hash、构建命令/输入、changelog、签名与制品归档：
- 人工批准绑定平台/受众/包 hash/revision；任何变动换 build_id 并重跑受影响测试：
- 补丁基础版本/下载校验/断电恢复/缓存/磁盘预算、完整旧包保留：
- 旧档样本/迁移脚本、成功/失败/重复/中断测试、备份与不可逆风险：
- 客户端/内容/配置/服务端/存档分别的恢复路径、允许顺序、停止扩散阈值：
- 恢复后原用例/兼容/代表关卡验证，负责人/实际结果/原始证据：

## 6. 证据

| 检查 | 工具/命令/cwd/env/输入 | stdout/stderr/exit | 产物/hash | pass/fail/not_run | reviewer |
|---|---|---|---|---|---|
