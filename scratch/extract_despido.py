import PyPDF2

filepath = "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Despido portero/Pedro carata de despido.pdf"

try:
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        print(f"Number of pages: {len(reader.pages)}")
        for i in range(len(reader.pages)):
            print(f"\n--- PAGE {i+1} ---")
            print(reader.pages[i].extract_text())
except Exception as e:
    print(f"Error reading PDF: {e}")
