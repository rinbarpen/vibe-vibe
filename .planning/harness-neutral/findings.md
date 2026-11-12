# 发现

- 用户纠正：不必兼容 Cursor；取消保留 Cursor 输出的路线。
- 当前源有 65 个 .mdc 与 6 个普通 .md 规则，业务与 globs/alwaysApply 需保留而不要求宿主解释 MDC。
- 便携 render 为 setup 与项目更新共用；旧 init/add 与直接 update 保持原单独入口与回退语义；统一新入口为 setup / project update，不扩展 Cursor 兼容。
- 不迁移无关业务阶段，也不改各模板的科学/人工门；源规则内容保持单一事实源。
