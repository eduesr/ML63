import requests

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

record = {
    "fecha_inicio": "2026-05-01",
    "fecha_fin": "2026-05-15",
    "consumo_kwh": 100,
    "tipo_suministro": "gas",
    "proveedor": "Test Fake",
    "numero_factura": "TEST_FAKE_001",
    "consumo_valido": True,
    "validacion_notas": "Testing fake column",
    "completely_fake_column_abc": "fake"
}

try:
    response = requests.post(f"{SUPABASE_URL}/rest/v1/consumos_suministros", headers=headers, json=record)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Error: {e}")
