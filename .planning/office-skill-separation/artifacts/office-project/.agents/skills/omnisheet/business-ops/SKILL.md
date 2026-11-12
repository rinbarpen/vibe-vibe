---
name: omnisheet-business-ops
description: Business operations spreadsheet generation — CRM, inventory management, invoice templates, sales pipelines. Use when the user asks for 客户管理、库存、发票、销售管道 or any business operations Excel file.
---

# Business Operations Sheets (业务运营)

Generates professional business spreadsheets for daily operations, client management, and sales workflows.

## When to Use

- 客户关系管理 (CRM / Customer relationship tracking)
- 库存管理 (Inventory / Stock management)
- 发票模板 (Invoice templates)
- 销售管道管理 (Sales pipeline tracking)
- 任何业务运营和管理表格

## Quick Start

```
Create a simple CRM tracker for a small business.
Columns: Company, Contact, Email, Phone, Stage (Lead/Qualified/Proposal/Negotiation/Closed), Last Contact Date, Next Follow-up, Notes.
Add conditional formatting for overdue follow-ups and stage colors.
```

## Preset Templates

### Preset 1: 客户CRM (Customer CRM)

```
Create a customer relationship management tracker in .xlsx format:

**Structure:**
- Sheet 1 "客户总览":
  - Columns: ID | 公司名称 | 联系人 | 职位 | 邮箱 | 电话 | 行业 | 来源 | 阶段 | 最后联系日 | 下次跟进日 | 负责人 | 备注
  - Auto-filter on all columns
  - Freeze first row + first 2 columns

  - Dashboard summary at top (rows 1-6):
    - Total contacts: =COUNTA()
    - By stage: table with =COUNTIF() per stage
    - Overdue follow-ups: =COUNTIF(下次跟进列, "<"&TODAY())
    - New this month: =COUNTIFS(创建日期列, ">="&EOMONTH(TODAY(),-1)+1)
    - Conversion rate: =Closed/Total

  - Data validation:
    - 阶段: 潜在客户, 初步接触, 需求确认, 报价/提案, 谈判, 已成交, 已流失
    - 来源: 官网, 推荐, 展会, 电话, 社交媒体, 广告, 其他
    - 行业: dropdown list

- Sheet 2 "跟进记录":
  - Columns: 日期 | 客户ID | 联系人 | 方式(电话/邮件/拜访/微信) | 内容摘要 | 下一步计划 | 下次跟进日期 | 负责人
  - Linked to Sheet 1 via ID
  - =XLOOKUP() or =INDEX/MATCH to pull company name from Sheet 1

- Sheet 3 "销售漏斗":
  - Funnel visualization table:
    - Columns: 阶段 | 数量 | 预计金额 | 加权金额(=预计金额*概率%)
    - Probability % per stage: 10%/25%/50%/70%/90%/100%
  - Funnel bar chart (horizontal)
  - Monthly trend: funnel stage counts by month

**Conditional Formatting:**
- Overdue follow-up: entire row red background (下次跟进日 < TODAY() AND 阶段 <> "已成交")
- Stage colors: gray(潜在), blue(接触), teal(确认), orange(报价), purple(谈判), green(成交), red(流失)
- Last contact > 30 days: yellow highlight
- High value (> 阈值): bold

**Formulas:**
- Overdue flag: =AND(K2<TODAY(), F2<>"已成交")
- Days since last contact: =TODAY()-J2
- Weighted amount: =C2*VLOOKUP(F2, 概率表, 2, 0)
```

### Preset 2: 库存管理 (Inventory Management)

```
Create an inventory management spreadsheet in .xlsx format:

**Structure:**
- Sheet 1 "库存总览":
  - Columns: SKU | 产品名称 | 类别 | 规格 | 供应商 | 采购价 | 销售价 | 当前库存 | 安全库存 | 最大库存 | 状态 | 最后盘点日 | 备注

  - Alert section at top:
    - 缺货预警 (=COUNTIF(当前库存, "<=0")): red
    - 低库存预警 (=COUNTIF(当前库存, "<="&安全库存)): yellow
    - 正常: green count
    - 超额 (=COUNTIF(当前库存, ">"&最大库存)): blue

  - Status formula: =IF(当前库存<=0,"缺货",IF(当前库存<=安全库存,"低库存",IF(当前库存>最大库存,"超额","正常")))

  - Data validation:
    - 类别: dropdown per business
    - 状态: auto-calculated, not manual

- Sheet 2 "出入库记录":
  - Columns: 日期 | 类型(入库/出库/退货/盘点调整) | SKU | 产品名称(=XLOOKUP) | 数量 | 单价 | 总价(=数量*单价) | 操作人 | 单号 | 备注
  - Running balance per SKU (challenging in Excel, use pivot or helper columns)

- Sheet 3 "采购计划":
  - Reorder suggestions:
    - Columns: SKU | 产品名 | 当前库存 | 月均销量 | 可用月数(=库存/月均) | 建议采购量(=MAX(安全库存*2-当前库存,0)) | 供应商 | 采购价 | 预计金额
  - Flag items with 可用月数 < 1

  - Purchase order template area:
    - 供应商 | 订单日期 | 预计到货 | 商品明细 | 总金额

**Formatting:**
- Status color coding: red(缺货), yellow(低库存), green(正常), blue(超额)
- Alternating rows
- Frozen header + SKU column
- Reorder suggestions sorted by urgency
- Currency: ¥#,##0

**Formulas:**
- Status: =IFS(D2<=0,"缺货",D2<=E2,"低库存",D2>F2,"超额",TRUE,"正常")
- Months of stock: =D2/H2
- Suggested reorder: =MAX(E2*2-D2, 0)
- Margin: =(G2-F2)/F2
```

### Preset 3: 发票模板 (Invoice Template)

```
Create a professional invoice template in .xlsx format:

**Structure:**
- Sheet 1 "发票": (print-ready layout)

  **Header section (rows 1-8):**
  - Row 1-2: Company logo placeholder + 发票/INVOICE title, 18pt bold
  - Row 4: 发票号: [INV-YYYY-XXXX] | 日期: [YYYY-MM-DD] | 到期日: [YYYY-MM-DD]
  - Row 6: 付款方式: [银行转账/微信/支付宝] | 参考号: [PO/合同号]

  **From/To section (rows 9-16):**
  - 发件方 (From): Company name, address, phone, email, tax ID
  - 收件方 (To/Bill To): Company name, address, contact person, phone

  **Line items (rows 18-35):**
  - Columns: 序号 | 产品/服务描述 | 数量 | 单位 | 单价 | 金额(=数量*单价)
  - 17 rows available for items
  - Subtle borders on all cells

  **Summary (rows 36-42):**
  - 小计 (Subtotal): =SUM(金额列)
  - 税率 (Tax Rate): [input cell, e.g., 13%]
  - 税额 (Tax): =小计*税率
  - 总计 (Total): =小计+税额
  - If applicable: 已付定金, 应付余额

  **Footer (rows 44-48):**
  - Payment instructions / bank details
  - Thank you note
  - Company stamp/signature line

  **Print settings (set via openpyxl):**
  - Page orientation: Portrait
  - Paper size: A4
  - Margins: 1.5cm all sides
  - Print area: A1:H48
  - Header/footer: company name, page number

- Sheet 2 "发票记录":
  - Register of all issued invoices:
    - Columns: 发票号 | 日期 | 客户 | 金额 | 税额 | 总计 | 状态(已付/未付/逾期) | 付款日期 | 备注
  - Running totals: =SUM() for outstanding

**Formatting:**
- Professional, minimal design
- Company branding color for header accents
- Clean borders (thin, consistent)
- Currency: ¥#,##0.00
- Tax ID in smaller font
- Invoice number: bold, prominent

**Formulas:**
- Line total: =D21*E21
- Subtotal: =SUM(F21:F37)
- Tax: =F39*F40
- Grand total: =F39+F41
```

### Preset 4: 销售管道 (Sales Pipeline)

```
Create a sales pipeline tracker in .xlsx format:

**Structure:**
- Sheet 1 "销售管道":
  - Deal card layout (one row per deal):
    - Columns: 机会ID | 客户名称 | 联系人 | 预计金额 | 阶段 | 概率% | 预计成交日 | 负责人 | 产品/服务 | 竞争对手 | 备注
  - Auto-filter
  - Freeze header + first 2 columns

  - Dashboard summary at top:
    - Pipeline total: =SUM(预计金额列)
    - Weighted pipeline: =SUMPRODUCT(预计金额列, 概率列)
    - Deals closing this month: =SUMIFS()
    - Win rate (last 90 days): =COUNTIFS(阶段, "已成交", ...)/COUNTIFS(...)
    - Average deal size: =AVERAGEIF()

  - Data validation:
    - 阶段: 初步接触(10%), 需求调研(25%), 方案演示(50%), 报价谈判(70%), 合同评审(90%), 已成交(100%), 已丢单(0%)
    - 概率% auto-filled via VLOOKUP from stage table

- Sheet 2 "销售活动":
  - Activity log per deal:
    - Columns: 日期 | 机会ID | 活动类型 | 内容 | 成果 | 下一步 | 负责人
  - 活动类型: 电话, 邮件, 拜访, 演示, 报价, 谈判, 合同

- Sheet 3 "月度分析":
  - Monthly pipeline metrics:
    - Columns: Month | New Deals | Closed Won | Closed Lost | Pipeline Created | Pipeline Closed | Win Rate | Avg Cycle (days)
  - Charts: funnel (bar), win rate trend (line), pipeline value trend (area)

**Conditional Formatting:**
- Stage colors: gradient from gray → blue → teal → orange → purple → green
- Close date within 7 days AND stage not "已成交": yellow highlight
- Close date past AND stage not closed: red "stale deal" alert
- Deal value > threshold: bold
- Recently updated (< 3 days): subtle green indicator

**Formulas:**
- Weighted value: =D2*VLOOKUP(E2, 阶段概率表, 2, 0)
- Days in current stage: =TODAY()-最后活动日期
- Win rate: =COUNTIFS(E:E, "已成交", 成交日列, ">="&EDATE(TODAY(),-1))/COUNTIFS(E:E, "<>*", 创建日列, ">="&EDATE(TODAY(),-1))
```

## Style Conventions

- **Professional, clean** — darker header, subtle borders, consistent spacing
- **Status-driven coloring**: clear visual signals for action items
- **Print-ready layouts** for invoices
- **Data validation on key fields** — dropdowns for stages, categories
- **Currency**: ¥#,##0 or $#,##0 with two decimals for financial sheets
- **Font**: Arial / Calibri, 11pt body, 12pt bold headers

## Common Formulas

```python
# Stage lookup
ws['F2'] = '=VLOOKUP(E2, 阶段概率表, 2, 0)'

# Weighted pipeline
ws['B3'] = '=SUMPRODUCT(D2:D100, F2:F100)'

# Overdue follow-up
ws['L2'] = '=AND(K2<TODAY(), F2<>"已成交")'

# Days since last contact
ws['M2'] = '=TODAY()-J2'

# Status from stock levels
ws['H2'] = '=IFS(D2<=0,"缺货",D2<=E2,"低库存",D2>F2,"超额",TRUE,"正常")'

# Invoice total
ws['F39'] = '=SUM(F21:F37)'
ws['F41'] = '=F39*F40'   # Tax
ws['F42'] = '=F39+F41'    # Grand total

# Months of inventory
ws['I2'] = '=D2/H2'
```

## Related Resources

- [../references/style-guide.md](../references/style-guide.md) — Full formatting reference
- [skills/anthropics/skills/xlsx](../../../skills/anthropics/skills/xlsx/SKILL.md) — openpyxl + recalc workflow
