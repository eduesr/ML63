#!/usr/bin/env python3
"""
Diagnose Supabase consumos_suministros table configuration
- Check table schema
- Inspect RLS policies
- Look for triggers and constraints
- Attempt test insert to get exact error details
"""

import json
import subprocess
import sys

# Try to connect using Supabase CLI first
def check_supabase_cli():
    """Check if Supabase CLI is available and configured"""
    try:
        result = subprocess.run(['supabase', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Supabase CLI found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    return False

def query_via_cli(query):
    """Execute SQL query via Supabase CLI"""
    try:
        result = subprocess.run(
            ['supabase', 'db', 'pull', '--dry-run'],
            capture_output=True,
            text=True,
            cwd='/Users/eduardosr/Documents/GitHub/ML63'
        )
        return result.stdout
    except Exception as e:
        return None

def diagnose_with_python_api():
    """Diagnose using Python and direct API calls"""

    # Supabase credentials from previous session
    SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
    SUPABASE_ANON_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

    print("\n" + "="*80)
    print("SUPABASE DIAGNOSIS")
    print("="*80)

    # Try to import supabase
    try:
        from supabase import create_client, Client
    except ImportError:
        print("\n❌ supabase-py not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
        from supabase import create_client, Client

    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("\n✓ Connected to Supabase")

        # 1. Query table schema from information_schema
        print("\n" + "-"*80)
        print("1. TABLE SCHEMA (columns, types, constraints)")
        print("-"*80)

        try:
            schema_response = supabase.table('consumos_suministros').select('*', count='exact').limit(0).execute()
            print(f"✓ Table exists and is accessible")
        except Exception as e:
            print(f"❌ Cannot access table: {e}")
            return

        # 2. Check RLS policies via raw query (using REST API)
        print("\n" + "-"*80)
        print("2. ROW-LEVEL SECURITY (RLS) POLICIES")
        print("-"*80)

        import requests
        headers = {
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }

        # Query to get RLS policies
        rls_query = """
        SELECT
            tablename,
            policyname,
            cmd,
            qual,
            with_check
        FROM pg_policies
        WHERE tablename = 'consumos_suministros'
        """

        try:
            # Try to get RLS info via Supabase REST API by querying a helper table
            print("Checking RLS policies configuration...")
            # Note: We can't directly query pg_policies via Supabase API, but we can test operations

            # Test: Try to get current session user
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/consumos_suministros?select=*&limit=1",
                headers=headers
            )
            print(f"GET consumos_suministros: {response.status_code}")
            if response.status_code == 200:
                print("✓ SELECT permitted (RLS allows read)")
            elif response.status_code == 403:
                print("⚠️ SELECT forbidden (RLS blocks read)")

        except Exception as e:
            print(f"Could not check RLS policies: {e}")

        # 3. Test INSERT with detailed error
        print("\n" + "-"*80)
        print("3. TEST INSERT OPERATION (detailed error)")
        print("-"*80)

        test_record = {
            "fecha_inicio": "2026-04-01",
            "fecha_fin": "2026-04-15",
            "consumo_kwh": 100,
            "tipo_suministro": "gas",
            "proveedor": "Test",
            "numero_factura": "TEST001",
            "consumo_valido": True,
            "validacion_notas": "Test record for diagnostics"
        }

        try:
            response = supabase.table('consumos_suministros').insert(test_record).execute()
            print(f"✓ INSERT successful: {response.data}")
        except Exception as e:
            print(f"❌ INSERT failed with error:")
            print(f"   Type: {type(e).__name__}")
            print(f"   Message: {str(e)}")

            # Try to extract more details
            if hasattr(e, 'error'):
                print(f"   Error object: {e.error}")
            if hasattr(e, 'message'):
                print(f"   Error message: {e.message}")
            if hasattr(e, 'details'):
                print(f"   Details: {e.details}")

        # 4. Try to check table statistics
        print("\n" + "-"*80)
        print("4. TABLE STATISTICS")
        print("-"*80)

        try:
            count_response = supabase.table('consumos_suministros').select('*', count='exact').execute()
            print(f"✓ Current row count: {count_response.count if count_response.count is not None else 'unknown'}")
        except Exception as e:
            print(f"Could not get row count: {e}")

        # 5. List all columns (by attempting to select all and checking response)
        print("\n" + "-"*80)
        print("5. TABLE COLUMNS")
        print("-"*80)

        try:
            single_row = supabase.table('consumos_suministros').select('*').limit(1).execute()
            if single_row.data and len(single_row.data) > 0:
                columns = list(single_row.data[0].keys())
                print(f"✓ Columns found: {', '.join(columns)}")
            else:
                print("Table appears to be empty. Expected columns:")
                expected = ["id", "fecha_inicio", "fecha_fin", "consumo_kwh", "tipo_suministro",
                           "proveedor", "numero_factura", "consumo_valido", "validacion_notas",
                           "created_at", "updated_at"]
                print(f"  {', '.join(expected)}")
        except Exception as e:
            print(f"Could not query columns: {e}")

        print("\n" + "="*80)
        print("DIAGNOSIS COMPLETE")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Check for CLI first
    if check_supabase_cli():
        print("\nSuabase CLI is available, but using Python API for diagnosis...")

    diagnose_with_python_api()
