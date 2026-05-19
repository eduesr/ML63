import PyPDF2

pdf_path = "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Actas/Junta 2026/ML63 BALANCE 2025 DOSIER/MODESTO LAFUENTE 63 GASTOS 2025.pdf"

print("--- EXTRACTING GASTOS 2025 PDF ---")
try:
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        print(f"Total pages: {len(reader.pages)}")
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            print(f"\n--- PAGE {i+1} ---")
            print(page_text)
except Exception as e:
    print(f"Error reading PDF: {e}")
