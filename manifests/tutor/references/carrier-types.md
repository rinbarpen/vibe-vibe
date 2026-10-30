# 知识载体类型参考 (Carrier Types)

## 两阶段处理

上传/导入和教材规划默认只读元数据、目录/标题层级、概览及必要样本，输出 `MATERIAL_INDEX.md`；详细提取只针对开始学习的单元。下表的提取策略是详细学习策略，不是导入时的全量任务。扫描/OCR 不完整时保留部分索引和待补项，路线规则见 `references/learning-path-design.md`。

## 支持的载体类型与提取策略

| 类型 | 常见格式 | 识别方式 | 提取策略 | 引用格式 |
|------|----------|----------|----------|----------|
| Slides (幻灯片) | .ppt, .pptx, .key | file extension | 逐页提取 + speaker notes | `[Source: 文件名, P#]` |
| PDF (文档) | .pdf | file extension | 选定章/节拆解 + 核心概念 | `[Source: 文件名, PDF页序 #, 印刷页码 #]`（仅列核验项） |
| Video (视频) | .mp4, .mov, .avi, .webm | file extension | 转录 + 时间分段 | `[Source: 文件名, HH:MM:SS]` |
| Web (网页) | URL, .html | URL pattern / extension | 正文提取 + 结构分析 | `[Source: URL, 标题]` |
| Audio (音频) | .mp3, .wav, .m4a, .ogg | file extension | 转录 + 分段 | `[Source: 文件名, HH:MM:SS]` |
| Image (图片) | .png, .jpg, .svg, .gif | file extension | OCR + 内容描述 | `[Source: 文件名]` |
| Exercise (习题) | .pdf, .docx, .txt | 内容检测 | 题目解析 + 知识点映射 | `[Source: 文件名, 题号]` |
| EPUB (电子书) | .epub | file extension | 章节点提取 | `[Source: 文件名, 章节]` |

## 文件组织

```
materials/
  slides/     # .ppt .pptx .key
  pdf/        # .pdf
  video/      # .mp4 .mov + .srt .vtt
  web/        # .html .url or bookmarks
  audio/      # .mp3 .wav .m4a
  images/     # .png .jpg .svg
  exercises/  # .pdf .docx
  epub/       # .epub
```

课程名与章节关联保存在 `projects/<教材或主题>/MATERIAL_INDEX.md`，不改用按课程分层的原件目录。PDF 页序和印刷页码分开；未知页码用已确认章节标题，目录所列位置注明正文待核。

## 提取注意事项

| 载体类型 | 注意事项 |
|----------|----------|
| Slides | PPT 中的动画和隐藏页可能包含额外内容；speaker notes 比页面文字更有价值 |
| PDF | 扫描版 PDF 需要 OCR；图表中的文字需要额外提取；公式可能需 LaTeX 转录 |
| Video | 自动转录可能有错，建议配合字幕文件；板书内容需截图描述 |
| Web | 注意 paywall/登录墙；动态加载页面可能无法完整提取 |
| Audio | 多人对话需区分说话人；背景噪音影响转录质量 |
| Image | 复杂图表需要详细描述数据关系；截图可能包含上下文依赖信息 |

当前对话需求优先于本载体的学习方法建议，不固定页数/分钟提问或自动全量提取；只处理选定范围，不强迫先生成路线。
