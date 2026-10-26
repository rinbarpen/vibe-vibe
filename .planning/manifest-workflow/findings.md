# 已确认事实

- 根 AGENTS.md 是本仓库 manifest 作者规范入口；manifests/vibe-coding 的 AGENTS/CLAUDE 是 MANIFEST.md 的软链接，属于安装后工程契约。
- Unity manifest 已有结构化源、零依赖 SVG 渲染器、漂移检查和安装测试；沿用其现有命名及未提交产物，不强制迁移。
- 通用安装器没有自动复制 references 的约定；本轮仅规范 manifest 创作交付，安装分发须由各模板明确实现和测试。
- 当前没有 dot；公共参考工具使用 Python 标准库，不增加第三方依赖。
