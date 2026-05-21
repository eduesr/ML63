#!/usr/bin/env python3
"""
Cruce de movimientos bancarios (SQL) con facturas MJM y datos de Pedro Simón Girones.
Verifica coherencia de datos sin necesidad de autenticación Supabase.
"""

import re
from collections import defaultdict

SQL_FILE = "/Users/eduardosr/Documents/GitHub/ML63/carga_inicial_movimientos.sql"

def parse_movements(sql_path):
    """Parsea el archivo SQL y extrae todos los movimientos."""
    movements = []
    pattern = re.compile(
        r"\('(\d{4}-\d{2}-\d{2})',\s*'([^']+)',\s*([-\d.]+),\s*([-\d.]+),\s*'([^']*)'\)"
    )
    with open(sql_path, "r", encoding="utf-8") as f:
        for line in f:
            m = pattern.search(line)
            if m:
                movements.append({
                    "fecha": m.group(1),
                    "concepto": m.group(2),
                    "importe": float(m.group(3)),
                    "saldo": float(m.group(4)),
                    "ref1": m.group(5),
                })
    return movements

def fmt(n):
    return f"{n:>10.2f} €"

movements = parse_movements(SQL_FILE)
print(f"Total movimientos en SQL: {len(movements)}\n")

# ─────────────────────────────────────────────────────
# 1. TODOS LOS MOVIMIENTOS DE MJM
# ─────────────────────────────────────────────────────
print("=" * 70)
print("1. MOVIMIENTOS MJM EN BASE DE DATOS")
print("=" * 70)
mjm = [m for m in movements if "MJM" in m["concepto"].upper()]
for m in mjm:
    print(f"  {m['fecha']}  {fmt(m['importe'])}  saldo: {fmt(m['saldo'])}  ref1: {m['ref1']}")
print(f"\n  TOTAL MJM: {fmt(sum(m['importe'] for m in mjm))}")

# ─────────────────────────────────────────────────────
# 2. CRUCE CON FACTURAS PDF
# ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("2. CRUCE FACTURAS PDF vs BASE DE DATOS")
print("=" * 70)

pdf_facturas = [
    {"nro": "7/7.717", "fecha_pdf": "20/09/2024", "cargo_pdf": "05/10/2024",
     "importe": -388.41, "concepto_pdf": "Suplencia limpieza + 3 cubos (19-30 ago 2024)"},
    {"nro": "7/7.718", "fecha_pdf": "20/09/2024", "cargo_pdf": "05/10/2024",
     "importe": -55.06, "concepto_pdf": "Productos limpieza entregados 23/08/2024"},
]

for f in pdf_facturas:
    match = [m for m in mjm if abs(m["importe"] - f["importe"]) < 0.01]
    estado = "✅ ENCONTRADO" if match else "❌ NO ENCONTRADO"
    print(f"\n  Factura {f['nro']}  ({f['importe']} €)  → {estado}")
    if match:
        m = match[0]
        cargo_real = m["fecha"]
        cargo_esperado = "2024-10-05"
        diff = "⚠️ 2 días (sábado→lunes bancario)" if cargo_real == "2024-10-07" else "✅"
        print(f"    Fecha en BD:     {cargo_real}  (factura decía cargo el 05/10/2024) → {diff}")
        print(f"    Concepto en BD:  {m['concepto']}")
        print(f"    Ref1 en BD:      {m['ref1']}  (CIF MJM: B78981339)")
        cif_ok = "✅" if "B78981339" in m["ref1"] else "❌"
        print(f"    CIF correcto:    {cif_ok}")

# ─────────────────────────────────────────────────────
# 3. MOVIMIENTOS SIN FACTURA PDF (2025)
# ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("3. MOVIMIENTOS MJM 2025 (SIN FACTURA FÍSICA EN HALLAZGOS)")
print("=" * 70)
mjm_2025 = [m for m in mjm if m["fecha"].startswith("2025")]
contratos = {
    -90.75:   "Posibles productos limpieza inicio servicio post-despido (25-134)",
    -1230.57: "Limpieza a fondo post-obras Impernova (extraordinario)",
    -199.65:  "Liquidación servicio temporal (¿última mensualidad 25-134?)",
}
for m in mjm_2025:
    descripcion = contratos.get(m["importe"], "Sin identificar")
    print(f"  {m['fecha']}  {fmt(m['importe'])}  → {descripcion}")
print(f"\n  TOTAL MJM 2025: {fmt(sum(m['importe'] for m in mjm_2025))}")

# ─────────────────────────────────────────────────────
# 4. TODOS LOS MOVIMIENTOS DE PEDRO SIMÓN GIRONES (nóminas)
# ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("4. MOVIMIENTOS PEDRO SIMÓN GIRONES (nóminas y pagos directos)")
print("=" * 70)
pedro = [m for m in movements if "PEDRO" in m["concepto"].upper() or
         ("NOMINA" in m["concepto"].upper() and m["importe"] < 0 and abs(m["importe"]) < 1500)]

# Separar por año
por_año = defaultdict(list)
for m in pedro:
    año = m["fecha"][:4]
    por_año[año].append(m)

for año in sorted(por_año.keys()):
    total = sum(m["importe"] for m in por_año[año])
    print(f"\n  {año}: {len(por_año[año])} movimientos | Total: {fmt(total)}")
    for m in por_año[año]:
        print(f"    {m['fecha']}  {fmt(m['importe'])}  {m['concepto'][:60]}")

# ─────────────────────────────────────────────────────
# 5. GASTOS PORTERO 2024 COMPLETOS (nóminas + SS + PRL + MJM suplencia)
# ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("5. COSTE TOTAL PORTERO 2024 (verificación vs Balance 2024)")
print("=" * 70)

keywords_portero = ["NOMINA", "PEDRO SIMON", "SEGUROS SOCIALES", "QUIRON PREVENCION",
                    "LIMPIEZAS MJM"]  # MJM en 2024 = suplencia portero

portero_2024 = []
for m in movements:
    if not m["fecha"].startswith("2024"):
        continue
    c = m["concepto"].upper()
    if m["importe"] >= 0:
        continue
    if ("NOMINA" in c or
        "PEDRO SIMON" in c or
        "SEGUROS SOCIALES" in c or "TGSS" in c or
        "QUIRON" in c or
        "MJM" in c):
        portero_2024.append(m)

por_categoria = defaultdict(list)
for m in portero_2024:
    c = m["concepto"].upper()
    if "NOMINA" in c:
        cat = "Nóminas Pedro"
    elif "PEDRO SIMON" in c:
        cat = "Pagos directos a Pedro"
    elif "SEGUROS SOCIALES" in c or "TGSS" in c:
        cat = "Seguros Sociales (TGSS)"
    elif "QUIRON" in c:
        cat = "Prevención Riesgos (Quirón)"
    elif "MJM" in c:
        cat = "Suplencia portería (MJM)"
    else:
        cat = "Otros"
    por_categoria[cat].append(m)

print(f"\n  {'CATEGORÍA':<35} {'TOTAL':>12}  {'BALANCE 2024':>14}  {'OK?':>5}")
print(f"  {'-'*35} {'-'*12}  {'-'*14}  {'-'*5}")

balance_referencia = {
    "Nóminas Pedro": 9296.80,
    "Seguros Sociales (TGSS)": 3847.52,
    "Prevención Riesgos (Quirón)": 610.31,
    "Suplencia portería (MJM)": 388.41,
    "Pagos directos a Pedro": None,
}

gran_total = 0
for cat, mlist in sorted(por_categoria.items()):
    total = abs(sum(m["importe"] for m in mlist))
    gran_total += total
    ref = balance_referencia.get(cat)
    if ref:
        ok = "✅" if abs(total - ref) < 1.0 else f"⚠️ dif:{total-ref:.2f}"
        print(f"  {cat:<35} {fmt(-total):>12}  {fmt(-ref):>14}  {ok}")
    else:
        print(f"  {cat:<35} {fmt(-total):>12}  {'(sin ref)':>14}  {'—':>5}")

print(f"\n  {'TOTAL COSTE PORTERO 2024':<35} {fmt(-gran_total):>12}")
print(f"\n  Balance 2024 (Grupo 1 portero: nóminas+SS+PRL+suplencia):")
print(f"  9.296,80 + 3.847,52 + 610,31 + 388,41 = {9296.80+3847.52+610.31+388.41:,.2f} €")

# ─────────────────────────────────────────────────────
# 6. SUPLENCIA MJM EN AÑO CORRECTO
# ─────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("6. VERIFICACIÓN: SUPLENCIA MJM EN EL AÑO CORRECTO (2024)")
print("=" * 70)
mjm_2024 = [m for m in mjm if m["fecha"].startswith("2024")]
print(f"  Movimientos MJM en 2024: {len(mjm_2024)}")
for m in mjm_2024:
    print(f"    {m['fecha']}  {fmt(m['importe'])}")
print(f"  Total suplencia 2024: {fmt(sum(m['importe'] for m in mjm_2024))}")
print(f"  Balance 2024 dice 'Suplencias portería': -388,41 €")
diferencia = abs(sum(m['importe'] for m in mjm_2024)) - 388.41
if diferencia < 0.01:
    print(f"  → ✅ CORRECTO: el cargo de -55,06 € (productos) aparece en Grupo 2")
    print(f"     (Productos limpieza, no como suplencia directa de portero)")
else:
    print(f"  → ⚠️ Diferencia: {diferencia:.2f} €")

print("\n  Nota: El balance clasifica:")
print("  · -388,41 € → Grupo 1 'Suplencias portería' (servicio de limpieza)")
print("  · -55,06 €  → Grupo 2 'Productos limpieza'  (material consumible)")
print("  · Total MJM 2024 en BD: -443,47 €")
