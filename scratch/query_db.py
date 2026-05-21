import urllib.request
import json

supabase_url = 'https://byqtsuskdbgwpyvyiprc.supabase.co'
supabase_key = 'sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx'

def query_supabase(endpoint):
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/{endpoint}",
        headers={
            'apikey': supabase_key,
            'Authorization': f"Bearer {supabase_key}",
            'Content-Type': 'application/json'
        }
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

if __name__ == "__main__":
    try:
        print("Fetching live MJM movements...")
        mjm_moves = query_supabase("movimientos?concepto=ilike.*mjm*&order=fecha.asc")
        print(f"\nFound {len(mjm_moves)} MJM movements in live database:")
        for m in mjm_moves:
            print(f"  - Date: {m.get('fecha')} | Concept: {m.get('concepto')} | Amount: {m.get('importe')}€ | Balance: {m.get('saldo')}€")

        print("\nFetching live PEDRO / SIMON / NOMINA movements (from 2024-09-01 to 2025-04-30)...")
        # Query for all payroll or porter-related entries
        endpoint = "movimientos?fecha=gte.2024-09-01&fecha=lte.2025-04-30&or=(concepto.ilike.*simon*,concepto.ilike.*nomina*,concepto.ilike.*girones*)&order=fecha.asc"
        pedro_moves = query_supabase(endpoint)
        print(f"\nFound {len(pedro_moves)} porter-related movements in live database:")
        for m in pedro_moves:
            print(f"  - Date: {m.get('fecha')} | Concept: {m.get('concepto')} | Amount: {m.get('importe')}€ | Balance: {m.get('saldo')}€")

    except Exception as e:
        print(f"Error querying database: {e}")
