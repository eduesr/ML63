import pdfplumber
import os

files = {
    "Pirtac (Tubería)": "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Alexandru Pirtac/Presupuesto de Cliente nº 0001-000034.pdf",
    "Navacon (Sellado Ventanal)": "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Navacon Vertical/PTTO090A-2026.pdf"
}

for name, path in files.items():
    print(f"\n==================================================")
    print(f"FILE: {name}")
    print(f"PATH: {path}")
    print(f"==================================================")
    if os.path.exists(path):
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"--- Page {i+1} ---")
                print(page.extract_text())
    else:
        print("ERROR: File not found!")
