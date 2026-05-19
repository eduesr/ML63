from supabase import create_client, Client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✓ Connected to Supabase")
    
    # Try to fetch user_roles
    response = supabase.table('user_roles').select('*').execute()
    print(f"✓ user_roles returned {len(response.data)} records:")
    for row in response.data:
        print(f"  - {row}")
except Exception as e:
    print(f"❌ Failed to fetch user_roles: {e}")
