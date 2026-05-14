#!/usr/bin/env python3
"""
Test different record values to identify what causes division by zero
"""

import sys
import subprocess
import json

try:
    from supabase import create_client, Client
except ImportError:
    print("Installing supabase-py...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client, Client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cXRzdXNrZGJnd3B5dnlpcHJjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzc2MTc5NCwiZXhwIjoyMDkzMzM3Nzk0fQ.sq7ik4LUxOXErsnRBdYZZP-70CFzrxWoy4qb2DsUymg"

supabase: Client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("TESTING VALUES TO IDENTIFY DIVISION BY ZERO CAUSE")
print("="*80)

# Test 1: Insert with NULL consumo_kwh (if division by kwh)
print("\n" + "-"*80)
print("Test 1: NULL consumo_kwh")
print("-"*80)

test1 = {
    "fecha_inicio": "2026-05-01",
    "fecha_fin": "2026-05-15",
    "consumo_kwh": 0,  # Try zero instead of NULL
    "tipo_suministro": "gas",
    "proveedor": "Test",
    "numero_factura": "TEST_ZERO_KWH",
    "consumo_valido": True,
    "validacion_notas": "Testing zero kWh"
}

try:
    response = supabase.table('consumos_suministros').insert(test1).execute()
    print(f"✓ Zero kWh insert SUCCESS")
    # Clean up
    supabase.table('consumos_suministros').delete().eq('numero_factura', 'TEST_ZERO_KWH').execute()
except Exception as e:
    print(f"✗ Zero kWh insert FAILED: {str(e)[:100]}")

# Test 2: Insert with actual problematic record to get detailed error
print("\n" + "-"*80)
print("Test 2: First problematic record (FE231370067490)")
print("-"*80)

# From the JSON file - this one failed
problematic = {
    "fecha_inicio": "2023-02-16",
    "fecha_fin": "2023-03-15",
    "consumo_kwh": 17900,
    "tipo_suministro": "gas",
    "proveedor": "Comercializadora Regulada",
    "numero_factura": "FE231370067490_TEST",
    "consumo_valido": True,
    "validacion_notas": "Extraído de FE23137006749032.pdf"
}

try:
    response = supabase.table('consumos_suministros').insert(problematic).execute()
    print(f"✓ Problematic record insert SUCCESS")
    supabase.table('consumos_suministros').delete().eq('numero_factura', 'FE231370067490_TEST').execute()
except Exception as e:
    error_msg = str(e)
    print(f"✗ Problematic record FAILED")
    print(f"  Error: {error_msg}")

    # Analyze error
    if "division" in error_msg.lower():
        print("  → Error is related to DIVISION")
    if "22012" in error_msg:
        print("  → PostgreSQL error 22012 = division by zero")

# Test 3: Try minimal record
print("\n" + "-"*80)
print("Test 3: Minimal record with required fields only")
print("-"*80)

minimal = {
    "fecha_inicio": "2026-05-01",
    "fecha_fin": "2026-05-15",
    "consumo_kwh": 100,
    "tipo_suministro": "gas",
    "proveedor": "Test",
    "numero_factura": "TEST_MINIMAL",
    "consumo_valido": True,
    "validacion_notas": "Minimal test"
}

try:
    response = supabase.table('consumos_suministros').insert(minimal).execute()
    print(f"✓ Minimal record insert SUCCESS")
    supabase.table('consumos_suministros').delete().eq('numero_factura', 'TEST_MINIMAL').execute()
except Exception as e:
    print(f"✗ Minimal record FAILED: {str(e)[:100]}")

print("\n" + "="*80)
print("Summary: Check if errors are consistent or specific to certain data")
print("="*80)
