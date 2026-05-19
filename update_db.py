import getpass
import sys
from supabase import create_client, Client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

def main():
    print("\n" + "="*60)
    print("ACTUALIZACIÓN BASE DE DATOS SUPABASE (ML63)")
    print("="*60)
    print("\nEste script actualizará automáticamente los proyectos en la base de datos.")
    
    email = input("\nIntroduce tu email de Supabase [eduesr@gmail.com]: ").strip()
    if not email:
        email = "eduesr@gmail.com"
        
    password = getpass.getpass("Introduce tu contraseña de Supabase: ")
    if not password:
        print("❌ La contraseña no puede estar vacía.")
        sys.exit(1)

    print(f"\nConectando con Supabase e iniciando sesión como {email}...")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Sign in to get user session (JWT token) which bypasses RLS
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        print("✓ Sesión iniciada con éxito.")
    except Exception as e:
        print(f"❌ Error al iniciar sesión: {e}")
        print("Verifica que tu email y contraseña sean correctos.")
        sys.exit(1)

    # 1. Update Tuberías agua · Proyecto grande
    print("\n1. Buscando y actualizando 'Tuberías agua · Proyecto grande'...")
    try:
        # Check if the project already exists
        check_pirtac = supabase.table('proyectos').select('*').eq('nombre', 'Tuberías agua · Proyecto grande').eq('año', '2026').execute()
        
        pirtac_data = {
            "año": "2026",
            "cat": "progreso",
            "nombre": "Tuberías agua · Proyecto grande",
            "pres": -12700.00,
            "progreso": 0.25,
            "obs": "Proveedor: A. Pirtac. Presupuesto de Cliente nº 0001-000034 (12.700,00€ sin IVA, 13.970,00€ con 10% IVA = 13.970,00€). Factura y conciliación bancaria pendientes.",
            "banco_ref": None
        }
        
        if check_pirtac.data:
            # Update existing
            print("   -> El proyecto ya existe. Actualizando presupuesto y observaciones...")
            res = supabase.table('proyectos').update({
                "pres": pirtac_data["pres"],
                "obs": pirtac_data["obs"],
                "banco_ref": None
            }).eq('nombre', 'Tuberías agua · Proyecto grande').eq('año', '2026').execute()
            print("   ✓ Proyecto 'Tuberías agua · Proyecto grande' actualizado en la DB.")
        else:
            # Insert new
            print("   -> El proyecto no existe. Creando nuevo registro...")
            res = supabase.table('proyectos').insert(pirtac_data).execute()
            print("   ✓ Proyecto 'Tuberías agua · Proyecto grande' creado en la DB.")
    except Exception as e:
        print(f"   ❌ Error al procesar proyecto de tuberías: {e}")

    # 2. Update Sellado y limpieza ventanal
    print("\n2. Buscando y actualizando 'Sellado y limpieza ventanal' (Navacon sustituye a Pinta Limpio)...")
    try:
        # Check if "Pinta Limpio" card exists to rename it
        check_old = supabase.table('proyectos').select('*').eq('nombre', 'Sellado y limpieza ventanal · Pinta Limpio').eq('año', '2026').execute()
        
        navacon_data = {
            "año": "2026",
            "cat": "pendiente",
            "nombre": "Sellado y limpieza ventanal · Navacon Vertical",
            "pres": -3051.00,
            "progreso": 0.00,
            "obs": "Proveedor: Navacon Vertical (sustituye a Pinta Limpio). Presupuesto nuevo PTTO090A-2026 (3.051,00€ sin IVA, 3.356,10€ con 10% IVA). Factura y conciliación bancaria pendientes.",
            "banco_ref": None
        }
        
        if check_old.data:
            print("   -> Se encontró el proyecto antiguo 'Sellado y limpieza ventanal · Pinta Limpio'. Renombrando y actualizando...")
            res = supabase.table('proyectos').update(navacon_data).eq('nombre', 'Sellado y limpieza ventanal · Pinta Limpio').eq('año', '2026').execute()
            print("   ✓ Proyecto renombrado y actualizado a 'Sellado y limpieza ventanal · Navacon Vertical'.")
        else:
            # Check if Navacon Vertical already exists to update it
            check_new = supabase.table('proyectos').select('*').eq('nombre', 'Sellado y limpieza ventanal · Navacon Vertical').eq('año', '2026').execute()
            if check_new.data:
                print("   -> El proyecto 'Sellado y limpieza ventanal · Navacon Vertical' ya existe. Actualizando datos...")
                res = supabase.table('proyectos').update({
                    "pres": navacon_data["pres"],
                    "obs": navacon_data["obs"],
                    "banco_ref": None
                }).eq('nombre', 'Sellado y limpieza ventanal · Navacon Vertical').eq('año', '2026').execute()
                print("   ✓ Datos de Navacon Vertical actualizados en la DB.")
            else:
                # Also search for "Sellado y limpieza ventanal con descuelgue" to update/rename
                check_descuelgue = supabase.table('proyectos').select('*').eq('nombre', 'Sellado y limpieza ventanal con descuelgue').eq('año', '2026').execute()
                if check_descuelgue.data:
                    print("   -> Se encontró el proyecto 'Sellado y limpieza ventanal con descuelgue'. Actualizando y renombrando...")
                    res = supabase.table('proyectos').update(navacon_data).eq('nombre', 'Sellado y limpieza ventanal con descuelgue').eq('año', '2026').execute()
                    print("   ✓ Proyecto actualizado y renombrado.")
                else:
                    print("   -> No se encontró ningún proyecto existente. Creando nuevo registro para Navacon Vertical...")
                    res = supabase.table('proyectos').insert(navacon_data).execute()
                    print("   ✓ Proyecto 'Sellado y limpieza ventanal · Navacon Vertical' creado en la DB.")
    except Exception as e:
        print(f"   ❌ Error al procesar proyecto de ventanal: {e}")

    print("\n" + "="*60)
    print("PROCESO TERMINADO. Abre o refresca ML63.html en tu navegador.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
