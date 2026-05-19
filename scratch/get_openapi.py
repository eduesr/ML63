import requests
import json

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

headers = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
}

print("--- FETCHING EXPOSED SUPABASE TABLES ---")
try:
    response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
    if response.status_code == 200:
        schema = response.json()
        paths = schema.get("paths", {})
        tables = []
        for path in paths.keys():
            if path.startswith("/"):
                name = path[1:]
                if name and "/" not in name:
                    tables.append(name)
        print("Exposed tables and endpoints:")
        for t in sorted(set(tables)):
            print(f"- {t}")
    else:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Failed to query: {e}")
