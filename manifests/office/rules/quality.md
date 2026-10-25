# Office 质量门禁

适用于 DOCX、XLSX、PPTX、PDF 的创建与修改。只读提取不触发制作后的独立 QA；提取结果仍须核对来源及页码/单元格定位。

## 工作流与角色

- 主 agent 负责需求、调度及最终交付；先读 `office/README.md`、本规则、`office/rules/file-safety.md` 及相关格式规则，再加载 `.agents/skills/office-quality/SKILL.md` 和对应格式 skill。
- 简单任务使用简短需求记录；复杂、多格式或跨会话任务使用持久化计划。确认受众、用途、输入、模板、格式、数据口径和验收条件，再制作。
- 图片/绘图先读 `.agents/skills/omnidraw/SKILL.md`（含 matplotlib 路由）；所有表格数据/模型/布局及工作簿先读 `.agents/skills/omnisheet/SKILL.md`，再进入底层格式 skill。visuals 交付实际素材或结构化数据，最终格式工程师写入原生表格/图表；不把表格转成图片、不额外创建未请求工作簿。计划和 QA 均核对来源、单位、版本及交接所有权。
- 同一文件只有一个写入者；跨格式任务共用一份已核对的数据和口径。正文/语气由 office-writer、图表素材由 office-visuals 按需准备，最终 Word 仅由 office-docx 装配。角色与交接协议见 `office/agents/subagent-roles.md`。
- 每次创建或修改交付文件后，交给独立的 `office-qa` 审查。独立指非该文件制作 agent 的另一次审查；制作 agent 的自检或脚本返回 0 不替代 QA。

## 必经门禁

1. 重新打开最终文件，检查格式结构、对象和编辑能力；验证脚本只证明其覆盖的结构事实。
2. 对照用户需求、原稿和来源核对正文、图表、单位、日期与关键数值；有语气仿写要求时比较作者样文/风格 profile 与最终正文，给出具体一致性和偏离；配图核对素材、数据/来源、题注、正文引用和替代文本。表格检查全部工作表的公式和数据，适用时完成真实重算。
3. 将用户约束映射到选择的原生样式/模板/编号/域/内容控件/受限编辑等机制，核对实际字段、锁定/删除标志、编辑范围和状态；应用自动化或宏以真实执行记录证明，不用脚本文案替代。只检查本任务选择的功能，不把未选择的宏或引擎列成必需门禁。
4. 渲染最终文件并审阅：DOCX/PPTX/PDF 覆盖所有页面；XLSX 覆盖全部工作表的数据/公式及所有声明为交付视图的打印区域，记录覆盖清单。
5. 独立 QA 读取最终文件和证据，按页、幻灯片或工作表/单元格定位问题。制作角色修复后，重新运行受影响门禁；若重新保存改变分页、布局或公式，重新检查相应全量覆盖。
6. 确认 QA 审查的 SHA-256 与最终交付文件一致；QA 后再编辑会使旧结论失效。

Word 涉及公式/图表动态编号时按 `office/docx/references/equations-and-fields.md` 验收源→OMML、独立 SEQ/书签及实际更新后的 REF/PAGEREF；不以域代码/缓存替代显示核验，不接管第三方文献域。

## 状态与证据

- 交付状态使用 `draft`、`pending`、`passed`：未验收草稿为 `draft`，缺本任务所需的渲染、重算、字体、独立 subagent 或选定的原生功能执行证据，或有未解决问题时为 `pending`。独立 QA 的 verdict 单独使用 `pass`、`pending`、`fail`，分别表示证据齐全且通过、缺条件/证据、已确认缺陷；QA `pending` / `fail` 均映射为交付 `pending`。
- 只有全部适用门禁有实际证据且独立 QA verdict 为 `pass`，才将交付状态标记 `passed`。结构检查通过、成功退出、文件存在或制作角色说已检查，都不是总体质量通过。
- 报告包括源文件及最终文件路径/哈希、需求和数据来源、实际命令/输入/字面输出/退出状态、渲染预览路径、逐页或逐工作表覆盖、数值核对、独立 QA 身份/结论/证据路径与剩余限制。
- 可用 `python office/scripts/doctor.py` 检查依赖，`python office/scripts/verify.py FILE --output REPORT.json [--baseline FILE]` 记录结构检查，`python office/scripts/render.py FILE --out-dir DIR` 获取预览；只有真实运行并检查产物后才记为已执行。这些工具不自动批准内容、视觉或独立 QA。
