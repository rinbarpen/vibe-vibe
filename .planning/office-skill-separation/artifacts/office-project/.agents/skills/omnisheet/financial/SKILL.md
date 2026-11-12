---
name: omnisheet-financial
description: Financial spreadsheet generation — budgets, investment tracking, loan calculators, cash flow forecasts. Use when the user asks for 预算、投资、贷款、现金流、财务模型 or any financial Excel file.
---

# Financial Sheets (财务模型)

Generates professional financial spreadsheets with industry-standard color coding (blue inputs, black formulas, green cross-references).

## When to Use

- 个人或家庭预算 (Personal / household budget)
- 投资组合追踪 (Investment portfolio tracking)
- 贷款还款计算 (Loan / mortgage calculators)
- 现金流预测 (Cash flow forecasting)
- 任何带财务计算和公式的表格

## Quick Start

```
Generate a personal monthly budget spreadsheet for 2026.
Income categories: 工资, 奖金, 投资收益.
Expense categories: 房租, 餐饮, 交通, 娱乐, 储蓄.
Include monthly totals, category subtotals, and budget vs actual comparison.
```

## Preset Templates

### Preset 1: 个人预算 (Personal Budget)

```
Create a comprehensive personal budget spreadsheet in .xlsx format:

**Structure:**
- Sheet 1 "年度预算": 12-month income/expense overview
  - Row 1: Header with title "2026年度个人预算", font 14pt bold
  - Row 3: Income section — 工资收入, 兼职收入, 投资收益, 其他收入
  - Row 8: Expense section — 房租/房贷, 水电煤, 餐饮, 交通, 通讯, 娱乐, 购物, 医疗, 教育, 储蓄, 其他
  - Row 22: Monthly totals (Income sum, Expense sum, Net = Income - Expense)
  - Columns: Category | Jan | Feb | ... | Dec | Total
  - Freeze pane at A2

**Formatting:**
- Income rows: light green background (RGB: 232,245,233)
- Expense rows: light red background (RGB: 255,235,238)
- Total row: bold, light gray background
- All sums use =SUM() formulas
- Currency format: ¥#,##0
- Negative net values: red text

**Features:**
- Budget vs Actual columns (budgeted amount, actual, variance as formula)
- Conditional formatting: variance > 10% highlighted yellow
- Sparkline for monthly net income trend in the last row
```

### Preset 2: 投资组合追踪 (Investment Portfolio)

```
Create an investment portfolio tracker in .xlsx format:

**Structure:**
- Sheet 1 "持仓明细": Current holdings
  - Columns: 代码/名称 | 类型(股票/基金/债券) | 买入价 | 现价 | 持仓数量 | 成本 | 市值(=B*E) | 盈亏(=F-G) | 盈亏%(=H/G) | 占比(=F/SUM(F))
  - Row 1: Header with "投资组合追踪 — YYYY-MM-DD", update date cell
  - Summary row at bottom: =SUM() for totals, weighted average for return %

- Sheet 2 "资产配置": Allocation pie data
  - Asset class breakdown: 股票, 债券, 基金, 现金
  - Target allocation % vs actual allocation %
  - Variance column

- Sheet 3 "交易记录": Transaction log
  - Columns: 日期 | 代码 | 类型(买入/卖出) | 数量 | 价格 | 金额 | 手续费 | 备注

**Formatting:**
- Financial color code: blue font for input cells (buy price, current price, quantity)
- Black font for all formulas
- Positive returns: green text, negative: red text
- Percentage format: 0.00%
- Currency: ¥#,##0.00

**Formulas:**
- Use =SUM(), =SUMPRODUCT() for weighted calculations
- XIRR-style approximation for annualized return
```

### Preset 3: 贷款计算器 (Loan Calculator)

```
Create a loan amortization calculator in .xlsx format:

**Structure:**
- Sheet 1 "贷款计算":
  - Input area (top-left, blue font):
    - 贷款金额 (Loan amount): [B2]
    - 年利率 (Annual rate): [B3]
    - 贷款期限/年 (Term years): [B4]
    - 还款方式 (Payment type): [B5] dropdown: 等额本息 / 等额本金
    - 首次还款日 (First payment date): [B6]

  - Output area:
    - 月还款额 (Monthly payment): =PMT() formula
    - 总还款额 (Total payment)
    - 总利息 (Total interest)

- Sheet 2 "还款明细": Full amortization schedule
  - Columns: 期数 | 还款日期 | 月还款额 | 本金 | 利息 | 剩余本金
  - Extends for full loan term (e.g., 360 rows for 30-year)
  - Interest = remaining principal * monthly rate
  - Principal = monthly payment - interest
  - Remaining balance = previous balance - principal

- Sheet 3 "提前还款对比":
  - Scenario table comparing extra payment amounts vs interest saved
  - Columns: 额外月供 | 缩短月数 | 节省利息

**Formatting:**
- Input cells: blue font, light yellow background
- Calculation cells: black font
- Sheet 2: alternate row shading
- Key outputs: bold, larger font

**All formulas use Excel functions**: =PMT(), =IPMT(), =PPMT(), =SUM()
```

### Preset 4: 现金流预测 (Cash Flow Forecast)

```
Create a 12-month cash flow forecast in .xlsx format:

**Structure:**
- Sheet 1 "现金流预测":
  - Title: "现金流预测 2026年度", 14pt bold
  - Header row freeze
  - Columns: 项目 | Jan | Feb | ... | Dec | Total
  - Sections:

  **Operating Activities (经营活动):**
  - 销售收入 (Sales revenue)
  - 应收账款回收 (AR collections)
  - 其他经营收入 (Other operating income)
  - Total Inflow =SUM()

  - 采购支出 (Purchases)
  - 工资支出 (Payroll)
  - 租金 (Rent)
  - 营销费用 (Marketing)
  - 其他运营支出 (Other opex)
  - Total Outflow =SUM()
  - Net Operating Cash Flow = Inflow - Outflow

  **Investing Activities (投资活动):**
  - 资产购置 (Asset purchases)
  - 资产处置 (Asset disposals)
  - Net Investing Cash Flow

  **Financing Activities (筹资活动):**
  - 借款收入 (Loan proceeds)
  - 还款支出 (Loan repayments)
  - Net Financing Cash Flow

  - Net Cash Flow = Operating + Investing + Financing
  - Beginning Cash Balance (link from prior month)
  - Ending Cash Balance = Beginning + Net Cash Flow

**Formatting:**
- Blue font: all assumption/input cells (revenue growth rates, cost percentages)
- Black font: all formulas
- Inflow: green text, Outflow: red text
- Net rows: bold
- Conditional formatting: negative ending balance → red background alert
- Waterfall-style: minor gridlines, major section borders

**Features:**
- All YoY growth and % of revenue as formulas linked to assumption cells
- Scenario switcher: 乐观/基准/保守 with different growth assumptions
```

## Style Conventions

- **Blue font (RGB: 0,0,255)**: Hardcoded inputs and assumptions
- **Black font (RGB: 0,0,0)**: All formulas
- **Green font (RGB: 0,128,0)**: Cross-sheet references
- **Yellow background**: Critical assumption cells
- **Currency**: `¥#,##0` or `$#,##0`, units in column headers
- **Percentages**: `0.0%` format
- **Negative numbers**: Parentheses `(123)` format for financial statements
- **Zeros**: Display as `-` (custom format)

## Common Formulas

```python
# Monthly payment (等额本息)
ws['B7'] = '=PMT(B3/12, B4*12, -B2)'

# Total interest
ws['B8'] = '=B7*B4*12-B2'

# SUM with conditions
ws['C10'] = '=SUMIF(A2:A100, "收入", C2:C100)'

# Weighted average return
ws['D5'] = '=SUMPRODUCT(F2:F100, G2:G100)/SUM(F2:F100)'

# XIRR approximation via IRR
ws['E5'] = '=IRR(H2:H14)'

# Running balance
ws['G10'] = '=G9+F10-E10'
```

## Related Resources

- [../references/style-guide.md](../references/style-guide.md) — Full color/font/formatting reference
- [skills/anthropics/skills/xlsx](../../../skills/anthropics/skills/xlsx/SKILL.md) — openpyxl + recalc workflow
