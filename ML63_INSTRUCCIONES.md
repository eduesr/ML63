# ML63 · Instrucciones operativas del proyecto · v0.20

> **Qué es este documento.** Reglas, protocolos y fuente de verdad de
> dónde vive cada cosa. NO es un repositorio de datos: los datos viven
> en Supabase. El `.md` es la guía de comportamiento que Claude sigue
> SIEMPRE en este proyecto.
>
> Objetivos: no inventar nada, no malgastar tokens repreguntando lo
> obvio, y mantener trazabilidad de gastos, ahorro y proyectos durante
> los 6-7 años del plan acordado en 2025 (horizonte oficial 2031-2032 tras análisis de viabilidad v0.11).

> **Comunidad.** CP Modesto Lafuente 63 · 28003 Madrid · Cuenta Sabadell
> `0081-7125-93-0001279538` · Titular COM.PROP.C.MODESTO LAFUENTE 63.
>
> **Interlocutor único.** Solo hablo con la presidencia (rol `admin` en
> Supabase). Sube los ficheros desde el upload y decide el orden de
> los proyectos.
>
> **App pública.** `https://esr-design.com/ML63/`

---

## 1. Arquitectura de datos: dónde vive qué

| Capa                   | Almacén                                          | Contenido                                          |
| ---------------------- | ------------------------------------------------ | -------------------------------------------------- |
| Reglas y protocolos    | **Este `.md`** (en repo Git)                     | Comportamiento Claude, censo, glosario, reglas     |
| Frontend               | **`/ML63/`** en `esr-design.com` (Git desplegado)| `index.html` + `/css` + `/js` + `/app`             |
| Datos vivos            | **Supabase**                                     | Proyectos, finanzas, contratos, ficheros, usuarios |
| Documentos fuente      | **Supabase Storage** + Project / Upload (chat)   | PDFs de actas, presupuestos, facturas, extractos   |
| Auth                   | **Supabase Auth** (magic link)                   | Sesiones, roles `admin` / `invitado`               |

**Fuente de verdad por dato:**

- **Reglas, censo, glosario, proveedores recurrentes** → este `.md`.
- **Estructura de la UI** → código del frontend.
- **Compromisos, deudas y caja real** → Supabase (tablas `budgets`,
  `invoices`, `bank_movements`).
- **PDF originales** → Supabase Storage (bucket `documents`).

---

## 2. Regla maestra de fuente de verdad financiera

> **El extracto bancario `finance.xls` (Banc Sabadell) es la ÚNICA
> fuente de verdad para CAJA REAL (lo efectivamente pagado).**

Los presupuestos y las facturas son fases **previas** al pago, no lo
sustituyen:

| Fase           | Pregunta que responde                | Documento origen        | Tabla            |
| -------------- | ------------------------------------ | ----------------------- | ---------------- |
| Presupuesto    | ¿Cuánto vamos a gastar?              | PDF de presupuesto      | `budgets`        |
| Factura        | ¿Cuánto debemos?                     | PDF de factura/recibo   | `invoices`       |
| Cargo bancario | ¿Cuánto hemos pagado realmente?      | Línea del `finance.xls` | `bank_movements` |

Reglas que se derivan de esto:

- Cualquier dato derivado de **caja** (saldo, ahorro, proyecciones,
  saldo disponible del hito 8A) se calcula **solo** desde
  `bank_movements`.
- Cualquier dato derivado de **devengo** (cuánto debemos a cierre de
  mes/año) se calcula desde `invoices`.
- Cualquier dato derivado de **compromiso** (cuánto está reservado por
  presupuestos aceptados) se calcula desde `budgets` con estado
  aceptado.
- Cuando hay discrepancia entre presupuesto, factura y cargo bancario,
  **el cargo bancario manda** para caja. La discrepancia se registra
  como aviso y se conserva la trazabilidad.

### 2.1 Ciclo trifásico presupuesto → factura → cargo

```
budgets          (presupuestos / ofertas)
  ↓ budget_id (FK opcional)
invoices         (facturas recibidas)
  ↓ invoice_id (FK opcional)
bank_movements   (cargos del extracto Sabadell)
```

- Las tres tablas se enlazan a `projects` por `project_id` cuando el
  movimiento corresponde a un proyecto del pull.
- Las relaciones son **opcionales** porque hay casos legítimos:
  - **Cargos sin factura previa**: comisiones bancarias, IRPF.
  - **Facturas sin presupuesto previo**: recibos recurrentes (Naturgy,
    agua, luz).
  - **Presupuestos sin factura final**: ofertas comparativas que no se
    aceptaron.
- **Cardinalidad**: un presupuesto aceptado puede generar varias
  facturas; una factura puede generar varios cargos (pagos aplazados,
  como el ascensor en 2025).

### 2.2 Estrategia de carga incremental del extracto

> Los extractos se suben **mes a mes (o cada dos meses)**, no el
> histórico completo cada vez.

- **Carga inicial (única)**: extracto completo desde 01/01/2021. Todos
  los movimientos se vuelcan a `bank_movements`.
- **Cargas posteriores (recurrentes)**: solo el último período. Antes
  de procesar:
  1. Consulto `MAX(F.Operativa)` en `bank_movements`.
  2. Filtro el extracto subido para procesar **solo movimientos
     posteriores** a esa fecha.
  3. Aplico la regla de duplicados de §9.3 por seguridad.
- **No reimporto histórico**.
- **Recálculos derivados** (ratios, medias móviles, proyecciones,
  KPIs): siempre **en tiempo de consulta** desde las tablas. Nunca
  agregados pre-calculados que puedan quedar desfasados.
- **Auditoría**: cada `finance.xls` subido se guarda en Storage para
  trazabilidad, pero el dato fuente son las filas de `bank_movements`.

---

## 3. Stack técnico

### 3.1 Frontend

- **HTML + CSS + JS vanilla**, sin build, sin frameworks, sin npm.
- **Supabase JS** desde CDN: `@supabase/supabase-js@2`.
- **Chart.js** desde CDN para gráficos.
- Una única SPA: `index.html` muestra login si no hay sesión y la app
  completa si la hay.

### 3.2 Backend

- **Supabase** (PostgreSQL + Auth + Storage).
- Auth: **magic link** vía email.
- Roles: `admin` (escritura total) e `invitado` (lectura filtrada).
- Row-Level Security activo en TODAS las tablas con datos.

### 3.3 Despliegue

- Repo Git → push a `main` → desplegado en `https://esr-design.com/ML63/`.

---

## 4. Estructura del repo

```
/ML63/
├── index.html              # Punto de entrada · login + SPA
├── README.md
├── ML63_INSTRUCCIONES.md
├── /css/
│   ├── base.css
│   ├── layout.css
│   ├── components.css
│   └── theme.css
├── /js/
│   ├── supabase-client.js
│   ├── auth.js
│   ├── router.js
│   ├── format.js
│   ├── upload.js
│   └── charts.js
├── /app/
│   ├── tab-2026.js
│   ├── tab-2025.js
│   ├── tab-energia.js
│   ├── tab-gastos.js
│   ├── tab-gestion.js
│   ├── tab-plan.js         # Plan plurianual + proyección 8A
│   └── tab-admin.js
└── /assets/
```

---

## 5. Reglas de comportamiento de Claude

### 5.1 Lo que SIEMPRE hago

- Cuando se sube un fichero nuevo: calculo `sha256`, consulto Supabase
  (tabla `documents`) para detectar duplicados, **recalculo derivados**
  y **propongo nueva versión del `.md`** si hay cambios estructurales.
- Para `finance.xls`: aplico §2.2 (carga incremental).
- Para PDFs de **presupuestos**: extraigo proveedor, fecha, validez,
  importe, conceptos. Inserto en `budgets`. Enlazo a proyecto si se
  indica.
- Para PDFs de **facturas/recibos**: extraigo proveedor, fecha, número,
  importe, conceptos. Inserto en `invoices`. Si existe presupuesto
  previo del mismo proveedor con importe similar, propongo enlazar.
- Para movimientos del **extracto bancario**: tras insertar en
  `bank_movements`, busco facturas en `invoices` con (proveedor +
  importe + fecha cercana) y propongo enlazar.
- **Detecto duplicados** con criterio §9.3 (misma fecha + mismo
  importe). Aviso y NO contabilizo.
- **Detecto ficheros ya conocidos** por hash. Si existe en `documents`,
  aviso aunque el nombre sea distinto.
- Uso siempre **EUR español**: `1.234,56 €`. Dos decimales exactos.
- Uso siempre la nomenclatura del censo (§7): `Propiedad XY`. **Nunca**
  nombres ni apellidos de propietarios.
- Aplico el **criterio de signos homogéneo** (§9.2): gastos `-`,
  ingresos `+`.
- Cuando el extracto y otra fuente discrepan en caja, **aplico el
  extracto** y registro la discrepancia.
- **Aviso** ante cualquier cambio relevante en datos del edificio,
  proveedores, importes recurrentes, contratos o estado de un proyecto.

### 5.2 Lo que NUNCA hago

- **No clasifico proyectos por prioridad.** El campo `etiqueta` es
  metadato, no se usa para ordenar ni recomendar.
- **No sugiero orden de ejecución** salvo petición explícita.
- **No invento** importes, fechas, presupuestos, proveedores, ni
  esquemas de tabla. Si un dato no consta, digo "no consta" y pregunto.
- **No uso nombres ni apellidos de propietarios** en NINGÚN output.
- **No llamo "derrama" al acuerdo de trasteros** (§13).
- **No reproduzco** literalmente largos pasajes de actas o contratos.
- **No mantengo tablas de datos vivos en este `.md`**.
- **No uso `localStorage` ni `sessionStorage`** en el frontend.
- **No expongo la `service_role` key de Supabase** en el frontend.
- **No reimporto movimientos bancarios ya almacenados** (§2.2).
- **No descuento del saldo de caja los presupuestos ni las facturas
  pendientes** — solo lo efectivamente pagado en banco. Los
  compromisos y deudas se muestran como información aparte (§11.5).

### 5.3 Cuándo pregunto vs. cuándo actúo

| Situación                                             | Acción              |
| ----------------------------------------------------- | ------------------- |
| Dato faltante para responder                          | Pregunto            |
| Cambio relevante detectado en datos del `.md`         | Aviso, no toco      |
| Duplicado detectado (importe + fecha)                 | Aviso, no cuento    |
| Fichero ya conocido por hash                          | Aviso, no recuento  |
| Conciliación factura↔cargo posible                    | Propongo enlace, espero confirmación |
| Discrepancia entre presupuesto/factura/banco          | Aplico banco para caja, aviso |
| Petición explícita de orden / recomendación           | Lo doy, justificado |
| Esquema de tabla concreto pendiente de SQL real       | Pregunto antes de codear |

---

## 6. Protocolo al subir un fichero nuevo

### 6.1 Flujo común

1. Calculo `sha256` del fichero subido.
2. Consulto `documents` por ese hash.
   - **Hash existe** → aviso "fichero ya procesado el [fecha]".
   - **Hash nuevo, nombre coincide** → aviso "versión nueva del fichero X".
   - **Hash nuevo, nombre nuevo** → continúo.
3. Identifico tipo: presupuesto, factura/recibo, extracto bancario,
   acta, contrato.

### 6.2 Específico por tipo

#### Presupuesto (PDF)

1. Extraigo: proveedor, fecha emisión, validez, importe, conceptos,
   proyecto al que se asocia (si la presidencia lo indica).
2. Inserto en `budgets` con estado `pendiente_aceptacion` por defecto.
3. Subo PDF a Storage.
4. Si hay otros presupuestos del mismo proyecto, los muestro juntos
   para que la presidencia decida cuál aceptar.

#### Factura / recibo (PDF)

1. Extraigo: proveedor, fecha, número factura, importe, IVA,
   conceptos.
2. Compruebo duplicado por (fecha + importe) contra `invoices` y
   `bank_movements`.
3. Busco en `budgets` algún presupuesto del mismo proveedor con
   importe similar y estado `aceptado`. Si lo encuentro, **propongo
   enlazar** (no enlazo automáticamente, espero confirmación).
4. Inserto en `invoices`.
5. Subo PDF a Storage.

#### Extracto bancario (`finance.xls`)

1. Aplico §2.2 (carga incremental).
2. Para cada movimiento nuevo, tras insertar en `bank_movements`:
   busco en `invoices` facturas con (proveedor coincidente + importe
   exacto + fecha ±5 días). Si hay candidata clara, **propongo
   enlazar**.
3. Subo XLS a Storage para auditoría.
4. Recalculo proyección 8A (§11.5).

#### Acta (PDF)

1. Extraigo acuerdos vinculantes y los enlazo con proyectos del pull.
2. Subo PDF a Storage. Inserto en `meetings`.

#### Contrato (PDF)

1. Extraigo proveedor, fechas vigencia, importe, condiciones clave.
2. Inserto en `contracts`.

### 6.3 Cierre

4. Recalculo derivados afectados y resumo cambios.
5. **Propongo nueva versión del `.md`** si hay impacto estructural.

### 6.4 Flujo de archivos: opción A · solo local

> Decisión 07/05/2026: los PDFs y XLS originales **se mantienen solo
> en local** (disco de la presidencia). NO se replican al Storage de
> Supabase. La presidencia es el único punto de entrada de archivos.

```
   Disco local (presidencia)              ← ÚNICO archivo físico
   ~/Documents/GitHub/ML63/...
              │
              ▼
        Subida al chat                    ← canal único hacia Claude
   (botón adjuntar / /upload)
              │
              ▼
   Claude lee, extrae, valida
              │
              ▼
        SQL INSERT generado
              │
              ▼
   Supabase: tablas con DATOS             ← solo datos estructurados
   (movimientos, proyectos,                  (texto, números, fechas)
    documentos, futuras...)
```

**Reglas operativas del flujo:**

- **Archivo físico = solo en local de la presidencia.** Tu disco es el
  único archivo. Recomendable hacer backup propio (Time Machine,
  Drive personal, etc.).
- **Storage de Supabase NO se usa** para archivos PDF/XLS de
  proveedores. Se mantiene vacío para los archivos rutinarios.
- **Claude no tiene acceso al disco local ni al Storage**. Los archivos
  llegan a Claude solo vía: (a) Project Knowledge inicial, (b) subida
  al chat por la presidencia.
- **Los invitados ven datos, no PDFs.** El frontend muestra KPIs,
  gráficos, tablas. Si excepcionalmente algún propietario pide ver
  un PDF concreto, la presidencia se lo facilita por canal externo.
- **`documentos.url`** queda como campo vacío o como ruta de
  referencia local (texto descriptivo tipo `local:2026/Naturgy_2026-04.pdf`).
  No es una URL clicable; es un identificador de "dónde tiene la
  presidencia el archivo en su disco".

**Implicaciones para el `.md`:**

- Cualquier mención previa a "subir el PDF a Storage" queda anulada
  por esta decisión.
- La detección de duplicados por hash sigue siendo crítica (§6.1):
  protege contra subir dos veces el mismo PDF al chat por error.

---

## 7. Censo del edificio

### 7.1 Viviendas (22)

| Planta | A    | B    | C    |
| ------ | ---- | ---- | ---- |
| 1      | 1A   | 1B   | 1C   |
| 2      | 2A   | 2B   | 2C   |
| 3      | 3A   | 3B   | 3C   |
| 4      | 4A   | 4B   | 4C   |
| 5      | 5A   | 5B   | 5C   |
| 6      | 6A   | 6B   | 6C   |
| 7      | 7A   | 7B   | —    |
| 8      | 8A   | 8B   | —    |

- Plantas 1ª–6ª: tres viviendas (A, B, C). Plantas 7ª y 8ª: solo A y B.
- **Propiedad 8A es propiedad de la Comunidad** ("Vivienda CP" o "Piso
  CP"). La ocupaba el portero hasta el despido en 2025. Pendiente
  reforma plurianual estimada en `-30.000,00 €` con ROI esperado
  `≥ +1.000,00 €/mes` una vez ejecutada.

### 7.1b Censo de propietarios y coeficientes

> Fuente: lista oficial CP (documento físico). Verificar con Susana para estado actualizado.
> **⚠️ Cambios de titularidad conocidos** marcados — el documento puede tener más discrepancias.

| Propiedad | Titular registrado | Coef. | Notas |
|-----------|-------------------|-------|-------|
| **Sótano** | **Five West Inversiones, S.L.** | 1,36% | En JGO 04/02/2025 representado por Diego Mariño (mismo rep. que Dimarvi/Lc I). Titularidad Five West confirmada por presidencia — no vendido a Dimarvi. |
| Lc Dcha.  | José Bendahan Pinto | 4,48% | Karaoke |
| **Lc I**  | ~~Five West Inversiones, S.L.~~ → **Dimarvi Properties S.L.** | 11,52% | ⚠️ Vendido a Dimarvi. Rep: Diego Mariño. Inquilino: **Sanitas** (clínica; usa bombas de aire, no calefacción central) |
| 1º A      | Yolanda Mª Fernández Salgueiro | 3,73% | Asiste en persona a juntas. No morosa. |
| 1º B      | Rosario Hernández Recio | 3,73% | Pagos realizados por **Adela Puyo Hernández** (familiar, parentesco exacto desconocido) |
| 1º C      | Elías Bendahan Muyal | 4,39% | |
| 2º A      | José Bendahan Pinto | 3,73% | |
| 2º B      | Consuelo Bendahan Sananes | 3,73% | |
| 2º C      | Yolanda Chocrón Bendahan | 4,39% | |
| 3º A      | Elena Ruth Chocrón | 3,73% | |
| 3º B      | Consuelo Bendahan Sananes | 3,73% | |
| 3º C      | Consuelo Bendahan Sananes | 4,39% | |
| 4º A      | Diana Esther Chocrón | 3,73% | |
| 4º B      | Consuelo Bendahan Sananes | 3,73% | |
| 4º C      | Viviane Rebecca Line Assa | 4,39% | |
| 5º A      | Beatriz Eva Chocrón | 3,73% | |
| 5º B      | Alicia Chocrón Bendahan | 3,73% | |
| 5º C      | Consuelo Bendahan Sananes | 4,39% | |
| 6º A      | Consuelo Bendahan Sananes | 3,73% | |
| 6º B      | Laura Curieses Marina | 3,73% | |
| 6º C      | Viviane Rebecca Line Assa | 4,39% | |
| 7º A      | Eduardo Sánchez Ruiz | 3,86% | Presidente |
| **7º B**  | ~~José Bendahan Pinto~~ → **María Soledad Alonso López** | 4,39% | ⚠️ Vendido. Figura en acta JGE 27/01/2026 como "Mª Soledad Alonso" (titular única). "Pedro" = conviviente, no copropietario registrado. Tiene certificado de discapacidad (obras accesibilidad terraza). |
| 8º B      | José Bendahan Pinto | 3,29% | |
| **8º A**  | **Comunidad de Propietarios** | —     | Sin coeficiente; pendiente reforma |
| **Total** | **14 titulares únicos** (con cambios) | **100,00%** | |

**Concentración de voto destacable:**
- Consuelo Bendahan Sananes: 6 unidades · **23,70%** (mayor propietaria)
- José Bendahan Pinto: 4 unidades · **15,89%** (Lc Dcha + 2A + 8B; 7B vendido)
- **Dimarvi Properties S.L.**: Lc I · **11,52%** (tercer mayor coeficiente; rep. Diego Mariño)
- **Five West Inversiones S.L.**: Sótano · **1,36%** (Diego Mariño actúa como apoderado de Five West en juntas; solo se vendió el Lc I a Dimarvi)

### 7.2 Locales comerciales (2)

- **Local Izq** (Local Izquierda) — **Dimarvi Properties S.L.** (rep. Diego Mariño) · inquilino: **Sanitas** (clínica; bombas de aire, no usa calefacción central). Fuente: acta JGO 04/02/2025.
- **Local Dcho** (Local Derecho) — José Bendahan Pinto · actividad: Karaoke · **tiene inquilina** (no lo explota Bendahan directamente). Quejas de 1ºA por música alta (acta JGE 27/01/2026).

### 7.3 Zonas comunes con contador

- Cuarto Calderas
- Comunidad Caldera (contador agua dedicado)
- Comunidad Limpieza Grifo Basura
- Comunidad 8ºA (zona común planta 8)

### 7.4 Acuerdos de cesión de uso (NO son propiedades)

- **Cuartos comunitarios** (mal llamados "trasteros"): uno por planta,
  aledaños a letra B. Son **elementos comunes** (no figuran en la
  escritura de división horizontal). Algunos pisos los tienen
  **anexionados de facto** a la vivienda.
  - **Acuerdo JGE 27/01/2026**: pisos B (1º al 7º) adquieren el
    cuarto de su planta por **1.200 € c/u** (7 × 1.200 = **8.400 €**
    total). Pagos recibidos en banco (mar-abr 2026) ✅.

    | Fecha      | Pagador banco                  | Piso B | Titular |
    |------------|-------------------------------|--------|---------|
    | 30/03/2026 | CONSUELO BENDAHAN SANANES     | 2º B   | Consuelo Bendahan |
    | 30/03/2026 | CONSUELO BENDAHAN SANANES     | 3º B   | Consuelo Bendahan |
    | 30/03/2026 | CONSUELO BENDAHAN SANANES     | 4º B   | Consuelo Bendahan |
    | 30/03/2026 | CONSUELO BENDAHAN SANANES     | 5º B   | Alicia Chocrón (pagó Consuelo) |
    | 01/04/2026 | MARIA SOLEDAD ALONSO LOPEZ    | 7º B   | Sol Alonso |
    | 06/04/2026 | CURIESES MARINA LAURA         | 6º B   | Laura Curieses |
    | 16/04/2026 | ADELA PUYO HERNANDEZ          | 1º B   | Familiar de Rosario Hernández Recio (nombre operativo) |
  - **Compromiso del propietario**: realizar obra para **eliminar la
    puerta del descansillo** e integrar el espacio dentro de la
    vivienda. Hasta que no se haga esa obra, el cuarto no está
    formalmente integrado. Estado actual: **pendiente de obra por
    cada propietario**.
  - **Pendiente legal**: escritura de División Horizontal + nueva
    medición de coeficientes, en el mismo paquete que los
    **Estatutos** (previsto fin 2026 / inicio 2027).
  - **6ºB**: usaba el cuarto de su planta hasta ene 2026; desalojado
    y llave entregada al Presidente en la JGE.

### 7.5 Contratos puntuales (NO recurrentes)

- **Cesión temporal 8A → Propiedad 7B (Sol)**:
  - Aprobada por unanimidad en JGE **27/01/2026**. Duración: ~10
    semanas desde feb 2026.
  - Motivo: obras de accesibilidad en 7ºB (rampa + barandillas en
    puerta terraza para silla de ruedas; certificado de discapacidad).
  - Pago: **único** de **+1.700,00 €** (17/03/2026). Ya contabilizado.
  - La solicitud escrita inicial no fue aprobada; sí la explicación
    oral en junta.
  - **NO contar como ingreso recurrente en proyecciones** (§11.5).
  - A partir del fin de cesión: 8A vuelve vacío hasta reforma
    plurianual.

---

## 8. Catálogo de proveedores recurrentes

> Lista cerrada de proveedores que generan cargo periódico. **Si
> aparece un proveedor no listado, aviso para añadirlo.**

### 8.1 Energía y suministros

| Proveedor                | Concepto                              | Periodicidad   | Categoría        |
| ------------------------ | ------------------------------------- | -------------- | ---------------- |
| Naturgy Clientes S.A.U.  | Electricidad zonas comunes            | Mensual / bim. | Corriente        |
| Gas Power                | Gas calefacción central               | Mensual        | Corriente        |
| Canal de Isabel II       | Agua (recibo finca)                   | Bimestral      | Corriente        |
| Techem Energy Services   | Repartidores coste calefacción        | Mensual        | Corriente        |
| Multiservicios Tecn. SA  | Mantenimiento caldera gas             | Mensual        | Corriente        |
| Iberext S.A.             | Extintores (revisión anual)           | Anual          | Corriente        |
| ISTA Metering            | Contadores agua (regularización)      | Anual / event. | Corriente / Proy |

### 8.2 Servicios del edificio

| Proveedor                                   | Concepto                          | Periodicidad | Categoría |
| ------------------------------------------- | --------------------------------- | ------------ | --------- |
| Prevent XXI Servicios España SL (D. Cubo)   | Limpieza + cubos basura (cuota actual desde mar 2026: ~517,88 €/mes; antes solo cubos a ~165,77 €/mes) | Mensual | Corriente |
| El Pilar (cesado feb 2026)                  | Limpieza edificio (baja por burofax) | Mensual   | Histórico |
| MJM (cesado abr 2025)                       | Limpieza edificio (anterior)      | Mensual      | Histórico |
| Duplex Elevación                            | Mantenimiento ascensor + averías  | Mensual      | Corriente |
| Telefónica / Movistar                       | Móvil emergencias ascensor (690941447, 18,15 €/mes fijo) | Mensual | Corriente |
| Lasser (desde 25/03/2026)                   | Antena, vídeo y cámaras           | Mensual      | Corriente |
| Prisma (cesado 04/2026)                     | Antena, vídeo y cámaras (anterior)| Mensual      | Histórico |
| Ocaso Seguros · Póliza 303233               | Seguro edificio                   | Anual        | Corriente |
| Protesins                                   | Desinsectación anual              | Anual        | Corriente |

### 8.3 Administración, fiscal y software

| Proveedor / Concepto                  | Detalle                                  | Periodicidad |
| ------------------------------------- | ---------------------------------------- | ------------ |
| **Susana Fernández Robleda**          | Administración externa de la comunidad (desde jul 2024). Cuota: 233,20 €/mes hasta ene 2026; **300,00 €/mes desde feb 2026** (subida aprobada en JGE 27/01/2026). | Mensual |
| AEAT — IRPF retenciones (modelo 111)  | Autoliquidación trimestral               | Trimestral   |
| Conversia                             | LOPD/RGPD cumplimiento                   | Anual        |
| DEH (Dirección Electrónica Habilitada)| Notificaciones electrónicas              | Anual        |
| IESA / Aareon Proptech                | Software gestión comunidades             | Anual (2 cargos) |
| Comisiones bancarias Sabadell         | Comisión + impuesto sobre comisión       | Trimestral   |

### 8.4 Proveedores de obras / actuaciones puntuales

| Proveedor                | Tipo de servicio                              |
| ------------------------ | --------------------------------------------- |
| Pinta Limpio             | Trabajos verticales / descuelgue / sellados   |
| A. Pirtac (Alexandru)    | Albañilería, fontanería, obras menores        |
| Cerrajería Perón         | Cerrajería (puertas, cerraduras, buzones)     |
| Juan Francisco Agudo Pedreño | Fontanería (reparaciones puntuales)       |
| Mundo Reformas y Obras S.L. · CIF B87508784 | Reformas y obras menores — siniestro patinillo A/C 2024 (1.921,04 €) + impermeabilización patio 2025 (660,00 €). C/ Huerta del Cura, 20 · Moraleja de Enmedio. Tel. 671 473 163 (Jorge). info@mundoreformasyobras.com |
| Attias Arquitectura SL   | Servicios técnicos / arquitectura (revisión ITE)   |
| Impernova Servicios Integrales SL | Impermeabilización (obra cubiertas 7B/8B 2022-2024, completada) |

### 8.5 Histórico cerrado (no recurrente)

- **Personal laboral propio (portero)**: nómina, Seguridad Social
  (TGSS), mutua Quirón Prevención, sustituciones puntuales (el
  Portero), valor teórico vivienda 8A. **Cerrado en 2025** con
  despido, finiquito e indemnización (~12.636 € coste salida; embargos
  IRPF posteriores). Genera **ahorro estructural recurrente
  ~13.000 €/año de caja** desde 2026.

### 8.6 Alias de proveedor (regla operativa)

> Un mismo proveedor puede aparecer en `bank_movements` con varias
> grafías. Para no contarlo como proveedores distintos, la tabla
> `providers` tiene un campo `alias` (array de strings) con todas las
> variantes vistas en el banco.

- Regla: cuando un cargo bancario contiene una cadena que coincide
  con cualquier valor de `providers.alias`, el movimiento se asocia
  a ese proveedor.
- El **nombre canónico** se elige por la grafía mayoritaria en el
  histórico del banco (no la más reciente, no la más correcta
  ortográficamente — la mayoritaria, para minimizar normalización).
- Casos conocidos:
  - **Vanessa Álvarez Gómez** (canónico): aparece como `VANESA
    ALVAREZ GÓMEZ` (1×) y `VANESSA ALVAREZ GOMEZ` (3×) → mayoritaria
    `VANESSA`.
  - **Prevent XXI / D. Cubo / Don Cubo**: razón social y nombre
    comercial conviven; canónico = razón social `Prevent XXI
    Servicios España SL`.
- Cuando aparezca un alias nuevo no registrado, **aviso** y propongo
  añadirlo a `providers.alias`.

### 8.7 Alias de propietario (regla operativa)

> Los propietarios pueden aparecer en el banco con nombres completos
> o distintas grafías. La tabla `propietarios` tendrá un campo `alias`
> (array de strings) para identificarlos en transferencias entrantes.
> El **nombre de display** (cómo aparecen en la app) puede diferir del
> nombre legal y del nombre bancario.

| Nombre legal               | Grafía bancaria                  | Alias display | Unidad |
|---------------------------|----------------------------------|---------------|--------|
| María Soledad Alonso López | `MARIA SOLEDAD ALONSO LOPEZ`     | **Sol**       | 7º B   |

- **Regla Soledad → Sol**: cualquier aparición de `SOLEDAD` o
  `MARIA SOLEDAD ALONSO` en el banco se mapea a propietaria "Sol"
  (7º B). Regla aprobada: la grafía bancaria completa es el
  identificador; el display es el nombre coloquial.
- Los cobros de cuotas mensuales llegan por **REMESA RECIBOS Modesto
  Lafuente, 63** (lote SEPA): una sola línea de ingreso agrupa a todos
  los propietarios. Los nombres individuales de propietarios **no
  aparecen en el banco** salvo que paguen por transferencia manual.
- Propietarios que pagan por transferencia manual (identificados):
  - `ALBERTO BENDAHAN SANANES Y TRES MAS C.B.` → 7º B (hasta ~mar 2026; ahora vendido)
  - `FIVE WEST INVERSIONES S.L.` → Lc I + Sótano (última vez: 16/01/2025; vendidos a Dimarvi Properties S.L.; desde feb 2025 pagan por SEPA o domiciliación)
  - `CONSUELO BENDAHAN SANANES` → abonos puntuales
  - `CHOCRON BENDAHAN ELENA RUTH` → 3º A
- **Transferencias no identificadas en banco** (pendiente confirmar con
  Susana):
  - `SARA SILVO MARTIN` (20/01/2025 · 309,21 € + 28/01/2025 · 278,24 €) — no figura en censo
  - `ADELA PUYO HERNANDEZ` → 1º B (familiar de Rosario Hernández Recio; parentesco exacto desconocido). Nombre operativo para cobros y actas.

---

## 9. Reglas contables

### 9.1 Histórico

- Inicio del histórico contable: **01/01/2021**.

### 9.2 Criterio de signos (homogéneo)

> **Regla maestra**: gastos siempre `-`, ingresos siempre `+`. Si una
> fuente original trae signos invertidos, los normalizo al cargar y al
> mostrar.

### 9.3 Detección de duplicados

- Criterio: **misma fecha + mismo importe exacto** = duplicado.
- Aplica a `bank_movements`, `invoices` y `budgets`.
- Acción: aviso y descarto.

### 9.4 Separación de gasto

- **Corriente recurrente** (`gasto_comun`): luz, gas, agua, limpieza,
  ascensor, seguros, comunicaciones, extintores, repartidores,
  mantenimiento caldera, comisiones, IRPF, administración, software
  gestión, LOPD, DEH, desinsectación.
- **Proyectos / obras** (`mejora`): cualquier movimiento asociado a un
  proyecto del pull (§11).

### 9.5 Formato monetario

- EUR español, 2 decimales, separador miles `.`, separador decimal `,`.
- Ejemplos: `1.234,56 €`, `-30.000,00 €`, `+8.400,00 €`.

### 9.6 Cuenta de referencia

- `0081-7125-93-0001279538` (Banco Sabadell).

### 9.7 Cierre de ejercicio (regla firme)

- Año cerrado solo muestra proyectos en estado `completado`.
- Lo que sigue en `pendiente` o `progreso` se **arrastra** al
  siguiente ejercicio.
- Aplica retroactivamente a 2025 y a todos los futuros.

### 9.8 Saldo final cuando hay varios movimientos el mismo día

> Lección aprendida 07/05/2026 al validar la carga inicial.

El extracto Sabadell agrupa los movimientos del mismo día en orden no
cronológico estable. El campo `saldo` de cada fila refleja el saldo
**después de aplicar ese movimiento concreto**, pero el orden en el
archivo no respeta la secuencia real de cargos del día.

**Ejemplo real del 20/04/2026**: dos cargos (agua −737,64 €, Susana
−899,94 €). En el extracto aparecen en orden saldo 28.909,53 → 29.809,47,
pero la cronología real fue saldo inicial → 29.809,47 → 28.909,53.

**Regla operativa para calcular "saldo actual"**:

```sql
-- INCORRECTO (puede devolver un saldo intermedio del último día):
SELECT saldo FROM movimientos ORDER BY fecha DESC, uploaded_at DESC LIMIT 1;

-- CORRECTO: cuando hay varios cargos negativos el mismo día, el saldo
-- cronológicamente último es el MENOR de los saldos de ese día.
SELECT MIN(saldo) FROM movimientos
WHERE fecha = (SELECT MAX(fecha) FROM movimientos);
```

> Esta regla aplica al frontend, KPIs, gráficos y cualquier proyección.
> Implementarla también en el cálculo de "saldo a fin de mes/año" para
> los gráficos históricos.

### 9.9 Regularizaciones de cargos recurrentes

> Lección aprendida 07/05/2026.

Algunos proveedores recurrentes acumulan deuda y la cobran en un
único cargo de regularización en lugar de hacer cargos mensuales
separados. Esto distorsiona los gráficos de "gasto mensual por
proveedor" si no se trata.

**Caso de referencia · administración Susana Fernández Robleda**:

- Cuota habitual hasta enero 2026: **−233,20 €/mes**
- **Subida aprobada en JGE del 27/01/2026**: nueva cuota
  **−300,00 €/mes** desde febrero 2026
- **Hueco**: febrero, marzo y abril 2026 sin cargo mensual
- **20/04/2026**: transferencia única de **−899,94 €** que regulariza
  los 3 meses pendientes a la **nueva tarifa** (3 × 300,00 € =
  900,00 €, los 0,06 € de diferencia son redondeo)

**Regla para gráficos de gasto mensual recurrente**:

- En la **vista cronológica/contable real** (caja): el cargo aparece
  íntegro en el día en que se cobró. **No se redistribuye**.
- En la **vista normalizada** (para análisis de tendencia): el cargo
  acumulado puede repartirse entre los meses correspondientes para no
  distorsionar la serie. Esto es opcional y se aplica solo si la
  presidencia lo pide explícitamente.
- **Regla por defecto**: vista cronológica real. La regularización es
  una característica del flujo bancario y debe verse como tal.
- Si Claude detecta un **cargo anormalmente alto** de un proveedor
  recurrente conocido (>2× la cuota habitual), **avisa** y propone
  marcarlo como regularización en `movimientos.ref1` o en una nota.

### 9.10 Catálogo de cargos atípicos verificados

> Resultado del repaso completo de los 1.304 movimientos (07/05/2026).
> Sirve para que Claude no vuelva a marcar como "atípico" lo que ya
> está explicado, y para que el frontend pueda mostrar tooltips con
> contexto.

#### Obra Impernova · cubiertas 7B/8B (2022-2024) · obra PRE-plan

- **Coste real total**: **−65.729,07 €** (presupuesto inicial **31.111 €**, derrama aprobada **32.000 €**;
  incremento del **111%** sobre presupuesto por hallazgos durante la obra).
- **Periodo**: abril 2022 – junio 2024.
- **Naturaleza**: impermeabilización de las cubiertas de las viviendas
  7B y 8B; incluye reparación de humedades 7ºB (T/593). Obra **anterior al plan plurianual de 2025**.
- **Tres vías de pago** (todas la misma obra, NO triplicar):
  - Cheques bancarios directos: **−38.739,80 €** (cheques 2968586,
    2968588, 2968589, 2968591, 2968592, 2968593, 2968594).
  - Recibos directos a Impernova Servicios Integrales SL: **−5.135,00 €**.
  - Pagos canalizados por BMC (admin anterior): **−21.854,27 €**.
- **NO cuenta en el donut 180k** del plan (§11.6) porque es histórica
  pre-plan. Se documenta para auditoría y trazabilidad de qué se ha
  hecho ya en el edificio.

#### Cheques históricos del extracto — estado de identificación

El extracto Sabadell registra **17 cheques** (2968578–2968595) que totalizan **−45.341,77 €**
entre enero 2021 y diciembre 2023.

**7 ya identificados → Impernova (−38.739,80 €):**

| Cheque | Fecha | Importe | Concepto verificado |
|--------|-------|---------|---------------------|
| 2968586 | 04/04/2022 | −6.000,00 € | Pago a cuenta, inicio obra |
| 2968588 | 28/07/2022 | −10.000,00 € | Pago a cuenta |
| 2968589 | 30/08/2022 | −5.000,00 € | Pago a cuenta |
| 2968591 | 13/03/2023 | −4.667,30 € | Pago a cuenta |
| 2968592 | 13/03/2023 | −6.000,00 € | Pago a cuenta |
| 2968593 | 02/05/2023 | −1.072,50 € | Reparación humedades 7ºB (T/593 cuentas BMC 2022-2023) |
| 2968594 | 02/05/2023 | −6.000,00 € | Pago final |

**5 identificados, importe menor (−2.005,90 €) — cuentas BMC 2022-2023:**

| Cheque | Fecha | Importe | Nota |
|--------|-------|---------|------|
| 2968581-0 | 17/02/2022 | −120,00 € | Gasto menor vía BMC (cuentas 2022-2023) |
| 2968584 | 01/03/2022 | −1.386,00 € | Obra/servicio menor vía BMC (cuentas 2022-2023) |
| 2968587-6 | 19/07/2022 | −327,95 € | Gasto menor vía BMC (cuentas 2022-2023) |
| 2968590 | 05/01/2023 | −170,00 € | Gasto menor vía BMC (cuentas 2022-2023) |

**6 sin identificar (−4.596,07 €) — sin cuentas Alfredo 2021/jul20-jun21:**

| Cheque | Fecha | Importe | Nota |
|--------|-------|---------|------|
| 2968578 | 21/01/2021 | −1.754,50 € | Era Alfredo — sin cuentas disponibles |
| 2968579 | 01/03/2021 | −1.845,00 € | Era Alfredo — sin cuentas disponibles |
| 2968580 | 08/11/2021 | −359,27 €  | Era Alfredo — sin cuentas disponibles |
| 2968582 | 18/01/2022 | −141,41 € | Transición Alfredo/BMC — sin cuentas 2021-2022 disponibles |
| 2968583 | 18/01/2022 | −471,40 € | Transición Alfredo/BMC — sin cuentas 2021-2022 disponibles |
| 2968595-0 | 19/12/2023 | −26,44 €  | Importe pequeño, sin identificar |

Los 3 cheques de 2021 y los 2 de enero 2022 **no pueden ser Impernova** (la obra
empezó en abril 2022). Las cuentas BMC 2021-2022 (ejercicio jul-20/jun-21) no están disponibles;
sin esa documentación no es posible identificarlos.

#### Avería grande del ascensor (3 meses, dic 2025 – feb 2026)

- Duplex Elevación: **3 cargos consecutivos de −1.774,67 €** (cuota
  habitual ~716 €/mes).
- Naturaleza: **avería grande del ascensor**, pago a plazos.
- Coste total: **−5.324,01 €**.
- En el frontend mostrar como anomalía explicada, no como subida de
  cuota.

#### Telefónica · proyecto Petter Movistar (08/04/2026)

- Cargo único de **−200,00 €** vía transferencia.
- Naturaleza: **proyecto puntual del pull (Petter Movistar)** —
  retirada de cableado antiguo solicitada a Movistar.
- Ya marcado como proyecto completado en 2026.
- NO es subida de cuota: la cuota mensual del móvil 690941447
  (18,15 €) sigue su curso normal.

#### Cierre de contratos de limpieza anteriores

- **MJM (05/03/2025, −1.230,57 €)**: cierre de contrato con MJM,
  empresa de limpieza anterior. Servicio insatisfactorio motivó el
  cambio.
- **El Pilar (cesado feb 2026 por burofax)**: empresa intermedia
  entre MJM y Prevent. Sus cargos pequeños finales (−6,05 € el
  19/05/2025, −39,20 € el 02/07/2025) son colas de regularización.

#### Cambio de servicio Prevent · solo cubos → limpieza + cubos

- **Hasta 26/03/2026**: Prevent cobraba **~165,77 €/mes** (solo
  servicio de cubos de basura).
- **Desde 26/03/2026**: cuota subió a **~517,88 €/mes** (limpieza +
  cubos). Sustituye el servicio que prestaba El Pilar.
- NO es regularización ni cargo doble: es **nueva tarifa por nuevo
  alcance del servicio**.

#### Multiservicios Tecnológicos · 05/03/2025 (−1.230,57 €)

- Cuota habitual: ~86,36 €/mes (mantenimiento caldera).
- El cargo del 05/03/2025 incluye **cuota mensual + certificado
  energético** de la caldera, exigencia normativa puntual.

#### Iberext extintores · 22/12/2022 (−513,12 €)

- Cuota habitual: ~166 €/mes.
- Cargo puntual: **renovación anual** del contrato de mantenimiento
  con revisión completa (no es la cuota mensual, es el cargo anual).

#### Gas Power · 28/11/2024 (4 cargos altos el mismo día = ~4.022 €)

- Suma del día: **−4.022,02 €** (1.048 + 1.012 + 814 + 1.147 €
  aproximadamente).
- Naturaleza: **regularización masiva tras facturas atrasadas** que
  llegaron agrupadas.
- En el frontend: si se muestra "gasto de gas en noviembre 2024" debe
  contar este pico, pero también señalarse como atípico.

#### Naturgy 2021-2023 · cargos elevados recurrentes

- Cargos puntuales hasta **−5.516,42 €** en marzo 2022.
- Naturaleza: **crisis energética + tarifa regulada**. Coherente con
  el contexto macroeconómico (precios pico del gas natural).
- Resuelto al renegociar tarifa. La mediana actual 2024-2026
  (~130 €/mes) es muy inferior a la del periodo de crisis.

#### BMC · cargos altos 2023-2024 (eran obras canalizadas, NO honorarios)

- 7 cargos altos entre 1.500 € y 6.000 € en oct 2023 – mar 2024.
- **Suma total: −21.854,27 €**.
- **Naturaleza confirmada**: pagos de la **obra Impernova** que BMC
  adelantaba a Impernova y luego cobraba a la CP en sus recibos.
- **NO eran honorarios desproporcionados** como se interpretó en
  versiones previas del `.md`. Los honorarios reales de BMC eran
  **347,48 €/mes (2022)** y **364,85 €/mes (2023-2024)**.
- Esta confusión llevó a calcular un "ahorro estructural" inflado al
  cambiar a Susana. Cifras corregidas en §16.2 y §16.3.

#### Siniestro patinillo A/C 2024 — Mundo Reformas y Obras + Pedreño

- **Causa**: rotura en patinillo línea A y C, con afectación a varios pisos y portal.
- **Pedreño Fra. 35 (11/06/2024)**: reparación tubería corroída 6ºA y 5ºA — **−1.512,50 €** (pago banco 23/09/2024).
  > El pago bancario del **21/09/2023 a Pedreño (−2.007,50 €)** es un siniestro distinto: "bajada portal y sótano" = **siniestro sótano 2023** (ver bloque más abajo). No confundir con Fra. 35/2024 del patinillo.
- **Mundo Reformas Fra. 37 (15/07/2024)**: techo portal, pago 1/2 — **−674,52 €** (cargo banco 17/07/2024).
- **Mundo Reformas Fra. 42 (24/07/2024)**: techo portal, pago 2/2 — **−674,52 €** (cargo banco 30/07/2024).
- **Mundo Reformas Fra. 39**: pintura armario 3ºC por goteras — **−165,00 €** (cargo 13/08/2024).
- **Mundo Reformas Fra. 40**: saneado + pintura armario 3ºA por goteras — **−209,00 €** (cargo 13/08/2024).
- **Mundo Reformas Fra. 41**: tabique + alicatado baño 6ºA — **−198,00 €** (cargo 13/08/2024).
- **Subtotal Mundo Reformas**: **−1.921,04 €** · **Total siniestro 2024**: **−3.433,54 €**.
- Presupuesto de referencia: **PJ.24.097.01** (techo portal, 11/07/2024).

#### Siniestro patio de luces 2025 — Mundo Reformas y Obras

- **Mundo Reformas Fra. 29 (06/06/2025)**: impermeabilización terraza patio de luces — **−660,00 €** (cargo banco 12/06/2025).
- **Total siniestro 2025**: **−660,00 €**.

#### Bomba calefacción caudal variable (2022-2023) — Multiservicios Tecnológicos

- **Motivo**: adaptación necesaria para instalación de repartidores de costes Techem (obligación legal 2022).
- **Pagos a plazos via Multiservicios**:

| Fecha        | Importe       | Concepto                          |
| ------------ | ------------- | --------------------------------- |
| 07/11/2022   | −1.753,69 €   | Instalación bomba doble, pago 1/3 |
| 05/12/2022   | −1.753,69 €   | Instalación bomba doble, pago 2/3 |
| 05/01/2023   | −1.754,22 €   | Instalación bomba doble, pago 3/3 |
| 07/12/2022   | −435,60 €     | Inspección eficiencia energética  |
| **Total**    | **−5.697,20 €** |                                 |

- Estos cargos son atípicos respecto a la cuota mensual de Multiservicios (~78-89 €/mes) pero están completamente explicados.

#### Siniestro sótano 2023

- **Total**: **−3.569,50 €** en fontanería + albañilería + pintura.
- **NO fue atendido por Caser** (aseguradora de la época) — fue el motivo principal del cambio a Ocaso en la JGO 23/01/2024.
- Documentado en acta JGO 23/01/2024 y en cuentas BMC 2022-2023.
- **Desglose por proveedor** (verificado contra cuentas BMC 2022-2023):
  - **Pedreño** (21/09/2023, banco): "bajada portal y sótano" — **−2.007,50 €**
  - **Albañilería vía BMC** (cheque/recibo BMC): trabajos de albañilería sótano — **−1.562,00 €**
- El cargo bancario 21/09/2023 `JUAN FRANCISCO AGUDO PEDRENO −2.007,50 €` pertenece a **este** siniestro, no al patinillo 2024.

#### Embargos sobre la cuenta (2024-2025)

- **4 cargos** con concepto `EMBARGO COMUNICADO EL DIA X` que totalizan **−1.663,56 €**.
- Formato Sabadell: la fecha del cargo es ~2 semanas posterior a la fecha comunicada al banco.

| Fecha banco | Fecha comunicado | Importe |
|-------------|-----------------|---------|
| 13/08/2024  | 30/07/2024      | −31,29 € |
| 15/04/2025  | 31/03/2025      | −792,35 € |
| 13/05/2025  | 29/04/2025      | −816,05 € |
| 12/06/2025  | 30/05/2025      | −23,87 € |

- **Hipótesis más probable para los 3 de 2025**: los embargos de marzo/abril/mayo 2025
  comenzaron exactamente **un mes después del despido del portero** (24/02/2025, finiquito
  −10.186,44 €). Probable acreedor: **TGSS** (cotizaciones pendientes del periodo de
  liquidación) o **AEAT** (retenciones IRPF del portero no ingresadas), o ejecución de
  **juzgado de lo Social** si el portero impugnó el despido.
- El embargo de **agosto 2024** (31,29 €) es anterior al despido y probablemente
  sin relación con él — deuda administrativa menor independiente.
- **Acreedor no identificado**: el extracto Sabadell no identifica al embargante.
  **Verificar con Susana** para determinar origen exacto y si hay procedimiento activo.

#### Quirón Prevención · cargos erróneos post-despido (resuelto)

- **Hasta enero 2025**: cobros trimestrales pagados sin incidencia (~137–154 €/trimestre).
  Servicio de vigilancia de la salud laboral ligado al contrato del portero.
- **Contrato cancelado** al despedir al portero (febrero 2025). Quirón lo reconoció.
- **Desde abril 2025**: Quirón continuó emitiendo recibos **por error** (reconocido por
  ellos). La CP devuelve cada cargo y avisa a Quirón; Quirón confirma el error:
  - 24/04/2025 −158,06 € → anulado 28/04/2025
  - 22/07/2025 −158,06 € → anulado 29/07/2025
  - 20/10/2025 −158,06 € → anulado 23/10/2025
- **Impacto económico neto: 0 €** — todos los cargos fueron devueltos.
- **Coste atribuible al portero**: el gasto real de Quirón (vigilancia salud laboral)
  forma parte del coste total del servicio de portería. Los ~137–154 €/trimestre
  (~548–616 €/año) deben sumarse al análisis del coste del portero junto con nómina,
  TGSS, mutua y valor de la vivienda 8A.

#### Susana · cargos complementarios (gastos de oficina)

- Además del caso ya documentado (§9.9), hay dos cargos pequeños:
  **−21,00 € el 20/12/2024** y **−31,15 € el 27/11/2025**.
- **Naturaleza**: gastos de oficina de la administración (sello de la
  CP, papelería, etc.) que la administradora factura aparte de su
  cuota mensual fija.
- Esto significa que la administración tiene **dos componentes**:
  cuota mensual (300 €/mes desde feb 2026) + suplidos esporádicos de
  oficina.

#### Impagados SEPA · propietario moroso persistente

- **27 devoluciones** de remesas domiciliadas entre 2022 y 2026, total **−2.161,39 €**.
- El extracto no identifica al propietario devolvente; se requiere cruce con lista de
  cuotas en poder de la administradora (Susana).

| Año  | Devoluciones | Total |
|------|-------------|-------|
| 2022 | 2           | −317,32 € |
| 2023 | 1           | −74,03 € |
| 2024 | 7           | −908,91 € |
| 2025 | 13          | −799,92 € |
| 2026 | 4 (solo ene) | −61,21 € |
| **Total** | **27** | **−2.161,39 €** |

- **Patrón**: escalada clara de 2023 a 2024 y 2025 (13 devoluciones en un año).
  En 2026 ya hay 4 en el primer mes de enero. Indica **al menos un propietario con impago
  sistemático y creciente**, no un error puntual.
- Candidatos conocidos (verificar con Susana): propietario **1ºC** (Elías Bendahan Muyal /
  Ferrín) o el **local izquierda** (Dimarvi / Five West) u otro propietario.
  **1ºA (Yolanda Mª Fernández) descartada** — asiste a juntas y está al corriente.

#### Pintalimpio S.L. · 03/03/2026 (−1.033,34 €)

- **Nombre legal**: PINTALIMPIO S.L. (transferencia, ref. 228554109).
- **Naturaleza probable**: trabajos verticales / descuelgue / sellado (especialidad de la empresa).
- **Contexto de fechas**: mismo período que A. Pirtac (ene-mar 2026, ver bloque siguiente)
  y Cerrajería Perón (03/03/2026, −585,64 €). Pinta Limpio corresponde a un trabajo distinto.
- **Origen sin confirmar**. Acción: verificar concepto con Susana y asignar `proyecto_id`
  en Supabase.

#### A. Pirtac · reparaciones varias ene-mar 2026 (8 pagos, −9.570 €)

8 transferencias verificadas contra facturas. Proyectos independientes entre sí:

| Fra. | Fecha pago  | Importe  | Proyecto / Ubicación |
|------|-------------|----------|----------------------|
| 228  | 05/01/2026  | −704 €   | Bajante + pladur techo + pintura · despacho comunidad *(siniestro sanitas)* |
| 229  | 05/01/2026  | −3.245 € | General agua fría (hierro → multicapa) + azulejos · local y sótano *(siniestro sanitas)* |
| 233  | 22/01/2026  | −726 €   | Avería patinillo líneas C y B · injerto uralita → PVC 110 + mangueta WC · suelo patio *(siniestro sanitas)* |
| 246  | 10/02/2026  | −1.496 € | Avería calefacción 5B/6B · tuberías generales + radiadores + pintura + tarima |
| 248  | 10/02/2026  | −1.595 € | Puerta nueva + pladur + aislante ruido + cerradura · cuarto (basuras o similar) |
| 251  | 18/02/2026  | −528 €   | 3 tubos PVC desagüe · terraza |
| 260  | 13/03/2026  | −968 €   | 3 bajantes + 7 m tubería general · 6º y 7º piso |
| 261  | 13/03/2026  | −308 €   | Agua fría/caliente + sifón + fregadero/lavadora/lavavajillas · portería 8A |

- **Fra. 245** (radiador Alicia Chocrón) **NO es de la comunidad** — aprovechó que Pirtac estaba en el edificio por la avería 5B/6B (Fra. 246) para cambiarle el radiador; ella le pagó directamente a Pirtac. Guardada en la carpeta del proyecto solo como referencia de contexto; **no contabilizar**.
- **Cerrajería Perón** (03/03/2026, −585,64 €) complementa Fra. 248: cerradura exterior y copias de llaves del mismo cuarto.
- Fra. 261 (portería 8A) está relacionada con el proyecto **Alquiler temporal 8A** ya registrado en Supabase.

---

## 10. KPIs económicos por fase

> Cada KPI debe declarar de qué tabla sale y qué responde, para evitar
> mezclar caja con devengo o compromiso.

| KPI                          | Fuente            | Pregunta que responde                        |
| ---------------------------- | ----------------- | -------------------------------------------- |
| Saldo en cuenta              | `bank_movements`  | ¿Qué tenemos hoy en el banco?                |
| Gasto pagado YTD             | `bank_movements`  | ¿Cuánto hemos pagado en lo que va de año?    |
| Ingresos cobrados YTD        | `bank_movements`  | ¿Cuánto hemos cobrado en lo que va de año?   |
| Ahorro neto mes/año          | `bank_movements`  | Ingresos − Gastos por período                |
| Deuda devengada pendiente    | `invoices`        | ¿Cuánto debemos por facturas no pagadas?     |
| Compromiso aceptado pendiente| `budgets`         | ¿Cuánto está reservado por presupuestos aceptados sin factura aún? |
| Saldo disponible 8A          | `bank_movements`  | Saldo banco − compromisos del año en curso del propio plan (§11.5) |
| Avance plan plurianual       | `bank_movements` + `projects` | Hecho / Por hacer sobre objetivo 180k (§11.6) |

> El "saldo disponible 8A" descuenta solo lo que ya está siendo
> pagado o lo que la presidencia ha decidido reservar explícitamente
> dentro del plan. NO descuenta presupuestos ni facturas pendientes
> de proveedores externos.

---

## 11. Pull de proyectos

> Datos vivos en Supabase. Aquí solo el modelo y reglas.

### 11.1 Modelo `projects`

| Campo         | Tipo       | Descripción                                                |
| ------------- | ---------- | ---------------------------------------------------------- |
| `id`          | uuid       | PK                                                         |
| `nombre`      | text       | Nombre del proyecto                                        |
| `año`         | int        | 2025 / 2026 / ...                                          |
| `etiqueta`    | enum       | Alta / Normal / Baja — **metadato heredado, NO prioriza**  |
| `progreso`    | numeric    | 0.00 → 1.00                                                |
| `cat`         | enum       | `pendiente` / `progreso` / `completado`                    |
| `pres`        | numeric    | Presupuesto / aportación con signo                         |
| `obs`         | text       | Observaciones libres                                       |
| `banco_ref`   | text       | Texto libre con referencia al cargo bancario               |
| `created_at`  | timestamp  | Auto                                                       |
| `updated_at`  | timestamp  | Auto                                                       |

### 11.2 Estados de `cat`

- `pendiente` — sin iniciar (`progreso = 0`).
- `progreso` — en curso (`0 < progreso < 1`).
- `completado` — terminado (`progreso = 1`).

### 11.3 Reglas del pull

- **No hay prioridad asignada por Claude.**
- **Imprevistos** (averías, goteras, mejoras urgentes) entran al pull
  como cualquier otro proyecto y **recalculan el plan**.
- **Plan acordado en 2025**, horizonte oficial **6-7 años** (2025-2031/2032), tras análisis de viabilidad v0.11.
- Cada proyecto puede tener:
  - **N presupuestos** (`budgets` con `project_id = X`)
  - **N facturas** (`invoices` con `project_id = X`)
  - **N cargos** (`bank_movements` con `project_id = X`)

### 11.4 Sub-hito Vivienda CP / 8A (dentro del plan plurianual)

> El 8A es un **proyecto del pull**, no un hito independiente. Pero
> tiene una condición de disponibilidad de caja antes de ejecutarse,
> y desbloquea un ingreso futuro relevante (alquiler), por eso se
> trata aparte con su propia proyección.

- **Proveedor candidato para la reforma**: Mundo Reformas y Obras S.L. ya presupuestó la vivienda 8A en **PJ.25.033.01 (21/04/2025)**. Tenerlo en cuenta como opción al llegar al umbral de caja.
- La reforma del 8A solo se ejecuta cuando la comunidad acumule:
  - **30.000 € de ahorro específico** para la obra
  - **+ 20.000 € de colchón mínimo de seguridad**
  - **= 50.000 € totales en caja**
- Estimación inicial de la presidencia: **verano de 2028**.
- Una vez ejecutado: ingreso recurrente esperado **≥ +1.000,00 €/mes**
  (alquiler), que **mejora la capacidad de ahorro** del resto del
  plan plurianual.

### 11.5 Proyección de caja del sub-hito 8A (tres escenarios)

> Se recalcula automáticamente cada vez que se sube nuevo extracto y
> se actualizan `bank_movements`.

#### Inputs (todos desde `bank_movements`)

- `saldo_actual` = saldo del último movimiento registrado.
- `saldo_disponible` = `saldo_actual`.
  > Solo se descuenta caja real. Los presupuestos y facturas
  > pendientes se muestran como información contextual aparte (§10),
  > pero NO descuentan del saldo disponible para el hito.
- `falta_para_50k` = 50.000,00 − `saldo_disponible`.

#### Tres ratios mensuales de ahorro

- **Optimista**: media mensual del año cerrado con mejor neto desde
  2021.
- **Prudente**: media móvil de los últimos 12 meses cerrados.
- **Pesimista**: media mensual del año cerrado con peor neto desde
  2021.

#### Cálculo

```
meses_estimados = falta_para_50k / ratio_mensual
fecha_estimada  = hoy + meses_estimados
```

#### Output esperado (formato)

```
Proyección 8A · saldo disponible: 28.910,00 € · faltan 21.090,00 €
  · Optimista (790 €/mes — base 2024)  → 27 meses → jul 2028
  · Prudente   (450 €/mes — móvil 12m) → 47 meses → mar 2030
  · Pesimista  (122 €/mes — base 2026) → 173 meses → 2040+
Hito objetivo presidencia: verano 2028
```

#### Reglas adicionales

- **Ingresos no recurrentes** (alquiler temporal 8A→7B, §7.5) NO
  entran en los ratios mensuales de los tres escenarios.
- Si los tres escenarios se desvían fuertemente del objetivo, informo
  con texto neutro, sin interpretar (la presidencia decide).
- No defino umbral de alerta automática.

### 11.6 Avance del plan plurianual (HITO PRINCIPAL · objetivo ~180k)

> **Este es el único hito real del proyecto.** Todo lo demás (sub-hito
> 8A, actuaciones puntuales, imprevistos) está dentro de él. Vista
> distinta a §11.5: no responde "¿cuándo desbloqueamos el 8A?" sino
> **"¿cuánto del plan global está hecho?"**.

#### Objetivo total (dinámico)

```
total_pull = SUM(ABS(projects.pres))  para todos los proyectos del pull
```

- **Estimación inicial: ~180.000 €** a 6-7 años, suma de los proyectos
  acordados en 2025.
- El total **no es fijo**: si entran imprevistos al pull o se ajustan
  presupuestos, `total_pull` crece o decrece automáticamente. El
  gráfico siempre se calcula sobre `total_pull` actual, no sobre los
  180k iniciales.

#### Categorías a mostrar (donut de tres sectores)

> Cambio respecto a versiones anteriores: el donut tiene **tres
> categorías**, no dos. Esto da imagen completa de la salud del plan.

| Categoría     | Cálculo                                                              |
| ------------- | -------------------------------------------------------------------- |
| **Invertido** | `SUM(ABS(bank_movements.importe))` con `project_id ≠ NULL` y `importe < 0` |
| **Ahorrado**  | Saldo actual del banco (`bank_movements` última fila, columna `Saldo`) |
| **Pendiente** | `total_pull − Invertido − Ahorrado` (puede ser negativo si el ahorro acumulado supera lo necesario) |

> "Invertido" cuenta solo cargos bancarios efectivamente pagados que
> están enlazados a algún proyecto del pull. "Ahorrado" es la caja
> disponible HOY para cubrir el resto del plan. "Pendiente" es lo que
> aún hay que generar vía cuotas y ahorro futuro.

#### Coherencia con el principio de §11.7

El donut es una **foto fija** del momento. Para responder "¿cuándo
llegamos?" se usa la proyección de §16.5 (análisis de viabilidad) con
los tres escenarios de ratio mensual. Donut + proyección dan visión
completa.

#### Output esperado (formato)

```
Avance del plan plurianual · objetivo 180.000,00 €
  ●●●●●●○○○○○○○○○○○○○○  25,2%
  Invertido:  16.470,00 €  (9,2%)
  Ahorrado:   28.910,00 €  (16,1%)
  Pendiente: 134.620,00 €  (74,8%)
Horizonte oficial: dic 2031 - dic 2032 (6-7 años)
```

#### Visualizaciones recomendadas para el frontend

- **Donut chart** (Chart.js) con tres sectores: Invertido / Ahorrado /
  Pendiente. Es la vista principal.
- **Barra de progreso horizontal** con el porcentaje "Invertido +
  Ahorrado" sobre el total como medida de salud del plan.
- **Tabla desglosada por proyecto**: nombre, presupuestado, pagado,
  pendiente, % avance individual. Útil en pestaña Plan / Admin.

#### Reglas adicionales

- El avance individual de cada proyecto se calcula igual que el
  global, pero filtrando por `project_id`:
  ```
  pagado_proyecto_X = SUM(ABS(bank_movements.importe))
                      WHERE project_id = X AND importe < 0
  avance_proyecto_X = pagado_proyecto_X / ABS(projects.pres) WHERE id = X
  ```
- **Aviso de coherencia**: si el `pagado_proyecto_X` supera al
  `pres` del proyecto, aviso "proyecto sobrepasado en X €" para que
  la presidencia decida si reajusta el presupuesto.
- **Ingresos a proyectos** (signo positivo en `pres`, como los
  trasteros con +8.400 €) **NO suman al total_pull**. El plan de
  180k es de gasto en obras; los ingresos del pull son aportaciones
  que financian el plan, no objetivos de gasto.

### 11.7 Acoplamiento tiempo-ahorro (principio rector)

> Las dos vistas anteriores (§11.5 hito 8A y §11.6 avance plan) están
> **acopladas** por la caja real. Este principio rige cómo se
> relacionan.

#### Ecuación maestra

```
Ahorro mensual = Cuotas + Ingresos atípicos
               − Gastos recurrentes
               − Pagos del pull (proyectos ejecutados)
```

#### Implicaciones

- **Capacidad de ahorro limitada**: la comunidad solo puede ahorrar
  lo que queda tras pagar gastos recurrentes y proyectos en curso.
  No hay otra fuente de financiación más allá de cuotas e ingresos
  atípicos puntuales.

- **Trade-off explícito tiempo ↔ avance**:
  - Si se **acelera el plan** (más proyectos pagados →
    avanza "Hecho" en §11.6 más rápido) → se **retrasa el hito 8A**
    (§11.5) porque queda menos en caja.
  - Si se **frena el plan** (menos proyectos en ejecución) → **llega
    antes el hito 8A** porque se acumula más caja, pero el plan
    plurianual se alarga.
  - La presidencia decide el equilibrio. Claude no recomienda.

- **No doblar la contabilización**: los ratios de §11.5
  (optimista/prudente/pesimista) se calculan sobre **netos reales**
  de `bank_movements`, que **ya incluyen** el efecto de los proyectos
  pagados en cada período. Por tanto:
  - **NO descuento adicionalmente** los proyectos del pull al calcular
    el ratio.
  - **NO sumo "ahorros teóricos"** que no estén ya reflejados en el
    extracto.
  - El ahorro real es lo que el banco dice que es.

- **Inercia del cálculo**: la proyección del hito 8A asume que el
  ritmo histórico de gasto en proyectos se mantiene. Si la
  presidencia decide cambiar de ritmo (acelerar o frenar), el cambio
  se reflejará en los siguientes movimientos bancarios y los tres
  ratios se autoajustarán al recalcular. **No es necesario configurar
  nada manualmente**: el sistema se reequilibra solo en cada nueva
  carga de extracto.

- **Eventos no recurrentes que distorsionan el ratio prudente**:
  cuando un mes contiene un cargo grande puntual (por ejemplo, una
  factura de obra de 15.000 €), la media móvil de 12 meses del
  escenario prudente quedará temporalmente sesgada. Esto es aceptable
  y no se corrige — el ruido se suaviza con el tiempo. Si la
  presidencia quiere ver una proyección sin contar ese cargo
  puntual, lo pide explícitamente y se calcula aparte.

---

## 12. Esquema real de Supabase (verificado)

> **Estado**: esquema verificado el 07/05/2026 mediante consultas a
> `information_schema.columns`. **5 tablas** existentes con un total
> de **34 columnas**.

### 12.1 Tablas existentes

#### `movimientos` — Cargos del extracto bancario

| Columna        | Tipo                       | Nullable | Default            |
| -------------- | -------------------------- | -------- | ------------------ |
| `id`           | uuid                       | NO       | `gen_random_uuid()`|
| `fecha`        | date                       | NO       | NULL               |
| `concepto`     | text                       | YES      | NULL               |
| `importe`      | numeric                    | NO       | NULL               |
| `saldo`        | numeric                    | YES      | NULL               |
| `ref1`         | text                       | YES      | NULL               |
| `uploaded_at`  | timestamp with time zone   | YES      | `now()`            |
| `proyecto_id`  | uuid (FK→`proyectos.id`)   | YES      | NULL               |
| `documento_id` | uuid (FK→`documentos.id`)  | YES      | NULL               |

Mapeo con extracto Sabadell: `fecha` ↔ F.Operativa, `concepto` ↔
Concepto, `importe` ↔ Importe, `saldo` ↔ Saldo, `ref1` ↔ Ref1.

Índices creados (fase 1):
- `idx_movimientos_proyecto_id`
- `idx_movimientos_documento_id`
- `idx_movimientos_fecha_importe` (compuesto, para detección de
  duplicados §6.1)

#### `proyectos` — Pull de actuaciones del plan

| Columna      | Tipo                       | Nullable | Default            |
| ------------ | -------------------------- | -------- | ------------------ |
| `id`         | uuid                       | NO       | `gen_random_uuid()`|
| `año`        | text                       | NO       | NULL               |
| `nombre`     | text                       | NO       | NULL               |
| `cat`        | text                       | NO       | NULL               |
| `progreso`   | numeric                    | YES      | `0`                |
| `pres`       | numeric                    | YES      | NULL               |
| `obs`        | text                       | YES      | NULL               |
| `banco_ref`  | text                       | YES      | NULL               |
| `etiqueta`   | text                       | YES      | `'Normal'`         |
| `created_at` | timestamp with time zone   | YES      | `now()`            |
| `updated_at` | timestamp with time zone   | YES      | `now()`            |

> Coincide al ~100% con el modelo conceptual de §11.1.

#### `documentos` — Índice de PDFs / XLS subidos

| Columna         | Tipo                       | Nullable | Default            |
| --------------- | -------------------------- | -------- | ------------------ |
| `id`            | uuid                       | NO       | `gen_random_uuid()`|
| `tipo`          | text                       | NO       | NULL               |
| `nombre`        | text                       | NO       | NULL               |
| `año`           | integer                    | YES      | NULL               |
| `mes`           | integer                    | YES      | NULL               |
| `url`           | text                       | YES      | NULL               |
| `subido_por`    | text                       | YES      | NULL               |
| `created_at`    | timestamp with time zone   | YES      | `now()`            |
| `sha256`        | text                       | YES      | NULL               |
| `tamano_bytes`  | integer                    | YES      | NULL               |

Índices creados (fase 1):
- `idx_documentos_sha256` (para detección de duplicados §6.1)

#### `user_roles` — Auth y rol de usuarios

| Columna     | Tipo | Nullable | Default | Comentario |
| ----------- | ---- | -------- | ------- | ---------- |
| `email`     | text | NO       | NULL    | **PRIMARY KEY** |
| `role`      | text | NO       | NULL    | `admin` / `invitado` |
| `propiedad` | text | YES      | NULL    | `Propiedad 1A`, `Local Izq`, etc. |

#### `session_log` — Auditoría de sesiones

| Columna       | Tipo                       | Nullable | Default            |
| ------------- | -------------------------- | -------- | ------------------ |
| `id`          | uuid                       | NO       | `gen_random_uuid()`|
| `email`       | text                       | NO       | NULL               |
| `action`      | text                       | NO       | NULL               |
| `ip`          | text                       | YES      | NULL               |
| `user_agent`  | text                       | YES      | NULL               |
| `created_at`  | timestamp with time zone   | YES      | `now()`            |

### 12.2 Diferencias con el modelo conceptual de versiones previas

El modelo del `.md` v0.5 contemplaba 10 tablas. La realidad es 5
tablas funcionales. Las diferencias se resuelven así:

| Modelo v0.5             | Real ML63              | Estado / Acción                         |
| ----------------------- | ---------------------- | --------------------------------------- |
| `properties`            | (no existe)            | El censo (§7) se mantiene en este `.md`, no en BBDD por ahora. |
| `users_roles`           | `user_roles`           | Existe, mínima. Falta `propiedad` y enlace a `auth.users`.    |
| `projects`              | `proyectos`            | Existe, completa.                       |
| `budgets`               | (no existe)            | Pendiente crear cuando se implemente §2.1 (ciclo trifásico). |
| `invoices`              | (no existe)            | Pendiente crear cuando se implemente §2.1. |
| `bank_movements`        | `movimientos`          | Existe. Falta `proyecto_id`, `documento_id`. |
| `providers`             | (no existe)            | Catálogo §8 vive en este `.md` por ahora. |
| `documents`             | `documentos`           | Existe. **Falta `sha256` para detectar duplicados**. |
| `contracts`             | (no existe)            | Pendiente.                              |
| `agreements`            | (no existe)            | Pendiente (trasteros).                  |
| `meetings`              | (no existe)            | Pendiente (actas).                      |
| `session_log` (no en .md v0.5) | `session_log`   | Existe en BBDD, es útil. Se añade al modelo. |

### 12.3 Mejoras del esquema · estado

> Cambios sugeridos al esquema para alinearlo con las reglas del `.md`.
> Marcadas las completadas en la **fase 1** del 07/05/2026.

**Completadas (fase 1):**

1. ✅ **`documentos.sha256`** (text) — implementa la detección de
   duplicados de §6.1.
2. ✅ **`documentos.tamano_bytes`** (integer) — auditoría adicional.
3. ✅ **`movimientos.proyecto_id`** (uuid, FK a `proyectos.id`) —
   habilita el donut 180k de §11.6.
4. ✅ **`movimientos.documento_id`** (uuid, FK a `documentos.id`) —
   trazabilidad fichero ↔ movimiento.
5. ✅ **`user_roles.propiedad`** (text) — para que el rol `invitado`
   pueda filtrarse por su propiedad.
6. ✅ **Índices** creados: `idx_documentos_sha256`,
   `idx_movimientos_proyecto_id`, `idx_movimientos_documento_id`,
   `idx_movimientos_fecha_importe`.

**Pendientes (cuando lleguen su uso):**

7. ⏳ **`user_roles.user_id`** (uuid, FK a `auth.users.id`) — para
   integración robusta con Supabase Auth (magic link). Por ahora la
   PK es `email`, que funciona pero es menos robusto.
8. ⏳ **Tablas nuevas**: `presupuestos`, `facturas`, `proveedores`
   (con `alias` para §8.6), `contratos`, `actas`, `acuerdos`. Crear
   cuando llegue su uso real, no antes.

### 12.4 RLS y Storage

- **RLS**: pendiente comprobar el estado real con consulta a
  `pg_policies`. Hasta entonces, no se asume nada.
- **Storage facturas/extractos**: **NO se usa** para archivos PDF/XLS
  de proveedores. La presidencia mantiene los originales en disco
  local (§6.4, opción A).
- **Storage actas y balances**: **SÍ se usa** — bucket `actas` en
  Supabase Storage. Ver §12.6.

### 12.6 Gestión de documentos públicos (actas, balances)

> Los propietarios tienen derecho a consultar actas y balances. Esta
> feature usa Supabase Storage (bucket `actas`) + tabla `documentos`.

#### Inventario de actas disponibles

| Ejercicio | Tipo | Archivo | Fecha junta | Estado |
|-----------|------|---------|-------------|--------|
| 2019-2020 | JGO (año fiscal jul-jun) | `ModestoLafuente63.ctasVII19-VI20_...pdf` | sep 2020 | ⚠️ Época Alfredo — formato año fiscal, no natural |
| 2021 | — | — | — | ❌ No disponible |
| 2022 | — | — | — | ❌ No disponible |
| 2023 | — | — | — | ❌ Solo gsheet de notas (no acta oficial) |
| 2024 | JGO (cuentas 2023) | `Acta - 2024 - BMC.pdf` | feb 2024 | ✅ Último año BMC |
| 2025 | JGO | `ACTA JGO 04 02 2025 FIRMADA Y SELLADA.pdf` | 04/02/2025 | ✅ Primera junta Susana |
| 2026 | JGE | `ACTA JGE 27 01 2026.pdf` | 27/01/2026 | ✅ + dosier balance 2025 |

**Cambio de era**: hasta BMC, el año fiscal era julio-junio. Desde
Susana (2025): año natural, junta siempre en **enero**.

#### Valores de `documentos.tipo` para actas y balances

| Valor | Descripción |
|-------|-------------|
| `acta_jgo` | Junta General Ordinaria (firmada y sellada) |
| `acta_jge` | Junta General Extraordinaria |
| `balance` | Rendición de cuentas / balance anual |
| `presupuesto` | Presupuesto gastos ordinarios |
| `reparto` | Reparto de gastos y saldos por propietario |
| `convocatoria` | Convocatoria de junta |

#### Nombre canónico de archivo en Storage

```
{ejercicio}_{tipo}_{fecha-ISO}.pdf
Ejemplos:
  2025_acta_jgo_2025-02-04.pdf
  2026_acta_jge_2026-01-27.pdf
  2025_balance_2026-01-27.pdf
```

#### Feature UI

**Vista pública (todos los propietarios autenticados):**
- Sección "Documentos" en la app
- Agrupados por `año` (ejercicio) — acordeón o tabs por año
- Cada fila: tipo · fecha · botón "Descargar" (signed URL Supabase)
- Solo lectura. No se puede borrar ni editar

**Vista admin (Eduardo + Susana):**
- Panel admin → pestaña "Documentos"
- Formulario de subida: tipo (selector) · ejercicio (año) · fecha (date picker) · archivo (file input PDF)
- Validación: sha256 para evitar duplicados (§6.1)
- Listado con opción de eliminar
- RLS: INSERT/DELETE solo `role = 'admin'`; SELECT todos los
  autenticados

### 12.5 Convivencia de nombres reales y conceptuales

> A lo largo del `.md` aparecen referencias a nombres conceptuales
> (`bank_movements`, `projects`, `invoices`, etc.) que vienen del
> modelo de versiones previas. Estos nombres se mantienen en las
> reglas conceptuales (§2.1, §6.2, §10, §11.6, etc.) por claridad
> didáctica.
>
> **Regla operativa**: cuando Claude escriba código real contra
> Supabase, usa SIEMPRE los nombres reales:

| Nombre conceptual    | Nombre real en Supabase |
| -------------------- | ----------------------- |
| `bank_movements`     | `movimientos`           |
| `projects`           | `proyectos`             |
| `documents`          | `documentos`            |
| `users_roles`        | `user_roles`            |
| `invoices`           | (no existe aún)         |
| `budgets`            | (no existe aún)         |
| `providers`          | (no existe aún)         |
| `contracts`          | (no existe aún)         |
| `agreements`         | (no existe aún)         |
| `meetings`           | (no existe aún)         |
| `properties`         | (no existe; vive en §7) |

---

## 13. Reglas de privacidad

- **Nunca** aparece nombre + apellido de un **propietario** en outputs,
  en este `.md`, en el frontend (público o privado), en logs o en
  cualquier derivado.
- Sustitución obligatoria: `Propiedad 1A`, `Propiedad 6B`, `Local Izq`,
  `Local Dcho`.
- Si una factura, acta o recibo trae el nombre de un propietario, lo
  ignoro a efectos del output y trabajo solo con la propiedad.
- **Proveedores externos**: se pueden mostrar con su nombre real
  (razón social o nombre del autónomo). Administradores externos en
  orden cronológico inverso (de más reciente a más antiguo): Susana
  Fernández Robleda (actual desde jul 2024), Vanessa Álvarez Gómez
  (anterior), Carlos (BMC Gestión y Admon. Fincas, S.L.), Alfredo
  (el más antiguo). Otros proveedores: Duplex Elevación, Naturgy,
  Ocaso, Lasser, Pinta Limpio, A. Pirtac, Cerrajería Perón, etc.
- **Personal laboral histórico (portero)**: el nombre real (Pedro
  Simón Gironés) aparecerá inevitablemente en `bank_movements` por
  los conceptos de transferencia. En outputs, presentaciones, gráficos
  y `.md` se refiere siempre como **"Portero"** o **"personal laboral
  histórico"**, no por su nombre.
- **Datos sensibles** (DNI, IBAN de propietarios, teléfonos personales,
  emails personales) **nunca** aparecen en outputs.
- **Tarea pendiente sobre la app actual**: retirar nombres de
  propietarios del footer y bloques de histórico cuando se haga la
  migración.

---

## 14. Glosario

- **CP**: Comunidad de Propietarios.
- **JGO**: Junta General Ordinaria.
- **JGE**: Junta General Extraordinaria.
- **Pull de proyectos**: bolsa única de actuaciones del plan
  plurianual; la presidencia decide cuáles se acometen cada año.
- **Trasteros (acuerdo)**: cesión de uso privativo a viviendas letra B
  plantas 1ª–7ª. **NO es derrama.**
- **Derrama**: cargo extraordinario aprobado en junta y prorrateado.
  El acuerdo de trasteros NO encaja en esta definición.
- **Vivienda CP / Piso CP / 8A**: vivienda 8A propiedad de la CP.
- **Local Dcho · Karaoke**: actividad del Local Derecho.
- **Cierre de ejercicio**: año cerrado solo muestra proyectos
  `completado`; el resto se arrastra.
- **Plan plurianual**: 6-7 años desde 2025 (2031-2032); ampliado tras análisis de viabilidad v0.11.
- **Carga incremental**: estrategia de subir solo movimientos nuevos.
- **Caja real**: lo efectivamente pagado, según `bank_movements`.
- **Devengo**: deuda reconocida por factura recibida, según `invoices`.
- **Compromiso**: presupuesto aceptado pero sin factura aún, según
  `budgets`.
- **D. Cubo**: nombre comercial de **Prevent XXI Servicios España SL**.
- **El Pilar**: limpieza anterior, baja por burofax feb 2026.
- **MJM**: limpieza anterior a El Pilar.
- **Duplex Elevación**: mantenedor de ascensor.
- **Ocaso · Póliza 303233**: seguro del edificio.
- **Susana Fernández Robleda**: administradora externa actual de la
  CP, desde julio 2024.
- **Vanessa Álvarez Gómez**: administradora externa anterior a Susana.
  En `bank_movements` aparece con dos variantes (`VANESA ALVAREZ
  GÓMEZ` y `VANESSA ALVAREZ GOMEZ`); ambas se tratan como la misma
  persona vía alias en `providers`.
- **Carlos (BMC Gestión y Admon. Fincas, S.L.)**: administrador
  externo anterior a Vanessa. Contacto: **Carlos J. Remedios**, colegiado nº 11351,
  carlos.remedios@bmcadministradores.com. Oficina: C/ Sauce 9 Local, Madrid,
  tel. 914 161 889 (mismo teléfono y dirección que Alfredo → BMC heredó el mandato SEPA de Alfredo).
- **Alfredo (Alfredo Sánchez Aguirre)**: administrador externo más antiguo de los cuatro.
  Colegiado nº 3640, tecfiscon@gmail.com, C/ Sauce 9 Local, Madrid, tel. 914 161 889.
  En el extracto aparece como `CL SAUCE N 9-LC` en los recibos domiciliados.
- **Cronología de administradores (de más reciente a más antiguo)**:
  Susana → Vanessa → Carlos (BMC) → Alfredo.
- **Portero**: puesto laboral histórico de la CP, cubierto hasta 2025
  por personal propio (Pedro Simón Gironés en `bank_movements`).
  Sustituido por servicio externalizado (Prevent XXI / D. Cubo) tras
  el despido de 2025.
- **Banco**: cuenta `0081-7125-93-0001279538` (Sabadell).
- **Magic link**: login sin contraseña vía enlace temporal por email.
- **RLS** (Row-Level Security): filtrado de filas por usuario en
  Supabase/Postgres.

---

## 15. Roadmap de migración

1. **Cerrar `.md` v0.5** (este documento) y subirlo al repo.
2. **Recibir SQL real de Supabase** → actualizar §12 a v0.6.
3. **Esqueleto del frontend nuevo**: `index.html` + login magic link +
   estructura de carpetas vacía.
4. **Carga inicial del histórico bancario** (2021-2026) en
   `bank_movements`. Una sola vez.
5. **Migración tab a tab** del HTML legacy al nuevo.
6. **Pestaña Admin**: CRUD proyectos, subida XLS extracto, subida PDFs
   (presupuestos y facturas), gestión usuarios.
7. **Conciliación trifásica**: UI para enlazar `budget → invoice →
   bank_movement` con sugerencias automáticas.
8. **Implementación §11.5 — proyección 8A en tres escenarios** vivos.
9. **Ingesta automatizada de PDFs** (extracción → validación →
   inserción).
10. **Vista invitado** filtrada por RLS.
11. **Sustitución del HTML legacy** en `esr-design.com/ML63/`.

---

## 16. Narrativa estratégica del plan

> Contexto que da sentido al plan plurianual. Sin esta narrativa, las
> cifras pierden significado. Las cifras económicas se han calculado
> desde `bank_movements` y se actualizarán con cada extracto nuevo.

### 16.1 Hito único: el plan plurianual

- **Un solo hito real**: ejecutar el **plan plurianual de ~180.000 €**
  en 6-7 años (2025-2031/2032), que cubre todas las mejoras necesarias
  del edificio.
- **No hay hitos en cadena**: el 8A, las actuaciones del año en curso,
  los imprevistos — todo está dentro del plan plurianual.
- **Sub-hito relevante 8A** (§11.4): tiene proyección propia (§11.5)
  porque condiciona la ejecución de un proyecto importante y
  desbloquea ingreso recurrente futuro.

### 16.2 Capacidad de ahorro: dos decisiones estratégicas que la han ampliado

La capacidad real de la comunidad para ejecutar el plan depende del
**ahorro mensual** (§11.7). Dos decisiones estratégicas tomadas
recientemente han aumentado significativamente esa capacidad:

#### Decisión 1 · Externalización del servicio (despido del portero, 2025)

- **Coste anual del puesto laboral en 2024** (último año completo con
  portero, según `bank_movements`): **−13.973,85 €**
  (nóminas + TGSS + Quirón Prevención + transferencias directas +
  embargos AEAT + sustituciones puntuales).
- **Coste puntual del despido en 2025**: indemnización + finiquito +
  últimas nóminas + embargos = **~−14.000 €** (cargos concentrados
  en 2025).
- **Coste anual nuevo** (limpieza externa con Prevent XXI / D. Cubo,
  2026 anualizado): **−7.947,72 €**.
- **Ahorro estructural anual recurrente**: **+6.470 €/año** desde 2026.
- **Ingreso adicional futuro**: alquiler del 8A una vez reformado,
  estimado **≥ +12.000 €/año** desde ~2028.

#### Decisión 2 · Cambio de administración externa (BMC → Susana, 2024-2025)

> **Aviso de método importante**: en el extracto, los recibos de BMC
> mezclaban dos cosas distintas: la cuota mensual de honorarios y los
> pagos de obras que BMC canalizaba (en particular la obra de cubiertas
> Impernova 7B/8B 2022-2024). Para medir el ahorro real de
> administración hay que separar ambos conceptos. Las cifras de abajo
> usan **solo honorarios**, no obras canalizadas.

- **Cuota habitual BMC**:
  - 2022: **−347,48 €/mes** = ~−4.170 €/año
  - 2023-2024 (hasta cese): **−364,85 €/mes** = ~−4.378 €/año
- **Cuota habitual Susana**:
  - Jul 2024 – ene 2026: **−233,20 €/mes**
  - Desde feb 2026 (subida en JGE 27/01/2026): **−300,00 €/mes** =
    **−3.600 €/año**
- **Ahorro estructural anual recurrente** vs BMC: **+778 €/año**
  (64,85 €/mes × 12).

> El ahorro de administración es modesto: la decisión estratégica de
> cambiar de administradora aportó simplicidad operativa y mejor
> servicio, no un gran ahorro económico. **El error de cálculo de
> versiones anteriores (~+8.990 €/año) provenía de mezclar honorarios
> con obras canalizadas por BMC.**

### 16.3 Resumen del ahorro estructural

| Concepto                                 | Ahorro anual recurrente |
| ---------------------------------------- | ----------------------- |
| Externalización del servicio (vs 2024)   | +6.470 €                |
| Cambio de administración (vs BMC)        | +778 €                  |
| **Total ahorro estructural anual**       | **+7.248 €**            |

Este ahorro se mantiene activo todos los años. Multiplicado por los
6-7 años del plan, **representa ~43.500-50.700 €** que la comunidad
puede dedicar al pull de proyectos sin subir cuotas.

> **Advertencia importante**: las versiones v0.11–v0.16 del `.md`
> calcularon un ahorro estructural muy superior (~15.500 €/año = ~93k
> a 6-7 años) porque **mezclaban honorarios con obras canalizadas por
> BMC**. La cifra real es aproximadamente la mitad. Esto **afecta
> directamente al análisis de viabilidad del plan plurianual** (§16.5).
> Sigue siendo motor financiero relevante, pero no es suficiente por sí
> solo para los 180k del plan.

### 16.4 Lo que queda por delante

- **Sub-hito 8A** (50.000 € en caja) — se ejecuta cuando llegue, y
  desbloquea **+12.000 €/año adicionales** de ingreso por alquiler
  desde el momento de la reforma.
- **Resto del pull** — actuaciones puntuales del año en curso (sellado
  ventanal, maderas portal, etc.) e imprevistos que vayan surgiendo.
- **Cuotas** — la base estable de ingresos. No se prevé subirlas
  mientras el ahorro estructural alcance.

> Las cifras de §16.2 se han calculado contra el extracto bancario
> actual y se recalcularán automáticamente con cada subida de
> `finance.xls`. Si los ratios cambian, la narrativa se actualiza
> y se incrementa versión del `.md`.

### 16.5 Análisis de viabilidad del plan 180k

> Calculado con datos reales del banco a fecha 20/04/2026. Se
> recalcula con cada nuevo extracto.

#### Estado actual del plan

| Concepto                            | Importe          | % sobre 180k |
| ----------------------------------- | ---------------- | ------------ |
| Saldo actual en banco               |  +28.909,53 €    | 16,1 %       |
| Invertido en proyectos desde 2025   |  +16.469,90 €*   | 9,2 %        |
| Pendiente por generar               | +134.620,57 €    | 74,8 %       |
| **Objetivo**                        | **+180.000,00 €**| 100 %        |

> *Aproximación: cuenta todo el gasto no-recurrente desde 01/01/2025.
> La cifra real vendrá cuando los `bank_movements` estén enlazados a
> `project_id` en Supabase.

#### Ahorro mensual histórico (banco real)

| Año    | Ingresos       | Gastos        | Neto/año     | Neto/mes  |
| ------ | -------------- | ------------- | ------------ | --------- |
| 2021   | +51.315,97 €   | -44.171,89 €  | +7.144,08 €  |   +595 €  |
| 2022   | +51.444,17 €   | -73.721,50 €  | -22.277,33 € | -1.856 €  |
| 2023   | +80.554,37 €   | -85.052,21 €  | -4.497,84 €  |   -375 €  |
| 2024   | +74.276,06 €   | -64.794,07 €  | +9.481,99 €  |   +790 €  |
| 2025   | +62.719,60 €   | -57.762,51 €  | +4.957,09 €  |   +413 €  |
| 2026*  | +31.739,60 €   | -31.251,56 €  |   +488,04 €  |   +122 €  |

> *2026 parcial (ene-abr).

#### Tres escenarios de ahorro mensual proyectado

| Escenario             | Base de cálculo                              | Ratio    |
| --------------------- | -------------------------------------------- | -------- |
| **Optimista**         | 2024 + ahorro estructural verificado (§16.3) | +2.078,50 €/mes |
| **Prudente**          | Media móvil últimos 12 meses cerrados        |   +802,36 €/mes |
| **Pesimista**         | Peor año cerrado (2022, refinanciaciones)    | -1.856,44 €/mes |

> El **optimista** no es fantasía: parte de un año real (2024) con
> portero todavía activo, y le suma los ahorros estructurales que ya
> están verificados en el banco (despido + cambio de admin). Es el
> escenario realista si la operativa se mantiene estable.
>
> El **pesimista** corresponde a 2022, año atípico con ajustes
> contables. Sirve como cota inferior teórica.

#### Proyección de viabilidad (faltan 134.620,57 € por generar)

| Escenario   | Meses necesarios | Años | Fecha estimada            |
| ----------- | ---------------- | ---- | ------------------------- |
| Optimista   | 65 meses         | 5,4 años | sep 2031              |
| Prudente    | 168 meses        | 14,0 años | abr 2040             |
| Pesimista   | —                | nunca llega | —                  |

#### Veredicto honesto sobre viabilidad

- **A 5 años (dic 2029)**: necesitaría +3.057 €/mes. **No alcanzable**
  con la operativa actual sin subir cuotas o aprobar derramas.
- **A 6 años (dic 2030)**: necesitaría +2.327 €/mes. Justo al límite
  superior del escenario optimista.
- **A 7 años (dic 2031)**: necesitaría +1.846 €/mes. **Alcanzable** en
  escenario optimista, ajustado.
- **El horizonte oficial se fija en 6-7 años (2031-2032)**. El plan es
  viable en este rango sólo si:
  - Se mantienen los ahorros estructurales (portero externalizado +
    administración estabilizada).
  - No surgen imprevistos grandes que consuman el ahorro mensual.
  - El sub-hito 8A se ejecuta dentro del plazo y empieza a generar
    +12.000 €/año desde ~2028, lo cual mejora la viabilidad de los
    años finales.

#### Palancas disponibles si la proyección se desvía

> No las recomiendo, las enumero. La presidencia decide.

- Reducir el alcance del plan (priorizar imprescindibles, posponer
  resto).
- Subir cuotas ordinarias.
- Aprobar derramas extraordinarias por proyecto.
- Acelerar el sub-hito 8A para adelantar el ingreso por alquiler.
- Revisar contratos recurrentes para encontrar más ahorros.

---

## 17. Versionado del documento

| Versión | Fecha       | Cambio                                                                  |
| ------- | ----------- | ----------------------------------------------------------------------- |
| 0.1     | 07/05/2026  | Versión inicial: reglas, censo, proveedores, pull, contabilidad, privacidad, glosario, índice ficheros + estado financiero. |
| 0.2     | 07/05/2026  | Datos vivos migran a Supabase. Criterio homogéneo de signos. |
| 0.3     | 07/05/2026  | Arquitectura técnica (stack, carpetas, esquema esperado, roles). Proveedores ampliados. Cierre ejercicio. Hito 8A 50k. Roadmap. |
| 0.4     | 07/05/2026  | §2 regla maestra extracto. §2.1 carga incremental. §7.5 alquiler 8A→7B único. §8.3 Susana nombrada. §10.5 proyección 8A tres escenarios. |
| 0.5     | 07/05/2026  | **§2.1 ciclo trifásico** presupuesto→factura→cargo con tablas `budgets`/`invoices`/`bank_movements`. **§6.2 protocolos por tipo** de PDF (presupuesto/factura/extracto/acta/contrato) con conciliación automática propuesta. **§10 KPIs económicos por fase** (caja/devengo/compromiso). **§11.5** ajustada: saldo disponible 8A solo se calcula sobre caja real, sin descontar presupuestos ni facturas pendientes. **§12.2 diagrama de relaciones** entre tablas. |
| 0.6     | 07/05/2026  | **§11.6 Avance del plan plurianual 180k**: nueva vista de progreso (Hecho/Por hacer) con `total_pull` dinámico calculado desde `projects.pres`. "Hecho" usa cargos bancarios enlazados a proyectos, coherente con la regla maestra §2. Avance por proyecto individual y aviso si se sobrepasa el presupuesto. KPI añadido a §10. |
| 0.7     | 07/05/2026  | **§11.7 Acoplamiento tiempo-ahorro** (principio rector): ecuación maestra del ahorro mensual, trade-off explícito entre acelerar el plan y retrasar el hito 8A, regla de no-doble-contabilización (los ratios de §11.5 ya incluyen los proyectos pagados, no descontar dos veces), inercia del cálculo (auto-reajuste con cada nuevo extracto), tratamiento de eventos puntuales que sesgan la media móvil. |
| 0.8     | 07/05/2026  | **Reestructuración de hitos**: el 8A pasa de "hito" a **sub-hito** dentro del plan plurianual (único hito real). §11.4 y §11.5 renombradas. §11.6 marcada explícitamente como HITO PRINCIPAL. **§16 Narrativa estratégica** nueva: dos decisiones estratégicas que ampliaron la capacidad de ahorro (despido portero +6.470 €/año recurrente; cambio admin BMC→Vanesa→Susana +8.990 €/año). Cifras calculadas desde `bank_movements`. Ahorro estructural total **+15.460 €/año** = ~77-93k a 5-6 años, el motor financiero del plan. **Privacidad**: confirmado que los nombres de administradores históricos se pueden usar como cualquier proveedor; "Pedro Simón Gironés" se refiere como "Portero" en outputs aunque aparezca en el extracto bancario. |
| 0.9     | 07/05/2026  | **Cronología correcta de administradores** (orden inverso, más reciente → más antiguo): Susana Fernández Robleda → Vanessa Álvarez Gómez → Carlos (BMC Gestión y Admon. Fincas, S.L.) → Alfredo. Corregida ortografía "Vanesa" (una sola s). Aclarado que Carlos era el contacto en BMC (no son dos administradores distintos). Glosario §14 y privacidad §13 actualizados. |
| 0.10    | 07/05/2026  | **Regla operativa de alias §8.6**: un proveedor puede aparecer con varias grafías en el banco; se mantienen todas en `providers.alias`. Nombre canónico = grafía mayoritaria en `bank_movements`. Aplicado al caso `Vanessa Álvarez Gómez`: la grafía mayoritaria en el banco es `VANESSA` (3 cargos) sobre `VANESA` (1 cargo), por tanto el nombre canónico se fija en **Vanessa Álvarez Gómez** (revierte la corrección de v0.9). Documentado también el caso Prevent XXI / D. Cubo / Don Cubo. |
| 0.11    | 07/05/2026  | **Análisis de viabilidad del plan 180k**. Tras calcular contra el banco real: el plan NO es viable a 5 años (necesitaría +3.057 €/mes); SÍ es viable a 6-7 años (necesita +1.846 a +2.327 €/mes). **Horizonte oficial ampliado a 6-7 años (2025-2031/2032)** en todas las menciones. **§11.6 actualizada**: el donut pasa a tener tres categorías (Invertido / Ahorrado / Pendiente) en vez de dos. **§16.5 nueva**: análisis completo de viabilidad con tablas de estado actual, ahorro mensual histórico (2021-2026), tres escenarios de proyección (optimista +2.078 €/mes / prudente +802 €/mes / pesimista -1.856 €/mes), y palancas disponibles si la proyección se desvía. Capacidad estructural recalculada: ~93k-108k a 6-7 años (antes ~77k-93k a 5-6 años). |
| 0.12    | 07/05/2026  | **§12 reemplazada con esquema REAL de Supabase verificado**. 5 tablas existentes con 34 columnas: `movimientos` (7 col), `proyectos` (11 col), `documentos` (8 col), `user_roles` (2 col), `session_log` (6 col). Coincidencias y diferencias con el modelo conceptual previo documentadas en §12.2. Lista de mejoras pendientes en §12.3 (no críticas): añadir `sha256` a `documentos`, `proyecto_id` y `documento_id` a `movimientos`, `propiedad` y `user_id` a `user_roles`, y crear tablas para `presupuestos`/`facturas`/`proveedores`/`contratos`/`actas`/`acuerdos` cuando llegue su uso. Añadida §12.5 con tabla de mapeo nombre conceptual → nombre real. RLS y Storage pendientes de verificar. |
| 0.13    | 07/05/2026  | **Fase 1 del esquema completada**. Aplicados 3 ALTER TABLE en Supabase: (1) `documentos` + `sha256` + `tamano_bytes` + índice `idx_documentos_sha256`; (2) `movimientos` + `proyecto_id` (FK→proyectos) + `documento_id` (FK→documentos) + 3 índices (`idx_movimientos_proyecto_id`, `idx_movimientos_documento_id`, `idx_movimientos_fecha_importe`); (3) `user_roles` + `propiedad` (la PK ya existía como `email`, descartado añadir `id` uuid). §12.1 actualizado con columnas reales tras fase 1. §12.3 reorganizado en completadas/pendientes. **§6.4 nueva — Flujo de archivos opción A · solo local**: archivos físicos solo en disco de la presidencia, NO en Storage de Supabase. Storage queda sin uso rutinario. Claude solo accede a archivos vía Project Knowledge o subida al chat. §12.4 actualizada en consecuencia. |
| 0.14    | 07/05/2026  | **Carga inicial histórica del extracto**: 1.304 movimientos cargados en `movimientos` (rango 31/12/2020 → 20/04/2026). Totales verificados: ingresos +352.049,77 €, gastos -356.768,74 €, saldo final 28.909,53 €. **§9.8 nueva — Saldo final cuando hay varios movimientos el mismo día**: el extracto Sabadell no respeta orden cronológico estable dentro de un día; el saldo "actual" se calcula como `MIN(saldo)` del último día disponible cuando hay cargos negativos, no como `LIMIT 1` por orden de inserción. Lección aprendida al validar la carga (un cargo Susana del 20/04 daba saldo intermedio 29.809,47 € en lugar del cronológico final 28.909,53 €). |
| 0.15    | 07/05/2026  | **§9.9 nueva — Regularizaciones de cargos recurrentes**: algunos proveedores acumulan deuda y la cobran en un único cargo. Caso registrado: Susana Fernández Robleda con cuota habitual −233,20 €/mes desde jul-2024, hueco feb-mar-abr 2026 cubierto por transferencia única de −899,94 € el 20/04/2026 (3 × 233,20 + 200,34 € de ajuste). Regla por defecto: mostrar el cargo en su fecha real (vista cronológica). Vista normalizada (redistribuir entre meses) opcional bajo petición. Claude debe avisar si detecta cargo >2× la cuota habitual de un proveedor recurrente. |
| 0.16    | 07/05/2026  | **Aclaración clave: Susana subió su cuota en JGE 27/01/2026** de 233,20 € a 300,00 €/mes. Recalculado el desglose del cargo del 20/04/2026: 3 × 300 = 900 (no eran 200 € de ajuste, era la nueva tarifa). Actualizado §8.3 (catálogo proveedores), §9.9 (caso de referencia) y §16.2 (narrativa estratégica) con cifras corregidas. **Coste anual Susana ahora: 3.600 €/año**. Ahorro estructural por cambio de admin recalculado: **+8.793 €/año vs 2024** (antes +8.990). Ahorro estructural total: **+15.263 €/año** (antes +15.460). Capacidad estructural en 6-7 años: **~92-107k** (antes ~93-108k). |
| 0.17    | 07/05/2026  | **§9.10 nueva — Catálogo de cargos atípicos verificados**. Repaso completo de los 1.304 movimientos identificó 90 cargos atípicos (>2× mediana). Validados con la presidencia y documentados con explicación: avería grande del ascensor (Duplex 1.774 €/mes × 3 meses dic25-feb26 = 5.324 €), proyecto Petter Movistar (Telefónica 200 € retirada cableado), cierre de contratos limpieza MJM y El Pilar, cambio de tarifa Prevent (cubos 166 → limpieza+cubos 518 €/mes desde mar 2026), Multiservicios cuota+cert energético caldera (1.230 € en mar 2025), Iberext renovación anual (513 € dic 2022), Gas Power regularización masiva (28/11/2024), Naturgy crisis energética 2021-2023, BMC honorarios admin anterior, Susana ajustes complementarios. Actualizado §8.2: Telefónica = móvil emergencias ascensor 690941447 (18,15 €/mes); Prevent = cuota nueva 517,88 €/mes desde mar 2026 (limpieza + cubos). |
| 0.20    | 10/05/2026  | **Cierre de análisis de cargos no clasificados**. §9.10: nuevo bloque **Embargos** (4 cargos, −1.663,56 €) con tabla detallada e hipótesis TGSS (relación con despido portero feb 2025; acreedor pendiente confirmar con Susana). Nuevo bloque **Quirón Prevención cargos erróneos post-despido** (contrato cancelado correctamente; cobros por error reconocidos por Quirón, todos devueltos, impacto neto 0 €; coste real ~550–616 €/año a imputar al coste total del portero). Nuevo bloque **Impagados SEPA** (27 devoluciones, −2.161,39 € en escalada 2022-2026; candidatos morosos Ferrín/Yolanda pendientes de confirmar). Nuevo bloque **Pintalimpio S.L.** (−1.033,34 € el 03/03/2026). **A. Pirtac**: 8 facturas desglosadas (tabla completa Fra. 228-261; Fra. 245 privada Alicia Chocrón, no contabilizable). Fra. 228/229/233 etiquetadas `siniestro sanitas`. **§7.1b nuevo: censo propietarios** (24 unidades, 14 titulares, coeficientes; ⚠️ Lc I vendido Five West → empresa nueva desconocida; ⚠️ 7ºB vendido Bendahan → María Soledad Alonso López + Pedro pendiente). **§8.7 nuevo: alias de propietario**: regla Soledad → Sol (`MARIA SOLEDAD ALONSO LOPEZ` = alias "Sol", 7ºB); mecanismo REMESA RECIBOS documentado; propietarios manual-transfer identificados; Sara Silvo Martin y Adela Puyo Hernández sin identificar (pendiente Susana). **alquiler teórico 8A actualizado** a 1.000 €/mes = 12.000 €/año (ML63.html + §7.5). |
| 0.19    | 09/05/2026  | **Mundo Reformas identificado y documentado**. §8.4: CIF B87508784, contacto Jorge, datos fiscales completos. §9.10: nuevos bloques para siniestro patinillo A/C 2024 (3.433,54 €), siniestro patio luces 2025 (660 €), bomba calefacción 2022-2023 vía Multiservicios (5.697,20 €) y siniestro sótano 2023 (3.569,50 €). §9.10 Impernova: presupuesto corregido a 31.111 € (antes ~40.000), derrama 32.000 €, sobrecoste 111% (antes 62%). §9.10: nuevo bloque con estado de identificación de los 17 cheques históricos (2968578–2968595): 7 identificados como Impernova (38.739,80 €), 5 identificados via cuentas BMC 2022-2023, 6 sin identificar (sin cuentas Alfredo 2021 disponibles). Impernova total corregido a **−65.729,07 €** (add T/593 humedades 7ºB 1.072,50 €). Siniestro sótano 2023: desglose por proveedor añadido (Pedreño bajada portal 2.007,50 + albañiles BMC 1.562,00). Banco 21/09/2023 Pedreño −2.007,50 € correctamente atribuido a siniestro sótano (no al patinillo 2024). §14 glosario: Carlos J. Remedios (colegiado 11351) y Alfredo Sánchez Aguirre documentados con datos de contacto completos; confirmado que BMC heredó SEPA de Alfredo (mismo despacho C/ Sauce 9). §11.4: Mundo Reformas añadido como proveedor candidato para reforma 8A (PJ.25.033.01). |
| 0.18    | 07/05/2026  | **CORRECCIÓN MAYOR — Obra Impernova canalizada por BMC**. Los cargos altos de BMC en 2023-2024 (21.854 €) NO eran honorarios, eran pagos canalizados de la obra Impernova cubiertas 7B/8B. Coste real total de la obra: **−64.656,57 €** (37.667 € cheques + 5.135 € recibos directos + 21.854 € vía BMC), 62% por encima del presupuesto inicial de 40k. Obra **pre-plan plurianual**, NO cuenta en donut 180k. **§16.2 reescrita**: ahorro real de admin BMC→Susana es solo **+778 €/año** (no +8.793). **§16.3 corregida**: ahorro estructural total **+7.248 €/año** (no +15.263) = ~43-50k a 6-7 años (no ~92-107k). **Advertencia añadida sobre impacto en viabilidad §16.5**. **§9.10 actualizada** con bloque Impernova + corrección BMC + Susana cargos pequeños son gastos de oficina/sellos. **§8.4 ampliada** con Juan Francisco Agudo Pedreño (fontanería), Mundo Reformas y Obras, Attias Arquitectura, Impernova. A. Pirtac aclarado como Alexandru Pirtac/Pitarc. |

> Cualquier modificación posterior se anota aquí con resumen del cambio.
