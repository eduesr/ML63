# Supabase Import Diagnostic Guide

## Issue Summary
All 24 consumption records failed to import to `consumos_suministros` table:
- **12 records**: "new row violates row-level security policy"
- **12 records**: "division by zero" error (PostgreSQL code 22012)

## Root Cause Diagnosis

### Step 1: Check RLS Policies (Supabase Dashboard)

1. Go to **Supabase Dashboard** → **Authentication** → **Policies**
2. Find table `consumos_suministros`
3. Look for RLS policies that might block INSERT:
   - Check if INSERT policy requires `auth.uid() = user_id` but table has no `user_id` column
   - Check if `auth.role() = 'authenticated'` but you're using `anon` key (no user session)

**To fix RLS blocking inserts:**
```sql
-- Option A: Temporarily disable RLS for testing
ALTER TABLE consumos_suministros DISABLE ROW LEVEL SECURITY;

-- Option B: Create permissive INSERT policy for anon users
CREATE POLICY "Allow anonymous inserts" ON consumos_suministros
  FOR INSERT
  WITH CHECK (true);

-- Option C: Use service_role key (admin) instead of anon key
-- (Requires new API key from Supabase dashboard)
```

### Step 2: Check for Triggers or Computed Columns (SQL Editor)

Run this query in **Supabase SQL Editor** to identify what's causing "division by zero":

```sql
-- 1. List all triggers on the table
SELECT
  tgname AS trigger_name,
  tgtype AS trigger_type,
  pg_get_triggerdef(oid) AS trigger_definition
FROM pg_trigger
WHERE tgrelid = 'consumos_suministros'::regclass;

-- 2. Check for GENERATED columns (computed columns)
SELECT
  column_name,
  is_generated,
  generation_expression
FROM information_schema.columns
WHERE table_name = 'consumos_suministros'
AND is_generated != 'NEVER';

-- 3. Check table constraints
SELECT
  constraint_name,
  constraint_type,
  check_clause
FROM information_schema.table_constraints
WHERE table_name = 'consumos_suministros';
```

### Step 3: Check Table Schema (Supabase Dashboard)

1. Go to **Database** → **Tables** → `consumos_suministros`
2. Verify all expected columns exist:
   - `id` (UUID, Primary Key, Auto-generated)
   - `fecha_inicio` (TEXT or DATE)
   - `fecha_fin` (TEXT or DATE)
   - `consumo_kwh` (INTEGER or NUMERIC)
   - `tipo_suministro` (TEXT)
   - `proveedor` (TEXT)
   - `numero_factura` (TEXT)
   - `consumo_valido` (BOOLEAN)
   - `validacion_notas` (TEXT)
   - `created_at` (TIMESTAMP with timezone, auto-generated)
   - `updated_at` (TIMESTAMP with timezone, auto-updated)

3. Look for any columns with:
   - **DEFAULT VALUE** that divides by zero (e.g., `1/COUNT(...)`)
   - **GENERATED COLUMN** with division in expression
   - **CHECK CONSTRAINT** with division

### Step 4: Run Test Insert (SQL Editor)

```sql
-- Test single insert with all fields
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
  '2026-04-01',
  '2026-04-15',
  100,
  'gas',
  'Gas Power',
  'TEST_001',
  true,
  'Test record'
);

-- If successful, check the inserted row
SELECT * FROM consumos_suministros WHERE numero_factura = 'TEST_001';
```

## Common Causes of "Division by Zero"

1. **Calculated column** dividing by null or zero:
   ```sql
   -- Example: price per kWh = total_price / consumption
   -- If consumption is 0 or null → division by zero
   ALTER TABLE consumos_suministros
   DROP COLUMN precio_por_kwh; -- Remove if exists
   ```

2. **Trigger calculating statistics:**
   ```sql
   CREATE OR REPLACE TRIGGER update_season_stats
   BEFORE INSERT ON consumos_suministros
   FOR EACH ROW
   EXECUTE FUNCTION calc_season_average(); -- This might divide by record count
   ```

3. **Function in DEFAULT clause:**
   ```sql
   -- Check for defaults like:
   cost_per_day NUMERIC DEFAULT (annual_cost / 365)
   ```

## If RLS is the issue:

The "row violates row-level security policy" error occurs when:
- Table has RLS enabled
- INSERT policy requires a condition that doesn't apply
- Common: policy checks for `auth.uid() = owner_id` but:
  - No `owner_id` column exists
  - Using `anon` key (no authenticated user)

**Quick Fix - Run in SQL Editor:**
```sql
-- Temporarily disable RLS (for testing only)
ALTER TABLE consumos_suministros DISABLE ROW LEVEL SECURITY;

-- Re-enable after testing
ALTER TABLE consumos_suministros ENABLE ROW LEVEL SECURITY;

-- OR create open policy
DROP POLICY IF EXISTS "temp_allow_insert" ON consumos_suministros;
CREATE POLICY "temp_allow_insert" ON consumos_suministros
  FOR INSERT
  TO anon
  WITH CHECK (true);
```

## If Using Service Role Key:

If you have a service_role key (admin), it bypasses RLS and can insert directly:

```python
# Update import script to use service_role instead of anon
from supabase import create_client

SUPABASE_URL = "https://byqtsuskdbgwpyvyiprc.supabase.co"
SERVICE_ROLE_KEY = "your_service_role_key"  # From Supabase Dashboard → Project Settings → API Keys

supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
# Now inserts will bypass RLS
response = supabase.table('consumos_suministros').insert(record).execute()
```

## Steps to Fix and Re-import:

1. **Diagnose** using SQL queries above
2. **Fix** by:
   - Disabling RLS temporarily, OR
   - Creating permissive INSERT policy, OR
   - Using service_role key instead of anon key
   - Removing problematic triggers/defaults
3. **Test** with a single test record
4. **Re-run** the Python import script
5. **Verify** with a SELECT query:
   ```sql
   SELECT COUNT(*) as total_records FROM consumos_suministros;
   -- Should show 24 if all imported successfully
   ```

## Next Steps After Successful Import:

Once data is in Supabase, update `ML63.html` to fetch dynamically:

```javascript
// Instead of hardcoded values:
const heatingSeasons = {
  '2025/26': [91.4, 356.6, 547.2, 733.8, 716.7, 247.4, 0.0, 0.0]
};

// Fetch from Supabase:
async function loadHeatingSeasons() {
  const { data, error } = await supabase
    .from('consumos_suministros')
    .select('*')
    .order('fecha_inicio', { ascending: true });

  if (error) {
    console.error('Error loading consumption data:', error);
    return;
  }

  // Process data by season and month
  const heatingSeasons = {};
  // ... process data ...

  return heatingSeasons;
}
```
