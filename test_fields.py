#!/usr/bin/env python3
"""
Test each field of the problematic record to identify the culprit
"""

import sys
import subprocess

try:
    from supabase import create_client
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "TU_SERVICE_ROLE_KEY_AQUI"

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("TESTING FIELDS TO IDENTIFY DIVISION BY ZERO CAUSE")
print("="*80)

# Base working record
base = {
    "fecha_inicio": "2026-05-01",
    "fecha_fin": "2026-05-15",
    "consumo_kwh": 100,
    "tipo_suministro": "gas",
    "proveedor": "Test",
    "numero_factura": "TEST_BASE",
    "consumo_valido": True,
    "validacion_notas": "Base test"
}

# Problematic values
problematic_values = {
    "fecha_inicio": "2023-02-16",
    "fecha_fin": "2023-03-15",
    "consumo_kwh": 17900,
    "tipo_suministro": "gas",
    "proveedor": "Comercializadora Regulada",
    "numero_factura": "FE231370067490_TEST",
    "consumo_valido": True,
    "validacion_notas": "Extraído de FE23137006749032.pdf"
}

# Test each field by replacing one at a time
fields = ["fecha_inicio", "fecha_fin", "consumo_kwh", "tipo_suministro", "proveedor", "numero_factura", "consumo_valido", "validacion_notas"]

print("\nTesting each field from problematic record:\n")

for field in fields:
    test_record = base.copy()
    test_record[field] = problematic_values[field]
    test_record["numero_factura"] = f"TEST_{field}_{len(test_record)}"

    try:
        response = supabase.table('consumos_suministros').insert(test_record).execute()
        result = "✓ SUCCESS"
        # Clean up
        try:
            supabase.table('consumos_suministros').delete().eq('numero_factura', test_record["numero_factura"]).execute()
        except:
            pass
    except Exception as e:
        result = f"✗ FAILED: {str(e)[:80]}"

    print(f"  {field:20s} = {str(problematic_values[field]):40s} → {result}")

print("\n" + "="*80)
print("Now test combinations of problematic fields:")
print("="*80 + "\n")

# Test with ALL problematic fields
all_problematic = problematic_values.copy()
all_problematic["numero_factura"] = "TEST_ALL_PROBLEMATIC"

try:
    response = supabase.table('consumos_suministros').insert(all_problematic).execute()
    print("✓ ALL problematic fields together: SUCCESS")
    supabase.table('consumos_suministros').delete().eq('numero_factura', 'TEST_ALL_PROBLEMATIC').execute()
except Exception as e:
    print(f"✗ ALL problematic fields together: FAILED")
    print(f"  Error: {str(e)}")
