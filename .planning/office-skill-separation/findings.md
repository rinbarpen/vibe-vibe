# 发现
- 当前通用 Office 资源和工具均在 manifests/office；office-quality 仅有质量编排，没有这些工具。
- Skill 安装是完整目录复制，不递归安装 dependencies。办公项目 skills.txt 须显式列出 office 和已知九项依赖。
- 便携 setup 原生调用 install_office.py，历史 init/add 经 shell 委托同一 Python 安装器。
- 当前工作区已有大量用户暂存变更；本任务只编辑已快照的 Office 相关路径，保持 index 不变。
- 当前图源为 Mermaid，需保留既有运行图；新增项目契约图使用标准库 renderer + JSON + --check。

## 已验证的分层
- `vibe add skill office <target>` 只安装可复用能力，不覆盖项目入口、不注册原生角色，也不隐式安装其他 Skills。
- `vibe init office <target>` 安装业务契约、Office 和九项配套能力；角色来自 Office Skill 的唯一源。
- 历史 update 只新增办公项目明确管理的规则/图源/渲染器/模板选择，不扩大到用户旧格式目录。
- 原 Word/Excel VBA 模块迁移前后逐字节 SHA-256 相同。
