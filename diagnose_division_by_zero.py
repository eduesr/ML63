#!/usr/bin/env python3
"""
Diagnose division by zero error in consumos_suministros table
Query for GENERATED columns, DEFAULT values, and CHECK constraints
"""

import sys
import subprocess

try:
    from supabase import create_client
except ImportError:
    print("Installing supabase-py...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

# Supabase credentials
SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cXRzdXNrZGJnd3B5dnlpcHJjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3Nzc2MTc5NCwiZXhwIjoyMDkzMzM3Nzk0fQ.sq7ik4LUxOXErsnRBdYZZP-70CFzrxWoy4qb2DsUymg"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("\n" + "="*80)
print("DIAGNOSING DIVISION BY ZERO ERROR")
print("="*80)

# Query 1: Check columns, defaults, and generated expressions
print("\n" + "-"*80)
print("QUERY 1: Columns, Defaults, and Generated Expressions")
print("-"*80)

query1 = """
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default,
  is_generated,
  generation_expression
FROM information_schema.columns
WHERE table_name = 'consumos_suministros'
ORDER BY ordinal_position;
"""

try:
    # Execute raw SQL via Supabase
    result = supabase.postgrest.sql(query1).execute()
    print("\n✓ Query 1 successful:")
    if result:
        for row in result:
            print(f"  Column: {row.get('column_name', 'N/A')}")
            print(f"    Type: {row.get('data_type', 'N/A')}")
            print(f"    Nullable: {row.get('is_nullable', 'N/A')}")
            print(f"    Default: {row.get('column_default', 'NULL')}")
            print(f"    Generated: {row.get('is_generated', 'NEVER')}")
            if row.get('generation_expression'):
                print(f"    Generation Expression: {row.get('generation_expression')}")
            print()
except Exception as e:
    print(f"❌ Query 1 failed: {e}")
    # Try alternative approach using raw REST API
    print("\nTrying alternative diagnostic approach...")

# Query 2: Check CHECK constraints
print("\n" + "-"*80)
print("QUERY 2: CHECK Constraints")
print("-"*80)

query2 = """
SELECT
  constraint_name,
  constraint_type,
  check_clause
FROM information_schema.table_constraints
WHERE table_name = 'consumos_suministros'
AND constraint_type = 'CHECK';
"""

try:
    result = supabase.postgrest.sql(query2).execute()
    print("\n✓ Query 2 successful:")
    if result:
        for row in result:
            print(f"  Constraint: {row.get('constraint_name', 'N/A')}")
            print(f"    Type: {row.get('constraint_type', 'N/A')}")
            print(f"    Check Clause: {row.get('check_clause', 'N/A')}")
            print()
    else:
        print("  No CHECK constraints found")
except Exception as e:
    print(f"❌ Query 2 failed: {e}")

# Query 3: Get constraint definitions
print("\n" + "-"*80)
print("QUERY 3: Full Constraint Definitions")
print("-"*80)

query3 = """
SELECT
  con.conname AS constraint_name,
  pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
JOIN pg_class rel ON con.conrelid = rel.oid
JOIN pg_namespace nsp ON rel.relnamespace = nsp.oid
WHERE rel.relname = 'consumos_suministros'
AND nsp.nspname = 'public';
"""

try:
    result = supabase.postgrest.sql(query3).execute()
    print("\n✓ Query 3 successful:")
    if result:
        for row in result:
            print(f"  {row.get('constraint_name', 'N/A')}")
            print(f"    {row.get('constraint_definition', 'N/A')}")
            print()
    else:
        print("  No constraints found")
except Exception as e:
    print(f"❌ Query 3 failed: {e}")

print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80)
