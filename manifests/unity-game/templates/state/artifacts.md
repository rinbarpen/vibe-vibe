# 产物与验证索引

主代理单写。模板不登记为实际完成产物；路径、输入版本和实际证据齐全后登记。

| ID | 阶段/任务 | 产物路径 | 源码/文档/构建版本 | 验证状态 | 命令/日志/XML/试玩证据 | owner / 接收角色 |
|---|---|---|---|---|---|---|

## 覆盖与缺口
- 真实 Editor：not_run
- EditMode / PlayMode：not_run
- 目标平台构建/设备 smoke：not_run
- 真人试玩与目标设备性能：not_run
- 独立审查：not_run
- 实际外部发布：not_run

运行验证结果仅使用 passed / failed / not_run；独立审查另记review_status与passed / changes_requested / blocked，并链接审查报告、输入哈希与批准revision。保留失败尝试与环境依赖，不将缺结果、零测试、超时或文档检查写成运行通过。
