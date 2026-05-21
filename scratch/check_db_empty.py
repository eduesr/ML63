import urllib.request
import json

supabase_url = 'https://byqtsuskdbgwpyvyiprc.supabase.co'
supabase_key = 'sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx'

def query_supabase(endpoint):
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/{endpoint}",
        headers={
            'apikey': supabase_key,
            'Authorization': f"Bearer {supabase_key}",
            'Content-Type': 'application/json'
        }
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

if __name__ == "__main__":
    try:
        print("Checking first 5 movements in database...")
        moves = query_supabase("proyectos?limit=5")
        print(f"Result count: {len(moves)}")
        for m in moves:
            print(m)
    except Exception as e:
        print(f"Error: {e}")
