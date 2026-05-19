import json

with open("pirtac_invoices_summary.json", "r") as f:
    invoices = json.load(f)

print("--- INSPECTING INVOICE CONCEPTS ---")
for inv in invoices:
    print(f"\n==================================================")
    print(f"FILE: {inv['file']} | Date: {inv['date']} | Total parsed: {inv['total']}")
    print(f"==================================================")
    
    # Let's print the first 10 lines of the invoice text
    lines = inv['text'].split('\n')
    concept_lines = []
    capture = False
    
    # Try to find lines under "Artículo" or "Descripción"
    for line in lines:
        if any(keyword in line.upper() for keyword in ["CONCEPTO", "DESCRIPCIÓN", "ARTÍCULO", "CANTIDAD"]):
            capture = True
            idx = lines.index(line)
            concept_lines = lines[idx:idx+15]
            break
            
    if not concept_lines:
        # Just print lines containing money or work descriptions
        concept_lines = [l for l in lines if any(k in l.upper() for k in ["BAJANTE", "TUBERIA", "FALCA", "AGUA", "PORTAL", "MADERA", "PVC", "OBRA", "PLADUR", "IMPORTE"])]
        if not concept_lines:
            concept_lines = lines[:15]
            
    print("\n".join(concept_lines[:15]))
