#!/usr/bin/env python3
"""
Debug PDF extraction to see what text is actually being extracted
"""

import os
from pathlib import Path
from PyPDF2 import PdfReader

def check_pdf(pdf_path):
    """Extract and display text from a PDF"""
    try:
        reader = PdfReader(pdf_path)
        print(f"\n{'='*80}")
        print(f"File: {os.path.basename(pdf_path)}")
        print(f"Pages: {len(reader.pages)}")
        print(f"{'='*80}")

        text = ""
        for page_num in range(min(3, len(reader.pages))):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            print(f"\n--- Page {page_num + 1} ({len(page_text)} chars) ---")
            print(page_text[:2000])  # First 2000 chars
            text += page_text

        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        import traceback
        traceback.print_exc()
        return ""

# Test with a few key PDFs
test_pdfs = [
    '/Users/eduardosr/Documents/GitHub/ML63/Recursos/Gas Power/FE25137025698878.pdf',
    '/Users/eduardosr/Documents/GitHub/ML63/Recursos/Gas Power/FE24137011684224.pdf',
    '/Users/eduardosr/Documents/GitHub/ML63/Recursos/Gas Power/FE23137001890342.pdf',
]

for pdf_path in test_pdfs:
    if os.path.exists(pdf_path):
        check_pdf(pdf_path)
    else:
        print(f"\nFile not found: {pdf_path}")
