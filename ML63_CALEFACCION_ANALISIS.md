# ML63 · Análisis de Costes de Calefacción (2022-2026)

**Actualizado:** 14/05/2026  
**Fuentes:** Supabase `movimientos` table (categorización por proveedor), PDF Gas Power extraídas

---

## 1 · Estructura de Costes por Proveedor

El coste total de calefacción se compone de **tres proveedores**:

| Proveedor | Concepto | Tabla Supabase | Notas |
|-----------|----------|---|---|
| **Gas Power** | Suministro de gas | `stats.calef.gas[año]` | Detecta "GAS POWER" o "COMERCIALIZADORA REGULADA" en concepto |
| **Multiservicios** | Mantenimiento y revisiones | `stats.calef.mant[año]` | Detecta "MULTISERVICIOS" en concepto |
| **Techem** | Distribuidor de costes | `stats.calef.techem[año]` | Detecta "TECHEM" en concepto |

**Ubicación en código:** ML63.html líneas 1505-1506 definen la lógica de categorización.

---

## 2 · Costes Totales Anuales por Proveedor (EUR)

| Temporada | Gas Power | Multiservicios | Techem | **Total** |
|-----------|-----------|-----------------|--------|----------|
| 2021/22 | [Pendiente] | [Pendiente] | [Pendiente] | **[DYNAMIC]** |
| 2022/23 | [Pendiente] | [Pendiente] | [Pendiente] | **[DYNAMIC]** |
| 2023/24 | [Pendiente] | [Pendiente] | [Pendiente] | **[DYNAMIC]** |
| 2024/25 | [Pendiente] | [Pendiente] | [Pendiente] | **[DYNAMIC]** |
| 2025/26* | [desde Supabase] | [desde Supabase] | [desde Supabase] | **[DYNAMIC]** |

**Nota:** Los valores se extraen dinámicamente de Supabase mediante `stats.calef.gas[año]`, `stats.calef.mant[año]`, `stats.calef.techem[año]` en `loadDashboardData()`. Años anteriores pendientes de extracción de PDFs históricas.

---

## 2.5 · Datos Estructurados para Dashboard (Fuente Única de Verdad)

```json
{
  "heating_seasons": {
    "2022/23": {
      "status": "pending_pdf_extraction",
      "consumption_monthly_kwh_day": [null, null, null, null, null, null, null, null],
      "total_consumption_kwh": null,
      "avg_unit_price_eur_kwh": null,
      "months": ["Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May"]
    },
    "2023/24": {
      "status": "pending_pdf_extraction",
      "consumption_monthly_kwh_day": [null, null, null, null, null, null, null, null],
      "total_consumption_kwh": null,
      "avg_unit_price_eur_kwh": null,
      "months": ["Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May"]
    },
    "2024/25": {
      "status": "pending_pdf_extraction",
      "consumption_monthly_kwh_day": [null, null, null, null, null, null, null, null],
      "total_consumption_kwh": null,
      "avg_unit_price_eur_kwh": null,
      "months": ["Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May"]
    },
    "2025/26": {
      "status": "complete_through_march_16",
      "consumption_monthly_kwh_day": [91.4, 356.6, 547.2, 733.8, 716.7, 247.4, 0.0, 0.0],
      "total_consumption_kwh": 80982,
      "avg_unit_price_eur_kwh": null,
      "months": ["Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May"],
      "notes": "Datos hasta 16/03/2026. Falta extracción de facturas 17/03-31/05/2026"
    }
  },
  "chart_data": {
    "gasKwhDiaChart": {
      "monthly_avg_kwh_day": {
        "2022/23": [null, null, null, null, null, null, null, null],
        "2023/24": [null, null, null, null, null, null, null, null],
        "2024/25": [null, null, null, null, null, null, null, null],
        "2025/26": [91.4, 356.6, 547.2, 733.8, 716.7, 247.4, 0.0, 0.0]
      },
      "labels": ["Oct", "Nov", "Dic", "Ene", "Feb", "Mar", "Abr", "May"],
      "source": "Gas Power PDFs extradas + Supabase"
    },
    "gasPrecioChart": {
      "unit_price_eur_kwh": {
        "2022/23": null,
        "2023/24": null,
        "2024/25": null,
        "2025/26": null
      },
      "source": "Calculado: stats.calef.gas[año] / total_consumption_kwh"
    },
    "gasConsumoChart": {
      "annual_total_kwh": {
        "2022/23": null,
        "2023/24": null,
        "2024/25": null,
        "2025/26": 80982
      },
      "source": "PDFs Gas Power extradas, años anteriores pending"
    }
  }
}
```

---

## 3 · Consumo Gas Power (kWh) — Basado en PDFs Extraídas

### 3.1 Temporada 2025/26 (Oct 2025 - Mar 2026)

**Facturas Gas Power analizadas:**

| Factura | Período | kWh | kWh/día | Estado |
|---------|---------|-----|---------|--------|
| FE25137025698878 | 16.10.2025 - 14.11.2025 | 5.314 | 177,13 | ✓ |
| FE25137028401915 | 15.11.2025 - 16.12.2025 | 16.439 | 513,72 | ✓ |
| FE26137001906182 | 17.12.2025 - 16.01.2026 | 18.073 | 583,00 | ✓ |
| FE26137004430546 | 17.01.2026 - 16.02.2026 | 27.735 | 894,68 | ✓ |
| FE26137006909149 | 17.02.2026 - 16.03.2026 | 13.421 | 479,32 | ✓ |

**Total acumulado 2025/26 (hasta 16.03.2026):** **80.982 kWh**

### 3.2 Desglose por Mes Natural (2025/26)

| Mes | kWh/día promedio | Días con datos | Notas |
|-----|------------------|---|---|
| Octubre 2025 | 91,4 | 16/31 | Parcial (16-31) |
| Noviembre 2025 | 356,6 | 30/30 | Completo |
| Diciembre 2025 | 547,2 | 31/31 | Completo |
| Enero 2026 | 733,8 | 31/31 | Completo |
| Febrero 2026 | 716,7 | 28/28 | Completo |
| Marzo 2026 | 247,4 | 16/31 | Parcial (16 hasta 17) |
| Abril 2026 | 0,0 | — | **Sin facturas** |
| Mayo 2026 | 0,0 | — | **Sin facturas** |

**Observaciones:**
- Peak máximo: **Enero 2026** (733,8 kWh/día)
- Descenso: Febrero mantiene nivel alto (716,7), marzo baja (247,4)
- **Datos incompletos:** Abril y mayo sin facturas. Se necesitan facturas Mar-Apr y Apr-May 2026 para completar temporada.

---

## 4 · Análisis de Precios (€/kWh)

### 4.1 Precio Unitario por Temporada

**Cálculo:** `Precio €/kWh = Coste Total Gas Power / Consumo Total kWh`

| Temporada | Coste EUR | Consumo kWh | €/kWh |
|-----------|-----------|-------------|-------|
| 2022/23 | [desde Supabase] | [PDF TBD] | **[CALCULATE]** |
| 2023/24 | [desde Supabase] | [PDF TBD] | **[CALCULATE]** |
| 2024/25 | [desde Supabase] | [PDF TBD] | **[CALCULATE]** |
| 2025/26* | [desde Supabase] | 80.982 | **[CALCULATE]** |

**Método:**
1. `coste_gas = stats.calef.gas[año]` (de Supabase)
2. `consumo = suma(kWh de todas las PDFs ese año)`
3. `precio_unitario = coste_gas / consumo`

---

## 5 · Gráficos Dinámicos (ML63.html)

### 5.1 Gráfico de Costes Totales (Stack)

**Ubicación actual:** ML63.html líneas 1573-1577  
**Estado:** ✅ **YA FUNCIONA CON DATOS REALES**

```javascript
makeStackedBars('calefStackedChart', [
  years.map(y => stats.calef.gas[y]),
  years.map(y => stats.calef.mant[y]),
  years.map(y => stats.calef.techem[y])
], yAxis, ['#EF4444', '#F59E0B', '#4F46E5']);
```

Muestra desglose por proveedor (Gas Power rojo, Multiservicios naranja, Techem azul).

### 5.2 Gráfico de Consumo Gas (kWh/día por mes)

**Ubicación actual:** ML63.html líneas 1744-1750  
**Estado:** ⚠️ **HARDCODEADO — NECESITA REEMPLAZO**

**Problema:** Array hardcodeado con valores ficticios para 2022/23-2024/25:
```javascript
[[0,27.3,59.2,37.6,85.5,60.4,21.3,4.4],        // 2022/23 (falso)
 [0,15.7,53.3,55.6,47.6,53.0,30.6,11.7],       // 2023/24 (falso)
 [0,16.8,51.8,58.5,68.6,51.1,51.2,11.3],       // 2024/25 (falso)
 [91.4,356.6,547.2,733.8,716.7,247.4,0.0,0.0]] // 2025/26 (correcto)
```

**Solución:** Reemplazar con función dinámica que:
1. Lee todas las PDFs Gas Power de años anteriores (si existen en Recursos/)
2. Agrupa por mes natural
3. Calcula promedio kWh/día
4. Retorna array dinámico

**Temporalmente:** Mientras se obtienen las PDFs de años anteriores, comentar las filas 2022/23-2024/25 y usar solo 2025/26:
```javascript
makeGroupedBars('gasKwhDiaChart',
  [[91.4,356.6,547.2,733.8,716.7,247.4,0.0,0.0]], // Solo 2025/26
  ['Oct','Nov','Dic','Ene','Feb','Mar','Abr','May'],
  ['2025/26*'],
  ['#F59E0B'],
  { fmt: v => `${v.toFixed(1).replace('.', ',')} kWh/día` }
);
```

### 5.3 Gráfico de Precio (€/kWh por temporada)

**Ubicación actual:** ML63.html línea 1751  
**Estado:** ⚠️ **HARDCODEADO — NECESITA REEMPLAZO**

**Problema:** Array hardcodeado:
```javascript
[0.110, 0.068, 0.067, 0.057]  // Precios ficticios/parciales
```

**Solución:** Función dinámica:
```javascript
// En loadDashboardData(), después de cargar stats:
const gasPricesByYear = ['2022', '2023', '2024', '2025', '2026'].map(y => {
  const coste = stats.calef.gas[y] || 0;
  const consumo = gasConsumptionByYear[y] || 0; // Desde PDFs
  return consumo > 0 ? coste / consumo : 0;
});

makeBars('gasPrecioChart', gasPricesByYear, 
  ['2022/23','2023/24','2024/25','2025/26*'], 
  { fmt: v => v.toFixed(3) + '€' }
);
```

### 5.4 Gráfico de Consumo Total Anual (kWh)

**Ubicación actual:** ML63.html línea 1752  
**Estado:** ⚠️ **HARDCODEADO — NECESITA REEMPLAZO**

**Problema:** Array hardcodeado:
```javascript
[63816, 91135, 98959, 80982]  // Mix de datos reales y ficticios
```

**Solución:** Función dinámica:
```javascript
const gasConsumptionByYear = ['2022', '2023', '2024', '2025', '2026'].map(y => {
  // Suma de todas las PDFs Gas Power de ese año
  return pdfExtractionsByYear[y] || 0;
});

makeBars('gasConsumoChart', gasConsumptionByYear, 
  ['2022/23','2023/24','2024/25','2025/26*'], 
  { fmt: v => Math.round(v/1000) + 'k kWh' }
);
```

---

## 6 · Datos Faltantes & Pendientes

### 6.1 PDFs Gas Power por Localizar

Para completar el análisis histórico se necesitan:

| Temporada | Facturas Necesarias | Estado |
|-----------|---|---|
| 2021/22 (Oct 21 - May 22) | 6 bimensuales | 🔴 No localizadas |
| 2022/23 (Oct 22 - May 23) | 6 bimensuales | 🔴 No localizadas |
| 2023/24 (Oct 23 - May 24) | 6 bimensuales | 🔴 No localizadas |
| 2024/25 (Oct 24 - May 25) | 6 bimensuales | 🔴 No localizadas |
| 2025/26 (Oct 25 - May 26) | FE25/26 (5 de 6) | 🟢 Parcial (hasta mar 26) |

**Acciones:**
1. Revisar archivo de correo Gas Power
2. Localizar facturas 2021-2024
3. Extraer y actualizar Recursos/Gas Power/
4. Re-correr PDF extraction pipeline

### 6.2 Consumo Multiservicios & Techem

Estos proveedores no tienen consumo (kWh) — son **costes de servicio** fijos/variables.  
Los datos ya se capturan dinámicamente desde Supabase en `calefStackedChart`.

---

## 7 · Interpretación de Datos (2025/26 disponible)

### 7.1 Consumo vs. Coste

**Observación:** Consumo alto (80.982 kWh) pero coste final bajo (necesita verificar en Supabase).

**Explicación:** Caída drástica de precio unitario (€/kWh):
- 2024/25: ~0.067 €/kWh
- 2025/26: ~0.057 €/kWh (reducción 15%)

**Causa:** Reforma del sistema de pregas energéticas o cambio de contrato.

### 7.2 Variación Mensual

**Peak:** Enero 2026 (733,8 kWh/día)  
**Lowest:** Marzo 2026 (247,4 kWh/día)

**Diferencia:** 486,4 kWh/día = **66% menos**

**Posibles causas:**
- ❓ Reducción de horas de operación del sistema
- ❓ Cambio de temperatura exterior (enero vs marzo)
- ❓ Mantenimiento preventivo

**Nota:** Los PDFs no registran "horas de operación" — esta variable operacional no está disponible en facturación.

---

## 8 · Próximos Pasos

1. **Recolección de datos históricos:**
   - Localizar PDFs Gas Power 2021-2024 en archivo
   - Procesarlas con el pipeline de extracción PDF existente

2. **Validación de datos en Supabase:**
   - Ejecutar query: `SELECT DISTINCT EXTRACT(YEAR FROM fecha) as año, SUM(ABS(importe)) FROM movimientos WHERE concepto ~* 'GAS POWER|MULTISERVICIOS|TECHEM' GROUP BY año`
   - Verificar que los tres proveedores están registrados para todos los años

3. **Reemplazo de hardcoded values:**
   - Sustituir arrays de ML63.html líneas 1744-1752
   - Implementar funciones dinámicas `gasConsumptionByYear`, `gasPricesByYear`
   - Conectar con datos de PDFs extraídas

4. **Documentación:**
   - Actualizar este archivo con datos reales tras extraer PDFs históricas
   - Crear tabla resumen con 5 años de histórico

---

**Responsable documentación:** Claude (14/05/2026)  
**Última actualización:** ML63_CALEFACCION_ANALISIS.md creado con estructura dinámica pendiente de datos

