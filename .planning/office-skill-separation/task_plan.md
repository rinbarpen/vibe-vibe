# Office Skill 与办公 Manifest 分层

## 目标
将通用办公流程、格式指南、宏与验证工具迁入可独立安装的 mine/office；保留 manifests/office 作为业务项目协作模板，显式包含 office 及具体技能依赖。不改无关已暂存变更。

## 阶段
1. [x] 核对当前安装器、资源、技能与回归测试。
2. [x] 保存基线与基线测试；抽取 Office 技能并重写办公项目契约。
3. [x] 对齐安装、原生角色、路径、目录说明与可复现工作流。
4. [x] 验证独立 Skill、Manifest init/add/setup/update、原有功能与回滚。

## 决策
- 保留 office 作为办公项目 Manifest 的兼容名称；mine/office 是可复用能力的唯一源。
- Manifest 保留项目目标、来源/版本、交付/决策/归档约定；不再拥有格式实现。
- 沿用已有格式 Skill、office-quality 和 Omni 系列，不复制第三方能力，不增加公共 CLI。
- 既有用户项目不删除旧 office/ 数据或静默迁移；新安装使用 .agents/skills/office。
