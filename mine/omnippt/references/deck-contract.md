# 原创 Deck Contract 与静态检查

`templates/deck-contract.example.json` 是本仓库原创的两页合成案例，数据在同目录 `sample-data.csv`。所有用户选择标为 `evidence_type: simulated`，不是真实批准或现实业务数据。字体、画幅和色彩仅为该例参数，可按模板与用户需求调整。

## 最小契约

- `schema_version: 1`、稳定 deck `id`、正整数 `revision`，`mode` 为 create/template/edit；brief 记录 audience/outcome。
- canvas 记录 width/height/unit，所有 storyboard `box: [x,y,w,h]` 为同一画布坐标系中的绝对坐标。tokens 记录 font、background/foreground/accent 和正文/标题 pt 值；不是强制设计标准。
- sources 有稳定 id、kind(data/url/file/user)、location；facts 有 id、text、source_ids；outline 依顺序列稳定 slide id、conclusion、fact_ids。建议或假设不能伪称来源事实。
- storyboard 与 outline 的 slide ID 一致；elements 有 id、kind、box、native、fact_ids，按需有 text、parent、chart、operation。`parent` 明确有意包含；其他区域避免意外重叠。kind 区分 text/shape/card/table/chart/image/group，原生数据表不得标作 image；图片或 SVG 数据图也显式 `chart:true`，不能躲过决定门禁。
- `stage_revisions` 的 outline/storyboard/design 跟随当前 revision；改内容后同步策划/视觉，不以老计划绑定新文件。edit 合同只列本次选定页面，outline/storyboard 的 ID 集合与 edit_scope.slide_ids 完全一致，并写 notes；原文件基线及未选页保留另外核验，最终文件仍全页视觉审阅。template 路线记录 template.path/sha256。
- decisions.chart/macro 各有 decision(yes/no/pending)、scope、source 和 evidence_type(user/simulated)，宏另有 requested_modes(preserve/create/modify/invoke)。yes/no 必须有本次来源；同一 scope 内仍是两个独立决定。宏选 create/modify/invoke 时在 macro.operation_details 下按模式记录 target、intent、effects；invoke/modify 另给精确 entry。细节不全仅该操作 pending，不把 yes 当作任意宏可运行。

## 使用已捆绑检查器

从安装后的 skill 实际目录调用，不依赖源仓库：

```bash
python3 scripts/validate_deck.py templates/deck-contract.example.json
# 用户项目实际合同可给绝对路径；报告使用新路径
python3 scripts/validate_deck.py /ABSOLUTE/PROJECT/deck-contract.json --report /ABSOLUTE/PROJECT/evidence/contract-check.json
```

可导入 `validate_deck(contract, *, base_dir=None)` 取得检查记录；本地来源/模板相对 base_dir 解析，不传时对应文件检查待验收，CLI 自动使用合同所在目录。它提供来源 ID/事实引用、阶段/页面映射、坐标/层级与确认范围等**静态**证据，不联网核实来源、不认证用户答复、不执行宏，也不生成或打开 PPTX。CLI 退出 0 只说明 structure_valid，仍须查看 blocked_operations 与 ready_for_all_requested_build，不得忽略待确认分支。检查通过仍是策划草稿/`quality_status=pending`，不证明字体可用、真实对象可编辑、数据正确、文本不溢出或视觉/独立 QA 完成。

pending 图表只让新增制图范围待确认，非图表策划仍可继续；明确 no 与新增图表并存则先修合同矛盾，不生成图片绕过。模拟合同不得用于真实宏执行或真实用户确认。模板路径、来源文件、字体与目标应用的可用性按实际路线另查；合同文本中的 native 标志只是目标，实际文件重新打开、对象检查、全页渲染和独立审查才验收交付。
