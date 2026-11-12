# 统一写作 Skill

## 目标
新增独立 z-writing 入口，组合已有写作/文风引擎与 z-humanizer；Office 通过它写正文，不复制科研阶段或公众号流水线。不改上游子模块。

## 阶段
1. [x] 核对 AI Vibe、z-humanizer、Writing Plan 和 writing-agent 边界。
2. [x] 创建可独立安装的统一入口、场景说明和上下文约定。
3. [x] 修复学术润色打包缺口并接入 Office。
4. [x] 验证完整安装、源仓库移除、更新/恢复、既有回归，交付补丁和可运行回滚。

## 决策
- 名称 z-writing，与 z-humanizer 并列；它负责写作任务，humanizer 只处理已有文字。
- 通过源仓库相对链接复用规范引擎，安装器物化完整副本；不复制第三方内容为新的维护源。
- Office 依赖用 z-writing 替换直接 ai-vibe-writing，仍为十项；其他科研/基金模板本轮保持原契约。
