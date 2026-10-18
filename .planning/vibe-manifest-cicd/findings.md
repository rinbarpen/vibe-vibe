# 已确认事实

- 现有 vibe-init.sh 总是复制 GitHub 治理文件与 12 个工作流，未在目标根目录生成 CHANGELOG。
- 现有 release.yml 标签 glob、可复用 CI 调用和跨 job 制品传递存在问题；hotfix.yml 在打标签后才尝试写 Changelog。
- vibe CLI 尚无 provider 参数；初始化脚本有独立 dry-run 路径。
- Gitee Go 官方文档支持 PR/Push/Tag 触发，流水线文件位于 .workflow；首次需在平台启用。
