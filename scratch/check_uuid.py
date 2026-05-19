import sys
from supabase import create_client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    res = supabase.table('proyectos').select('id, nombre, año').execute()
    print("--- Proyectos IDs and Names ---")
    for r in res.data:
        print(f"ID: {r['id']} | Name: {r['nombre']} | Year: {r['año']}")
except Exception as e:
    print(f"Error: {e}")
