# 发现

- 已有项目内 .vibe-tool/installations.json（schema 1）；上一轮 setup 另有 .vibe-setup.json 哈希与 agent 入口约定。
- 原 project_update 可复用已安装 skill 来源、生成选项、资源白名单和事务；全局索引不复制这些数据。
- 内部 skill 安装和渲染使用临时目录，自动登记必须放在 CLI 成功边界/真实 setup 应用完成后，防止收录临时项目。
- 不改变旧 init/add/update 的覆盖策略；setup 更新由单独的路径维护导入侧车、Claude 副本与 setup 哈希。
- 仓库已有未提交更改及上一轮完成产物，按本轮开始状态备份，不回滚到 HEAD。
