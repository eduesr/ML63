import os
import sys
from supabase import create_client, Client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("Connected to Supabase.")
        
        # Query movements matching 'PILAR'
        res = supabase.table('movimientos').select('*').ilike('concepto', '%PILAR%').execute()
        data = res.data
        print(f"Found {len(data)} movements for 'PILAR' in database:")
        for idx, m in enumerate(sorted(data, key=lambda x: x.get('fecha', ''))):
            print(f"{idx+1}. Fecha: {m.get('fecha')} | Concepto: {m.get('concepto')} | Importe: {m.get('importe')} | Saldo: {m.get('saldo')}")
            
    except Exception as e:
        print(f"Error querying Supabase: {e}")

if __name__ == '__main__':
    main()
