import requests

url = "https://byqtsuskdbgwpyvyiprc.supabase.co/rest/v1/proyectos?id=eq.9dff4e15-ca6a-8535-9dff-4e15ca6a8535"
headers = {
    "apikey": "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
    "Authorization": "Bearer sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Try updating 'orden'
print("--- Test 1: Updating 'orden' ---")
res = requests.patch(url, headers=headers, json={"orden": 1})
print("Status Code:", res.status_code)
print("Response Text:", res.text)

# Try updating 'cat' only
print("\n--- Test 2: Updating 'cat' only ---")
res2 = requests.patch(url, headers=headers, json={"cat": "pendiente"})
print("Status Code:", res2.status_code)
print("Response Text:", res2.text)
