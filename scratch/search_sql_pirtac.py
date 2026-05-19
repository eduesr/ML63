import re

sql_file = "/Users/eduardosr/Documents/GitHub/ML63/carga_inicial_movimientos.sql"
print(f"Reading {sql_file}...")

pirtac_moves = []
with open(sql_file, 'r', encoding='utf-8') as f:
    content = f.read()
    
# Find all insert statements or lines containing PIRTAC
lines = content.split('\n')
for line in lines:
    if "PIRTAC" in line.upper() or "ALEXANDRU" in line.upper():
        pirtac_moves.append(line)

print(f"\nFound {len(pirtac_moves)} bank movements containing 'Pirtac' or 'Alexandru':")
for move in sorted(pirtac_moves):
    print(move)
