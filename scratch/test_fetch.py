#!/usr/bin/env python3
from supabase import create_client, Client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

def test_all_tables():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    tables = ['proyectos', 'movimientos', 'user_roles', 'session_log', 'documentos', 'consumos_suministros']
    for t in tables:
        try:
            res = supabase.table(t).select('*', count='exact').limit(2).execute()
            print(f"Table '{t}': status=OK, count={res.count}, sample={res.data}")
        except Exception as e:
            print(f"Table '{t}': error={e}")

if __name__ == '__main__':
    test_all_tables()
