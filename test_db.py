import urllib.request, json, ssl

url = 'https://byqtsuskdbgwpyvyiprc.supabase.co'
key = 'sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx'

req = urllib.request.Request(f"{url}/rest/v1/movimientos?select=fecha,concepto,importe,saldo&order=fecha.desc&limit=10", headers={
    'apikey': key,
    'Authorization': f'Bearer {key}'
})
ctx = ssl._create_unverified_context()
with urllib.request.urlopen(req, context=ctx) as res:
    print(json.dumps(json.loads(res.read().decode()), indent=2))
