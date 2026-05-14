#!/usr/bin/env python3
import sys, subprocess, json
try:
    from supabase import create_client
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

with open('/Users/eduardosr/Documents/GitHub/ML63/supabase_import.json') as f:
    records = json.load(f)

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cXRzdXNrZGJnd3B5dnlpcHJjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzc2MTc5NCwiZXhwIjoyMDkzMzM3Nzk0fQ.sq7ik4LUxOXErsnRBdYZZP-70CFzrxWoy4qb2DsUymg"
supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("IMPORTING ALL 24 RECORDS (After cleanup)")
print("="*80 + "\n")

success = 0
for i, r in enumerate(records, 1):
    try:
        supabase.table('consumos_suministros').insert(r).execute()
        print(f"✓ {i:2d}. {r['numero_factura']:25s} {r['fecha_inicio']} → {r['fecha_fin']}")
        success += 1
    except Exception as e:
        print(f"✗ {i:2d}. {r['numero_factura']:25s} {r['fecha_inicio']} → {r['fecha_fin']} | {str(e)[:60]}")

print(f"\n{'='*80}\n✓ SUCCESS: {success}/24\n{'='*80}\n")
