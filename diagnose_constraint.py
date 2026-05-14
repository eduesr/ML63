#!/usr/bin/env python3
"""
Query the database schema to find what uses day 16
"""

import sys
import subprocess
import requests
import json

try:
    import psycopg2
except ImportError:
    print("Installing psycopg2-binary...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'], check=True)
    import psycopg2

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cXRzdXNrZGJnd3B5dnlpcHJjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzc2MTc5NCwiZXhwIjoyMDkzMzM3Nzk0fQ.sq7ik4LUxOXErsnRBdYZZP-70CFzrxWoy4qb2DsUymg"

print("\n" + "="*80)
print("QUERYING DATABASE SCHEMA FOR DAY 16 CONSTRAINT/TRIGGER")
print("="*80)

# Use Supabase REST API to query the information schema
headers = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Query 1: Check all columns for generated expressions
print("\n" + "-"*80)
print("QUERY 1: Columns with Generated Expressions")
print("-"*80)

# Since we can't run raw SQL via REST, let's try a simpler approach:
# Create a test record with a specific date and catch the detailed error

try:
    from supabase import create_client
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

# Try to insert a day 16 record and capture the full error
test_record = {
    "fecha_inicio": "2023-02-16",
    "fecha_fin": "2023-03-15",
    "consumo_kwh": 100,
    "tipo_suministro": "gas",
    "proveedor": "Test",
    "numero_factura": "DEBUG_ERROR_MESSAGE",
    "consumo_valido": True,
    "validacion_notas": "Attempting to capture full error"
}

try:
    response = supabase.table('consumos_suministros').insert(test_record).execute()
    print("✓ Record inserted (no error)")
except Exception as e:
    print(f"✗ DETAILED ERROR MESSAGE:")
    print(f"{str(e)}\n")
    
    # Try to extract more details from the error
    error_str = str(e)
    if "division" in error_str.lower():
        print("→ Confirmed: Division by zero error")
    if "CHECK" in error_str:
        print("→ Likely cause: CHECK constraint")
    if "function" in error_str.lower() or "trigger" in error_str.lower():
        print("→ Likely cause: Trigger or function")
    if "generated" in error_str.lower():
        print("→ Likely cause: GENERATED column")

print("\n" + "="*80)
print("NEXT STEP: Check database directly using psycopg2")
print("="*80)
print("\nTo find the exact constraint, run this SQL in Supabase SQL Editor:\n")

sql_commands = [
    ("View all CHECK constraints:", """
SELECT
  con.conname AS constraint_name,
  pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
JOIN pg_class rel ON con.conrelid = rel.oid
WHERE rel.relname = 'consumos_suministros'
AND con.contype = 'c';
"""),
    ("View all GENERATED columns:", """
SELECT
  column_name,
  is_generated,
  generation_expression
FROM information_schema.columns
WHERE table_name = 'consumos_suministros'
AND is_generated = 'ALWAYS';
"""),
    ("View all triggers:", """
SELECT
  trigger_name,
  event_manipulation,
  action_statement
FROM information_schema.triggers
WHERE event_object_table = 'consumos_suministros';
""")
]

for title, sql in sql_commands:
    print(f"\n{title}")
    print("-" * 80)
    print(sql.strip())
