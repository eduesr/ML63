import PyPDF2 as pypdf
import sys

def check_pdf(path):
    try:
        reader = pypdf.PdfReader(path)
        print(f"File: {path}")
        print(f"Pages: {len(reader.pages)}")
        text = ""
        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                text += t
        if text.strip():
            print("Selectable text found (first 1000 chars):")
            print(text[:1000])
        else:
            print("No selectable text found. The PDF is likely scanned.")
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    check_pdf("/Users/eduardosr/Documents/GitHub/ML63/Recursos/Actas/Junta 2024/Acta - 2024 - BMC.pdf")
