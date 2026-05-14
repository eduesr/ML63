#!/usr/bin/env python3
"""
Verify the complete dataset by heating season
"""

import sys
import subprocess

try:
    from supabase import create_client
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cXRzdXNrZGJnd3B5dnlpcHJjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzc2MTc5NCwiZXhwIjoyMDkzMzM3Nzk0fQ.sq7ik4LUxOXErsnRBdYZZP-70CFzrxWoy4qb2DsUymg"

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("DATA VERIFICATION BY HEATING SEASON")
print("="*80)

try:
    response = supabase.table('consumos_suministros').select('numero_factura, fecha_inicio, fecha_fin, consumo_kwh').order('fecha_inicio', desc=False).execute()

    if not response.data:
        print("ERROR: No records found in database!")
        sys.exit(1)

    print(f"\n✓ Total records in database: {len(response.data)}\n")

    # Group by heating season
    seasons = {}

    for record in response.data:
        inicio = record['fecha_inicio']
        year = int(inicio[0:4])
        month = int(inicio[5:7])

        # Heating season: October (month 10) through May (month 5)
        if month >= 10:
            season_key = f"{year}/{year+1}"
        else:
            season_key = f"{year-1}/{year}"

        if season_key not in seasons:
            seasons[season_key] = {'count': 0, 'total_kwh': 0, 'records': []}

        seasons[season_key]['count'] += 1
        seasons[season_key]['total_kwh'] += record['consumo_kwh']
        seasons[season_key]['records'].append(record)

    # Display by season
    total_kwh_all = 0
    for season in sorted(seasons.keys()):
        data = seasons[season]
        print(f"🔥 Heating Season {season}")
        print(f"   {data['count']} records | Total: {data['total_kwh']:,} kWh")
        print()

        for record in data['records']:
            factura = record['numero_factura']
            inicio = record['fecha_inicio']
            fin = record['fecha_fin']
            kwh = record['consumo_kwh']
            print(f"   • {factura} | {inicio} → {fin} | {kwh:,} kWh")

        print()
        total_kwh_all += data['total_kwh']

    print("="*80)
    print(f"TOTAL: {len(response.data)} records | {total_kwh_all:,} kWh")
    print("="*80)

except Exception as e:
    print(f"Error querying database: {e}")
    sys.exit(1)
