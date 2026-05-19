import requests

url = "https://byqtsuskdbgwpyvyiprc.supabase.co/rest/v1/proyectos"
headers = {
    "apikey": "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
    "Authorization": "Bearer sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"
}

res = requests.get(url, headers=headers)
print("Status Code:", res.status_code)
print("Headers:", dict(res.headers))
print("Response Text:", res.text)
