import PyPDF2
with open("/Users/eduardosr/Documents/GitHub/ML63/Recursos/Gas Power/FE26137006909149.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    for i in range(len(reader.pages)):
        print(reader.pages[i].extract_text())
