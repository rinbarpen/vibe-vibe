# PDF：提取、处理与全页验收

先读 `office/rules/quality.md`、`office/rules/file-safety.md`、`office/rules/pdf.md` 和 `.agents/skills/anthropics-skills-pdf/SKILL.md`。命令从安装后的项目根目录执行。

## 操作约定

创建/修改 PDF 涉及新图片或数据绘图时先经 `.agents/skills/omnidraw/SKILL.md`；涉及表格数据/布局时先经 `.agents/skills/omnisheet/SKILL.md`，再由源格式/PDF 引擎处理实际输出。纯读取/提取沿用 PDF 路径，不额外生成素材或工作簿。

- 明确是只读提取、合并拆分、页面排序/旋转、表单填写还是从办公源文件导出；确认页码采用的编号、保留书签/链接/表单要求及输出文件列表。
- 只读提取不修改输入，返回来源页码/区域和提取限制；需要保留多栏、表格或公式语义时对照页面核验，纯文本顺序不等于真实阅读顺序。
- 扫描件先判定文字层是否足够，再按需 OCR。注明识别语言、页码与低置信度/易混淆内容，关键数字、姓名、表格和公式对照原图核对。
- 修改以副本为基础并记录源哈希；签名、加密权限、可填表单、链接、书签和附件等特性先盘点，避免处理后静默丢失。签名文档修改可能使原签名失效，应明确标识输出状态。
- 办公文件导出 PDF 时同时保留可编辑源件；PDF 通常不是原生可编辑源文档的替代品。

## 创建/修改后的验收

```bash
python3 office/scripts/verify.py "deliverables/merged.pdf" --output "evidence/merged-structure.json"
python3 office/scripts/render.py "deliverables/merged.pdf" --out-dir "evidence/merged-preview"
```

1. 重新打开 PDF，检查实际页数、顺序、页框、方向、文本、字体和图像；合并/拆分逐一对应约定的源页映射。
2. 表单填写检查字段名、类型、值、勾选状态及渲染后可见外观；需要继续填写时保留字段，不默认为扁平化。
3. 使用新建或空的预览目录保留 `render.json`，渲染并审阅全部页面，确认无空白、截断、中文缺字、表格/链接损失或导出布局偏移；已脱敏文档还需检查文字层和相关对象是否残留目标内容。
4. 交接最终 PDF、输入/最终哈希、页映射或字段核对记录、结构检查和全页预览给独立 `office-qa`。修改后重验；缺条件标记 `pending`。

细化清单见 `office-quality` 的 `references/pdf.md`；纯读取/提取任务免独立 QA，不因此宣称未做过的全页审查。
