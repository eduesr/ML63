import pdfplumber
import os
import glob
import re
import json

folder = "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Alexandru Pirtac/"
pdf_files = glob.glob(os.path.join(folder, "*.pdf"))

print(f"Found {len(pdf_files)} PDF files in Alexandru Pirtac directory:")

invoices = []

for f in sorted(pdf_files):
    name = os.path.basename(f)
    try:
        with pdfplumber.open(f) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            
            # Look for invoice date, number, base, total, and main concept
            lines = text.split('\n')
            
            date_match = re.search(r'(\d{2}-\d{2}-\d{4})', text)
            inv_date = date_match.group(1) if date_match else "Unknown Date"
            
            num_match = re.search(r'(Número|Número factura|Factura nº)\s*[:\-\s]?\s*(\d+/\d+|\d+)', text, re.IGNORECASE)
            inv_num = num_match.group(2) if num_match else "Unknown Num"
            
            # Let's find the total amount with or without decimal commas
            total_match = re.search(r'(TOTAL|TOTAL FACTURA|TOTAL\s+I\.V\.A\.)\s*[:\-\s]?\s*([\d\.,]+)\s*€?', text, re.IGNORECASE)
            # Find the actual total amount (we can also search for the last occurrence of the amount with a currency sign or after "TOTAL")
            totals = re.findall(r'TOTAL\s+I\.V\.A\.\s+([\d\.,]+)|TOTAL\s+([\d\.,]+)', text, re.IGNORECASE)
            # Let's print a sample of the text or look for the exact line
            inv_total = "Unknown Total"
            for line in lines:
                if "TOTAL" in line.upper():
                    t_match = re.search(r'([\d\.,]+)\s*€', line)
                    if t_match:
                        inv_total = t_match.group(1)
            
            if inv_total == "Unknown Total":
                t_match = re.search(r'TOTAL\s+I\.V\.A\.\s+([\d\.,]+)|TOTAL\s+([\d\.,]+)', text, re.IGNORECASE)
                if t_match:
                    inv_total = t_match.group(1) or t_match.group(2)
                
            invoices.append({
                "file": name,
                "date": inv_date,
                "num": inv_num,
                "total": inv_total,
                "text": text[:2000] # First 2000 chars
            })
            print(f"Parsed {name}: Date: {inv_date} | Num: {inv_num} | Total: {inv_total}")
    except Exception as e:
        print(f"Error parsing {name}: {e}")

# Save results
with open("pirtac_invoices_summary.json", "w") as out:
    json.dump(invoices, out, indent=2)
