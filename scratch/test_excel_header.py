#!/usr/bin/env python3
import pandas as pd
import glob

excel_files = glob.glob('/Users/eduardosr/Documents/GitHub/ML63/Recursos/Banco/*.xls*')
for f in excel_files:
    try:
        # Try header=8 (the 9th row, which is the 8th 0-indexed row in Excel)
        df = pd.read_excel(f, header=8, engine='xlrd')
        print(f"\nFile: {f}")
        print("Columns:", list(df.columns))
        print("Data shape:", df.shape)
        print("First 2 rows:")
        print(df.head(2).to_string())
    except Exception as e:
        print(f"Error reading {f}: {e}")
