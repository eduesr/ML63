#!/usr/bin/env python3
"""
Extract all Gas Power PDFs and prepare data for Supabase insertion.
Outputs JSON with all records ready for consumos_suministros table.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from PyPDF2 import PdfReader

def convert_european_number(text):
    """Convert European format (1.234,56) to float (1234.56)"""
    if not text:
        return None
    # Remove spaces
    text = text.strip()
    # Remove periods (thousands separator)
    text = text.replace('.', '')
    # Convert comma to period (decimal)
    text = text.replace(',', '.')
    try:
        return float(text)
    except:
        return None

def extract_dates_fe(text):
    """Extract dates from FE invoice format: 'del 16.10.2025 al 14.11.2025'"""
    # Normalize whitespace (PDFs extract with many newlines)
    normalized = re.sub(r'\s+', ' ', text)

    pattern = r'[Dd]el?\s+(\d{1,2})\.(\d{1,2})\.(\d{4})\s+al?\s+(\d{1,2})\.(\d{1,2})\.(\d{4})'
    match = re.search(pattern, normalized)
    if match:
        start_day, start_month, start_year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        end_day, end_month, end_year = int(match.group(4)), int(match.group(5)), int(match.group(6))
        return {
            'start': f"{start_year:04d}-{start_month:02d}-{start_day:02d}",
            'end': f"{end_year:04d}-{end_month:02d}-{end_day:02d}"
        }
    return None

def extract_consumption_fe(text):
    """Extract consumption from FE invoices"""
    # Normalize whitespace (PDFs extract with many newlines)
    normalized = re.sub(r'\s+', ' ', text)

    # Primary pattern: "Consumo gas 5.314 kWh" (handles spaces)
    pattern1 = r'[Cc]onsumo\s+(?:gas\s+)?([0-9.,]+)\s*kWh'
    match = re.search(pattern1, normalized)
    if match:
        value = convert_european_number(match.group(1))
        if value:
            return value

    # Secondary pattern: "Consumo kWh: ... 5.314 kWh" (detailed breakdown)
    pattern2 = r'[Cc]onsumo\s*kWh:\s*[\d.,]+\s*m³\s*x\s*[\d.,]+\s*kWh\*?\s+([0-9.,]+)\s*kWh'
    match = re.search(pattern2, normalized)
    if match:
        value = convert_european_number(match.group(1))
        if value:
            return value

    return None

def extract_invoice_number(filename):
    """Extract invoice number from filename"""
    # Format: FE25137025698878 or FE26137001906182
    match = re.search(r'(FE\d{14,16})', filename)
    if match:
        return match.group(1)[:14]  # Normalize to 14 chars
    return None

def get_supplier_from_filename(filename):
    """Determine supplier from filename"""
    filename_lower = filename.lower()
    if 'fe23' in filename_lower or 'fe24' in filename_lower:
        return 'Comercializadora Regulada'
    elif 'fe25' in filename_lower or 'fe26' in filename_lower:
        return 'Gas Power'
    return 'Gas Power'  # Default

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        # Read first 3 pages max
        for page_num in range(min(3, len(reader.pages))):
            page = reader.pages[page_num]
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def process_pdf_file(pdf_path):
    """Process a single PDF and return record or None"""
    filename = os.path.basename(pdf_path)

    # Extract text
    text = extract_pdf_text(pdf_path)
    if not text:
        return None

    # Extract dates
    dates = extract_dates_fe(text)
    if not dates:
        return None

    # Extract consumption
    consumption_kwh = extract_consumption_fe(text)
    if not consumption_kwh:
        return None

    # Extract invoice number
    invoice_num = extract_invoice_number(filename)
    if not invoice_num:
        return None

    # Get supplier
    supplier = get_supplier_from_filename(filename)

    # Build record
    record = {
        'fecha_inicio': dates['start'],
        'fecha_fin': dates['end'],
        'consumo_kwh': int(consumption_kwh),
        'tipo_suministro': 'gas',
        'proveedor': supplier,
        'numero_factura': invoice_num,
        'consumo_valido': True,
        'validacion_notas': f"Extraído de {filename}"
    }

    return record

def main():
    """Process all PDFs in Recursos/Gas Power/"""
    base_path = Path('/Users/eduardosr/Documents/GitHub/ML63/Recursos/Gas Power')

    if not base_path.exists():
        print(f"Error: {base_path} not found")
        return

    records = []
    pdf_files = sorted(base_path.glob('*.pdf'))

    print(f"Found {len(pdf_files)} PDF files")
    print("=" * 80)

    for pdf_path in pdf_files:
        record = process_pdf_file(pdf_path)
        if record:
            records.append(record)
            print(f"✓ {pdf_path.name}")
            print(f"  {record['fecha_inicio']} → {record['fecha_fin']} | {record['consumo_kwh']:,} kWh | {record['proveedor']}")
        else:
            print(f"✗ {pdf_path.name} (failed to extract)")

    print("=" * 80)

    # Group by heating season
    seasons = {}
    for record in records:
        start_date = datetime.fromisoformat(record['fecha_inicio'])
        year = start_date.year
        month = start_date.month

        # Heating season: Oct (10) - May (5)
        if month >= 10:
            season = f"{year}/{year+1}"
        else:
            season = f"{year-1}/{year}"

        if season not in seasons:
            seasons[season] = {'total_kwh': 0, 'count': 0, 'records': []}

        seasons[season]['total_kwh'] += record['consumo_kwh']
        seasons[season]['count'] += 1
        seasons[season]['records'].append(record)

    # Print summary
    print("\nSummary by Heating Season:")
    print("-" * 80)
    for season in sorted(seasons.keys()):
        data = seasons[season]
        print(f"{season}: {data['count']} invoices = {data['total_kwh']:,} kWh")

    # Output JSON for insertion
    output_file = Path('/Users/eduardosr/Documents/GitHub/ML63/supabase_import.json')
    with open(output_file, 'w') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(records)} records to: {output_file}")
    print("\nNext step: Import this JSON into Supabase consumos_suministros table")
    print("Use Supabase Studio: Insert → Multi-line JSON paste")

if __name__ == '__main__':
    main()
