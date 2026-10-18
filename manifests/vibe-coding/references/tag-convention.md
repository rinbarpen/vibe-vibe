# Tag Convention Guide

## Tag Naming

| Tag Pattern | 用途 | 示例 |
|-------------|------|------|
| `vMAJOR.MINOR.PATCH` | 标准发布 | `v1.2.3` |
| `vMAJOR.MINOR.PATCH-rc.N` | 预发布候选 | `v1.2.3-rc.1` |
| `vMAJOR.MINOR.PATCH-hotfix.N` | 紧急修复 | `v1.2.3-hotfix.1` |

### 规则

- 所有 release tag 以 `v` 开头
- 严格遵循 SemVer 格式
- RC 序号从 1 开始递增（`-rc.1`, `-rc.2`, ...）
- Hotfix 序号从 1 开始递增（`-hotfix.1`, `-hotfix.2`, ...）
- 其他 SemVer 预发布后缀（如 `-beta.1`）也可使用，但 `VERSION`、Changelog 与 tag 必须完全一致

## GPG 签名

所有发布 tag **必须** GPG 签名。

### 配置 GPG 密钥

```bash
# 生成密钥
gpg --full-generate-key

# 列出密钥
gpg --list-secret-keys --keyid-format LONG

# 配置 Git 使用该密钥
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true
git config --global tag.gpgSign true
```

### 创建签名 tag

```bash
git tag -s v1.2.3 -m "v1.2.3"
```

### 验证 tag 签名

```bash
git tag -v v1.2.3
```

输出示例：
```
object abc123...
type commit
tag v1.2.3
tagger User <user@example.com>

gpg: Signature made ...
gpg: Good signature from "User <user@example.com>"
```

### 在 GitHub 上传公钥

1. 导出公钥：`gpg --armor --export <KEY_ID>`
2. 复制输出
3. 访问 GitHub Settings > SSH and GPG keys > New GPG key
4. 粘贴公钥并保存

## Tag Protection

### 推送保护

在 GitHub Web UI 中配置（Settings > Branches > Add tag protection rule）：

| 规则 | 值 |
|------|-----|
| Tag pattern | `v*` |
| 允许推送 | Only admins |

### 不可变性

- Release tag 一旦创建，**不可移动**（禁止 `git tag -f`）
- Release tag 一旦创建，**不可删除**
- RC tag 可以被后续的 RC 或 final release tag 取代（先创建新 tag）
- Hotfix tag 和 final release tag 同等对待

### 审计追踪

Tag push 作为 release 触发器（而非按钮 workflow_dispatch）的原因：
- `git log --tags` 可以追溯完整的发布历史
- `git push origin v1.2.3` 的行为被 GitHub audit log 记录
- 无法绕过的审计链（必须保有 SSH key 的 access）

## Workflow 中的 Tag

### release.yml 响应 tag push

```yaml
on:
  push:
    tags:
      - "v*"
```

`release.yml` **不创建 tag** — tag 由 release manager 手动创建，workflow 只响应。

### Hotfix tag

`hotfix.yml` 先校验 `VERSION`、Changelog 和项目检查，不创建 tag 或自动部署。合并后由发布负责人运行 `python3 scripts/version_guard.py check --tag "v$(cat VERSION)"`，再创建 GPG 签名 tag 并推送。

## 常用命令

```bash
# 列出所有 tag
git tag -l

# 搜索 tag
git tag -l "v1.2.*"

# 查看 tag 详情
git show v1.2.3

# 基于 tag 创建分支
git checkout -b hotfix/v1.2.4 v1.2.3

# 删除本地 tag（仅紧急情况）
git tag -d v1.2.3
```
