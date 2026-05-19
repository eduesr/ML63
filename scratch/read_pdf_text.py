import sys
import os

pdf_files = [
    "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Alexandru Pirtac/Presupuesto de Cliente nº 0001-000034.pdf",
    "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Navacon Vertical/PTTO090A-2026.pdf",
    "/Users/eduardosr/Documents/GitHub/ML63/Presupuesto sellado ventanal/PTTO090-2026.pdf",
    "/Users/eduardosr/Documents/GitHub/ML63/Presupuesto sellado ventanal/PRESUPUESTO 2600141.PDF",
    "/Users/eduardosr/Documents/GitHub/ML63/Presupuesto sellado ventanal/Modesto Lafuente 63, 53   26.pdf"
]

print("Python version:", sys.version)

for f in pdf_files:
    if os.path.exists(f):
        print(f"\n--- Checking file: {os.path.basename(f)} (Size: {os.path.getsize(f)} bytes)")
        # Try importing common libraries
        try:
            import pdfplumber
            with pdfplumber.open(f) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                print("Extracted via pdfplumber:")
                print(text[:2000]) # First 2000 chars
            continue
        except ImportError:
            pass
            
        try:
            from pypdf import PdfReader
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            print("Extracted via pypdf:")
            print(text[:2000])
            continue
        except ImportError:
            pass

        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            print("Extracted via PyPDF2:")
            print(text[:2000])
            continue
        except ImportError:
            pass
            
        print("No Python PDF parsing libraries found!")
    else:
        print(f"File not found: {f}")
