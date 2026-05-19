import requests

url = "https://byqtsuskdbgwpyvyiprc.supabase.co/rest/v1/user_roles"
headers = {
    "apikey": "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx",
    "Authorization": "Bearer sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"
}

res = requests.get(url, headers=headers)
print("Status Code:", res.status_code)
print("Response Text:", res.text)
