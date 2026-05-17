#!/usr/bin/env python3
"""
Import complete, corrected dataset to Supabase
- Removes test records and duplicates from previous attempts
- Imports all 25 records with corrected invoice numbers
"""

import sys
import subprocess
import json

try:
    from supabase import create_client
except ImportError:
    print("Installing supabase-py...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "TU_SERVICE_ROLE_KEY_AQUI"

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("IMPORTING COMPLETE DATASET - With Corrected Invoice Numbers")
print("="*80)

# Load corrected data
with open('supabase_import_fixed.json', 'r') as f:
    records = json.load(f)

print(f"\nLoaded {len(records)} records from supabase_import_fixed.json")

# Step 1: Remove any test records from previous attempts
print("\n" + "-"*80)
print("Step 1: Cleaning test records from previous attempts")
print("-"*80)

test_patterns = ['TEST_', '_TEST', 'FE231370067490_TEST', 'FE241370116842_TEST']

for pattern in test_patterns:
    try:
        response = supabase.table('consumos_suministros').delete().ilike('numero_factura', f'%{pattern}%').execute()
        print(f"  ✓ Removed test records matching '{pattern}'")
    except Exception as e:
        print(f"  ℹ No test records matching '{pattern}' found")

# Step 2: Import records
print("\n" + "-"*80)
print("Step 2: Importing corrected records")
print("-"*80 + "\n")

success_count = 0
failed_records = []

for i, record in enumerate(records, 1):
    try:
        response = supabase.table('consumos_suministros').insert(record).execute()
        print(f"✓ [{i:2d}] {record['numero_factura']:20s} {record['fecha_inicio']} → {record['fecha_fin']} ({record['consumo_kwh']:6d} kWh)")
        success_count += 1
    except Exception as e:
        error_msg = str(e)
        print(f"✗ [{i:2d}] {record['numero_factura']:20s} → FAILED")
        print(f"       Error: {error_msg[:100]}")
        failed_records.append((record['numero_factura'], error_msg))

# Summary
print("\n" + "="*80)
print(f"IMPORT COMPLETE: {success_count}/{len(records)} records successfully imported")
print("="*80)

if failed_records:
    print(f"\n⚠️  {len(failed_records)} records failed:")
    for factura, error in failed_records:
        print(f"  - {factura}: {error[:80]}")
else:
    print("\n✓ All records imported successfully!")

# Verify import
print("\n" + "-"*80)
print("Verification: Current database record count")
print("-"*80)

try:
    response = supabase.table('consumos_suministros').select('numero_factura').execute()
    current_count = len(response.data) if response.data else 0
    print(f"\n✓ Total records in database: {current_count}")

    # Group by year
    years_dict = {}
    for record in response.data:
        factura = record['numero_factura']
        year = factura[2:4]  # Extract year from FE[YY]...
        if year not in years_dict:
            years_dict[year] = 0
        years_dict[year] += 1

    print("\n  Breakdown by year:")
    for year in sorted(years_dict.keys()):
        print(f"    20{year}: {years_dict[year]} records")

except Exception as e:
    print(f"✗ Error verifying import: {e}")
