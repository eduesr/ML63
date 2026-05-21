import re

def parse_sql_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    insert_pattern = re.compile(
        r"INSERT INTO public\.movimientos\s*\([^)]*\)\s*VALUES\s*(.*?);",
        re.DOTALL | re.IGNORECASE
    )
    
    movements = []
    
    for match in insert_pattern.finditer(content):
        values_block = match.group(1)
        row_pattern = re.compile(r"\s*\((.*?)\)\s*(?:,|$)", re.DOTALL)
        for row_match in row_pattern.finditer(values_block):
            row_str = row_match.group(1).strip()
            if not row_str:
                continue
                
            tokens = []
            current = ""
            in_quotes = False
            escaped = False
            
            i = 0
            while i < len(row_str):
                c = row_str[i]
                if in_quotes:
                    if escaped:
                        current += c
                        escaped = False
                    elif c == "'":
                        if i + 1 < len(row_str) and row_str[i+1] == "'":
                            current += "'"
                            i += 1
                        else:
                            in_quotes = False
                            tokens.append(current)
                            current = ""
                    elif c == "\\":
                        escaped = True
                    else:
                        current += c
                else:
                    if c == "'":
                        in_quotes = True
                    elif c in (',', ' ', '\t', '\n', '\r'):
                        val = current.strip()
                        if val:
                            tokens.append(val)
                            current = ""
                    else:
                        current += c
                i += 1
            val = current.strip()
            if val:
                tokens.append(val)
                
            if len(tokens) >= 4:
                fecha = tokens[0]
                concepto = tokens[1]
                
                try:
                    importe = float(tokens[2])
                except ValueError:
                    importe = 0.0
                    
                try:
                    saldo = float(tokens[3])
                except ValueError:
                    saldo = 0.0
                    
                movements.append({
                    'fecha': fecha,
                    'concepto': concepto,
                    'importe': importe,
                    'saldo': saldo
                })
                
    return movements

if __name__ == '__main__':
    filepath = '/Users/eduardosr/Documents/GitHub/ML63/carga_inicial_movimientos.sql'
    moves = parse_sql_file(filepath)
    
    # Let's filter for 2024 and 2025 cleaning/cubos/portero related concepts
    target_moves = []
    for m in moves:
        if m['fecha'] < '2024-01-01' or m['fecha'] > '2025-12-31':
            continue
            
        concepto_upper = m['concepto'].upper()
        
        # Check if relevant
        is_relevant = False
        category = ""
        
        if 'MJM' in concepto_upper:
            is_relevant = True
            category = "MJM"
        elif 'PILAR' in concepto_upper:
            is_relevant = True
            category = "EL PILAR"
        elif 'CUBO' in concepto_upper:
            is_relevant = True
            category = "DON CUBO / CUBOS"
        elif 'PREVENT' in concepto_upper:
            is_relevant = True
            category = "PREVENT"
        elif 'NOMINA' in concepto_upper:
            is_relevant = True
            category = "NOMINA PORTERO"
        elif 'GIRONES' in concepto_upper:
            is_relevant = True
            category = "PORTERO TRANSF"
        elif 'EMBARGO' in concepto_upper:
            is_relevant = True
            category = "EMBARGO PORTERO"
        elif 'TGSS' in concepto_upper or 'SEGUROS SOCIALES' in concepto_upper:
            is_relevant = True
            category = "TGSS PORTERO"
            
        if is_relevant:
            m['category'] = category
            target_moves.append(m)
            
    print(f"Found {len(target_moves)} target movements in 2024-2025:")
    print("="*100)
    print(f"{'FECHA':10s} | {'CATEGORIA':15s} | {'IMPORTE':10s} | {'CONCEPTO'}")
    print("="*100)
    for m in sorted(target_moves, key=lambda x: (x['fecha'], x['category'])):
        print(f"{m['fecha']:10s} | {m['category']:15s} | {m['importe']:8.2f}€ | {m['concepto']}")
