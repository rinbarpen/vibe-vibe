# Harness 无关的 Manifest 规则

## 目标
Manifest 业务契约和规则不依赖 Cursor。新 setup 输出普通 Markdown 规则、作用域和通用 PROJECT_RULES.md；保留 Codex/Claude 入口，并提供 generic harness 入口。旧 .mdc 仅作为存量源输入，不维护 Cursor 输出兼容层；不删除用户旧目录。

## 阶段
1. [complete] 核对规则源、安装/更新入口与用户最新要求。
2. [complete] 中立规则包、通用入口、安装/项目更新/回退贯通。
3. [complete] 业务规则与范围保真、全 manifest/场景与真实安装测试。
4. [complete] 文档/图同步、基线对照与回退验证。

## 决定
- 单一业务源，生成普通 Markdown/规则索引；不手工复制两套业务事实。
- 新 setup 不分发 .cursor；现有用户目录不批量删除。
- 文件分发/规则可读性与宿主实际加载/工具可用性分别验收。

## 错误记录
无。
