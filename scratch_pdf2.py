import PyPDF2
import re

with open("/Users/eduardosr/Documents/GitHub/ML63/Recursos/Gas Power/FE26137006909149.pdf", "rb") as f:
    reader = PyPDF2.PdfReader(f)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + " "

print("TEXT PREVIEW:")
print(text[:1000])

print("\nDATE MATCHES:")
print(re.findall(r'(\d{1,2}\.\d{1,2}\.\d{2,4})', text))

print("\nCONSUMO MATCHES:")
print(re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d+)?\s*(?:kWh|m³))', text, re.IGNORECASE))
