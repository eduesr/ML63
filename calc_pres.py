import re

moves = []
with open('carga_inicial_movimientos.sql', 'r') as f:
    for line in f:
        match = re.search(r"\('([^']+)',\s*'([^']+)',\s*([^,]+),\s*([^,]+),\s*'([^']+)'\)", line)
        if match:
            moves.append({
                '_iso': match.group(1),
                'concepto': match.group(2),
                'importe': float(match.group(3))
            })

def is_recurring(concepto):
    c = concepto.upper()
    keywords = [
        'NATURGY', 'IBERDROLA', 'CURENERGIA', 'GAS POWER', 'MADRID DISTRIBUCION',
        'CANAL ISABEL', 'ISTA', 'TECHEM',
        'MJM', 'LIMPIEZA', 'PILAR', 'PREVENT', 'VANESSA',
        'ALFREDO SANCHEZ', 'FINCAS', 'HONORARIOS', 'ADMINISTRACION',
        'NOMINA', 'TGSS', 'SEGURIDAD SOCIAL', 'IRPF', 'MUTUA', 'QUIRON', 'PREVENCION',
        'COMISION', 'INTERES', 'IVA SOBRE', 'LIQUIDACION', 'MANTENIMIENTO DE CUENTA',
        'SEGURO', 'ALLIANZ', 'MAPFRE', 'CASER', 'OCASO',
        'LASSER', 'PRISMA', 'MULTISERVICIOS', 'EXTINTOR', 'IBEREXT', 'RIESGOS', 'LOPD', 'PROTECCION DATOS',
        'ASCENSOR', 'ORONA', 'THYSSEN', 'SCHINDLER', 'FAIN',
        'RECIBO', 'CUOTA', 'DEVOLUCION', 'REMESAS', 'TALONARIO', 'PROVISION'
    ]
    return any(k in c for k in keywords)

completed_projects = []
for m in moves:
    if m['importe'] >= 0: continue
    if m['importe'] > -50: continue
    if is_recurring(m['concepto']): continue
    year = int(m['_iso'].split('-')[0])
    if year >= 2025: continue
    
    completed_projects.append({
        'pres': abs(m['importe']),
        '_iso': m['_iso']
    })

with open('ML63.html', 'r') as f:
    html = f.read()

data_match = re.search(r'const DATA = (\{.*?\});', html, re.DOTALL)
if data_match:
    data_str = data_match.group(1)
    # Match pres: <value> for completado objects
    # This might be tricky if formatting varies, let's just grab everything with 'cat': 'completado'
    blocks = re.split(r"\{", data_str)
    for block in blocks:
        if "'completado'" in block or '"completado"' in block:
            pres_match = re.search(r'pres\s*:\s*(-?[\d.]+)', block)
            if pres_match:
                completed_projects.append({
                    'pres': abs(float(pres_match.group(1))),
                    '_iso': '2025-01-01'
                })

total_inv = sum(p['pres'] for p in completed_projects)
total_pres = sum(p['pres'] for p in completed_projects if p['_iso'] >= '2022-03-28')

print('Total:', total_inv)
print('Desde presidencia:', total_pres)
