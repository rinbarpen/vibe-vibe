# 一句话配置项目

## 目标
已有 Codex / Claude Code 后，以一句自然语言完成 manifest 选择或生成、skills 安装、项目初始化与验证；Windows/macOS/Linux 共享 Python 标准库入口，不要求用户拼接 shell 命令。

## 阶段
1. [complete] 核对现有安装/发现/双端目录约定，定义可验证跨平台边界。
2. [complete] 一句话引导、跨平台入口与双端技能映射、保留已有文件及回退。
3. [complete] 安装/预览/冲突/回退与平台矩阵测试，文档/图一致性验证。

## 决定
AI 选择/生成业务 manifest；确定性安装器不猜测自然语言。沿用已有事实源与安装记录。

## 错误记录
- 首次 provider 内容对照多复制了 commands 根索引，已修正布局并通过对照。
- 完整工具回归初次缺 lxml，使用隔离 uv 环境补齐依赖后通过。
- 真实 CLI 预览发现 repo 来源/生成参数重名，已改为 source_root 并加入实际 CLI dispatch 测试。
