# AGENTS.md — CP Modesto Lafuente 63

Guía para Codex al trabajar en este repositorio.

## Descripción del proyecto

Dashboard de gestión financiera y de obras para la comunidad de propietarios de **Modesto Lafuente 63, Madrid**. Permite:
- Seguimiento de proyectos/mejoras del edificio por año
- Análisis de energía (gas, electricidad, agua)
- Categorización de gastos y servicios
- Conciliación bancaria (movimientos Banc Sabadell 2020–2026)
- Gestión de usuarios y auditoría de sesiones
- Planificación plurianual 2025–2029

## Stack técnico

- **Frontend:** HTML + CSS + JS vanilla. Sin framework, sin build system.
- **Backend/DB:** [Supabase](https://supabase.com) — auth, base de datos PostgreSQL, storage.
- **Librerías CDN:** `@supabase/supabase-js@2`, Chart.js, Montserrat (Google Fonts).
- **Supabase URL:** `https://byqtsuskdbgwpyvyiprc.supabase.co`
- **Anon key:** en `ML63.html` línea ~1736 (publishable, no es un secreto).

## Estructura de archivos

```
ML63/
├── ML63.html                      # App completa (single-file SPA)
├── carga_inicial_movimientos.sql  # Carga histórica 1.304 movimientos (2020–2026)
├── AGENTS.md
└── Recursos/                      # Documentos de la comunidad
    ├── Actas/
    ├── Alexandru Pirtac/
    ├── Banco/
    ├── Coeficientes/
    ├── GPT/
    ├── Gas Power/
    ├── Ista/
    └── Naturgy/
```

> El objetivo a medio plazo es **refactorizar ML63.html** en múltiples ficheros (`index.html` + `css/` + `js/`) sin romper funcionalidad.

## Tabs / secciones de la app

| Tab ID | Etiqueta | Propósito |
|--------|----------|-----------|
| `tab2026` | 📋 2026 · En Curso | Proyectos año en curso + resumen tesorería |
| `tab2025` | ✓ 2025 · Cerrado | Vista de año cerrado (solo lectura) |
| `energia` | ⚡ Energía | Análisis de costes energéticos |
| `gastos` | 💼 Gastos & Servicios | Desglose de gastos operativos |
| `admin` | 🏛️ Gestión | Gestión de usuarios, logs de sesión, documentos |
| `plan` | 🎯 Plan 2025–2029 | Planificación plurianual |
| `admin-panel` | ⚙️ Admin | Controles solo para admins (oculto a viewers) |

## Tablas Supabase

| Tabla | Operaciones | Descripción |
|-------|-------------|-------------|
| `proyectos` | SELECT / INSERT / UPDATE / DELETE | Proyectos de mejora con presupuesto, estado, notas. **UNIQUE(nombre, año)** |
| `movimientos` | SELECT / INSERT | Movimientos bancarios (fecha, concepto, importe, saldo, ref1). **UNIQUE(fecha, concepto, importe, saldo)** |
| `user_roles` | SELECT / INSERT / UPDATE / UPSERT | Email → rol (admin / viewer) |
| `session_log` | SELECT / INSERT | Auditoría de logins/logouts |
| `documentos` | SELECT | Extractos bancarios y documentos subidos |

## Funciones JS principales

| Función | Propósito |
|---------|-----------|
| `initAuth()` | Comprueba sesión Supabase al cargar |
| `doLogin()` | Login email/password |
| `showApp(email)` | Carga rol, muestra UI, fetcha datos |
| `doLogout()` | Cierra sesión y recarga |
| `loadFromSupabase()` | Carga proyectos de la tabla `proyectos` |
| `switchTab(e, name)` | Navega entre tabs |
| `openModal()` / `closeModal()` | Modal de crear/editar proyecto |
| `saveProyecto()` | INSERT o UPDATE de proyecto |
| `delProyecto()` | DELETE de proyecto |
| `processBancoFile(file)` | Parsea Excel de Sabadell e inserta en `movimientos` |
| `loadAdminPanel()` | Carga panel admin (solo admins) |
| `calcPlan()` | Calcula KPIs y agregados del plan plurianual |
| `renderProjects2026()` / `renderProjects2025()` | Renderiza tarjetas de proyecto por año |
| `makeBars()` / `makeStackedBars()` / `makeGroupedBars()` | Renderiza gráficas con Chart.js |

## Variables CSS

```css
--primary: #4F46E5
--secondary: #10B981
--accent: #F59E0B
--danger: #EF4444
--info: #0EA5E9
--purple: #8B5CF6
--bg: #FAFBFC
--surface: #FFFFFF
--text: #0F172A
--text-soft: #475569
--text-muted: #64748B
--border: #E2E8F0
```

## Roles de usuario

- **admin** — acceso completo: crear/editar/borrar proyectos, panel admin, subir documentos
- **viewer** — solo lectura

## Datos bancarios

- Fuente: Banc Sabadell, cuenta `0081-7125-93-0001279538`
- Rango histórico: 2020-12-31 → 2026-05-12
- Total: 1.326 movimientos (tras deduplicación 13/05/2026)
- La carga inicial está en `carga_inicial_movimientos.sql` — ejecutar **solo** si `movimientos` está vacía
- **Restricciones UNIQUE activas** — las tablas `proyectos` y `movimientos` tienen constraints que impiden inserciones duplicadas (ver §Tablas Supabase)

## Normas de desarrollo

- **No editar CSS directamente en el `<style>` del HTML** sin motivo — cuando se refactorice, el CSS irá a ficheros externos.
- **No exponer secretos** — la anon key de Supabase es pública por diseño; nunca añadir la service key al frontend.
- **Sin frameworks** — mantener vanilla JS; no introducir React, Vue, etc.
- **Sin build system** — los ficheros se sirven directamente, no hay npm run build.
- La app se despliega abriendo `ML63.html` directamente en el navegador (o via servidor estático).
