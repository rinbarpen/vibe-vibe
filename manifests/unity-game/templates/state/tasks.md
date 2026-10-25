# 任务与路径所有权

主代理单写；子代理通过 handoff 返回建议。任务状态使用 todo / ready / running / blocked / done，验证结果另用 passed / failed / not_run。

| ID | 阶段/角色 | 目标 | 输入版本/依赖 | 唯一可写路径 | 状态 | 验收/证据 | 交接对象 |
|---|---|---|---|---|---|---|---|

## 执行与审查关联
- 每项任务记录阶段执行skill、原专项skill/owner、冻结输入revision/哈希。
- 审查报告记录reviewer skill/profile、独立上下文、review_status、verdict和批准revision。
- changes_requested回原skill/owner；blocked或not_run保持待验。修改生成新revision并复审，主代理单写推进状态。

## 排队与锁
| 资源/Scene/Prefab/配置/Editor | owner / 任务 ID | 开始/释放条件 |
|---|---|---|
| .unity-game/state/* | 主代理 | 全程单写 |

## 最近批次
- 实际启用角色与执行方式：待分配
- 集成结果与失败修复任务：无
- 下游解锁条件：待定义
