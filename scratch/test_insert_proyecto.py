import requests
import json

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Test project record matching exact columns
record = {
    "nombre": "Test Project 123",
    "año": "2026",
    "cat": "pendiente",
    "pres": -1000.0,
    "progreso": 0.0,
    "obs": "Test project insert under anon key",
    "banco_ref": None
}

try:
    response = requests.post(f"{SUPABASE_URL}/rest/v1/proyectos", headers=headers, json=record)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Error: {e}")
