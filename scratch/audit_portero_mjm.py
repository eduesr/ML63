import requests
import json

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

headers = {
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "apikey": SUPABASE_ANON_KEY,
    "Content-Type": "application/json"
}

# 1. First test connection and get count
url = f"{SUPABASE_URL}/rest/v1/movimientos?select=count"
print("Testing REST API connection to 'movimientos'...")
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")

# 2. Test 'proyectos' count
url_proj = f"{SUPABASE_URL}/rest/v1/proyectos?select=count"
print("\nTesting REST API connection to 'proyectos'...")
response_proj = requests.get(url_proj, headers=headers)
print(f"Status: {response_proj.status_code}")
print(f"Body: {response_proj.text}")

# 3. Try to select a single record from 'movimientos' to see columns
url_single = f"{SUPABASE_URL}/rest/v1/movimientos?select=*&limit=1"
print("\nQuerying 1 record from 'movimientos'...")
response_single = requests.get(url_single, headers=headers)
print(f"Status: {response_single.status_code}")
print(f"Body: {response_single.text}")
