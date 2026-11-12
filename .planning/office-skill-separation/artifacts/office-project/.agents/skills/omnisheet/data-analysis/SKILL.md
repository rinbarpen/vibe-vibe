---
name: omnisheet-data-analysis
description: Data analysis spreadsheet generation — sales reports, survey statistics, A/B test analysis, data cleaning. Use when the user asks for 数据分析、销售报表、问卷统计、AB测试 or any analytical Excel file.
---

# Data Analysis Sheets (数据分析)

Generates analytical spreadsheets for data exploration, statistical summary, and reporting. Uses pandas for heavy data manipulation and openpyxl for formatted output.

## When to Use

- 销售数据分析报告 (Sales performance analysis)
- 问卷调查结果统计 (Survey/Questionnaire results)
- A/B 测试结果分析 (A/B test results)
- 数据质量清洗报告 (Data quality & cleaning reports)
- 任何需要统计分析和汇总的表格

## Quick Start

```
Analyze this sales data and generate a formatted Excel report:
- Sheet 1: Raw data (cleaned)
- Sheet 2: Monthly summary with YoY growth
- Sheet 3: By product category with charts
- Sheet 4: Top 10 customers
Include pivot tables and sparklines where useful.
```

## Preset Templates

### Preset 1: 销售数据分析 (Sales Report)

```
Create a comprehensive sales analysis report in .xlsx format:

**Structure:**
- Sheet 1 "数据总览": Raw cleaned data
  - Columns: 日期 | 订单号 | 客户 | 产品 | 类别 | 数量 | 单价 | 金额 | 区域 | 销售员
  - Auto-filter on all columns
  - Amount column: =数量*单价 (formula, not hardcoded)
  - Freeze header row

- Sheet 2 "月度汇总": Monthly summary
  - Columns: 月份 | 订单数 | 总金额 | 客单价(=总金额/订单数) | 环比增长% | 同比增长%
  - Growth rates as formulas
  - Sparklines for monthly trend (column chart, 12 months)
  - Total row at bottom: =SUM()

- Sheet 3 "类别分析": Product category breakdown
  - Columns: 类别 | 销售额 | 占比% | 订单数 | 均价
  - Sorted by 销售额 descending
  - Bar chart: sales by category
  - Pie chart: revenue share by category

- Sheet 4 "区域分析": Regional analysis
  - Pivot-style table: regions × months
  - Conditional formatting: color scale on values

- Sheet 5 "Top 20": Top 20 customers/products
  - =LARGE() or sorted with INDEX/MATCH

**Formatting:**
- Dark header row (RGB: 52,73,94) with white text
- Alternating row shading (RGB: 245,247,250 / white)
- Currency: ¥#,##0
- Growth rates: 0.0% format, green if positive, red if negative
- Charts placed next to data tables (embedded in sheet)
```

### Preset 2: 问卷调查统计 (Survey Results)

```
Create a survey results analysis spreadsheet in .xlsx format:

**Structure:**
- Sheet 1 "原始数据": Raw responses
  - Columns: 编号 | 提交时间 | Q1 | Q2 | ... | QN
  - Each question column uses data validation or coded values
  - Freeze header + first column

- Sheet 2 "频率分布": Frequency distributions
  - One table per multiple-choice question
  - Columns: 选项 | 频数 | 百分比
  - =COUNTIF() formulas for frequency
  - Total row confirms 100%
  - Bar chart for each question

- Sheet 3 "交叉分析": Cross-tabulation
  - Selectable dimensions in cells A1, A2 (dropdowns for questions to cross)
  - Dynamic cross-tab using =COUNTIFS() or =SUMPRODUCT()
  - Heatmap conditional formatting

- Sheet 4 "统计摘要": Summary statistics
  - For scale/rating questions:
    - Mean, Median, Mode, Std Dev, Min, Max
    - =AVERAGE(), =MEDIAN(), =MODE(), =STDEV(), =MIN(), =MAX()
  - Response count, completion rate

- Sheet 5 "图表": Charts dashboard
  - All charts collected on one sheet for easy export
  - Bar, pie, radar charts as appropriate

**Formatting:**
- Clean academic style
- Question labels as text, not codes
- All statistics as Excel formulas (recalculable)
```

### Preset 3: A/B测试分析 (A/B Test Results)

```
Create an A/B test analysis spreadsheet in .xlsx format:

**Structure:**
- Sheet 1 "测试结果": Main analysis
  - Input section (blue font):
    - Control visitors [B2], Control conversions [B3]
    - Variant visitors [B4], Variant conversions [B5]
    - Confidence level [B6] dropdown: 90%/95%/99%

  - Output section (formulas):
    - Control conversion rate =B3/B2
    - Variant conversion rate =B5/B4
    - Lift = (Variant - Control) / Control
    - Z-score: =(P2-P1)/SQRT(P_pooled*(1-P_pooled)*(1/N1+1/N2))
    - P-value: =2*(1-NORM.S.DIST(ABS(Z), TRUE))
    - Significant?: =IF(P_value < 1-confidence, "YES", "NO")
    - Confidence interval for lift

  - Summary box: conclusion with effect size

- Sheet 2 "细分分析": Segment breakdown
  - By device type, traffic source, user type
  - Same metrics per segment
  - Conditional formatting for significant segments

- Sheet 3 "统计细节": Statistical details
  - Full z-test calculation breakdown
  - Power analysis: =1-NORM.S.DIST(NORM.S.INV(1-alpha/2)-effect*SQRT(N), TRUE)
  - Sample size needed for significance

**Formatting:**
- Input cells: blue font + yellow background
- Significant positive: green bold
- Significant negative: red bold
- Non-significant: gray
- Use Excel statistical functions throughout
```

### Preset 4: 数据清洗报告 (Data Quality Report)

```
Create a data quality and cleaning report in .xlsx format:

**Structure:**
- Sheet 1 "数据质量概览": Quality overview
  - Columns per field: 字段名 | 总行数 | 空值数 | 空值率 | 唯一值数 | 重复率 | 异常值数 | 质量评分
  - =COUNTBLANK(), =COUNTA(), =COUNTUNIQUE()-style formulas
  - Quality score: composite formula weighing completeness + uniqueness
  - Color scale: green (≥95%), yellow (80-95%), red (<80%)

- Sheet 2 "空值明细": Missing value details
  - Row-level missing value matrix
  - Columns: 行号 | Field1_missing | Field2_missing | ... | Total_missing
  - Conditional formatting: cells with missing values highlighted
  - Summary: rows with >50% missing flagged

- Sheet 3 "异常值检测": Outlier detection
  - For numeric fields: IQR method
  - Columns: 行号 | 字段 | 值 | Q1 | Q3 | IQR | 下限 | 上限 | 是否异常
  - All thresholds as formulas: Q1-1.5*IQR, Q3+1.5*IQR
  - Flagged outliers in red

- Sheet 4 "清洗记录": Cleaning log
  - Columns: 日期 | 字段 | 操作(填充/删除/修正) | 原值 | 新值 | 理由 | 执行人
  - Data validation on 操作 column

- Sheet 5 "修正后数据": Cleaned dataset
  - Full cleaned data with corrections applied

**Formatting:**
- Data quality traffic light coloring
- Problem cells highlighted
- Readable, audit-friendly layout
```

## Style Conventions

- **Header**: Dark background (RGB: 52,73,94), white text, bold
- **Alternate rows**: Subtle gray (RGB: 245,247,250)
- **Numbers**: Right-aligned, `#,##0` format
- **Percentages**: `0.0%` or `0.00%`
- **Negatives**: Red text (RGB: 231,76,60)
- **Charts**: Embedded in relevant sheets, consistent color palette

## Common Formulas

```python
# Frequency distribution
ws['C5'] = '=COUNTIF(原始数据!B:B, B5)'
ws['D5'] = '=C5/SUM(C:C)'

# Cross-tabulation
ws['D5'] = '=COUNTIFS(原始数据!C:C, $B5, 原始数据!D:D, D$4)'

# Z-test for proportions
ws['B10'] = '=(B5/B4-B3/B2)/SQRT((B3+B5)/(B2+B4)*(1-(B3+B5)/(B2+B4))*(1/B2+1/B4))'

# P-value from z-score
ws['B11'] = '=2*(1-NORM.S.DIST(ABS(B10), TRUE))'

# Outlier detection (IQR)
ws['F2'] = '=OR(C2<$D2-1.5*($E2-$D2), C2>$E2+1.5*($E2-$D2))'

# Ranking
ws['B2'] = '=RANK(C2, C:C, 0)'
```

## Related Resources

- [../references/style-guide.md](../references/style-guide.md) — Full formatting reference
- [skills/anthropics/skills/xlsx](../../../skills/anthropics/skills/xlsx/SKILL.md) — pandas + openpyxl workflow
