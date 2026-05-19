import sys
from supabase import create_client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Connected to Supabase")
    
    # 1. Check consumos_suministros
    res_cs = supabase.table('consumos_suministros').select('*').limit(5).execute()
    print(f"\n--- consumos_suministros (sample of 5) ---")
    print(f"Total returned: {len(res_cs.data)}")
    for r in res_cs.data:
        print(r)
        
    # 2. Check proyectos
    res_pr = supabase.table('proyectos').select('*').limit(5).execute()
    print(f"\n--- proyectos (sample of 5) ---")
    print(f"Total returned: {len(res_pr.data)}")
    for r in res_pr.data:
        print(r)
        
    # 3. Check movimientos
    res_mv = supabase.table('movimientos').select('*').limit(5).execute()
    print(f"\n--- movimientos (sample of 5) ---")
    print(f"Total returned: {len(res_mv.data)}")
    for r in res_mv.data:
        print(r)

except Exception as e:
    print(f"Error checking database contents: {e}")
