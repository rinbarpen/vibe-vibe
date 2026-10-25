# 已确认事实

- CLAUDE.md 触发 manifest 动态发现，scripts/*init*.sh 选择自定义安装器。
- 通用安装器不复制 references/templates/角色目录，因此本模板自带安装器。
- CLI 无专门 flag map 时自动传 -f/-n，支持计划内接口而无需修改 CLI。
- 可用 skills: version-management、git-manager、omnidraw、state-machine-reasoning。
- 角色目录标题 + Claude YAML + Codex TOML 由 scripts/validate-agent-compat.py 校验。
- Unity 项目资源和 .meta 成对；同工程 Editor 串行；证据区分 passed/failed/not_run。

## 集成审查修正
- 既有 CLI 将 manifest --force 传给必需技能安装器，会删除自定义技能。新增可选 skills-policy.json/preserve_existing，Unity 启用；其他 manifests 默认行为保持，显式 add skill --force 保持。
- 安装器将 .agents/skills 路径纳入写入前 symlink/目录预检。
- 独立审查要求补齐基础 Sprite/模型/贴图制作或获取 owner，以及源资产→导入→最终验收记录。
- helper 成功需有效 XML/产物与非空 Editor 日志；构建输出保护覆盖 symlink 资源根。

## Skills 分层实现
- 采用 mine/unity-game-development 下的 1+9+29 树，所有目录名与 frontmatter 名一致，使用 unity-game-* 前缀避免冲突。
- 父入口只链接自身子技能；29 个叶子自包含，独立安装仍具备输入、步骤、产物和验收。
- skill-map.json 维护九阶段与20角色映射；两个原生运行时正文保持一致。
- skills.txt 仅添加总包一次，现有递归复制机制安装全部后代，无需改发现/安装 CLI。
- manifest 强制刷新继续保留已有技能，旧工程补装缺失包；更新已有技能包使用显式 add skill --force。

- 独立前向样例实际生成了存档回归计划、性能数据摘要和经济模型CSV。性能样例避免混比Editor与设备；数值样例区分连续收入和离散掉落；存档叶子根据观察补充专项范围裁剪。
- 本轮增量共43个新增文件、53个变更文件；补丁与回滚保留此前完成的Unity manifest。副本应用后70测试通过，回滚后恢复此前61测试通过。

## Executor / Reviewer / SVG
- 保留原39技能，添加9个阶段execute和reviewer的5个技能，共53。目录schema v2显式维护execution/review/profile/approval与review_policy。
- 每阶段固定实际execute入口；reviewer为独立game-reviewer上下文，用unity-game-review和4类审查subskills检查固定revision/哈希。
- verdict与测试状态分开；blocked或review not_run不推进，changes_requested回原skill/owner，新revision复审，用户三个门保留。
- SVG由同目录生成器基于目录生成，安装后优先本项目技能包而非相邻源码，--check只读。
- 独立前向原型样例blocked，设计样例changes_requested；对仅静态规格未强加Editor或全套GDD。

## 模型/DCC核验
- 根mcp.json实际不存在，因此仅归档可选config，不宣称vibe mcp add blender为现成接口。
- mcp-for-blender==2.2.4以PyPI发布元数据核验；Unity MCP v10.3.0以维护者固定README/UPM核验。软件通道需真实发现schema或读取实际软件skill。
- 默认Blender模板为已有静态网格导出，不是模型生成器；--new须提供实际创作脚本。副本相对依赖、任意Python权限和真实Unity验收边界已记录。
- glTF/GLB依赖项目实际importer；.blend直导依赖DCC。DCC保存/重开、导出、Unity导入、设备实测分别记录状态。

## 实际游戏测试与可靠性核验
- 实际测试skill通过真实发现的输入工具/harness/桌面或浏览器skill执行，Scene检查/状态注入不冒称普通输入覆盖；AI不等于真人好玩反馈。
- 会话JSON与独立review侧车分开，避免批准哈希自引用；验证器检查记录契约，不证明物理观察真实性。
- 安装事务在新版本移除旧journal路径时保守停止并提示先用原来源恢复，不自动接纳任意旧路径所有权。
- 真实Editor/Blender集成、2D/玩法/UI等更深专项和完整DAG状态引擎仍是后续可选工作，未在本轮冒称完成。
