---
name: omnisheet-academic-research
description: Academic and research spreadsheet generation — experiment logs, literature review matrices, grant budgets, thesis progress trackers. Use when the user asks for 实验记录、文献矩阵、经费预算、论文进度 or any academic/research Excel file.
---

# Academic Research Sheets (科研学术)

Generates academic and research-oriented spreadsheets with clean, publication-quality formatting. Focus on clarity, reproducibility, and grant-compliance.

## When to Use

- 实验数据记录与管理 (Experiment data logging)
- 文献综述矩阵 (Literature review matrices)
- 科研经费预算 (Grant budget preparation)
- 论文/学位论文进度追踪 (Thesis / dissertation progress tracking)
- 任何科研和学术管理表格

## Quick Start

```
Create an experiment data log for a biology wet-lab study.
Sections: Experiment ID, Date, Protocol, Sample ID, Treatment, Measurement, Observations.
Include data validation for treatment types and conditional formatting for outlier values.
```

## Preset Templates

### Preset 1: 实验记录 (Experiment Log)

```
Create an experiment data log in .xlsx format:

**Structure:**
- Sheet 1 "实验记录":
  - Columns:
    - 实验编号 | 日期 | 实验类型 | 方案/Protocol | 样本ID | 处理组 | 测量值1 | 测量值2 | 测量值3 | 均值(=AVERAGE) | 标准差(=STDEV) | 是否异常(>2σ) | 备注

  - Data validation dropdowns:
    - 实验类型: PCR, Western Blot, ELISA, Cell Culture, Microscopy, Sequencing, Other
    - 处理组: Control, Treatment A, Treatment B, ...

  - Statistical rows per experiment group:
    - Group mean, SD, N, SEM (=SD/SQRT(N))
    - Significance test results (t-test p-value)

  - Outlier detection:
    - Z-score: =(测量值-AVERAGE(组))/STDEV(组)
    - Flag: =IF(ABS(Z-score)>2, "异常", "")
    - Conditional formatting: red highlight on flagged cells

- Sheet 2 "实验方案库":
  - Protocol reference library:
    - Columns: 方案编号 | 方案名称 | 类型 | 步骤描述 | 试剂/材料 | 设备 | 关键参数 | 参考来源 | 最后修改日期
  - Searchable by type (auto-filter)

- Sheet 3 "试剂库存":
  - Reagent/supply tracking:
    - Columns: 试剂名称 | 目录号 | 供应商 | 存储位置 | 库存量 | 单位 | 最低库存 | 过期日期 | 需要订购? | 备注
  - Conditional formatting: expired items red, expiring within 30 days yellow
  - 需要订购: =IF(库存量<最低库存, "是", IF(过期日期<TODAY()+30, "是", ""))

**Formatting:**
- Clean, academic minimal style (Times New Roman 10pt)
- Alternating row colors (white/light gray)
- Outlier cells: red background
- Group separator rows: bold, light blue background
- Frozen headers + first column
- Print-ready: grayscale, A4

**Formulas:**
- Mean: =AVERAGE(G2:I2)
- Std Dev: =STDEV.S(G2:I2)
- SEM: =J2/SQRT(COUNT(G2:I2))
- Z-score: =(G2-AVERAGE(G:G))/STDEV.S(G:G)
- Group mean: =AVERAGEIFS(G:G, F:F, "Control")
```

### Preset 2: 文献矩阵 (Literature Matrix)

```
Create a literature review matrix in .xlsx format:

**Structure:**
- Sheet 1 "文献矩阵":
  - Columns:
    - ID | APA/GB引用格式 | 年份 | 研究类型 | 研究问题 | 方法论 | 数据集 | 主要发现 | 关键指标/结果 | 局限性 | 与本研究关系 | 重要性(1-5) | 已读状态 | 笔记 | PDF路径/DOI

  - Data validation:
    - 研究类型: 实证研究, 理论研究, 综述, 元分析, 案例研究, 技术报告
    - 方法论: 实验, 调查, 案例研究, 模型推导, 模拟, 文献分析, 混合方法
    - 与本研究关系: 直接相关, 方法论参考, 背景知识, 对比参照
    - 重要性: 1(泛读) to 5(核心)

  - Summary at top:
    - Total papers: =COUNTA()
    - By year: histogram or count table
    - By type: pie data
    - By methodology: count table
    - Read vs unread: =COUNTIF()

  - Conditional formatting:
    - Importance 5: bold, light green background
    - Unread: yellow highlight
    - Directly related: blue left border

- Sheet 2 "关键发现汇总":
  - Thematic synthesis matrix:
    - Columns: 主题/维度 | Paper 1 finding | Paper 2 finding | ... | 综合结论
    - Theme headers: bold, grouped
    - Synthesis column: merged qualitative summary

- Sheet 3 "引用检查":
  - Reference accuracy checklist:
    - Columns: 文中引用 | 参考文献列表 | 匹配? | DOI可查? | 页码? | 备注
  - =IF(EXACT()) comparison formulas

**Formatting:**
- Academic/scholarly: Times New Roman, clean lines
- Color minimal — use for status only
- Frozen ID + citation column
- Print on A4 with narrow margins

**Formulas:**
- Read count: =COUNTIF(L:L, "已读")
- Year distribution: =COUNTIF(C:C, 2024)
- Type distribution: =COUNTIF(D:D, "实证研究")
```

### Preset 3: 经费预算 (Grant Budget)

```
Create a research grant budget spreadsheet in .xlsx format:

**Structure:**
- Sheet 1 "经费预算总表":
  - Title: "[项目名称] 经费预算表", 14pt bold
  - Budget period: YYYY-MM to YYYY-MM

  - Main budget table:
    - Columns: 科目 | 类别 | 第一年 | 第二年 | 第三年 | 合计 | 经费占比% | 计算依据
    - Rows by NSFC/standard categories:
      **一、直接费用:**
      - 设备费 (Equipment)
      - 材料费 (Materials/Consumables)
      - 测试/计算/分析费 (Testing/Analysis)
      - 燃料动力费 (Energy/Fuel)
      - 差旅/会议/国际合作 (Travel/Conference)
      - 出版/文献/知识产权 (Publication/IP)
      - 劳务费 (Personnel/RA stipends)
      - 专家咨询费 (Expert consultation)
      - 其他支出 (Other)
      **二、间接费用:**
      - 管理费 (Overhead): formula linked to direct cost %

  - Formula-driven calculations:
    - 合计: =SUM(每年)
    - 经费占比: =合计/SUM(合计)
    - 间接费用: =直接费用_合计*管理费率

  - Input cells (blue font):
    - Annual amounts per category
    - Overhead rate %
    - Equipment unit prices and quantities

- Sheet 2 "经费明细":
  - Drill-down detail per category:
    - Equipment: name, model, quantity, unit price, total, justification
    - Travel: destination, purpose, people, days, daily rate, total
    - Personnel: name, role, months, monthly rate, total

- Sheet 3 "年度使用计划":
  - Quarterly spending plan:
    - Columns: 科目 | Q1 | Q2 | Q3 | Q4 | 年度合计
  - Cumulative spending curve data
  - Line chart: planned vs actual (if tracking)

**Formatting:**
- Financial color coding (blue inputs, black formulas)
- Section headers: bold, light gray background
- Total rows: bold, top border
- Currency: ¥#,##0 (万元 or 元, specify in header)
- Percentages: 0.0%
- Print area set to A4

**Key Formulas:**
- Category total: =SUM(C2:E2)
- Direct cost subtotal
- Indirect cost: =直接费用*管理费率
- Grand total: =直接费用+间接费用
- Percentage: =F2/SUM(F:F)
```

### Preset 4: 论文进度 (Thesis Tracker)

```
Create a thesis/dissertation progress tracker in .xlsx format:

**Structure:**
- Sheet 1 "论文进度":
  - Chapter/section tracker:
    - Columns: 章节编号 | 章节标题 | 目标字数 | 当前字数 | 完成度% | 初稿状态 | 修改轮次 | 导师反馈 | 最后修改日 | 备注

  - Status per chapter:
    - 初稿状态: 未开始, 写作中, 初稿完成, 修改中, 终稿
    - Conditional formatting data bar for 完成度%

  - Milestone timeline:
    - 里程碑 | 目标日期 | 完成日期 | 状态
    - Milestones: 开题报告, 文献综述完成, 实验完成, 初稿完成, 导师审阅, 修改完成, 答辩

  - Summary dashboard:
    - Overall completion: =SUMPRODUCT(字数×完成度)/SUM(目标字数)
    - Words to go: =SUM(目标字数)-SUM(当前字数)
    - Next milestone with date
    - Days until next deadline: =目标日期-TODAY()

- Sheet 2 "写作日志":
  - Daily writing log:
    - Columns: 日期 | 章节 | 起始字数 | 结束字数 | 净增字数(=结束-起始) | 写作时长(h) | 效率(字/h) | 笔记
  - Weekly/monthly summary:
    - Week | Total words | Avg per day | Best day
  - Progress chart: cumulative words over time with milestone markers

- Sheet 3 "参考文献管理":
  - Reference tracker:
    - Columns: Key | Full Citation | 章节引用 | 类型 | 已确认格式? | DOI | 备注
  - Format check column with validation

- Sheet 4 "审阅意见":
  - Reviewer feedback log:
    - Columns: 日期 | 来源 | 章节 | 意见 | 类型(内容/格式/语法) | 优先级 | 处理状态 | 回复 | 处理日期
  - Priority: 高/中/低
  - Status: 待处理/处理中/已完成/忽略

**Formatting:**
- Academic, motivating visual design
- Progress bars: green data bars
- Overdue milestones: red
- Today marker: light blue column highlight
- Weekends in writing log: gray
- Clean print layout

**Formulas:**
- Completion %: =D2/C2
- Overall progress: =SUMPRODUCT(C2:C20, E2:E20)/SUM(C2:C20)
- Days remaining: =F2-TODAY()
- Weekly words: =SUMIFS(净增字数列, 日期列, ">="&week_start, 日期列, "<="&week_end)
- Avg efficiency: =AVERAGE(效率列)
```

## Style Conventions

- **Font**: Times New Roman 10pt (body), 11pt bold (headers)
- **Color**: Minimal, grayscale preferred for print/publication
- **Status colors**: Subtle — green(完成), blue(进行中), gray(未开始), red(逾期)
- **Borders**: Thin, black, consistent
- **Numbers**: `#,##0` for counts, `0.0%` for percentages, `0.00` for measurements
- **Scientific notation**: Use for very large/small values where appropriate
- **Print-ready**: All sheets should print cleanly on A4 with reasonable margins

## Common Formulas

```python
# Group statistics
ws['H2'] = '=AVERAGEIFS(G:G, F:F, "Control")'
ws['I2'] = '=STDEV.S(IF(F:F="Control", G:G))'  # array formula

# Outlier detection (z-score > 2)
ws['M2'] = '=IF(ABS((G2-AVERAGE(G:G))/STDEV.S(G:G))>2, "异常", "")'

# Literature count by type
ws['B3'] = '=COUNTIF(D:D, "实证研究")'

# Budget total
ws['G2'] = '=SUM(C2:E2)'
ws['G15'] = '=SUM(G2:G14)'  # direct cost total
ws['G16'] = '=G15*0.05'     # overhead at 5%

# Thesis progress
ws['E2'] = '=D2/C2'
ws['B20'] = '=SUMPRODUCT(C2:C19, E2:E19)/SUM(C2:C19)'

# Days until deadline
ws['H2'] = '=G2-TODAY()'
```

## Related Resources

- [../references/style-guide.md](../references/style-guide.md) — Full formatting reference
- [skills/anthropics/skills/xlsx](../../../skills/anthropics/skills/xlsx/SKILL.md) — openpyxl + recalc workflow
