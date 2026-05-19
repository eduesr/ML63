#!/usr/bin/env python3
import json
import re
from collections import defaultdict
from supabase import create_client, Client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx"

def fetch_all_movements():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("Conectando a Supabase para descargar movimientos...")
    
    all_rows = []
    limit = 1000
    offset = 0
    
    while True:
        print(f"Descargando filas {offset} a {offset + limit}...")
        response = supabase.table('movimientos').select('*').order('fecha', desc=True).range(offset, offset + limit - 1).execute()
        data = response.data
        if not data:
            break
        all_rows.extend(data)
        if len(data) < limit:
            break
        offset += limit
        
    print(f"Total movimientos descargados: {len(all_rows)}")
    return all_rows

def clean_concept(concept):
    """Normalize and clean the concept to extract the main merchant/concept name."""
    c = concept.upper().strip()
    
    # Remove standard prefix numbers, reference numbers or codes
    c = re.sub(r'\b\d{10,}\b', '', c) # Long numbers
    
    # Check for known categories or patterns
    if "SEGUROS CAJA" in c or "CAJA DE SEGUROS" in c:
        return "CAJA DE SEGUROS REUNIDOS (CASER)"
    if "OCASO" in c:
        return "SEGUROS OCASO"
    if "CASER" in c:
        return "SEGUROS CASER"
    if "NATURGY" in c or "GAS NATURAL" in c:
        if "COMERCIALIZADORA" in c or "REGULADO" in c or "S.U.R." in c:
            return "NATURGY (GAS/LUZ)"
        return "NATURGY"
    if "IBERDROLA" in c:
        return "IBERDROLA"
    if "ENDESA" in c:
        return "ENDESA"
    if "TOTALENERGIES" in c or "TOTAL ENERGIES" in c:
        return "TOTALENERGIES"
    if "SABADELL" in c or "COMISION" in c or "COMIS.MANT." in c or "COM.MANT" in c or "LIQUIDACION" in c or "INTERESES" in c or "ADMINISTRACION" in c:
        if "RECARGO" in c:
            return "BANCO SABADELL - RECARGO/DEVOLUCION"
        return "BANCO SABADELL - COMISIONES Y GASTOS"
    if "TGSS" in c or "SEGUROS SOCIALES" in c or "TESORERIA GENERAL" in c:
        return "SEGURIDAD SOCIAL (TGSS)"
    if "HACIENDA" in c or "AEAT" in c or "MODELO" in c or "I.R.P.F." in c or "MINISTERIO DE HACIENDA" in c:
        return "HACIENDA (AEAT)"
    if "MJM" in c or "LIMPIEZAS MJM" in c:
        return "LIMPIEZAS MJM"
    if "EL PILAR" in c or "LIMPIEZAS EL PILAR" in c:
        return "LIMPIEZAS EL PILAR"
    if "PREVENT" in c or "PREVENT XXI" in c:
        return "PREVENT XXI (CONSERJERÍA/SEGURIDAD)"
    if "ALEXANDRU" in c or "PIRTAC" in c:
        return "ALEXANDRU PIRTAC (MANTENIMIENTO/OBRAS)"
    if "ISTA" in c:
        return "ISTA (REPARTIDORES/CALEFACCION)"
    if "KONE" in c or "ASCENSORES KONE" in c:
        return "KONE ASCENSORES"
    if "OTIS" in c or "ZARDOYA" in c:
        return "OTIS ASCENSORES"
    if "CANAL DE ISABEL" in c or "CYII" in c or "CANAL ISABEL II" in c:
        return "CANAL DE ISABEL II (AGUA)"
    if "TELEFONICA" in c or "MOVISTAR" in c:
        return "TELEFONICA/MOVISTAR"
    if "COMUNIDAD" in c or "RECIBO DE" in c or "CUOTA" in c:
        # Check if it is an income (positive amount) -> Community fee collection
        return "CUOTAS COMUNEROS (INGRESO)"
        
    # Return first few words or cleaned string
    words = c.split('.')
    first_part = words[0].strip()
    if len(first_part) < 5:
        if len(words) > 1:
            first_part = (first_part + " " + words[1]).strip()
    
    # Truncate to make it a generic supplier
    first_part = re.sub(r'\s+', ' ', first_part)
    # Remove dates, numbers, IBANs
    first_part = re.sub(r'ES\d{22}', '', first_part)
    first_part = re.sub(r'\b\d+\b', '', first_part)
    return first_part.strip()

def analyze_movements(movements):
    # Separate into positive (incomes) and negative (expenses)
    expenses = [m for m in movements if m['importe'] < 0]
    incomes = [m for m in movements if m['importe'] >= 0]
    
    print(f"\n--- ANÁLISIS DE GASTOS ({len(expenses)} movimientos) ---")
    
    # Group by merchant
    merchant_totals = defaultdict(float)
    merchant_counts = defaultdict(int)
    merchant_dates = defaultdict(list)
    merchant_raw_concepts = defaultdict(set)
    
    for m in expenses:
        concept = m['concepto']
        cleaned = clean_concept(concept)
        amount = m['importe']
        date = m['fecha']
        
        merchant_totals[cleaned] += amount
        merchant_counts[cleaned] += 1
        merchant_dates[cleaned].append(date)
        merchant_raw_concepts[cleaned].add((concept, amount, date))
        
    # Sort merchants by total expense (descending, meaning largest negative number first)
    sorted_merchants = sorted(merchant_totals.items(), key=lambda x: x[1])
    
    print("\nPROVEEDORES Y CONCEPTOS DE GASTO PRINCIPALES:")
    for merchant, total in sorted_merchants:
        count = merchant_counts[merchant]
        dates = sorted(merchant_dates[merchant])
        min_date = dates[0]
        max_date = dates[-1]
        print(f"- {merchant}: {total:,.2f} € | {count} pagos | Periodo: {min_date} a {max_date}")

    # Now let's find potential "suspicious" or "weird" categories
    # 1. Rare expenses (occurring only 1-5 times in 6 years, but with significant amounts)
    print("\n" + "="*80)
    print("1. PAGOS INFRECUENTES (1 a 5 veces en 6 años) CON IMPORTES RELEVANTES:")
    print("="*80)
    for merchant, total in sorted_merchants:
        count = merchant_counts[merchant]
        if count <= 5 and abs(total) > 100:
            print(f"\nProveedor: {merchant} (Total: {total:,.2f} € | {count} pagos)")
            for raw, amt, date in sorted(list(merchant_raw_concepts[merchant]), key=lambda x: x[2]):
                print(f"  [{date}] {raw} | Importe: {amt:.2f} €")

    # 2. Check for unexpected Insurance (Seguros) or double insurance
    print("\n" + "="*80)
    print("2. ANÁLISIS DE SEGUROS (Revisión de pólizas activas/duplicadas):")
    print("="*80)
    insurance_merchants = ["CAJA DE SEGUROS REUNIDOS (CASER)", "SEGUROS OCASO", "SEGUROS CASER", "CASER"]
    found_insurance = False
    for merchant, total in sorted_merchants:
        if any(ins in merchant for ins in insurance_merchants):
            found_insurance = True
            print(f"\nSeguro encontrado: {merchant} (Total gastado: {total:,.2f} € | {merchant_counts[merchant]} pagos)")
            for raw, amt, date in sorted(list(merchant_raw_concepts[merchant]), key=lambda x: x[2]):
                print(f"  [{date}] {raw} | Importe: {amt:.2f} €")
                
    # 3. Direct debits (Recibos domiciliados) that are unrecognized or vague
    print("\n" + "="*80)
    print("3. RECIBOS DOMICILIADOS O CARGOS VAGOS O EXTRAÑOS:")
    print("="*80)
    suspicious_keywords = ["CARGO DE", "RECIBO DE", "LIQUIDACION", "VARIOS", "TRANSFERENCIA", "PAGO SE", "ADEUDO"]
    
    # We want to identify merchants/concepts that:
    # - are not in our list of standard community suppliers (Naturgy, Canal Isabel II, Sabadell, TGSS, AEAT, MJM, El Pilar, Prevent, Alexandru Pirtac, Ista, Kone, Otis, Telefonica)
    # - look like companies/services that might not belong to a building community
    standard_keywords = [
        "NATURGY", "IBERDROLA", "ENDESA", "GAS", "CANAL DE ISABEL", "AGUA", "TELEFONICA", "MOVISTAR",
        "SABADELL", "TGSS", "SEGURIDAD SOCIAL", "HACIENDA", "AEAT", "MODELO", "MJM", "EL PILAR", "PREVENT",
        "ALEXANDRU", "PIRTAC", "ISTA", "KONE", "OTIS", "OCASO", "CASER", "CAJA DE SEGUROS", "INTERESES",
        "COMUNIDAD", "CUOTA", "PORTER", "INTEGRA", "CONSERJE", "MUNDO REFORMAS", "IMPERNOVA", "NAVACON"
    ]
    
    unrecognized_expenses = []
    for merchant, total in sorted_merchants:
        is_standard = False
        for kw in standard_keywords:
            if kw in merchant.upper():
                is_standard = True
                break
        if not is_standard and abs(total) > 50:
            unrecognized_expenses.append((merchant, total, merchant_counts[merchant], merchant_raw_concepts[merchant]))
            
    for merchant, total, count, raw_set in unrecognized_expenses:
        print(f"\nProveedor No Estándar: {merchant} (Total: {total:,.2f} € | {count} pagos)")
        for raw, amt, date in sorted(list(raw_set), key=lambda x: x[2]):
            print(f"  [{date}] {raw} | Importe: {amt:.2f} €")

    # 4. Analyze bank commissions and charges (Banco Sabadell)
    print("\n" + "="*80)
    print("4. ANÁLISIS DE COMISIONES Y GASTOS BANCARIOS (Sabadell):")
    print("="*80)
    sabadell_concept = "BANCO SABADELL - COMISIONES Y GASTOS"
    if sabadell_concept in merchant_totals:
        print(f"Total pagado en comisiones y gastos Sabadell: {merchant_totals[sabadell_concept]:,.2f} € | {merchant_counts[sabadell_concept]} cobros")
        # List largest charges or recurring charges
        sorted_sabadell = sorted(list(merchant_raw_concepts[sabadell_concept]), key=lambda x: x[1]) # sorted by amount (negative)
        print("\nComisiones bancarias más caras o sospechosas:")
        for raw, amt, date in sorted_sabadell[:20]: # Show top 20 largest fees
            print(f"  [{date}] {raw} | Importe: {amt:.2f} €")
    else:
        print("No se encontraron comisiones de Sabadell bajo esa clave.")

if __name__ == '__main__':
    movements = fetch_all_movements()
    analyze_movements(movements)
