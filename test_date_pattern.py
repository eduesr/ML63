#!/usr/bin/env python3
"""
Find the pattern in problematic dates
"""

import sys
import subprocess
from datetime import datetime, timedelta

try:
    from supabase import create_client
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'supabase'], check=True)
    from supabase import create_client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "TU_SERVICE_ROLE_KEY_AQUI"

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

# Get all the dates from failed records
failed_records = [
    ("FE231370067490", "2023-02-16", "2023-03-15"),
    ("FE231370296400", "2023-11-16", "2023-12-15"),
    ("FE241370116842", "2023-12-16", "2024-01-15"),  # First instance
    ("FE241370116843", "2024-02-16", "2024-03-15"),  # First instance
    ("FE241370265667", "2024-10-16", "2024-11-15"),
    ("FE251370063237", "2025-02-15", "2025-03-14"),
    ("FE261370019061", "2025-12-17", "2026-01-16"),
    ("FE261370044305", "2026-01-17", "2026-02-16"),
    ("FE261370069091", "2026-02-17", "2026-03-16"),
]

print("\n" + "="*80)
print("ANALYZING PATTERN IN PROBLEMATIC DATES")
print("="*80 + "\n")

print("Failed records and their patterns:\n")
for record_id, fecha_inicio, fecha_fin in failed_records:
    # Parse dates
    start = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    end = datetime.strptime(fecha_fin, "%Y-%m-%d")
    days = (end - start).days + 1

    # Check for patterns
    day_of_month_start = start.day
    month_start = start.month
    year_start = start.year

    # Check for leap year
    is_leap = (year_start % 4 == 0 and year_start % 100 != 0) or (year_start % 400 == 0)

    print(f"{record_id:20s} {fecha_inicio} → {fecha_fin} ({days:2d} days)")
    print(f"  → Day of month: {day_of_month_start:2d}, Month: {month_start:2d}, Year: {year_start}")
    print(f"  → Leap year: {is_leap}, Days between: {days}")
    print()

# Test specific date: 2023-02-16
print("\n" + "="*80)
print("HYPOTHESIS: Division by zero when day >= 16?")
print("="*80 + "\n")

test_dates = [
    ("2023-02-15", "2023-03-15", "Test day 15"),
    ("2023-02-16", "2023-03-15", "Test day 16 (SHOULD FAIL)"),
    ("2023-02-17", "2023-03-15", "Test day 17"),
    ("2023-02-01", "2023-03-15", "Test day 1"),
    ("2023-02-28", "2023-03-15", "Test day 28"),
]

for i, (start_date, end_date, description) in enumerate(test_dates):
    test_record = {
        "fecha_inicio": start_date,
        "fecha_fin": end_date,
        "consumo_kwh": 100,
        "tipo_suministro": "gas",
        "proveedor": "Test",
        "numero_factura": f"TEST_DATE_{i}",
        "consumo_valido": True,
        "validacion_notas": description
    }

    try:
        response = supabase.table('consumos_suministros').insert(test_record).execute()
        result = "✓"
        supabase.table('consumos_suministros').delete().eq('numero_factura', f"TEST_DATE_{i}").execute()
    except Exception as e:
        result = "✗"

    print(f"{result} {start_date} {description}")

print("\n" + "="*80)
print("HYPOTHESIS 2: Division by zero when in a specific month?")
print("="*80 + "\n")

# Test across months
test_months = [
    ("2023-01-16", "2023-02-16", "Jan 16-Feb 16"),
    ("2023-02-16", "2023-03-16", "Feb 16-Mar 16 (SHOULD FAIL)"),
    ("2023-03-16", "2023-04-16", "Mar 16-Apr 16"),
    ("2023-10-16", "2023-11-16", "Oct 16-Nov 16"),
    ("2023-11-16", "2023-12-16", "Nov 16-Dec 16 (SHOULD FAIL)"),
]

for i, (start_date, end_date, description) in enumerate(test_months):
    test_record = {
        "fecha_inicio": start_date,
        "fecha_fin": end_date,
        "consumo_kwh": 100,
        "tipo_suministro": "gas",
        "proveedor": "Test",
        "numero_factura": f"TEST_MONTH_{i}",
        "consumo_valido": True,
        "validacion_notas": description
    }

    try:
        response = supabase.table('consumos_suministros').insert(test_record).execute()
        result = "✓"
        supabase.table('consumos_suministros').delete().eq('numero_factura', f"TEST_MONTH_{i}").execute()
    except:
        result = "✗"

    print(f"{result} {description}")
