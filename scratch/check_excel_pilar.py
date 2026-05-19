import pandas as pd
import glob
import os

print("--- EXCEL INSPECTION FOR 'PILAR' ---")
excel_files = glob.glob('/Users/eduardosr/Documents/GitHub/ML63/Recursos/Banco/*.xls*')
print("Found Excel files:", excel_files)

for file_path in excel_files:
    print(f"\nInspecting file: {os.path.basename(file_path)}")
    try:
        # Since these are .xls (Excel 97-2003) files, pandas might need xlrd. Let's try to read.
        df = pd.read_excel(file_path)
        print(f"Loaded successfully. Shape: {df.shape}")
        
        # Search for PILAR in any text columns
        mask = df.astype(str).apply(lambda x: x.str.contains('PILAR', case=False)).any(axis=1)
        matches = df[mask]
        print(f"Found {len(matches)} matching rows:")
        for idx, row in matches.iterrows():
            print(f"Row {idx}: {list(row.values)}")
    except Exception as e:
        print(f"Error reading with pandas: {e}")
        print("Trying alternative engines...")
        try:
            df = pd.read_excel(file_path, engine='xlrd')
            mask = df.astype(str).apply(lambda x: x.str.contains('PILAR', case=False)).any(axis=1)
            matches = df[mask]
            print(f"Found {len(matches)} matching rows (xlrd):")
            for idx, row in matches.iterrows():
                print(f"Row {idx}: {list(row.values)}")
        except Exception as err:
            print(f"Could not read excel file: {err}")
