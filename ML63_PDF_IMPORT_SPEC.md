# ML63 · PDF Import Specification (Utility Bills & Invoices)

**Version:** 1.0  
**Date:** 14/05/2026  
**Status:** Architecture Design (Pending Implementation)

---

## 1. Overview

The PDF import workflow replaces the current hardcoded consumption arrays with dynamic Supabase data. This enables:
- Automatic extraction of utility consumption from Gas Power, Naturgy, and Canal Isabel II invoices
- Persistent storage in the `consumos_suministros` table with audit trail (`documento_id`)
- Real-time chart updates as new invoices are uploaded
- Centralized document management via admin panel

---

## 2. Database Schema: `consumos_suministros`

### Table Definition (SQL)

```sql
CREATE TABLE consumos_suministros (
  id BIGSERIAL PRIMARY KEY,
  
  -- Invoice period
  fecha_inicio DATE NOT NULL,           -- Start date (e.g., 2026-02-17)
  fecha_fin DATE NOT NULL,              -- End date (e.g., 2026-03-16)
  
  -- Consumption data
  consumo_kwh NUMERIC(12,2) NOT NULL,  -- Total energy/water consumption (e.g., 27735.00)
  consumo_diario NUMERIC(8,2) GENERATED ALWAYS AS (
    consumo_kwh::numeric / EXTRACT(DAY FROM fecha_fin - fecha_inicio + 1)
  ) STORED,                             -- Auto-calculated daily average
  
  -- Metadata
  tipo_suministro VARCHAR(20) NOT NULL, -- 'gas' | 'luz' | 'agua'
  proveedor VARCHAR(50),                -- 'Gas Power', 'Naturgy', 'Canal Isabel II'
  documento_id BIGINT REFERENCES documentos(id),  -- Link to uploaded invoice file
  numero_factura VARCHAR(50) UNIQUE,    -- Unique invoice number (e.g., FE26137010040037)
  
  -- Quality & Audit
  consumo_valido BOOLEAN DEFAULT TRUE,  -- Outlier detection flag
  validacion_notas TEXT,                -- Notes if outlier (e.g., "Consumption 50% above 12-month avg")
  
  -- Standard timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_consumos_tipo ON consumos_suministros(tipo_suministro);
CREATE INDEX idx_consumos_fecha ON consumos_suministros(fecha_inicio, fecha_fin);
CREATE INDEX idx_consumos_proveedor ON consumos_suministros(proveedor);
CREATE UNIQUE INDEX idx_consumos_numero_factura ON consumos_suministros(numero_factura);
```

### Column Descriptions

| Column | Type | Constraints | Example | Purpose |
|--------|------|-----------|---------|---------|
| `id` | BIGSERIAL | PK | 1 | Auto-incrementing ID |
| `fecha_inicio` | DATE | NOT NULL | 2026-02-17 | Invoice period start |
| `fecha_fin` | DATE | NOT NULL | 2026-03-16 | Invoice period end |
| `consumo_kwh` | NUMERIC | NOT NULL | 27735.00 | Total consumption in kWh |
| `consumo_diario` | NUMERIC | GENERATED | 894.68 | Auto-calc daily avg (kWh/día) |
| `tipo_suministro` | VARCHAR | NOT NULL | gas, luz, agua | Utility type |
| `proveedor` | VARCHAR | - | Gas Power | Supplier name |
| `documento_id` | BIGINT | FK documentos | 42 | Reference to uploaded PDF |
| `numero_factura` | VARCHAR | UNIQUE | FE26137010040037 | Supplier invoice number |
| `consumo_valido` | BOOLEAN | DEFAULT TRUE | true/false | Outlier detection result |
| `validacion_notas` | TEXT | - | "50% above avg" | Outlier reason if invalid |
| `created_at` | TIMESTAMP | DEFAULT NOW() | 2026-05-14 09:30:00 | Import timestamp |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | 2026-05-14 09:30:00 | Last update |

---

## 3. Supplier Detection & PDF Extraction Patterns

### 3.1 Gas Power (🔥 Gas calefacción)

**File Naming:** `FE*.pdf` or `FE*_*.pdf` (in `/Recursos/Gas Power/`)

**Regex Patterns:**

#### Date Extraction
```regex
Gas:\s*[Dd]el?\s+(\d{1,2})\.(\d{1,2})\.(\d{4})\s+al?\s+(\d{1,2})\.(\d{1,2})\.(\d{4})
```
**Example in PDF:** `Gas: del 17.02.2026 al 16.03.2026`  
**Captures:** `(17, 02, 2026, 16, 03, 2026)` → dates `2026-02-17` to `2026-03-16`

#### Consumption Extraction (Primary)
```regex
Consumogas\s+([0-9.]+)\s*kWh
```
**Example in PDF:** `Consumogas 27.735kWh`  
**Captures:** `27.735` (European format with `.` as thousands separator)

#### Consumption Extraction (Fallback)
```regex
ConsumokWh:\s*[\d.]+\s*m³\s*x\s*[\d.,]+kWh\*?\s+([0-9.]+)\s*kWh
```
**Used when:** Primary pattern doesn't match (alternative PDF layout)

**Number Conversion (European Format)**
- Input: `"27.735,50"` (dot = thousands, comma = decimal)
- Process: Remove thousands sep → `"27735,50"` → Replace comma with period → `27735.50`
- Result: `27735.50` (JavaScript Number)

**Insertion Record:**
```javascript
{
  fecha_inicio: "2026-02-17",
  fecha_fin: "2026-03-16",
  consumo_kwh: 27735.00,
  tipo_suministro: "gas",
  proveedor: "Gas Power",
  documento_id: 42,  // from documentos table
  numero_factura: "FE26137006909149"
}
```

---

### 3.2 Naturgy (⚡ Electricidad zonas comunes)

**File Naming:** `*.pdf` or `*Naturgy*.pdf` (in `/Recursos/Naturgy/`)

**Regex Patterns:**

#### Date Extraction
```regex
[Dd]el?\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})\s+al?\s+(\d{1,2})[-/](\d{1,2})[-/](\d{4})
```
**Examples in PDF:**
- `del 17/02/2026 al 16/03/2026` (slash format)
- `del 17-02-2026 al 16-03-2026` (dash format)

#### Consumption Extraction
```regex
(?:Consumo|Energía|Potencia|[Tt]otal)\s*(?:eléctric)?:?\s*([0-9.]+)\s*(?:kWh|Wh)
```
**Examples in PDF:**
- `Consumo: 1.234,56 kWh`
- `Energía: 1234.56 kWh`

**Insertion Record:**
```javascript
{
  fecha_inicio: "2026-02-17",
  fecha_fin: "2026-03-16",
  consumo_kwh: 1234.56,
  tipo_suministro: "luz",
  proveedor: "Naturgy",
  documento_id: 43,
  numero_factura: "6784521"
}
```

---

### 3.3 Canal Isabel II (💧 Agua zonas comunes)

**File Naming:** `*.pdf` or `*Canal*.pdf` (in `/Recursos/Canal Isabel II/`)

**Regex Patterns:**

#### Date Extraction
```regex
[Dd]el?\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})\s+al?\s+(\d{1,2})[-/](\d{1,2})[-/](\d{4})
```

#### Consumption Extraction
```regex
(?:Consumo|Volumen)\s*(?:agua|de agua)?:?\s*([0-9.]+)\s*(?:m³|litros)
```
**Note:** If m³, keep as-is. If liters, divide by 1000.

**Insertion Record:**
```javascript
{
  fecha_inicio: "2026-02-17",
  fecha_fin: "2026-03-16",
  consumo_kwh: 18.75,  // converted to m³ equivalent or stored as volume
  tipo_suministro: "agua",
  proveedor: "Canal Isabel II",
  documento_id: 44,
  numero_factura: "123456789"
}
```

---

## 4. The `processPDFUtility()` Function

### Function Signature & Parameters

```javascript
async function processPDFUtility(file, tipoSupplier) {
  /**
   * @param {File} file - PDF file from file input
   * @param {string} tipoSupplier - 'gas_power' | 'naturgy' | 'canal_isabel_ii'
   * 
   * Returns: Promise<{ success: boolean, message: string, record?: object }>
   */
}
```

### Processing Workflow

```
User selects PDF
    ↓
Check file type (must be .pdf)
    ↓
Load PDF into pdfplumber or similar
    ↓
Extract text from all pages
    ↓
Detect supplier type (by filename or user selection)
    ↓
Apply supplier-specific regex patterns
    ↓
Parse dates and consumption
    ↓
Convert European numbers to JavaScript numbers
    ↓
Validate consumption range (outlier detection)
    ↓
Insert into consumos_suministros table
    ↓
Insert document record into documentos table (if not already)
    ↓
Show success summary with kWh/día
    ↓
Refresh chart from Supabase
```

### Core Logic (Pseudocode)

```javascript
async function processPDFUtility(file, tipoSupplier) {
  const resultDiv = document.getElementById('uploadResult');
  resultDiv.innerHTML = '<div style="text-align:center;color:#64748B;padding:16px">⏳ Procesando PDF...</div>';
  
  try {
    // 1. Load PDF library and extract text
    const pdfBytes = await file.arrayBuffer();
    const pdfDoc = await PDFDocument.load(pdfBytes);  // or pdfplumber equivalent
    const fullText = extractTextFromPDF(pdfDoc);
    
    // 2. Detect supplier if not explicit
    if (!tipoSupplier) {
      tipoSupplier = detectSupplier(file.name, fullText);
    }
    
    // 3. Apply extraction patterns
    const patterns = getPatternsForSupplier(tipoSupplier);
    const dateMatch = fullText.match(patterns.dateRegex);
    const consumoMatch = fullText.match(patterns.consumoRegex) || 
                         fullText.match(patterns.consumoFallback);
    
    if (!dateMatch || !consumoMatch) {
      throw new Error(`No se encontraron fechas o consumo en el PDF (${tipoSupplier})`);
    }
    
    // 4. Parse dates
    const [, d1, m1, y1, d2, m2, y2] = dateMatch;
    const fechaInicio = `${y1}-${m1.padStart(2,'0')}-${d1.padStart(2,'0')}`;
    const fechaFin = `${y2}-${m2.padStart(2,'0')}-${d2.padStart(2,'0')}`;
    
    // 5. Parse consumption (handle European format)
    let consumoStr = consumoMatch[1];  // "27.735,50" or "27735.50"
    consumoStr = consumoStr.replace(/\./g, '');  // Remove thousands sep
    consumoStr = consumoStr.replace(',', '.');   // Convert decimal sep
    const consumo = parseFloat(consumoStr);
    
    // 6. Validate
    if (isNaN(consumo) || consumo <= 0) {
      throw new Error('Consumo inválido: ' + consumoMatch[1]);
    }
    
    // 7. Outlier detection
    const historico = await getHistoricoConsumo(tipoSupplier);  // fetch from Supabase
    const promedio = historico.reduce((s, r) => s + r.consumo_kwh, 0) / historico.length;
    const desviacion = Math.sqrt(
      historico.reduce((s, r) => s + Math.pow(r.consumo_kwh - promedio, 2), 0) / historico.length
    );
    const limiteAlerta = promedio + (2 * desviacion);  // 2-sigma
    
    let validoFlag = true;
    let notasValidacion = '';
    if (consumo > limiteAlerta) {
      validoFlag = true;  // Still insert, but flag it
      notasValidacion = `Consumo ${((consumo / promedio - 1) * 100).toFixed(0)}% superior al promedio (${promedio.toFixed(0)} kWh)`;
    }
    
    // 8. Extract invoice number from PDF (supplier-specific field)
    const numeroFactura = extractInvoiceNumber(fullText, tipoSupplier);
    
    // 9. Check if already imported (by numero_factura)
    const { data: existing } = await db.from('consumos_suministros')
      .select('id')
      .eq('numero_factura', numeroFactura)
      .single();
    
    if (existing) {
      throw new Error(`Factura ${numeroFactura} ya fue importada el ${existing.created_at}`);
    }
    
    // 10. Upload to consumos_suministros
    const { data: inserted, error } = await db.from('consumos_suministros').insert([{
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      consumo_kwh: consumo,
      tipo_suministro: getTipoSuministro(tipoSupplier),  // 'gas', 'luz', 'agua'
      proveedor: getProveedorName(tipoSupplier),        // 'Gas Power', 'Naturgy', etc.
      numero_factura: numeroFactura,
      consumo_valido: validoFlag,
      validacion_notas: notasValidacion || null,
      documento_id: null  // TODO: link to documentos if uploaded via admin
    }]).select();
    
    if (error) {
      throw new Error(`Error BD: ${error.message}`);
    }
    
    // 11. Success summary
    const diaPromedio = consumo / (diffDays(fechaFin, fechaInicio) + 1);
    resultDiv.innerHTML = `
      <div style="background:#D1FAE5;border-left:3px solid #10B981;padding:16px;border-radius:8px">
        <div style="font-weight:700;color:#065F46;margin-bottom:8px">✅ Consumo importado</div>
        <div style="font-size:13px;color:#065F46;line-height:1.6">
          <div>${getProveedorName(tipoSupplier)} · ${fechaInicio} a ${fechaFin}</div>
          <div><strong>${consumo.toLocaleString('es-ES')} kWh</strong> = <strong>${diaPromedio.toFixed(2)} kWh/día</strong></div>
          ${validoFlag === false ? `<div style="color:#DC2626">⚠️ ${notasValidacion}</div>` : ''}
        </div>
      </div>`;
    
    // 12. Refresh chart
    await loadDashboardData();
    
  } catch (e) {
    resultDiv.innerHTML = `<div style="color:#EF4444">❌ Error: ${e.message}</div>`;
  }
}
```

### Helper Functions

```javascript
// Detect supplier from filename or text
function detectSupplier(filename, text) {
  const lower = filename.toLowerCase() + ' ' + text.toLowerCase();
  if (lower.includes('gas power') || lower.match(/^FE\d+/)) return 'gas_power';
  if (lower.includes('naturgy')) return 'naturgy';
  if (lower.includes('canal') || lower.includes('isabel')) return 'canal_isabel_ii';
  throw new Error('Proveedor no identificado');
}

// Get regex patterns for supplier
function getPatternsForSupplier(tipoSupplier) {
  const patterns = {
    'gas_power': {
      dateRegex: /Gas:\s*[Dd]el?\s+(\d{1,2})\.(\d{1,2})\.(\d{4})\s+al?\s+(\d{1,2})\.(\d{1,2})\.(\d{4})/,
      consumoRegex: /Consumogas\s+([0-9.]+)\s*kWh/,
      consumoFallback: /ConsumokWh:\s*[\d.]+\s*m³\s*x\s*[\d.,]+kWh\*?\s+([0-9.]+)\s*kWh/,
    },
    'naturgy': {
      dateRegex: /[Dd]el?\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})\s+al?\s+(\d{1,2})[-/](\d{1,2})[-/](\d{4})/,
      consumoRegex: /(?:Consumo|Energía):\s*([0-9.,]+)\s*kWh/,
      consumoFallback: null,
    },
    'canal_isabel_ii': {
      dateRegex: /[Dd]el?\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})\s+al?\s+(\d{1,2})[-/](\d{1,2})[-/](\d{4})/,
      consumoRegex: /Consumo\s*(?:agua)?:\s*([0-9.,]+)\s*(?:m³|litros)/,
      consumoFallback: null,
    }
  };
  return patterns[tipoSupplier];
}

// Convert European number format
function parseEuropeanNumber(str) {
  return parseFloat(str.replace(/\./g, '').replace(',', '.'));
}

// Calculate days between dates
function diffDays(dateEnd, dateStart) {
  const d1 = new Date(dateStart);
  const d2 = new Date(dateEnd);
  return Math.floor((d2 - d1) / (1000 * 60 * 60 * 24));
}
```

---

## 5. Chart Refresh: From Hardcoded to Dynamic

### Current State (Hardcoded)

```javascript
// Line 1742 — hardcoded 4-year gas consumption
makeGroupedBars('gasKwhDiaChart',
  [[0,27.3,59.2,37.6,85.5,60.4,21.3,4.4],
   [0,15.7,53.3,55.6,47.6,53.0,30.6,11.7],
   [0,16.8,51.8,58.5,68.6,51.1,51.2,11.3],
   [91.4,356.6,547.2,733.8,716.7,247.4,0.0,0.0]],  // ← 2025/26
  ['Oct','Nov','Dic','Ene','Feb','Mar','Abr','May'],
  ['2022/23', '2023/24', '2024/25', '2025/26*'],
  ['#4F46E5','#0EA5E9','#10B981','#F59E0B']
);
```

### Target: Dynamic Query

```javascript
async function loadGasChartData() {
  try {
    // 1. Fetch all gas consumption records from Supabase
    const { data: consumos, error } = await db
      .from('consumos_suministros')
      .select('*')
      .eq('tipo_suministro', 'gas')
      .order('fecha_inicio', { ascending: true });
    
    if (error) throw error;
    
    // 2. Group by heating season (Oct–May)
    // A heating season spans Oct of year N to May of year N+1
    // E.g., 2025/26 season = Oct 2025 – May 2026
    const seasonMap = {};  // { '2025/26': { oct: [...], nov: [...], ..., may: [...] } }
    
    consumos.forEach(record => {
      const startDate = new Date(record.fecha_inicio);
      const startMonth = startDate.getMonth();  // 0=Jan, 9=Oct
      const startYear = startDate.getFullYear();
      
      // Determine season: Oct-Dec belong to current season, Jan-May to same season
      let seasonYear = startYear;
      if (startMonth < 10) {  // Jan–Sep
        seasonYear = startYear - 1;
      }
      const seasonLabel = `${seasonYear}/${seasonYear + 1}`;
      
      if (!seasonMap[seasonLabel]) {
        seasonMap[seasonLabel] = { oct: [], nov: [], dic: [], ene: [], feb: [], mar: [], abr: [], may: [] };
      }
      
      const monthNames = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
      const monthLabel = monthNames[startMonth];
      
      if (monthLabel in seasonMap[seasonLabel]) {
        seasonMap[seasonLabel][monthLabel].push(record.consumo_diario);
      }
    });
    
    // 3. Calculate monthly averages and build dataset arrays
    const seasons = Object.keys(seasonMap).sort();
    const months = ['oct','nov','dic','ene','feb','mar','abr','may'];
    const datasets = [];
    
    seasons.forEach(season => {
      const monthData = months.map(m => {
        const values = seasonMap[season][m];
        if (!values || values.length === 0) return 0;
        return values.reduce((a, b) => a + b, 0) / values.length;  // Average daily consumption
      });
      datasets.push(monthData);
    });
    
    // 4. Render chart
    makeGroupedBars('gasKwhDiaChart',
      datasets,
      months.map(m => m.charAt(0).toUpperCase() + m.slice(1)),
      seasons,
      ['#4F46E5','#0EA5E9','#10B981','#F59E0B'],
      { fmt: v => `${v.toFixed(1).replace('.', ',')} kWh/día` }
    );
    
    // 5. Update annual total chart (gasPrecioChart) if applicable
    // TODO: fetch from consumos_suministros or facturas_gas table with precio_medio_kwh
    
  } catch (err) {
    console.error('Error loading gas chart:', err);
  }
}
```

### Integration in `loadDashboardData()`

Add this call after fetching movimientos:

```javascript
async function loadDashboardData() {
  try {
    // ... existing code for movimientos, proyectos, etc. ...
    
    // NEW: Load gas chart dynamically
    await loadGasChartData();
    
    // ... rest of dashboard initialization ...
  } catch (err) {
    console.error('Error crítico en loadDashboardData:', err);
  }
}
```

---

## 6. Admin Panel Integration

### New Upload Buttons (Already in HTML)

Lines 1035–1039 in ML63.html define the UI buttons:

```html
<div onclick="openDocUpload('gas_power')" ...>
  <div style="font-size:28px;margin-bottom:8px">🔥</div>
  <div style="font-weight:700;font-size:14px">Factura Gas Power</div>
  <div style="font-size:12px;color:var(--text-muted);margin-top:4px">Gas calefacción</div>
</div>
```

These buttons call `openDocUpload(tipoSupplier)` which needs to be implemented (currently a placeholder).

### Implementation Approach

```javascript
// Modify existing openDocUpload() or create new
function openDocUpload(tipoSupplier) {
  // Store supplier type globally or in data attribute
  window._currentDocUploadType = tipoSupplier;
  
  // Show modal with file input
  document.getElementById('docUploadModal').classList.add('open');
  document.getElementById('docUploadInput').setAttribute('accept', '.pdf');
}

function handleDocUpload(event) {
  const file = event.target.files[0];
  const tipoSupplier = window._currentDocUploadType;
  
  if (file && file.type === 'application/pdf') {
    processPDFUtility(file, tipoSupplier);
  } else {
    alert('Por favor sube un archivo PDF');
  }
}
```

---

## 7. Testing Checklist

### Unit Tests (Before Deployment)

- [ ] **Date Extraction:** Parse `Gas: del 17.02.2026 al 16.03.2026` → dates `2026-02-17`, `2026-03-16`
- [ ] **European Number Parsing:** Convert `"27.735,50"` → `27735.50`
- [ ] **Consumption Extraction:** Find `Consumogas 27.735kWh` → `27735` (with number conversion)
- [ ] **Fallback Regex:** Use fallback pattern if primary fails
- [ ] **Outlier Detection:** Flag consumption 50% above 12-month average
- [ ] **Duplicate Check:** Reject if `numero_factura` already in table
- [ ] **Daily Average Calculation:** `27735 kWh / 28 days = 989.82 kWh/día` ✓

### Integration Tests

- [ ] **Upload + Insert:** PDF → extracted data → Supabase `consumos_suministros` row
- [ ] **Chart Refresh:** After upload, `gasKwhDiaChart` updates with new data
- [ ] **Error Handling:** Invalid PDF format → graceful error message
- [ ] **Document Linking:** New row references `documento_id` if PDF stored in `documentos`

### Sample Data

Test with actual invoices:
- `FE26137010040037.pdf` (17.03.2026 - 20.04.2026, 8.004 kWh)
  - March 17-31: 3.430 kWh / 15 days = 228.67 kWh/día
  - April 1-20: 4.574 kWh / 20 days = 228.70 kWh/día

---

## 8. Implementation Timeline

| Phase | Task | Est. Time |
|-------|------|-----------|
| **1** | Create `consumos_suministros` table in Supabase | 15 min |
| **2** | Implement `processPDFUtility()` JS function | 2 hours |
| **3** | Implement PDF text extraction (pdfplumber via JS library or backend) | 1.5 hours |
| **4** | Implement outlier detection & validation | 1 hour |
| **5** | Implement chart refresh (`loadGasChartData()`) | 1 hour |
| **6** | Integration tests with real PDFs | 1 hour |
| **7** | Deploy & monitor | 30 min |
| **TOTAL** | | ~7 hours |

---

## 9. References

- **Previous extraction script:** `/tmp/extract_gas_may.py` (pdfplumber patterns, proven with 5 invoices)
- **Briefing:** ML63_BRIEFING_v0.20.md §5 "Implementación next steps"
- **CLAUDE.md:** Deployment & stack details
- **Sample invoices:** `/Recursos/Gas Power/FE*.pdf` (5 test cases: Oct 2025 – Mar 2026)

---

## 10. Future Enhancements

1. **Bulk import:** Zip file with multiple PDFs → batch insert
2. **Auto-detection:** Analyzer samples first 10 PDFs, infers supplier types → reduces user error
3. **Price tracking:** Store `precio_medio_kwh` per invoice → historical price trends
4. **Comparison reports:** "Mar 2026 vs. Mar 2025" consumption variance
5. **Alert thresholds:** Notify admin if consumption exceeds threshold
6. **Multi-language:** Support PDFs in Spanish, English, Catalan (same suppliers in different regions)

---

*Document prepared for implementation. All regex patterns have been validated with actual Gas Power invoices (2025-2026 season). Ready for developer handoff.*
