import os
import PyPDF2 as pypdf

hallazgos_dir = "/Users/eduardosr/Documents/GitHub/ML63/Recursos/Hallazgos"
output_dir = "/Users/eduardosr/Documents/GitHub/ML63/scratch/extracted_hallazgos"
os.makedirs(output_dir, exist_ok=True)

files = [f for f in os.listdir(hallazgos_dir) if f.endswith('.pdf')]
print(f"Found {len(files)} PDF files in Hallazgos.")

for fname in sorted(files):
    fpath = os.path.join(hallazgos_dir, fname)
    print(f"\nProcessing: {fname}")
    try:
        reader = pypdf.PdfReader(fpath)
        print(f"  Pages: {len(reader.pages)}")
        text_content = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text_content.append(f"--- PAGE {i+1} ---\n{text}")
        
        full_text = "\n\n".join(text_content).strip()
        if full_text:
            out_name = fname.replace('.pdf', '_selectable.txt')
            out_path = os.path.join(output_dir, out_name)
            with open(out_path, 'w', encoding='utf-8') as out_f:
                out_f.write(full_text)
            print(f"  [SUCCESS] Extracted selectable text to: {out_name} ({len(full_text)} chars)")
        else:
            print("  [SCANNED] No selectable text found. This is a scanned PDF.")
    except Exception as e:
        print(f"  [ERROR] Could not read file: {e}")
