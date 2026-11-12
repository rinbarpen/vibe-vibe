---
name: omnisheet-project-management
description: Project management spreadsheet generation — Gantt timelines, task trackers, OKR sheets, risk registers. Use when the user asks for 甘特图、任务追踪、OKR、风险管理 or any project management Excel file.
---

# Project Management Sheets (项目管理)

Generates project management spreadsheets with visual timelines, task tracking, OKRs, and risk management matrices.

## When to Use

- 甘特图式项目时间线 (Gantt-style project timelines)
- 任务进度追踪 (Task progress tracking)
- OKR 目标管理 (OKR goal management)
- 风险管理矩阵 (Risk registers / matrices)
- 任何项目管理相关的追踪表格

## Quick Start

```
Create a project task tracker for a website redesign project.
Phases: Design, Development, Testing, Launch.
Columns: Task, Assignee, Priority, Status, Start Date, Due Date, Progress %, Notes.
Use conditional formatting for overdue items and status colors.
```

## Preset Templates

### Preset 1: 甘特图 (Gantt Timeline)

```
Create a Gantt-style project timeline in .xlsx format:

**Structure:**
- Sheet 1 "甘特图":
  - Left panel (columns A-F): WBS | 任务名称 | 负责人 | 开始日期 | 结束日期 | 状态
  - Right panel (columns G onwards): Weekly timeline (e.g., G1=Week1, H1=Week2, ... 12-52 weeks)
  - Timeline header rows:
    - Row 1: Month labels (merged cells)
    - Row 2: Week numbers
  - Gantt bars: conditional formatting formula fills cells where week falls within task's start-end range

  - Task hierarchy with indentation:
    - Phase 1 (bold)
    -   Task 1.1
    -   Task 1.2
    - Phase 2 (bold)
    -   ...

  - Data validation: 状态 column dropdown: 未开始/进行中/已完成/延期/阻塞

- Sheet 2 "任务清单": Detailed task list
  - Columns: WBS | 任务 | 描述 | 负责人 | 优先级 | 开始 | 结束 | 工期(天) | 前置任务 | 进度% | 状态 | 备注
  - 进度%: conditional formatting data bar
  - 工期: =NETWORKDAYS(开始, 结束) formula
  - 前置任务: comma-separated WBS codes

**Formatting:**
- Phases: bold, light blue background
- Today line: red vertical conditional format (formula checks if today is within week)
- Gantt bar color by status: green(完成), blue(进行中), yellow(延期), gray(未开始)
- Overdue: red background if End Date < TODAY() AND Progress < 100%
- Weekend columns (Sat/Sun): gray background

**Key Formulas:**
- Gantt cell: =AND(G$2>=$D3, G$2<=$E3) for conditional formatting
- Today marker: =AND(G$2>=TODAY(), G$2<TODAY()+7)
- Duration: =NETWORKDAYS(D3, E3)
```

### Preset 2: 任务追踪 (Task Tracker)

```
Create a comprehensive task tracker in .xlsx format:

**Structure:**
- Sheet 1 "任务面板":
  - Columns: ID | 任务名称 | 描述 | 负责人 | 优先级(P0-P3) | 状态 | 开始日期 | 截止日期 | 进度% | 预计工时(h) | 实际工时(h) | 阻碍 | 备注
  - Auto-filter on all columns
  - Freeze header + first column

  - Summary section at top (rows 1-5):
    - Total tasks: =COUNTA()
    - Completed: =COUNTIF()
    - Completion rate: formula
    - Overdue tasks: =COUNTIFS(状态,"<>已完成", 截止日期,"<"&TODAY())
    - At-risk (due within 3 days, not complete): formula

- Sheet 2 "按负责人": Pivot-style breakdown
  - Rows: 负责人
  - Columns: 状态 (未开始, 进行中, 已完成, 延期, 阻塞)
  - Values: count of tasks
  - =COUNTIFS() formulas

- Sheet 3 "时间线": Weekly burn-down/up
  - Columns: Week | Planned Complete | Actual Complete | Cumulative Planned | Cumulative Actual
  - Line chart: burn-down comparison

**Conditional Formatting:**
- P0 tasks: bold red text
- Overdue: entire row light red background
- Due within 3 days: yellow background
- Status colors: green(完成), blue(进行中), gray(未开始), red(延期), orange(阻塞)
- Progress data bars in 进度% column

**Data Validation:**
- 优先级: P0, P1, P2, P3
- 状态: 未开始, 进行中, 已完成, 延期, 阻塞
```

### Preset 3: OKR管理 (OKR Goal Management)

```
Create an OKR (Objectives and Key Results) tracker in .xlsx format:

**Structure:**
- Sheet 1 "OKR总览 Q1 2026":
  - Header section (rows 1-3): Quarter selector, team name, last updated date
  - Columns:
    O1: Objective (bold, merged for multiple KRs)
    KR: Key Result description
    起始值 (Starting value)
    目标值 (Target value)
    当前值 (Current value)
    进度% (=当前值/目标值, capped at 100%)
    信心度 (1-10 scale)
    负责人
    状态 (On Track / At Risk / Behind / Done)
    备注

  - Objective groups with light background shading
  - KR rows indented under each Objective
  - Scoring: 0.0 to 1.0 based on % completion
  - Average score per Objective: =AVERAGEIF() formula

  - Summary box:
    - Total Objectives, Total KRs
    - Average progress: =AVERAGE()
    - Status distribution: =COUNTIF() per status

- Sheet 2 "季度对比": Quarterly comparison
  - Columns: Quarter | Objective | KR | Q Score | Q+1 Score | Q+2 Score | Trend
  - Trend sparklines

- Sheet 3 "周报模板": Weekly check-in log
  - Columns: 日期 | Objective/KR | 本周进展 | 下周计划 | 风险/阻碍 | 信心变化

**Formatting:**
- Objectives: bold, colored background (one color per O)
- Progress: data bar conditional formatting (green gradient)
- Status: green(On Track), yellow(At Risk), red(Behind), blue(Done)
- Confidence: color scale (red-yellow-green)
- Frozen header + first 2 columns

**Formulas:**
- Progress: =MIN(B10/C10, 1) capped at 100%
- Average O score: =AVERAGEIF(A:A, A2, D:D)
```

### Preset 4: 风险矩阵 (Risk Register)

```
Create a risk management matrix in .xlsx format:

**Structure:**
- Sheet 1 "风险登记册":
  - Columns: ID | 风险描述 | 类别 | 概率(1-5) | 影响(1-5) | 风险等级(=概率*影响) | 触发条件 | 应对策略 | 负责人 | 状态 | 识别日期 | 最后更新

  - Risk heat map (top-right of sheet):
    - 5x5 grid (probability × impact)
    - Conditional formatting: green(1-6), yellow(8-12), orange(15-16), red(20-25)
    - Cell count from risk register per quadrant

  - Summary stats:
    - Total risks, by level, by category, by status
    - Top 5 risks by RPN (Risk Priority Number)

  - Data validation:
    - 类别: 技术/资源/进度/外部/合规/市场
    - 概率/影响: 1,2,3,4,5
    - 状态: 已识别/监控中/已发生/已关闭
    - 应对策略: 规避/转移/缓解/接受

- Sheet 2 "缓解计划": Mitigation action tracker
  - Columns: 风险ID | 缓解措施 | 负责人 | 截止日期 | 状态 | 成本估算 | 效果评估
  - Linked to Sheet 1 via risk ID

**Conditional Formatting:**
- 风险等级: 4-color scale per heat map (green→yellow→orange→red)
- Overdue mitigation: red row
- Closed risks: gray text strikethrough
- New (identified < 7 days): bold

**Formulas:**
- Risk score: =C2*D2
- Risk level: =IF(E2<=6,"低",IF(E2<=12,"中",IF(E2<=16,"高","严重")))
- Days since identified: =TODAY()-K2
```

## Style Conventions

- **Status colors**: Green (完成/On Track), Blue (进行中), Yellow (At Risk/延期), Red (Blocked/Overdue), Gray (未开始)
- **Priority**: P0=Red bold, P1=Orange, P2=Blue, P3=Gray
- **Headers**: Dark background, white text, bold
- **Progress bars**: Green data bar conditional formatting
- **Dates**: ISO format YYYY-MM-DD
- **Weekend columns** (Gantt): Gray background

## Common Formulas

```python
# Gantt cell highlight (week falls within task dates)
ws['G3'] = '=AND(G$1>=$D3-1, G$1<=$E3)'  # for conditional format

# Network days
ws['H3'] = '=NETWORKDAYS(D3, E3)'

# Completion rate
ws['B3'] = '=COUNTIF(状态列,"已完成")/COUNTA(任务列)'

# Overdue count
ws['B4'] = '=COUNTIFS(状态列,"<>已完成",截止日期列,"<"&TODAY())'

# OKR progress (capped)
ws['E2'] = '=MIN(D2/C2, 1)'

# Risk score
ws['E2'] = '=C2*D2'

# Days remaining
ws['F3'] = '=E3-TODAY()'
```

## Related Resources

- [../references/style-guide.md](../references/style-guide.md) — Full formatting reference
- [skills/anthropics/skills/xlsx](../../../skills/anthropics/skills/xlsx/SKILL.md) — openpyxl + recalc workflow
