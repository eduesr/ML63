#!/usr/bin/env python3
"""
Final import of all 24 records to Supabase with fixed consumo_diario formula
"""

import sys
import subprocess
import json

try:
    from supabase import create_client
except ImportError:
    print("Installing supabase...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

# Load data
with open('/Users/eduardosr/Documents/GitHub/ML63/supabase_import.json', 'r') as f:
    records = json.load(f)

# Supabase credentials
SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "TU_SERVICE_ROLE_KEY_AQUI"

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("IMPORTING 24 RECORDS TO SUPABASE (Division by Zero Fixed)")
print("="*80 + "\n")

success_count = 0
failed_records = []
consecutive_failures = 0

for i, record in enumerate(records, 1):
    try:
        response = supabase.table('consumos_suministros').insert(record).execute()
        print(f"✓ {i:2d}. {record['numero_factura']:25s} ({record['fecha_inicio']} → {record['fecha_fin']}) - SUCCESS")
        success_count += 1
        consecutive_failures = 0
    except Exception as e:
        error_msg = str(e)[:80]
        print(f"✗ {i:2d}. {record['numero_factura']:25s} ({record['fecha_inicio']} → {record['fecha_fin']}) - FAILED: {error_msg}")
        failed_records.append((record['numero_factura'], error_msg))
        consecutive_failures += 1
        
        if consecutive_failures >= 3:
            print(f"\n⚠️  3 consecutive failures detected. Stopping import.")
            break

print("\n" + "="*80)
print(f"IMPORT SUMMARY")
print("="*80)
print(f"✓ Successful: {success_count}/24")
print(f"✗ Failed: {len(failed_records)}/24")

if failed_records:
    print("\nFailed records:")
    for num_factura, error in failed_records:
        print(f"  - {num_factura}: {error}")

print("\n" + "="*80)
if success_count == 24:
    print("✓ ALL 24 RECORDS IMPORTED SUCCESSFULLY!")
    print("="*80)
    print("\nNext steps:")
    print("1. Verify data in Supabase dashboard")
    print("2. Check ML63.html charts display correct data by season")
    print("3. Breakdown:")
    print("   - 2022/23 (Oct 2022 - May 2023): 5 records, 63,816 kWh")
    print("   - 2023/24 (Oct 2023 - May 2024): 7 records, 81,732 kWh")
    print("   - 2024/25 (Oct 2024 - May 2025): 7 records, 98,959 kWh")
    print("   - 2025/26 (Oct 2025 - May 2026): 5 records, 80,982 kWh")
else:
    print(f"⚠️  IMPORT INCOMPLETE - {len(failed_records)} records still failing")
    print("="*80)
