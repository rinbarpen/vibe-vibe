# Omnisheet Style Guide

Shared formatting standards and conventions for all sheet generation sub-skills.

## Color Palettes

### Financial
- **Blue (RGB: 0,0,255)**: Hardcoded inputs / assumptions
- **Black (RGB: 0,0,0)**: Formulas and calculations
- **Green (RGB: 0,128,0)**: Cross-sheet references
- **Red (RGB: 255,0,0)**: External links
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention
- **Light gray header (RGB: 242,242,242)**: Column headers

### Data Analysis
- **Dark blue header (RGB: 52,73,94)**: White text on dark for headers
- **Alternate row (RGB: 245,247,250)**: Subtle zebra striping
- **Highlight (RGB: 41,128,185)**: Key metrics, totals row
- **Red accent (RGB: 231,76,60)**: Negative values, alerts

### Project Management
- **Green (RGB: 39,174,96)**: Complete / On track
- **Yellow (RGB: 241,196,15)**: In progress / At risk
- **Red (RGB: 231,76,60)**: Blocked / Overdue
- **Gray (RGB: 189,195,199)**: Not started

### Personal
- **Primary accent**: User's choice, default to warm blue (RGB: 66,133,244)
- **Category colors**: Distinct per category, pastel backgrounds
- **Progress**: Gradient from red → yellow → green

### Business
- **Professional blue (RGB: 33,150,243)**: Headers, company branding
- **Dark text (RGB: 33,33,33)**: Body text
- **Subtle borders (RGB: 224,224,224)**: Cell borders
- **Total row**: Bold, light gray background

### Academic
- **Black (RGB: 0,0,0)**: All text and borders
- **White (RGB: 255,255,255)**: Background
- **Light gray (RGB: 240,240,240)**: Header background only
- **No color** for data cells — grayscale/clean for publication

## Font Conventions

| Scenario | Font | Size (Header) | Size (Body) |
|----------|------|---------------|-------------|
| Financial | Arial / Calibri | 12pt bold | 11pt |
| Data Analysis | Arial | 12pt bold | 11pt |
| Project Mgmt | Arial / 微软雅黑 | 12pt bold | 11pt |
| Personal | 微软雅黑 / Arial | 12pt bold | 11pt |
| Business | Arial / 微软雅黑 | 12pt bold | 11pt |
| Academic | Times New Roman | 11pt bold | 10pt |

## Number Formatting

### Financial
- Currency: `$#,##0` or `¥#,##0` (specify units in header: "Revenue (万元)")
- Percentages: `0.0%` (one decimal)
- Multiples: `0.0x` (valuation multiples)
- Negative: parentheses `(123)` not minus `-123`
- Zeros: display as `-` (custom format: `$#,##0;($#,##0);-`)

### General
- Numbers > 999: use thousands separator `#,##0`
- Decimals: 0-2 places depending on precision needed
- Dates: `YYYY-MM-DD` (ISO format preferred)
- Percentages: `0.0%` or `0.00%` for precision

## Common Excel Patterns

### Freeze Panes
```python
# Always freeze the header row
ws.freeze_panes = 'A2'  # Freeze row 1
# For multi-column headers
ws.freeze_panes = 'B3'  # Freeze column A + rows 1-2
```

### Auto-Filter
```python
# Enable auto-filter on data tables
ws.auto_filter.ref = f'A1:{last_col_letter}{last_row}'
```

### Data Validation
```python
from openpyxl.worksheet.datavalidation import DataValidation

# Dropdown list
dv = DataValidation(type='list', formula1='"Option A,Option B,Option C"')
dv.error = 'Please select from the dropdown'
ws.add_data_validation(dv)
dv.add('B2:B100')

# Number range
dv = DataValidation(type='whole', operator='between', formula1=0, formula2=100)
ws.add_data_validation(dv)
```

### Conditional Formatting
```python
from openpyxl.formatting.rule import CellIsRule, DataBarRule, ColorScaleRule

# Highlight overdue items
ws.conditional_formatting.add('D2:D100',
    CellIsRule(operator='lessThan', formula=['TODAY()'],
              fill=PatternFill(start_color='FFE6E6', end_color='FFE6E6', fill_type='solid')))

# Data bars for progress
ws.conditional_formatting.add('E2:E100',
    DataBarRule(start_type='num', start_value=0, end_type='num', end_value=100,
                color='FF27AE60'))

# Color scale for values
ws.conditional_formatting.add('C2:C100',
    ColorScaleRule(start_type='min', start_color='FFE74C3C',
                   mid_type='percentile', mid_value=50, mid_color='FFF1C40F',
                   end_type='max', end_color='FF27AE60'))
```

### Column Width & Row Height
```python
# Auto-fit (approximate)
for col in ws.columns:
    max_length = max(len(str(cell.value or '')) for cell in col)
    ws.column_dimensions[col[0].column_letter].width = min(max_length + 2, 40)

# Fixed header row height
ws.row_dimensions[1].height = 30
```

## CRITICAL: Formula-First Rule

**Always use Excel formulas, never Python-computed hardcoded values.**

```python
# WRONG
total = sum(data)
ws['B10'] = total  # Hardcodes 5000

# CORRECT
ws['B10'] = '=SUM(B2:B9)'
```

After generation, recalculate with:
```bash
python skills/anthropics/skills/xlsx/scripts/recalc.py output.xlsx
```

## Sheet Naming

- Use descriptive names: `预算汇总`, `投资明细`, `实验数据`
- Max 31 characters
- No special chars: `\ / ? * [ ] :`
- Prefix with number for ordered sheets: `01_预算`, `02_图表`
