import re
import ast

def parse_sql_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all INSERT statements
    insert_pattern = re.compile(
        r"INSERT INTO public\.movimientos\s*\([^)]*\)\s*VALUES\s*(.*?);",
        re.DOTALL | re.IGNORECASE
    )
    
    movements = []
    
    for match in insert_pattern.finditer(content):
        values_block = match.group(1)
        # Parse individual rows
        # The block consists of (tuples), separated by commas and newlines
        # A row looks like: ('2020-12-31', 'INTERESES Y/O COMISIONES CUENTA', -15.00, 33613.50, NULL)
        # We can find all tuples inside the values block.
        # Let's match anything inside parentheses: ( ... )
        row_pattern = re.compile(r"\s*\((.*?)\)\s*(?:,|$)", re.DOTALL)
        for row_match in row_pattern.finditer(values_block):
            row_str = row_match.group(1).strip()
            if not row_str:
                continue
                
            # Parse the fields. To do this safely, we can replace NULL with None and parse it as a python tuple.
            # However, concepts might have commas inside single quotes, e.g. 'Modesto Lafuente, 63'
            # Let's use a safe parser: we can split by comma but respect quotes, or do regex.
            # A tuple in SQL: 'date', 'concept', numeric, numeric, ref
            # Let's write a simple scanner for the SQL tuple fields.
            
            # Let's scan fields:
            # We want: 
            # 1. Date (always string in single quotes)
            # 2. Concept (always string in single quotes, can have escaped quotes or commas)
            # 3. Importe (float)
            # 4. Saldo (float)
            # 5. Ref (NULL or string)
            
            # Let's parse with a regex that matches:
            # 'date', 'concept', importe, saldo, ref
            # Let's match single-quoted strings and numeric tokens:
            tokens = []
            current = ""
            in_quotes = False
            escaped = False
            
            # Simple scanner for SQL row values
            i = 0
            while i < len(row_str):
                c = row_str[i]
                if in_quotes:
                    if escaped:
                        current += c
                        escaped = False
                    elif c == "'":
                        # Check for SQL escaped quote ''
                        if i + 1 < len(row_str) and row_str[i+1] == "'":
                            current += "'"
                            i += 1  # Skip the second quote
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
                
                # Importe
                try:
                    importe = float(tokens[2])
                except ValueError:
                    importe = 0.0
                    
                # Saldo
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
    print(f"Parsed {len(moves)} movements from SQL file.")
    
    # Filter and sort
    mjm_moves = []
    portero_moves = []
    
    for m in moves:
        concepto_upper = m['concepto'].upper()
        
        # MJM
        if 'MJM' in concepto_upper:
            mjm_moves.append(m)
            
        # Portero
        is_portero = False
        if 'NOMINA' in concepto_upper:
            is_portero = True
        elif 'TGSS' in concepto_upper or 'SEGUROS SOCIALES' in concepto_upper:
            is_portero = True
        elif 'QUIRON' in concepto_upper:
            is_portero = True
        elif 'EL PORTERO' in concepto_upper:
            is_portero = True
        elif 'FINIQUITO' in concepto_upper or 'INDEMNIZACION' in concepto_upper:
            is_portero = True
        elif 'PEDRO' in concepto_upper and 'GIRONES' in concepto_upper:
            is_portero = True
        elif 'EMBARGO' in concepto_upper:
            is_portero = True
            
        if is_portero:
            portero_moves.append(m)
            
    print("\n" + "="*80)
    print("MJM MOVEMENTS:")
    print("="*80)
    for m in sorted(mjm_moves, key=lambda x: x['fecha']):
        print(f"{m['fecha']} | {m['importe']:10.2f}€ | Saldo: {m['saldo']:10.2f}€ | {m['concepto']}")
        
    print("\n" + "="*80)
    print("PORTERO MOVEMENTS (2024 - 2026):")
    print("="*80)
    # Filter portero movements starting in 2024 to focus on late 2024/2025/2026
    portero_filtered = [m for m in portero_moves if m['fecha'] >= '2024-01-01']
    for m in sorted(portero_filtered, key=lambda x: x['fecha']):
        print(f"{m['fecha']} | {m['importe']:10.2f}€ | Saldo: {m['saldo']:10.2f}€ | {m['concepto']}")
