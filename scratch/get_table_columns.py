import requests
import json

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

try:
    # Send OPTIONS request to the table endpoint
    response = requests.options(f"{SUPABASE_URL}/rest/v1/consumos_suministros", headers=headers)
    print(f"Status Code: {response.status_code}")
    print("\nHeaders:")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")
    
    # Check if there is a response body with schema
    if response.text:
        print("\nResponse Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
except Exception as e:
    print(f"Error: {e}")
