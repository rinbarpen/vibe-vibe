# Git 仓库跨平台管理 Manifest

> 产物记录的唯一账本是项目根目录 [`MANIFEST.md`](MANIFEST.md)；请追加记录，不要在指令文档中复制清单。

跨平台 Git 仓库管理项目。支持 GitHub、Gitee、自搭建 Git 服务（GitLab、Gitea 等）的仓库同步、镜像、审计与批量操作。

## 🚀 Getting Started（初始化流程）

首次使用本模板初始化新项目后，按以下步骤操作：

```bash
# 1. 创建目录结构
mkdir -p repos configs scripts mirrors

# 2. 配置平台令牌（写入 .env，确保已加入 .gitignore）
cat >> .env << 'EOF'
GITHUB_TOKEN=ghp_xxx
GITEE_TOKEN=xxx
GITLAB_TOKEN=xxx
GITEA_TOKEN=xxx
EOF

# 3. 克隆现有仓库到 repos/
git clone git@github.com:user/repo.git repos/user-repo

# 4. 配置镜像映射
mirror setup github/user/repo gitee/user/repo

# 5. 测试镜像（先用 dry-run）
mirror run github-user-repo --mode branch --dry-run

# 6. 确认无误后执行
mirror run github-user-repo --mode branch --with-tags

# 7. 验证完整性
./scripts/verify-mirror.sh https://github.com/user/repo.git https://gitee.com/user/repo.git
```

## Commands

| 命令 | 缩写 | 描述 |
|------|------|------|
| `mirror` | `m` | 跨平台仓库同步与镜像 |
| `br` |  | 分支批量管理 |
| `tag` |  | 标签管理（semver 版本晋升） |
| `ci` |  | CI/CD 流水线管理（自动镜像/标签/发布） |
| `audit` | `au` | 仓库健康度审计 |

## Architecture

```
<root>/
  repos/          # 本地仓库副本
  configs/        # 跨平台同步配置
  scripts/        # 自动化脚本（同步、审计、备份、CI 辅助）
    mirror-sync.sh      # 跨平台镜像同步
    branch-prune.sh     # 分支批量清理
    tag-manager.sh      # 标签管理（semver 晋升）
    repo-audit.sh       # 仓库健康审计
    verify-mirror.sh    # 镜像完整性验证
  mirrors/        # 镜像映射配置
```

## Environment

| 变量 | 用途 |
|------|------|
| `GITHUB_TOKEN` | GitHub API 令牌 |
| `GITEE_TOKEN` | Gitee API 令牌 |
| `GITLAB_TOKEN` | 自搭建 GitLab API 令牌 |
| `GITEA_TOKEN` | Gitea API 令牌 |

## Conventions

- 仓库命名跨平台保持一致
- 每个平台的默认分支统一为 `main`
- 标签（tag）命名遵循 semver 规范：`v<major>.<minor>.<patch>`
- API 令牌使用环境变量管理，不硬编码
- CI 工作流使用平台原生 Secrets 存储令牌
- 所有破坏性操作（force push、分支删除、标签覆盖）必须先 dry-run

## Gotchas

- **令牌安全**：API 令牌等同于密码，切勿提交到代码库
- **速率限制**：GitHub 未认证 60 req/h，认证 5000 req/h；Gitee 配额因账户等级而异（标准约 3000 req/h）
- **镜像冲突**：双向同步可能导致冲突，**强烈建议主从模式**
- **Tag 同步**：`git push --tags` 推送所有标签，确保跨平台一致
- **Webhook 安全**：使用 Secret Token 验证 webhook 请求来源
- **大仓库**：含 LFS 或大文件的仓库镜像需要额外配置 `git lfs fetch --all` + `git lfs push --all`
- **Force Push 保护**：启用分支保护后 force push 会被阻止，镜像时需 `--force` 标志
- **SSH 端口**：自搭建服务的 SSH 端口可能不是 22，需配置 `~/.ssh/config`
- **GitHub OIDC**：建议用 OIDC (OpenID Connect) 替代长期 Token，减少凭证泄露风险
- **空仓库**：首次同步空仓库时 `--mirror` 模式会失败，先用 `--all` + `--tags`
- **令牌轮换**：定期轮换 API 令牌，建议设置 90 天过期策略

## Workflow

1. **初始化**：配置令牌 → 克隆仓库 → 设置镜像
2. **分支管理**：使用 `br` 管理分支生命周期（ls → prune → protect）
3. **同步镜像**：使用 `mirror` 跨平台同步分支与标签
4. **版本发布**：使用 `tag promote` 晋升版本 → `ci promote` 触发 CI 发布
5. **CI/CD 自动同步**：使用 `ci setup-mirror` 配置自动镜像流水线
6. **健康审计**：定期运行 `audit` 检查各仓库健康度
