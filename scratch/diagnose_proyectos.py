import requests

url = "https://byqtsuskdbgwpyvyiprc.supabase.co/rest/v1/"
headers = {
    "apikey": "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
    "Authorization": "Bearer sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
    "Accept": "application/openapi+json"
}

try:
    res = requests.get(url, headers=headers)
    print("Status Code:", res.status_code)
    if res.status_code == 200:
        schema = res.json()
        definitions = schema.get('definitions', {})
        proyectos = definitions.get('proyectos', {})
        properties = proyectos.get('properties', {})
        print("\n--- Column Definitions for proyectos ---")
        for col, col_info in sorted(properties.items()):
            print(f"  • {col:15s} : {col_info.get('type'):10s} ({col_info.get('format', 'no format')})")
    else:
        print("Error:", res.text)
except Exception as e:
    print("Error:", e)
