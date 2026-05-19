import re

file_path = "/Users/eduardosr/Documents/GitHub/ML63/carga_inicial_movimientos.sql"
keywords = ["SEGUROS CAJA", "OCASO", "CASER"]

matches = []
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        # Check if line contains insert values
        if "INSERT INTO" in line or "VALUES" in line or line.strip().startswith("--"):
            continue
        line_lower = line.lower()
        # Filter for TGSS
        if "tgss" in line_lower or "sociales" in line_lower:
            continue
        
        found = False
        for kw in keywords:
            if kw.lower() in line_lower:
                found = True
                break
        if found:
            matches.append(line.strip())

print(f"Encontrados {len(matches)} movimientos históricos de seguros:")
for m in matches:
    print(m)
