# 工作包实例

状态：planned / in_progress / waiting_dependency / waiting_human / review / complete  
工作包 ID：production.json 中稳定 task id；实例 ID：同一工作包的批次/资产/修复实例  
owner（单写者）：；reviewer：独立 / self-review（具名）  
模式：design-only / implementation；阶段：lifecycle 节点；设计 revision：

## 目标与适用性

- 关联 REQ-ID、类型/平台/维度、选定引擎与版本、需求来源：
- 本包目标与明确排除：
- 适用性：适用 / 不适用；不适用理由与受影响的依赖/替代验证：
- 依赖 task/实例、输入产物路径/资产 ID/hash、当前就绪/阻断状态：
- 裁剪依赖的理由、替代输入和影响；若改变约定，DEC-ID 与决定：

## 执行计划与真实操作

- 工具/Editor/DCC/SDK 版本、接口/许可与实际 cwd/env：
- 源→导出→导入→运行的路径/资产 ID，缓存/生成物边界：
- 修改前 commit/分支/源文件快照/原件 hash，用户未提交改动与文件锁：
- 本次具体步骤/命令、输入/随机种子/测试存档、单写者路径：
- 运行结果：原始 stdout/stderr/exit、DCC/引擎日志、截图/录制与输出 hash：
- design-only 时仅完成规格/验收计划；实际文件制作或运行保留 not_run，不以文字替代模型/构建/试玩产物。

## 验收矩阵

| CHECK/TEST-ID | 输入/前置与样本 | 具体步骤/命令 | 可观察预期/数值阈值 | 实际结果与证据 | pass/fail/not_run | reviewer |
|---|---|---|---|---|---|---|

配置/静态检查、源文件可打开、导出、引擎导入、实际游玩、目标设备和真人反馈分别填；结果不能互相替代。验收阈值须在执行前明确，未测/已接受风险显式列出。

## 缺陷、返工与恢复

- BUG-ID、严重度、最短复现、预期/实际、原 owner 与下一次修复假设：
- 从 production task 绑定的 rollback 到本项目实际分支/快照/包/配置/数据：
- 恢复步骤、后续编辑冲突检查、恢复后重跑的原用例与相邻回归：
- 技术三轮实验结果仍需改变目标/预算/工具付费等约定时：选项/成本/推荐、DEC-ID、waiting_human 与明确 resume：
- 缺依赖时：waiting_dependency、缺失工具/设备/连接、可继续的其他工作与依赖就绪后恢复用例：
- 数据不可逆、外部发布或生产数据变更：先由相应 lifecycle 人工门记录决定，代码回退不代替服务/存档恢复。

## 交接与完成

- 产物、源/导出/导入/实现位置、hash、版本/锁文件、许可/来源：
- 需求追踪/资产账/证据台账更新位置：
- 作者自检与独立审查或 self-review 的分栏结果：
- 未测/已接受风险、依赖释放/锁交还、下一 owner、首个未完成动作与 resume：
