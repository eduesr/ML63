#!/usr/bin/env python3
import pandas as pd
import glob
import os

excel_files = sorted(glob.glob('/Users/eduardosr/Documents/GitHub/ML63/Recursos/Banco/*.xls*'))
for file_path in excel_files:
    print("\n" + "="*80)
    print(f"FILE: {os.path.basename(file_path)}")
    print("="*80)
    try:
        df = pd.read_excel(file_path, engine='xlrd')
        print(f"Columns: {list(df.columns)}")
        print(f"Shape: {df.shape}")
        print("\nFirst 10 rows:")
        print(df.head(10).to_string())
    except Exception as e:
        print(f"Error: {e}")
