import requests

url = "https://byqtsuskdbgwpyvyiprc.supabase.co/rest/v1/movimientos"
headers = {
    "apikey": "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
    "Authorization": "Bearer sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
}

# Fetch top 10 movements ordered by fecha descending, and id/created_at descending if possible
params = {
    "order": "fecha.desc",
    "limit": "15"
}

res = requests.get(url, headers=headers, params=params)
if res.status_code == 200:
    data = res.json()
    print(f"Top {len(data)} movimientos más recientes en Supabase:")
    print("-" * 80)
    for row in data:
        print(f"{row.get('fecha')} | {row.get('concepto')} | {row.get('importe')}€ | Saldo: {row.get('saldo')}€")
    print("-" * 80)
else:
    print("Error:", res.status_code, res.text)
