#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["xlsxwriter"]
# ///
"""
Create formatted xlsx from JSON data using xlsxwriter (fastest writer).

Usage:
  uv run scripts/create.py data.json output.xlsx
  uv run scripts/create.py '{"sheets": [{"name": "Sheet1", "columns": ["A","B"], "rows": [[1,2],[3,4]]}]}' output.xlsx
"""
import json
import sys
import xlsxwriter

def create_workbook(data_path, output_path):
    if data_path.endswith('.json'):
        with open(data_path) as f:
            data = json.load(f)
    else:
        data = json.loads(data_path)

    wb = xlsxwriter.Workbook(output_path)

    header_fmt = wb.add_format({
        'bold': True, 'bg_color': '#4472C4', 'font_color': 'white',
        'border': 1, 'text_wrap': True, 'valign': 'vcenter',
    })
    cell_fmt = wb.add_format({'border': 1, 'valign': 'vcenter'})
    num_fmt = wb.add_format({'border': 1, 'num_format': '#,##0.00', 'valign': 'vcenter'})
    pct_fmt = wb.add_format({'border': 1, 'num_format': '0.0%', 'valign': 'vcenter'})

    for sheet_def in data.get('sheets', []):
        ws = wb.add_worksheet(sheet_def.get('name', 'Sheet1'))
        ws.set_column(0, 26, 12)

        columns = sheet_def.get('columns', [])
        rows = sheet_def.get('rows', [])

        # Write headers
        for col, name in enumerate(columns):
            ws.write(0, col, name, header_fmt)

        # Write data rows
        for row_idx, row in enumerate(rows):
            for col_idx, val in enumerate(row):
                if isinstance(val, float):
                    ws.write(row_idx + 1, col_idx, val, num_fmt)
                else:
                    ws.write(row_idx + 1, col_idx, val, cell_fmt)

        # Auto-filter
        if columns:
            ws.autofilter(0, 0, len(rows), len(columns) - 1)

    wb.close()
    print(f"[OK] Created {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: uv run create.py <data.json|JSON_STRING> <output.xlsx>", file=sys.stderr)
        sys.exit(1)
    create_workbook(sys.argv[1], sys.argv[2])
