#!/usr/bin/env python3
"""
Import validated consumption records to Supabase consumos_suministros table
Version 2: Enhanced error handling and RLS workarounds
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, List

try:
    from supabase import create_client, Client
except ImportError:
    print("Installing supabase-py...")
    import subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client, Client

# Load validated data
DATA_FILE = Path('/Users/eduardosr/Documents/GitHub/ML63/supabase_import_cleaned.json')

def load_data() -> List[Dict]:
    """Load JSON records"""
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def get_credentials() -> tuple[str, str, str]:
    """Get Supabase credentials"""
    print("\n" + "="*80)
    print("SUPABASE IMPORT CONFIGURATION")
    print("="*80)

    # Option 1: Use provided credentials
    print("\nOption 1: Use existing credentials")
    print("Option 2: Enter new API keys")
    choice = input("\nChoice (1 or 2): ").strip()

    if choice == "2":
        url = input("Supabase URL (https://...supabase.co): ").strip()
        key = input("API Key (anon or service_role): ").strip()
        key_type = "anon" if "anon" in input("Key type - anon (a) or service_role (s)? [a]: ").lower() else "service_role"
        return url, key, key_type
    else:
        # Default credentials from previous session (may be expired)
        return (
            "https://byqtsuskdbgwpyvyiprc.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5cXRzdXNrZGJnd3B5dmlwcmMiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTcyNDk0NDA1NywiZXhwIjoxODgyNzA0MDU3fQ.0tKOb-pMIQXB-KJ7vXLM9dYIj-HvHa9D7fHN2QA4cBg",
            "anon"
        )

def test_connection(supabase: Client) -> bool:
    """Test if we can connect and access the table"""
    try:
        response = supabase.table('consumos_suministros').select('*', count='exact').limit(0).execute()
        return True
    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        return False

def diagnose_rls(supabase: Client) -> Optional[str]:
    """Diagnose RLS issues and return suggestion"""
    print("\nDiagnosing RLS policies...")

    # Try a test insert
    test_record = {
        "fecha_inicio": "2026-04-01",
        "fecha_fin": "2026-04-15",
        "consumo_kwh": 1,
        "tipo_suministro": "gas",
        "proveedor": "RLS_TEST",
        "numero_factura": "RLS_TEST_001",
        "consumo_valido": True,
        "validacion_notas": "RLS diagnostic test"
    }

    try:
        supabase.table('consumos_suministros').insert(test_record).execute()
        print("✓ Test insert succeeded - RLS is not blocking")
        # Clean up test record
        try:
            supabase.table('consumos_suministros').delete().eq('numero_factura', 'RLS_TEST_001').execute()
        except:
            pass
        return None
    except Exception as e:
        error_msg = str(e)
        if "row-level security" in error_msg.lower() or "policy" in error_msg.lower():
            print(f"⚠️ RLS policy is blocking inserts")
            return "rls"
        elif "division" in error_msg.lower() or "22012" in error_msg:
            print(f"⚠️ Division by zero error detected")
            return "division"
        else:
            print(f"⚠️ Unknown error: {error_msg}")
            return "unknown"

def import_records(supabase: Client, records: List[Dict], disable_rls: bool = False) -> Dict:
    """Import records to Supabase"""
    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }

    if disable_rls:
        print("\n⚠️ WARNING: This requires admin access (service_role key)")
        print("Attempting to disable RLS for this operation...")

    print(f"\nImporting {len(records)} records...")
    print("-" * 80)

    for idx, record in enumerate(records, 1):
        try:
            response = supabase.table('consumos_suministros').insert(record).execute()
            results['success'] += 1
            status = "✓"
            msg = f"OK"
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'index': idx,
                'record': record['numero_factura'],
                'error': str(e)
            })
            status = "✗"
            msg = str(e)[:60]

        # Print progress
        pct = (idx / len(records)) * 100
        print(f"[{idx:2d}/{len(records)}] {status} {record['numero_factura']:20s} ({record['fecha_inicio']} → {record['fecha_fin']}) | {msg}")

        # Stop after first few failures if they're all the same issue
        if results['failed'] >= 3 and results['success'] == 0:
            print(f"\n⚠️ First 3 records failed with same issue. Stopping to investigate...")
            break

    print("-" * 80)
    print(f"\n✓ Success: {results['success']}")
    print(f"✗ Failed:  {results['failed']}")

    if results['errors']:
        print("\nFirst error details:")
        err = results['errors'][0]
        print(f"  Record: {err['record']}")
        print(f"  Error: {err['error']}")

    return results

def main():
    print("\n" + "="*80)
    print("ML63 CONSUMPTION DATA IMPORT TO SUPABASE")
    print("="*80)

    # Load data
    records = load_data()
    print(f"\nLoaded {len(records)} validated records from {DATA_FILE}")

    # Get credentials
    url, key, key_type = get_credentials()
    print(f"\nUsing {key_type} key")

    # Create client
    try:
        supabase = create_client(url, key)
    except Exception as e:
        print(f"\n❌ Failed to create Supabase client: {e}")
        sys.exit(1)

    # Test connection
    print("\nTesting connection...")
    if not test_connection(supabase):
        print("\n❌ Cannot connect to Supabase. Possible reasons:")
        print("   1. Invalid API key (may have expired)")
        print("   2. Network issues")
        print("   3. Wrong Supabase URL")
        print("\nRun again and select option 2 to enter new credentials.")
        sys.exit(1)
    print("✓ Connection successful")

    # Diagnose RLS
    rls_issue = diagnose_rls(supabase)

    if rls_issue == "rls":
        print("\n⚠️ RLS Policy Issue Detected")
        print("Options:")
        print("  1. Use service_role key instead (admin access, bypasses RLS)")
        print("  2. Continue with anon key (may fail)")
        print("  3. Exit and fix RLS in Supabase dashboard")
        choice = input("\nChoice (1-3): ").strip()
        if choice == "3":
            print("\nTo fix RLS in Supabase Dashboard:")
            print("  1. Go to Authentication → Policies")
            print("  2. Find consumos_suministros table")
            print("  3. Either disable RLS or create permissive INSERT policy")
            sys.exit(1)
        elif choice != "1":
            print("\nContinuing with current key (may fail)...")

    # Import records
    results = import_records(supabase, records)

    # Summary
    print("\n" + "="*80)
    if results['success'] == len(records):
        print(f"✅ SUCCESS: All {len(records)} records imported!")
        print("\nNext steps:")
        print("  1. Verify in Supabase Dashboard:")
        print("     Database → Tables → consumos_suministros")
        print("  2. Update ML63.html to fetch data dynamically from Supabase")
        print("  3. Update Chart.js to render real data instead of hardcoded values")
    else:
        print(f"❌ IMPORT INCOMPLETE: {results['success']}/{len(records)} imported")
        if rls_issue == "rls":
            print("\nRLS Policy is blocking inserts. To fix:")
            print("  • Supabase Dashboard → Authentication → Policies → consumos_suministros")
            print("  • Create policy: FOR INSERT WITH CHECK (true)")
            print("  • OR use service_role key instead of anon key")
        elif rls_issue == "division":
            print("\nDivision by zero error detected. Likely causes:")
            print("  • Trigger calculating with division")
            print("  • Generated column dividing by null/zero")
            print("  • DEFAULT value with division in formula")
            print("\nCheck SQL trigger definitions in Supabase SQL Editor")

    print("="*80)

if __name__ == '__main__':
    main()
