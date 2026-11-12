#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas", "openpyxl"]
# ///
"""
Analyze xlsx structure and data using pandas + openpyxl.

Usage:
  uv run scripts/analyze.py input.xlsx
"""
import sys
import pandas as pd

def analyze_xlsx(path):
    xls = pd.ExcelFile(path, engine='openpyxl')
    print(f"File: {path}")
    print(f"Sheets ({len(xls.sheet_names)}): {', '.join(xls.sheet_names)}")
    print()

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, engine='openpyxl')
        print(f"=== {sheet} ===")
        print(f"  Dimensions: {df.shape[0]} rows x {df.shape[1]} cols")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Dtypes: {dict(df.dtypes)}")
        print(f"  Missing values: {df.isna().sum().to_dict()}")
        print(f"  Summary stats:")
        for col in df.select_dtypes(include='number').columns:
            print(f"    {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}, median={df[col].median():.2f}")
        print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/analyze.py <input.xlsx>", file=sys.stderr)
        sys.exit(1)
    analyze_xlsx(sys.argv[1])
