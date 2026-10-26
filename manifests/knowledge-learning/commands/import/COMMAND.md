---
description: 导入学习材料并建立轻量来源索引；上传教材后引导生成章节学习路线
globs: ["materials/**/*", "projects/**/*"]
---

# /import

## Purpose

识别材料载体、保留原件并建立可回溯的教材地图。默认先索引，再规划，深入学习时才按需提取原子笔记和闪卡。

## Usage

```text
/import <path>          # 导入本地文件
/import <url>           # 导入网页
/import --batch <dir>   # 批量导入目录中的材料
/import --strict        # 本次强制严格引用；材料沿用当前选定项
```

Examples:
```text
/import textbook/统计学习方法.pdf
/import lectures/ch03-decision-tree.pptx
/import https://example.com/course-notes
/import --batch course-materials/
```

## Execution Logic

1. **识别与保存**：检测文件格式/URL 和内容类型，将原始材料复制/链接到 `materials/<type>/`，保留原件；目录约定见 `references/carrier-types.md`。重名但内容不同的材料保留独立路径，避免覆盖旧教材。
2. **轻量分析**：调用 material-processor，优先读取元数据、目录/书签、标题层级、概览和必要的代表性页面。PDF 扫描件只对需要的目录/章节页 OCR；视频和音频优先利用已有字幕、大纲，不为索引默认全文转录。
3. **建立教材地图**：使用 `.cursor/templates/MATERIAL_INDEX.md.example` 保存到 `projects/<教材或主题>/MATERIAL_INDEX.md`。记录原始路径、材料类型、真实章节标题、已验证位置、索引覆盖与待补信息。无目录时仅记录已确认结构，不假定全书已解析；多材料独立索引，对应关系必须有验证依据。
4. **先展示后提问**：向用户展示教材地图。上传教材后接入 `/learn [topic] --plan [--material <path>]` 的同一流程，复用已知学习目标、基础、已学章节，只集中补问缺失信息，不索要每日时长或截止日期。
5. **按需深入**：路线生成遵循 `references/learning-path-design.md`；用户开始具体单元学习时才对相关章节调用详细提取，写入有源引用的笔记。导入本身不生成整本教材的原子笔记、闪卡或每日课表。

用户明确只需归档时，完成索引并交付地图即可；不要自行启动学习会话。

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `path` | — | 本地文件路径或 URL |
| `--batch` | — | 批量导入目录 |
| `--strict` | false | 本次强制严格源引用模式；保留既有环境变量约定 |

## Source-Grounding

- 已核验事实附真实材料及定位；目录上标出的页码不等于已检查正文位置。
- PDF 页序与印刷页码区分记录；未知定位使用已确认章节标题并标“页码待核”，不补造页码或习题编号。
- 记录解析范围、OCR 存疑处和缺失页。直接提取也须核对后再标高置信度。
- 用户目标/基础不冒充教材事实；助手规划建议单独标注。细则见 `references/source-grounding.md`。
