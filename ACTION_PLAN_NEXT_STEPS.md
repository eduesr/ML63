# Action Plan: Fix Supabase Import and Activate Real Data

## Current Status (14/05/2026)

### ✅ Completed
- **PDF Extraction:** 90 PDFs processed → 25 records extracted → 24 validated (seasonal filtering)
- **Data Validation:** Records grouped by heating season (Oct-May), June-Sep excluded
- **JSON Export:** Validated data in `supabase_import_cleaned.json` with 24 records across 4 seasons:
  - 2022/23: 5 records = 63,816 kWh
  - 2023/24: 7 records = 81,732 kWh
  - 2024/25: 7 records = 98,959 kWh
  - 2025/26: 5 records = 80,982 kWh (through March 16)
- **Frontend Code:** ML63.html already contains async code to fetch from Supabase and render charts dynamically

### ❌ Blocked
- **Supabase Import:** All 24 import attempts failed:
  - 12 records: "row violates row-level security policy"
  - 12 records: "division by zero" error (code 22012)
- **Charts Display:** Empty because `consumos_suministros` table has no data

### 🔧 Root Causes to Diagnose
1. RLS (Row Level Security) policies blocking inserts
2. Database trigger or computed column with division operation
3. CHECK constraint with invalid formula
4. DEFAULT value that divides by zero

---

## Step-by-Step Fix Procedure

### STEP 1: Access Supabase Dashboard (5 mins)

1. Go to: https://supabase.com/dashboard
2. Project: **ML63** (byqtsuskdbgwpyvyiprc)
3. Keep dashboard open for diagnosis

### STEP 2: Run Diagnostic Queries (SQL Editor)

Open **SQL Editor** → Create New Query → Run each:

```sql
-- Query 1: Check for RLS policies
SELECT
  tablename,
  policyname,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE tablename = 'consumos_suministros';
```

**Expected:** Should show any RLS policies. If empty, RLS might be the issue.

```sql
-- Query 2: Check for triggers
SELECT
  tgname AS trigger_name,
  tgtype,
  pg_get_triggerdef(oid) AS definition
FROM pg_trigger
WHERE tgrelid = 'consumos_suministros'::regclass;
```

**Expected:** Should list any triggers. Look for division operations.

```sql
-- Query 3: Check table structure
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_name = 'consumos_suministros'
ORDER BY ordinal_position;
```

**Expected:** Should show all columns. Look for any DEFAULT that divides.

### STEP 3: Run Test Insert (SQL Editor)

```sql
INSERT INTO consumos_suministros (
  fecha_inicio,
  fecha_fin,
  consumo_kwh,
  tipo_suministro,
  proveedor,
  numero_factura,
  consumo_valido,
  validacion_notas
) VALUES (
  '2026-04-01'::date,
  '2026-04-15'::date,
  100,
  'gas',
  'TEST',
  'TEST_001',
  true,
  'Test insert'
);
```

**If succeeds:** RLS/triggers not blocking. Continue to step 5.
**If fails:** Note the exact error message and proceed to STEP 4.

### STEP 4: Fix RLS or Triggers (Based on Error)

**If error mentions "policy" or "row-level security":**

```sql
-- Option A: Temporarily disable RLS for testing
ALTER TABLE consumos_suministros DISABLE ROW LEVEL SECURITY;

-- Then re-run STEP 3 test insert
-- If successful, re-enable RLS before importing all records:
ALTER TABLE consumos_suministros ENABLE ROW LEVEL SECURITY;

-- Option B: Create permissive policy (if you want to keep RLS enabled)
CREATE POLICY "Allow gas data inserts" ON consumos_suministros
  FOR INSERT
  WITH CHECK (true);
```

**If error mentions "division" or "22012":**

1. Check the trigger definitions from Query 2
2. Either:
   - DROP the problematic trigger: `DROP TRIGGER trigger_name ON consumos_suministros;`
   - Fix the trigger function to handle NULL values
   - Remove any DEFAULT with division

3. Run STEP 3 test insert again

**If error mentions "constraint":**

```sql
-- Find problematic constraint
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'consumos_suministros';

-- Drop if needed
ALTER TABLE consumos_suministros DROP CONSTRAINT constraint_name;
```

### STEP 5: Verify Fix Works

1. Run STEP 3 test insert again
2. If successful: `SELECT * FROM consumos_suministros WHERE numero_factura = 'TEST_001';`
3. Delete test record: `DELETE FROM consumos_suministros WHERE numero_factura = 'TEST_001';`

### STEP 6: Import All 24 Records

**Option A: Python Script (Automatic)**

```bash
cd /Users/eduardosr/Documents/GitHub/ML63
python3 import_to_supabase_v2.py
```

Select option 1 (use existing credentials) or provide new API key if needed.

**Option B: Direct SQL (Manual)**

In SQL Editor, paste this generated INSERT statement:

```sql
-- Run this SQL to import all 24 records at once
INSERT INTO consumos_suministros (
  fecha_inicio, fecha_fin, consumo_kwh, tipo_suministro,
  proveedor, numero_factura, consumo_valido, validacion_notas
) VALUES
('2022-12-21', '2023-01-16', 10402, 'gas', 'Comercializadora Regulada', 'FE231370018903', true, 'Extraído de FE23137001890342.pdf'),
('2023-01-17', '2023-02-15', 27263, 'gas', 'Comercializadora Regulada', 'FE231370043109', true, 'Extraído de FE23137004310957.pdf'),
-- ... [remaining 22 records] ...
```

*Full SQL will be generated by the Python script*

### STEP 7: Verify Import Success

```sql
-- Check total records
SELECT COUNT(*) as total_records, SUM(consumo_kwh) as total_kwh
FROM consumos_suministros;
```

**Expected:** 24 records, 326,589 kWh total

```sql
-- Check by season
SELECT
  CASE
    WHEN fecha_inicio >= '2022-10-01' AND fecha_inicio < '2023-10-01' THEN '2022/23'
    WHEN fecha_inicio >= '2023-10-01' AND fecha_inicio < '2024-10-01' THEN '2023/24'
    WHEN fecha_inicio >= '2024-10-01' AND fecha_inicio < '2025-10-01' THEN '2024/25'
    WHEN fecha_inicio >= '2025-10-01' THEN '2025/26'
  END as season,
  COUNT(*) as records,
  SUM(consumo_kwh) as total_kwh
FROM consumos_suministros
GROUP BY season
ORDER BY season;
```

**Expected:**
```
2022/23: 5 records, 63816 kWh
2023/24: 7 records, 81732 kWh
2024/25: 7 records, 98959 kWh
2025/26: 5 records, 80982 kWh
```

### STEP 8: Verify Charts Display Real Data

1. Open `/Users/eduardosr/Documents/GitHub/ML63/ML63.html` in browser
2. Open DevTools (F12) → Console
3. Should see message: `✅ Gráfico Gas kWh/día actualizado dinámicamente`
4. Three gas consumption charts should display data:
   - **kWh/día por Mes**: 4 colored series (blue, cyan, green, orange)
   - **€/kWh por Temporada**: 4 bars with price per kWh
   - **Consumo Total kWh**: 4 bars with seasonal totals

---

## Files Involved

| File | Purpose | Status |
|------|---------|--------|
| `supabase_import_cleaned.json` | 24 validated records ready to import | ✅ Ready |
| `import_to_supabase_v2.py` | Automated import script with error handling | ✅ Created |
| `SUPABASE_DIAGNOSTIC_GUIDE.md` | Detailed diagnostic procedures | ✅ Created |
| `ML63.html` | Dashboard with dynamic chart rendering | ✅ Already configured |

---

## Timeline Estimate

- **STEP 1:** 2 minutes (Dashboard access)
- **STEP 2:** 3 minutes (Run diagnostics)
- **STEP 3:** 1 minute (Test insert)
- **STEP 4:** 5-10 minutes (Fix based on error)
- **STEP 5:** 1 minute (Verify fix)
- **STEP 6:** 2 minutes (Import records)
- **STEP 7:** 1 minute (Verify import)
- **STEP 8:** 1 minute (Check charts)

**Total: ~15-20 minutes**

---

## Critical Requirements (Per User)

✅ **"no pongas nada por tu cuenta, solo se ponen los gráficos que te diga si tenemos los valores reales"**

- Only real data from PDF-extracted records
- No hardcoded values
- Only display when Supabase has actual data
- Charts are already configured to do this (lines 1675-1788 of ML63.html)

---

## If Import Still Fails

1. **Check API Key:** 
   - Credentials from previous session may have expired
   - Get fresh anon or service_role key from Supabase Dashboard → Project Settings → API Keys

2. **Use Service Role Key:**
   - Service role key bypasses RLS
   - More reliable for bulk imports
   - Use in `import_to_supabase_v2.py` (option 2)

3. **Check Network:**
   - Verify internet connection
   - Some corporate networks block Supabase

4. **Contact Supabase Support:**
   - If division by zero persists after removing triggers
   - May indicate database corruption or hidden function

---

## Success Criteria

✅ Import complete: 24 records in `consumos_suministros`  
✅ Console shows: `✅ Gráfico Gas kWh/día actualizado dinámicamente`  
✅ Charts display real data from Supabase  
✅ No hardcoded values in charts  
✅ Three gas charts visible with all available seasons  

---

**Next Action:** Proceed with STEP 1 (Access Supabase Dashboard)
