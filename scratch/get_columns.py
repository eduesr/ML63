import requests
import json

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

try:
    # Query the table directly via REST API with a simple select
    response = requests.get(f"{SUPABASE_URL}/rest/v1/consumos_suministros?select=*", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Connected successfully. Number of records: {len(data)}")
        if len(data) > 0:
            print("Columns available:")
            for k in data[0].keys():
                print(f"  - {k}: {data[0][k]}")
            print("\nSample records:")
            for i, r in enumerate(data[:5]):
                print(f"  Record {i+1}: {r}")
        else:
            print("Table has 0 records.")
    else:
        print(f"❌ Failed to query REST: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
