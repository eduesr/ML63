#!/usr/bin/env python3
"""
Diagnose division by zero error using psycopg2 connection
"""

import sys
import subprocess

# Install psycopg2 if needed
try:
    import psycopg2
except ImportError:
    print("Installing psycopg2...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'], check=True)
    import psycopg2

# Supabase PostgreSQL connection info
# Host: project-ref.supabase.co
# Port: 5432
# Database: postgres
# User: postgres
# Password: from service_role key (not the JWT token)

# Actually, let's use the RPC approach - Supabase has a rpc function for raw SQL

import requests
import json

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "TU_SERVICE_ROLE_KEY_AQUI"

headers = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

print("\n" + "="*80)
print("DIAGNOSING DIVISION BY ZERO ERROR - Using REST API")
print("="*80)

# Query 1: Check columns
print("\n" + "-"*80)
print("QUERY 1: Columns with Defaults and Generated Expressions")
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

# Supabase doesn't expose raw SQL via REST, but we can use rpc if a function exists
# Instead, let's try a different approach: query the actual table to see what columns exist

try:
    url = f"{SUPABASE_URL}/rest/v1/consumos_suministros?select=*&limit=0"
    response = requests.get(url, headers=headers)

    print(f"\n✓ Table schema check:")
    if response.status_code == 200:
        # Headers contain column info
        print(f"  Status: 200 OK - Table is accessible")
        print(f"  Response headers: {response.headers}")
    else:
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")

except Exception as e:
    print(f"❌ Failed: {e}")

# Alternative: Try using psycopg2 directly with password auth
print("\n" + "-"*80)
print("QUERY 2: Using PostgreSQL Direct Connection")
print("-"*80)

# You need to get the actual database password, which is different from the JWT token
# For now, let's try a hacky approach via the Supabase SQL interface

print("\nℹ️  To diagnose this properly, I need to execute raw SQL on the database.")
print("   The easiest way is to run these queries directly in Supabase SQL Editor:\n")

queries = [
    ("Query 1: Columns and Defaults", """
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
"""),
    ("Query 2: CHECK Constraints", """
SELECT
  constraint_name,
  constraint_type,
  check_clause
FROM information_schema.table_constraints
WHERE table_name = 'consumos_suministros'
AND constraint_type = 'CHECK';
"""),
    ("Query 3: Full Constraint Definitions", """
SELECT
  con.conname AS constraint_name,
  pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_constraint con
JOIN pg_class rel ON con.conrelid = rel.oid
JOIN pg_namespace nsp ON rel.relnamespace = nsp.oid
WHERE rel.relname = 'consumos_suministros'
AND nsp.nspname = 'public';
""")
]

for title, query in queries:
    print(f"\n{'='*80}")
    print(title)
    print('='*80)
    print(query.strip())
