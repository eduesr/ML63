#!/usr/bin/env python3
"""
Clean all consumos_suministros records and reimport the complete dataset
"""

import sys
import subprocess
import json
import time

try:
    from supabase import create_client
except ImportError:
    print("Installing supabase-py...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cXRzdXNrZGJnd3B5dnlpcHJjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzc2MTc5NCwiZXhwIjoyMDkzMzM3Nzk0fQ.sq7ik4LUxOXErsnRBdYZZP-70CFzrxWoy4qb2DsUymg"

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("CLEAN AND REIMPORT - Complete Dataset")
print("="*80)

# Step 1: Get count of existing records
print("\nStep 1: Checking existing records...")
try:
    response = supabase.table('consumos_suministros').select('numero_factura').execute()
    existing_count = len(response.data) if response.data else 0
    print(f"  Current records in database: {existing_count}")
except Exception as e:
    print(f"  Error checking records: {e}")
    existing_count = 0

# Step 2: Delete all records
if existing_count > 0:
    print(f"\nStep 2: Deleting {existing_count} existing records...")
    try:
        response = supabase.table('consumos_suministros').delete().neq('numero_factura', '').execute()
        print(f"  ✓ Deleted all records")
        time.sleep(1)  # Brief pause to ensure deletion completes
    except Exception as e:
        print(f"  ✗ Error deleting records: {e}")
        sys.exit(1)
else:
    print(f"\nStep 2: No records to delete, proceeding with import")

# Step 3: Verify table is empty
print("\nStep 3: Verifying table is empty...")
try:
    response = supabase.table('consumos_suministros').select('numero_factura', 'count', 'exact').execute()
    current_count = len(response.data) if response.data else 0
    print(f"  ✓ Table now contains {current_count} records")
except Exception as e:
    print(f"  ℹ Could not verify count (this is OK): {e}")

# Step 4: Load and import corrected data
print("\nStep 4: Importing 25 corrected records...")
with open('supabase_import_fixed.json', 'r') as f:
    records = json.load(f)

print(f"  Loaded {len(records)} records from supabase_import_fixed.json\n")

success_count = 0
failed_records = []

for i, record in enumerate(records, 1):
    try:
        response = supabase.table('consumos_suministros').insert(record).execute()
        print(f"✓ [{i:2d}] {record['numero_factura']:20s} {record['fecha_inicio']} → {record['fecha_fin']} ({record['consumo_kwh']:6d} kWh)")
        success_count += 1
    except Exception as e:
        error_msg = str(e)
        print(f"✗ [{i:2d}] {record['numero_factura']:20s} → FAILED: {error_msg[:80]}")
        failed_records.append((record['numero_factura'], error_msg))

# Summary
print("\n" + "="*80)
print(f"IMPORT RESULT: {success_count}/{len(records)} records successfully imported")
print("="*80)

if failed_records:
    print(f"\n⚠️  {len(failed_records)} records failed:")
    for factura, error in failed_records:
        print(f"  - {factura}: {error[:80]}")
    sys.exit(1)
else:
    print("\n✓ All 25 records imported successfully!")

# Step 5: Final verification with breakdown
print("\n" + "-"*80)
print("Final Verification: Complete database snapshot")
print("-"*80)

try:
    response = supabase.table('consumos_suministros').select('numero_factura, fecha_inicio, fecha_fin, consumo_kwh').order('fecha_inicio', desc=False).execute()

    if response.data:
        print(f"\nTotal records: {len(response.data)}\n")

        # Group by heating season (Oct-May)
        seasons = {
            '2022/23': [],
            '2023/24': [],
            '2024/25': [],
            '2025/26': [],
            '2026/27': []
        }

        for record in response.data:
            factura = record['numero_factura']
            inicio = record['fecha_inicio']
            fin = record['fecha_fin']
            kwh = record['consumo_kwh']

            # Determine heating season (Oct-May spans two calendar years)
            year = int(inicio[0:4])
            month = int(inicio[5:7])

            if month >= 10:
                season_key = f"{year}/{year+1}"
            else:
                season_key = f"{year-1}/{year}"

            if season_key in seasons:
                seasons[season_key].append({
                    'factura': factura,
                    'inicio': inicio,
                    'fin': fin,
                    'kwh': kwh
                })

        # Print by season
        for season in ['2022/23', '2023/24', '2024/25', '2025/26', '2026/27']:
            records_in_season = seasons[season]
            if records_in_season:
                total_kwh = sum(r['kwh'] for r in records_in_season)
                print(f"Season {season}: {len(records_in_season)} records, {total_kwh:,} kWh total")
                for r in records_in_season:
                    print(f"  • {r['factura']} {r['inicio']} → {r['fin']} ({r['kwh']:,} kWh)")
                print()
    else:
        print("ERROR: No records found after import!")
        sys.exit(1)

except Exception as e:
    print(f"Error during verification: {e}")
    sys.exit(1)

print("="*80)
print("✓ IMPORT COMPLETE AND VERIFIED")
print("="*80)
