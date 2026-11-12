---
name: omnisheet-personal-life
description: Personal life spreadsheet generation — expense trackers, fitness plans, travel planners, habit trackers. Use when the user asks for 记账、健身、旅行计划、习惯打卡 or any personal organization Excel file.
---

# Personal Life Sheets (个人生活)

Generates personal organization spreadsheets with clean, friendly design. Focus on usability and visual clarity over corporate formatting.

## When to Use

- 月度/年度记账 (Monthly / annual expense tracking)
- 健身训练计划 (Fitness / workout plans)
- 旅行计划 (Travel itineraries and planners)
- 习惯打卡 (Habit tracking)
- 任何个人组织和生活管理表格

## Quick Start

```
Create a monthly expense tracker for June 2026.
Categories: 餐饮, 交通, 购物, 娱乐, 住房, 医疗, 教育, 其他.
Track daily spending, show category totals, and compare against a budget of ¥8,000.
```

## Preset Templates

### Preset 1: 月度记账 (Monthly Expense Tracker)

```
Create a personal monthly expense tracker in .xlsx format:

**Structure:**
- Sheet 1 "支出记录":
  - Columns: 日期 | 类别 | 项目 | 金额 | 支付方式 | 备注
  - 类别 dropdown: 餐饮, 交通, 购物, 娱乐, 住房, 医疗, 教育, 通讯, 服饰, 其他
  - 支付方式 dropdown: 微信, 支付宝, 银行卡, 现金, 其他
  - Auto-filter enabled
  - Daily subtotal row (optional toggle)

- Sheet 2 "月度汇总":
  - Budget setting at top: 月度预算 [B1], 储蓄目标 [B2]
  - Category breakdown table:
    - Columns: 类别 | 预算金额 | 实际支出(=SUMIF()) | 差额(=预算-实际) | 占比(=实际/SUM(实际))
  - Total row: =SUM()
  - 餐饮 includes sub-breakdown: 早/午/晚餐, 零食, 外卖

  - Visual summary:
    - Progress bar for total budget usage (=实际/预算, %)
    - Pie chart: spending by category
    - 每日支出趋势: daily spending line chart
    - Top 10 single expenses

- Sheet 3 "历史趋势":
  - 12-month overview: Month | Total | Budget | Variance | Savings Rate
  - Uses formulas referencing each monthly sheet
  - Line chart: spending trend over year

**Formatting:**
- Warm, personal color scheme (not corporate blue)
- Category colors: distinct pastel per category
- Over-budget: red cell highlight via conditional formatting
- Budget remaining > 30%: green
- Daily spending > average*2: flagged orange
- Currency: ¥#,##0

**Formulas:**
- Category actual: =SUMIF(支出记录!B:B, A5, 支出记录!D:D)
- Budget remaining: =B1-SUM(支出记录!D:D)
- Daily average: =SUM(支出记录!D:D)/COUNTUNIQUE(支出记录!A:A)
- Savings rate: =B2/SUM(B6:B7)
```

### Preset 2: 健身计划 (Fitness Plan)

```
Create a fitness and workout plan in .xlsx format:

**Structure:**
- Sheet 1 "周计划":
  - Weekly schedule grid:
    - Rows: time slots (Morning/Afternoon/Evening)
    - Columns: Mon-Sun
    - Fill with workout types
  - Legend: 力量训练, 有氧, 柔韧性, 休息, 户外
  - This week's focus area (cell)
  - Water intake tracker row: 8 glasses checkboxes

- Sheet 2 "训练库":
  - Exercise library organized by muscle group
  - Columns: 动作名称 | 目标肌群 | 组数 | 次数 | 重量(kg) | 休息(秒) | 备注 | 视频链接
  - Grouped by: 胸/背/肩/臂/腿/核心/有氧
  - 1RM calculator: input weight + reps → estimated 1RM

- Sheet 3 "训练日志":
  - Columns: 日期 | 训练类型 | 动作 | 组数 | 次数 | 重量 | 感受(RPE 1-10) | 备注
  - Auto-calculated: 训练量(=组数*次数*重量)
  - Weekly volume summary
  - Progress chart: key lift progress over time (line chart)

- Sheet 4 "身体数据":
  - Columns: 日期 | 体重 | 体脂% | 肌肉量 | 腰围 | 胸围 | 臂围 | 腿围
  - Delta from previous measurement
  - Weight trend chart with moving average
  - Goal weight line on chart

**Formatting:**
- Clean sporty aesthetic: dark green header with white text
- Workout type color coding: blue(力量), orange(有氧), purple(柔韧), gray(休息), green(户外)
- Progress: trend arrows (↑↓→) via formula
- Rest day cells: light gray background

**Formulas:**
- 1RM estimate: =weight*(1+reps/30) (Epley formula)
- Training volume: =组数*次数*重量
- Weight delta: =B5-B4
- BMI: =体重/(身高^2) if height provided
```

### Preset 3: 旅行计划 (Travel Planner)

```
Create a travel planner spreadsheet in .xlsx format:

**Structure:**
- Sheet 1 "行程总览":
  - Trip header: 目的地 | 日期 | 人数 | 预算总额
  - Daily itinerary:
    - Columns: 日期 | 时间 | 活动/景点 | 地址 | 交通方式 | 费用预算 | 实际费用 | 备注
    - Activities grouped by day with merged date cells
    - 交通方式 dropdown: 步行/公交/地铁/出租车/租车/火车/飞机
  - Map links column (clickable if possible)

- Sheet 2 "预算管理":
  - Pre-trip expenses:
    - Columns: 项目 | 类别 | 预算 | 实际 | 已支付? | 预订确认号
    - Categories: 机票/火车, 住宿, 签证, 保险, 装备
  - Daily budget tracker:
    - Per-day allocation = total / days
    - Daily actual, cumulative, over/under
    - Visual budget thermometer bar

- Sheet 3 "行李清单":
  - Packing checklist by category:
    - 证件/文件: 护照, 身份证, 签证, 保险单, 机票确认
    - 衣物: by type and count columns
    - 电子设备: 手机, 充电器, 转换插头, 相机
    - 洗漱用品: checklist items
    - 药品/急救: checklist items
    - 其他: checklist items
  - Checkbox column (☐/☑) for packed status
  - Weight estimate per category

- Sheet 4 "重要信息":
  - Flight/accommodation details table
  - Emergency contacts
  - Useful phrases (if international)
  - Daily weather forecast (3-5 day outlook)

**Formatting:**
- Fun, travel-inspired colors: teal/warm orange
- Packing list: strikethrough on checked items
- Budget: green(under), red(over)
- Clean card-like layout with merged cells for headers
```

### Preset 4: 习惯打卡 (Habit Tracker)

```
Create a monthly habit tracker in .xlsx format:

**Structure:**
- Sheet 1 "习惯打卡 2026年6月":
  - Grid layout:
    - Row 2: Day numbers 1-31 (or 28/30)
    - Row 3: Weekday labels (一二三四五六日)
    - Column A: Habit names (rows 5 onwards)
    - Cells: checkbox or ✓/✗ entries for daily completion

  - Suggested habit categories:
    - 健康: 早起(7:00前), 运动30分钟, 喝水8杯, 素食日
    - 学习: 阅读30分钟, 学习1小时, 记笔记
    - 生活: 冥想10分钟, 整理房间, 记账
    - 工作: 番茄钟x4, 无社交媒体日

  - Right panel (after day 31):
    - 目标天数 (Target days per month)
    - 已完成 (=COUNTIF() range)
    - 完成率% (=已完成/目标天数)
    - 连续天数 (Current streak: longest consecutive from today backwards)
    - 最长连续 (=MAX streak formula)
    - 完成率 data bar

  - Bottom summary row:
    - Daily completion count (=COUNTIF for each day column)
    - Daily completion % line chart

- Sheet 2 "年度视图":
  - 12-month overview by habit
  - Columns: Habit | Jan% | Feb% | ... | Dec% | 年平均
  - Color scale: green (≥80%), yellow (60-80%), red (<60%)
  - Year trend sparkline per habit

**Formatting:**
- Clean, minimal design with ample white space
- Weekends: subtle gray column background
- Today's column: light blue highlight
- Completion: green fill on ✓ cells
- Miss: light red fill on ✗ cells
- Habit categories: colored left border or icon
- Frozen row/column headers

**Formulas:**
- Completion rate: =COUNTIF(C5:AG5, "✓")/AH5
- Current streak: array formula counting consecutive ✓ from today backwards
- Daily score: =COUNTIF(C5:C20, "✓")/COUNTA($A5:$A20)
- Monthly average habit completion
```

## Style Conventions

- **Clean and friendly** — lighter, warmer palette than business sheets
- **Rounded, approachable feel** — thinner borders, pastel accents
- **Visual progress** — data bars, checkboxes, color coding for quick scanning
- **Chinese-friendly** — 微软雅黑 or system default, Chinese labels
- **Mobile-aware** — simple enough layouts to view on phone if synced
- **Currency**: ¥#,##0 for RMB, no decimals for daily expenses
- **Dates**: YYYY-MM-DD for logs, D/星期 for tracking grids

## Common Formulas

```python
# Category sum
ws['B5'] = '=SUMIF(支出记录!B:B, A5, 支出记录!D:D)'

# Budget remaining
ws['D2'] = '=B1-D1'  # budget - actual

# Streak (consecutive count)
# Helper row: if today done, increment; else reset

# Completion rate
ws['D5'] = '=COUNTIF(C5:AG5, "✓")/COUNTA(C5:AG5)'

# Daily summary
ws['C25'] = '=COUNTIF(C5:C24, "✓")'

# 1RM estimate
ws['E2'] = '=C2*(1+D2/30)'

# Training volume
ws['H2'] = '=D2*E2*F2'
```

## Related Resources

- [../references/style-guide.md](../references/style-guide.md) — Full formatting reference
- [skills/anthropics/skills/xlsx](../../../skills/anthropics/skills/xlsx/SKILL.md) — openpyxl workflow
