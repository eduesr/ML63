import PyPDF2 as pypdf
import sys

def search_pdf(path, keywords):
    try:
        reader = pypdf.PdfReader(path)
        print(f"File: {path}")
        print(f"Total pages: {len(reader.pages)}")
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            
            # Search line by line
            lines = text.split("\n")
            for line_no, line in enumerate(lines):
                for kw in keywords:
                    if kw.lower() in line.lower():
                        print(f"Page {i+1}, Line {line_no+1} [{kw}]: {line.strip()}")
                        break # Avoid printing the same line twice for different keywords
                        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    keywords = ["mjm", "limpieza", "portero", "pedro", "baja", "enfermedad", "médica", "vacaciones", "suspend"]
    search_pdf("/Users/eduardosr/Documents/GitHub/ML63/Recursos/Actas/Junta 2024/Acta - 2024 - BMC.pdf", keywords)
