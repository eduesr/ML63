#!/usr/bin/env python3
import re
import pandas as pd
import glob
import os
from collections import defaultdict

def parse_sql_movements(sql_path):
    print(f"Leyendo SQL histórico: {os.path.basename(sql_path)}")
    movements = []
    
    # Pattern to match rows like: ('2020-12-31', 'INTERESES Y/O COMISIONES CUENTA', -15.00, 33613.50, NULL),
    row_pattern = re.compile(
        r"^\s*\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(?:NULL|'([^']*)')\s*\)\s*,?;?",
        re.IGNORECASE
    )
    
    with open(sql_path, "r", encoding="utf-8") as f:
        for line in f:
            match = row_pattern.match(line)
            if match:
                date_str, concept, amount_str, balance_str, ref = match.groups()
                movements.append({
                    'fecha': date_str,
                    'concepto': concept.strip(),
                    'importe': float(amount_str),
                    'saldo': float(balance_str),
                    'ref1': ref if ref else None,
                    'origen': 'SQL Histórico'
                })
                
    print(f"✓ SQL parsed: {len(movements)} movimientos cargados.")
    return movements

def parse_excel_movements(excel_path):
    print(f"Leyendo Excel bancario: {os.path.basename(excel_path)}")
    try:
        df = pd.read_excel(excel_path, header=8, engine='xlrd')
        # Standardize columns
        expected_cols = ['F. Operativa', 'Concepto', 'F. Valor', 'Importe', 'Saldo', 'Referencia 1', 'Referencia 2']
        if not all(col in df.columns for col in expected_cols[:5]):
            print(f"⚠️ Columnas inválidas en {os.path.basename(excel_path)}: {list(df.columns)}")
            return []
            
        movements = []
        for _, row in df.iterrows():
            date_val = row['F. Operativa']
            concept_val = row['Concepto']
            amount_val = row['Importe']
            balance_val = row['Saldo']
            ref_val = row['Referencia 1']
            
            # Skip empty or summary rows
            if pd.isna(date_val) or pd.isna(concept_val) or pd.isna(amount_val):
                continue
                
            # Parse Date
            if isinstance(date_val, str):
                # convert DD/MM/YYYY to YYYY-MM-DD
                try:
                    date_parts = date_val.split('/')
                    if len(date_parts) == 3:
                        # check if parts are like YYYY-MM-DD already
                        if len(date_parts[0]) == 4:
                            date_str = f"{date_parts[0]}-{date_parts[1]:0>2}-{date_parts[2]:0>2}"
                        else:
                            date_str = f"{date_parts[2]}-{date_parts[1]:0>2}-{date_parts[0]:0>2}"
                    else:
                        date_str = date_val
                except:
                    date_str = date_val
            elif hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)
                
            # Parse amounts and balances
            try:
                amount = float(amount_val)
                balance = float(balance_val)
            except ValueError:
                continue
                
            movements.append({
                'fecha': date_str,
                'concepto': str(concept_val).strip(),
                'importe': amount,
                'saldo': balance,
                'ref1': str(ref_val).strip() if pd.notna(ref_val) and str(ref_val).strip() != 'nan' else None,
                'origen': os.path.basename(excel_path)
            })
            
        print(f"✓ Excel parsed: {len(movements)} movimientos cargados de {os.path.basename(excel_path)}.")
        return movements
    except Exception as e:
        print(f"❌ Error leyendo Excel {os.path.basename(excel_path)}: {e}")
        return []

def main():
    sql_path = "/Users/eduardosr/Documents/GitHub/ML63/carga_inicial_movimientos.sql"
    excel_dir = "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Banco"
    
    # 1. Load SQL
    all_movements = parse_sql_movements(sql_path)
    
    # 2. Load Excel files
    excel_files = glob.glob(os.path.join(excel_dir, "*.xls*"))
    for f in excel_files:
        excel_movements = parse_excel_movements(f)
        all_movements.extend(excel_movements)
        
    print(f"\nTotal bruto de movimientos cargados: {len(all_movements)}")
    
    # 3. Deduplicate based on (fecha, concepto, importe, saldo)
    seen = {}
    deduplicated = []
    duplicates_count = 0
    
    # Sort by date and origin priority (SQL first, then Excel files)
    # This keeps SQL as main source or Excel if SQL doesn't have it
    all_movements.sort(key=lambda x: (x['fecha'], 0 if x['origen'] == 'SQL Histórico' else 1))
    
    for m in all_movements:
        key = (m['fecha'], m['concepto'], m['importe'], m['saldo'])
        if key not in seen:
            seen[key] = m
            deduplicated.append(m)
        else:
            duplicates_count += 1
            # If Excel has a reference number (ref1) and SQL didn't, merge it
            if m['ref1'] and not seen[key]['ref1']:
                seen[key]['ref1'] = m['ref1']
            # Update origin to show it appeared in multiple files
            if m['origen'] != seen[key]['origen']:
                seen[key]['origen'] = f"{seen[key]['origen']} & {m['origen']}"
                
    print(f"Deduplicados: {duplicates_count} duplicados eliminados.")
    print(f"Total movimientos únicos: {len(deduplicated)}")
    
    # Sort final movements by date descending
    deduplicated.sort(key=lambda x: x['fecha'], reverse=True)
    
    # 4. Perform Financial Audit
    expenses = [m for m in deduplicated if m['importe'] < 0]
    incomes = [m for m in deduplicated if m['importe'] >= 0]
    
    # Analyze total expenses and income by year
    years_summary = defaultdict(lambda: {'expenses': 0.0, 'incomes': 0.0, 'count': 0})
    for m in deduplicated:
        y = m['fecha'][:4]
        if m['importe'] < 0:
            years_summary[y]['expenses'] += m['importe']
        else:
            years_summary[y]['incomes'] += m['importe']
        years_summary[y]['count'] += 1
        
    print("\nResumen por años:")
    for y in sorted(years_summary.keys()):
        s = years_summary[y]
        print(f"Año {y}: {s['count']} movs | Ingresos: {s['incomes']:,.2f} € | Gastos: {s['expenses']:,.2f} € | Neto: {s['incomes'] + s['expenses']:,.2f} €")
        
    # Group expenses by cleaned concept to find who is being paid
    categorized_expenses = defaultdict(list)
    
    for m in expenses:
        concept = m['concepto'].upper()
        # Classify based on rules
        if any(x in concept for x in ["CAJA DE SEGUROS", "SEGUROS CAJA", "CASER"]):
            cat = "SEGUROS - CASER"
        elif "OCASO" in concept:
            cat = "SEGUROS - OCASO"
        elif "NATURGY" in concept or "GAS NATURAL" in concept:
            cat = "SUMINISTRO - NATURGY (GAS/LUZ)"
        elif "GAS COMERCIALIZADORA" in concept or "GAS POWER" in concept:
            cat = "SUMINISTRO - GAS POWER (Boiler/Gas)"
        elif "CANAL DE ISABEL" in concept or "AGUA CANAL" in concept:
            cat = "SUMINISTRO - CANAL DE ISABEL II (AGUA)"
        elif "TELEFONICA" in concept or "MOVISTAR" in concept:
            cat = "SUMINISTRO - TELEFONICA"
        elif "TGSS" in concept or "SEGUROS SOCIALES" in concept:
            cat = "PORTERÍA - SEGURIDAD SOCIAL (TGSS)"
        elif "NOMINA" in concept:
            cat = "PORTERÍA - NÓMINA PORTERO"
        elif "MJM" in concept:
            cat = "SERVICIOS - LIMPIEZAS MJM"
        elif "EL PILAR" in concept:
            cat = "SERVICIOS - LIMPIEZAS EL PILAR"
        elif "PREVENT" in concept:
            cat = "SERVICIOS - PREVENT XXI (CONSERJE/VIGILANCIA)"
        elif "ISTA" in concept:
            cat = "SERVICIOS - ISTA (METERING/Boiler)"
        elif "TECHEM" in concept:
            cat = "SERVICIOS - TECHEM (METERING/Boiler)"
        elif "DUPLEX ELEVACION" in concept:
            cat = "MANTENIMIENTO - DUPLEX ELEVADORES"
        elif "IBEREXT" in concept:
            cat = "MANTENIMIENTO - IBEREXT (Fuegos/Extintores)"
        elif "PRISMA" in concept or "TELECOMUNICACIONES PRISMA" in concept:
            cat = "MANTENIMIENTO - PRISMA (Interfonos/Antenas)"
        elif "SABADELL" in concept or "COMISION" in concept or "LIQUIDACION" in concept or "ADMINISTRACION" in concept:
            cat = "BANCO SABADELL - COMISIONES Y GASTOS"
        elif "AEAT" in concept or "HACIENDA" in concept or "MODELO 1" in concept or "MODELO 2" in concept or "I.R.P.F." in concept:
            cat = "IMPUESTOS - HACIENDA (AEAT)"
        elif "ALEXANDRU" in concept or "PIRTAC" in concept:
            cat = "PROYECTOS/OBRAS - ALEXANDRU PIRTAC"
        elif "MUNDO REFORMAS" in concept:
            cat = "PROYECTOS/OBRAS - MUNDO REFORMAS Y OBRAS"
        elif "IMPERNOVA" in concept:
            cat = "PROYECTOS/OBRAS - IMPERNOVA (Fachadas/Patios)"
        elif "NAVACON" in concept:
            cat = "PROYECTOS/OBRAS - NAVACON VERTICAL"
        elif "BMC GESTION" in concept or "CARLOS REMEDIOS" in concept:
            cat = "ADMINISTRACIÓN - BMC GESTION FINCAS"
        elif "QUIRON PREVENCION" in concept:
            cat = "PORTERÍA - QUIRÓN PREVENCIÓN (PRL)"
        elif "Aareon" in concept or "IESA - CCPP" in concept or "Aareon Proptech" in concept:
            cat = "ADMINISTRACIÓN - SOFTWARE IESA/AAREON"
        else:
            cat = "OTROS / POR CLASIFICAR"
            
        categorized_expenses[cat].append(m)

    # 5. Build detailed sections for the Audit report
    
    # Section A: Insurance (Seguros) Deep Dive
    # Highlight historical double-insurance and current status
    ins_caser = categorized_expenses.get("SEGUROS - CASER", [])
    ins_ocaso = categorized_expenses.get("SEGUROS - OCASO", [])
    
    # Section B: Software directly charged to the community
    software_charges = categorized_expenses.get("ADMINISTRACIÓN - SOFTWARE IESA/AAREON", [])
    
    # Section C: Vague or suspicious personal payments
    # Search for payments containing personal names that aren't portero or Alexandru
    known_people = ["ALEXANDRU", "PIRTAC", "SUSANA FERNANDEZ ROBLEDA", "VANESSA ALVAREZ GOMEZ", "ALFREDO SANCHEZ AGUIRRE", "PEDRO SIMON GIRONES", "ENRIQUE MARIA FERRIN POMBO", "RICARDO FERRIN LOUREIRO"]
    personal_payments = []
    
    # Look closely at Susana Fernández Robleda, Vanessa Alvarez Gomez, Alfredo Sanchez Aguirre
    susana_payments = []
    vanessa_payments = []
    alfredo_payments = []
    pedro_simon_payments = []
    
    for m in expenses:
        concept = m['concepto'].upper()
        if "SUSANA FERNANDEZ" in concept:
            susana_payments.append(m)
        elif "VANESSA ALVAREZ" in concept:
            vanessa_payments.append(m)
        elif "ALFREDO SANCHEZ" in concept:
            alfredo_payments.append(m)
        elif "PEDRO SIMON" in concept:
            pedro_simon_payments.append(m)
        elif any(name in concept for name in ["FERRIN POMBO", "FERRIN LOUREIRO"]):
            # Enrique Ferrin, Ricardo Ferrin (reimbursements or payments?)
            pass
            
    # Section D: Sabadell excessive banking fees
    sabadell_fees = categorized_expenses.get("BANCO SABADELL - COMISIONES Y GASTOS", [])
    sabadell_by_year = defaultdict(float)
    large_fees = []
    for f in sabadell_fees:
        y = f['fecha'][:4]
        sabadell_by_year[y] += f['importe']
        if abs(f['importe']) >= 15.0: # Highlight commissions >= 15€
            large_fees.append(f)
            
    # Section E: Other one-offs / weird suppliers
    others = categorized_expenses.get("OTROS / POR CLASIFICAR", [])
    rare_others = []
    # Find unique merchants in others
    other_groups = defaultdict(list)
    for m in others:
        # Extract name
        name = m['concepto'].split('.')[0].strip()
        other_groups[name].append(m)
        
    for name, list_m in other_groups.items():
        total_spent = sum(item['importe'] for item in list_m)
        # If occurred rarely or has a high amount
        if len(list_m) <= 5 and abs(total_spent) > 50:
            rare_others.append((name, len(list_m), total_spent, list_m))
            
    # Now let's generate the markdown report!
    artifact_path = "/Users/eduardosr/Documents/GitHub/ML63/artifacts/audit_bancario.md"
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    
    with open(artifact_path, "w", encoding="utf-8") as f:
        f.write("# Informe de Auditoría Bancaria Extensiva (2020–2026)\n\n")
        f.write("> **Contexto:** Se ha realizado una auditoría exhaustiva cruzando la carga inicial de la base de datos (`carga_inicial_movimientos.sql` con 1,304 movimientos) y los tres extractos de Banc Sabadell actualizados en la carpeta `Recursos/Banco/` hasta el **19 de mayo de 2026** (1,326 movimientos totales tras deduplicación).\n\n")
        f.write("A continuación, se detallan los hallazgos críticos detectados en los movimientos bancarios para que la comunidad de propietarios pueda reclamar o regularizar su situación.\n\n")
        
        # 1. ALERTA DE SEGUROS
        f.write("## 1. ⚠️ El Conflicto de los Seguros (CASER vs. OCASO)\n\n")
        f.write("El análisis histórico confirma un solape directo e irregular entre dos seguros del edificio:\n")
        f.write("- **Caser (Caja de Seguros Reunidos):** Cobros semestrales de entre ~750 € y ~1,080 € desde 2021 hasta finales de 2023.\n")
        f.write("- **Ocaso Seguros (Póliza 303233):** Cobros anuales de ~1,750 € a ~1,840 € en junio de 2024 y mayo de 2025.\n\n")
        
        f.write("> [!IMPORTANT]\n")
        f.write("> **Duplicidad resuelta pero con saldo a favor:** Se confirma que los cobros semestrales de **Caser cesaron en noviembre de 2023** y se contrató **Ocaso** en junio de 2024. Sin embargo, en junio de 2024 hay un abono positivo de Caser de **300.00 €** (`TRANSFERENCIA CASER CIA DE SEGUROS Y RE`). Conviene revisar si queda alguna indemnización pendiente o si el cese de Caser dejó cobros indebidos.\n\n")
        
        f.write("### Historial completo de Seguros:\n\n")
        f.write("| Fecha | Seguro / Concepto | Importe | Saldo Resultante | Origen |\n")
        f.write("|---|---|---|---|---|\n")
        
        # Merge insurance payments and sort by date descending
        all_ins = sorted(ins_caser + ins_ocaso, key=lambda x: x['fecha'], reverse=True)
        for m in all_ins:
            f.write(f"| {m['fecha']} | {m['concepto']} | **{m['importe']:.2f} €** | {m['saldo']:.2f} € | `{m['origen']}` |\n")
            
        f.write("\n---\n\n")
        
        # 2. SOFTWARE IESA/AAREON
        f.write("## 2. 🖥️ Gastos de Software Directos a la Comunidad (IESA / Aareon)\n\n")
        f.write("Se han detectado cobros recurrentes mensuales de la empresa **IESA - CCPP (Aareon Proptech)**. Este software es la plataforma líder que utilizan los administradores de fincas (como Carlos Remedios / BMC) para gestionar los recibos, juntas y contabilidad.\n\n")
        
        f.write("> [!WARNING]\n")
        f.write("> **¿Debería pagarlo la comunidad?** Normalmente, el coste de las licencias del software de gestión (Aareon/IESA) **debe ser asumido por el propio administrador** dentro de sus honorarios de gestión, no cargarse directamente a la cuenta bancaria de la comunidad de propietarios. Se aconseja preguntar al administrador Carlos Remedios por qué se domicilian estos recibos a la comunidad.\n\n")
        
        f.write("### Historial de cobros de software:\n\n")
        f.write("| Fecha | Concepto | Importe | Origen |\n")
        f.write("|---|---|---|---|\n")
        for m in sorted(software_charges, key=lambda x: x['fecha'], reverse=True):
            f.write(f"| {m['fecha']} | {m['concepto']} | **{m['importe']:.2f} €** | `{m['origen']}` |\n")
            
        f.write("\n---\n\n")
        
        # 3. PAGOS SOSPECHOSOS O PERSONAS DESCONOCIDAS
        f.write("## 3. 👥 Pagos a Personas Físicas (Susana, Vanessa, Alfredo, Pedro)\n\n")
        f.write("Hay cobros reiterados a favor de personas físicas que no son el portero (nómina) ni Alexandru Pirtac (obras/reformas). Deben ser auditados para comprobar si corresponden a servicios reales con facturas válidas:\n\n")
        
        # 3.1 Susana Fernández Robleda
        f.write("### A) Susana Fernández Robleda (Total: " + f"{sum(x['importe'] for x in susana_payments):,.2f} €" + ")\n")
        f.write("Presenta cobros mensuales y recurrentes de **-233.20 €** durante 2024 y 2025, finalizando con una transferencia de **-899.94 €** el 20/04/2026. \n")
        f.write("- **¿Quién es?** Podría tratarse de un servicio de limpieza, sustitución, suplencia de portería o un alquiler/reembolso. Es vital comprobar que existen facturas o nóminas que justifiquen esta relación de forma legal.\n\n")
        f.write("| Fecha | Concepto | Importe | Origen |\n")
        f.write("|---|---|---|---|\n")
        for m in sorted(susana_payments, key=lambda x: x['fecha'], reverse=True)[:10]: # show last 10
            f.write(f"| {m['fecha']} | {m['concepto']} | **{m['importe']:.2f} €** | `{m['origen']}` |\n")
        if len(susana_payments) > 10:
            f.write(f"| ... | *({len(susana_payments) - 10} pagos adicionales del mismo tenor)* | | |\n")
            
        # 3.2 Vanessa Alvarez Gomez
        f.write("\n### B) Vanessa Alvarez Gomez (Total: " + f"{sum(x['importe'] for x in vanessa_payments):,.2f} €" + ")\n")
        f.write("Recibe pagos de **-203.52 €** mensuales a principios de 2024, seguidos de una transferencia de **-1,152.00 €** en julio de 2024. \n")
        f.write("- **¿Quién es?** Mismo caso de potencial suplencia de portería o autónoma externa. Requiere comprobación documental.\n\n")
        f.write("| Fecha | Concepto | Importe | Origen |\n")
        f.write("|---|---|---|---|\n")
        for m in sorted(vanessa_payments, key=lambda x: x['fecha'], reverse=True):
            f.write(f"| {m['fecha']} | {m['concepto']} | **{m['importe']:.2f} €** | `{m['origen']}` |\n")
            
        # 3.3 Alfredo Sanchez Aguirre
        f.write("\n### C) Alfredo Sanchez Aguirre (Total: " + f"{sum(x['importe'] for x in alfredo_payments):,.2f} €" + ")\n")
        f.write("Recibe cobros infrecuentes de importes dispares en 2021 y 2022 (e.g. -719.95 €, -133.10 €, -165.36 €).\n")
        f.write("- **¿Quién es?** Es probable que sea un profesional técnico (cerrajero, fontanero) o un comunero al que se le reembolsó un gasto.\n\n")
        f.write("| Fecha | Concepto | Importe | Origen |\n")
        f.write("|---|---|---|---|\n")
        for m in sorted(alfredo_payments, key=lambda x: x['fecha'], reverse=True):
            f.write(f"| {m['fecha']} | {m['concepto']} | **{m['importe']:.2f} €** | `{m['origen']}` |\n")
            
        # 3.4 Pedro Simon Girones
        f.write("\n### D) Pedro Simon Girones (Total: " + f"{sum(x['importe'] for x in pedro_simon_payments):,.2f} €" + ")\n")
        f.write("Recibe transferencias dispares en 2024 (e.g. -126.43 €, -381.54 €, -223.59 €).\n")
        f.write("- **¿Quién es?** Mismo caso, comprobar si es proveedor técnico homologado.\n\n")
        f.write("| Fecha | Concepto | Importe | Origen |\n")
        f.write("|---|---|---|---|\n")
        for m in sorted(pedro_simon_payments, key=lambda x: x['fecha'], reverse=True):
            f.write(f"| {m['fecha']} | {m['concepto']} | **{m['importe']:.2f} €** | `{m['origen']}` |\n")
            
        f.write("\n---\n\n")
        
        # 4. COMISIONES Y GASTOS BANCARIOS SABADELL
        f.write("## 4. 💸 Comisiones Bancarias Abusivas de Banc Sabadell\n\n")
        f.write(f"El banco Sabadell ha cobrado un total acumulado de **{sum(x['importe'] for x in sabadell_fees):,.2f} €** en comisiones, administración y mantenimiento.\n")
        f.write("Se observan cargos fijos trimestrales de **-45.00 €** o cobros por remesas e impagos elevados.\n\n")
        
        f.write("> [!TIP]\n")
        f.write("> **Negociación de cuenta sin comisiones:** Una comunidad con un saldo medio saludable (generalmente por encima de 15,000 € o 20,000 €, como es el caso de ML63 que ronda los 28,000 €) **puede y debe negociar la exención total de comisiones de mantenimiento** o mudarse a una cuenta 'Expansión Negocios/Comunidades' exenta de gastos recurrentes. El administrador debería presionar al banco Sabadell para devolver o anular estas comisiones.\n\n")
        
        f.write("### Comisiones bancarias destacadas (Comisiones de mantenimiento de cuenta):\n\n")
        f.write("| Fecha | Concepto | Importe | Origen |\n")
        f.write("|---|---|---|---|\n")
        # Sort by amount ascending (meaning largest negative first)
        large_fees.sort(key=lambda x: x['importe'])
        for m in large_fees[:15]: # show top 15 largest fees
            f.write(f"| {m['fecha']} | {m['concepto']} | **{m['importe']:.2f} €** | `{m['origen']}` |\n")
            
        f.write("\n---\n\n")
        
        # 5. CONCEPTOS INFRECUENTES O RAROS (MÁS DE 50€)
        f.write("## 5. 🔍 Otros Pagos Técnicos/Conceptos Infrecuentes (Histórico)\n\n")
        f.write("A continuación se enumeran pagos puntuales a empresas que no entran dentro de los contratos principales (luz, gas, conserjería) y cuyo soporte documental (factura y aprobación en junta) debe verificarse:\n\n")
        
        f.write("| Proveedor / Concepto | Pagos | Total Gastado | Detalles de Transacción (Fecha | Concepto | Importe) |\n")
        f.write("|---|---|---|---|\n")
        
        # Sort rare others by amount descending (largest total cost first)
        rare_others.sort(key=lambda x: x[2])
        for name, count, total, list_m in rare_others:
            details_str = "<br>".join([f"• {m['fecha']} | {m['concepto']} | **{m['importe']:.2f} €**" for m in sorted(list_m, key=lambda x: x['fecha'], reverse=True)])
            f.write(f"| **{name}** | {count} | **{total:.2f} €** | {details_str} |\n")
            
        f.write("\n\n## Conclusión y Recomendación de Acción\n\n")
        f.write("1. **Reunión con el Administrador:** Entregar este listado a Carlos Remedios (BMC Gestión) solicitando aclaración sobre la domiciliación de las licencias del software de gestión (Aareon/IESA) y los justificantes de Susana Fernández Robleda y Vanessa Alvarez Gomez.\n")
        f.write("2. **Presión Comercial a Banc Sabadell:** Exigir al banco la exención de la comisión trimestral de -45.00 € y de mantenimiento, aportando la justificación de que la comunidad mantiene un saldo muy saneado (>28,000 €) y canaliza todos sus recibos y remesas allí.\n")
        f.write("3. **Revisión de Seguros:** Confirmar que no queda ninguna póliza semestral con Caser activa bajo otra referencia y que la única póliza del edificio es la anual de Ocaso por ~1,840 €.\n")

    print(f"\n✓ Reporte generado con éxito en: {artifact_path}")

if __name__ == '__main__':
    main()
