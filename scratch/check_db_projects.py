import requests
import json

url = "https://byqtsuskdbgwpyvyiprc.supabase.co/rest/v1/proyectos"
headers = {
    "apikey": "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
    "Authorization": "Bearer sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"
}

# Fetch all projects
res = requests.get(url, headers=headers)
if res.status_code == 200:
    projects = res.json()
    print(f"Successfully fetched {len(projects)} projects:")
    for p in sorted(projects, key=lambda x: (x.get('año', ''), x.get('nombre', ''))):
        print(f"ID: {p.get('id')} | Año: {p.get('año')} | Cat: {p.get('cat')} | Nombre: {p.get('nombre')} | Pres: {p.get('pres')} | Estado: {p.get('estado')} | Notas: {p.get('notas')}")
else:
    print("Error fetching projects:", res.status_code, res.text)
