-- =============================================================================
-- SQL UPDATE SCRIPT: 2026 ACTIVE COMMUNITY PROJECTS (CP MODESTO LAFUENTE 63)
-- =============================================================================
-- This script updates the database records in the 'proyectos' table for:
-- 1. Tuberías agua · Proyecto grande (A. Pirtac)
-- 2. Sellado y limpieza ventanal · Navacon Vertical (replaces Pinta Limpio)
--
-- No bank references are linked yet, as invoice documents are pending.
-- RUN THIS SCRIPT IN SUPABASE SQL EDITOR TO SYNCHRONIZE DATABASE.
-- =============================================================================

-- 1. UPDATE: "Tuberías agua · Proyecto grande" (A. Pirtac)
-- Budget: 12.700,00 € (Base Imponible sin IVA) | 13.970,00 € (con 10% IVA)
-- Stored under Year 2026 (En Curso).
INSERT INTO public.proyectos (año, cat, nombre, pres, progreso, obs, banco_ref)
VALUES (
  '2026',
  'progreso',
  'Tuberías agua · Proyecto grande',
  -12700.00,
  0.25, -- Active project in progress
  'Proveedor: A. Pirtac. Presupuesto de Cliente nº 0001-000034 (12.700,00€ sin IVA, 13.970,00€ con 10% IVA = 13.970,00€). Factura y conciliación bancaria pendientes.',
  NULL
)
ON CONFLICT (nombre, año) 
DO UPDATE SET 
  cat = EXCLUDED.cat,
  pres = EXCLUDED.pres,
  obs = EXCLUDED.obs,
  banco_ref = NULL; -- Explicitly keep bank references unlinked until invoice upload


-- 2. UPDATE: "Sellado y limpieza ventanal · Pinta Limpio" ➔ "Sellado y limpieza ventanal · Navacon Vertical"
-- First, let's rename the old "Pinta Limpio" project if it exists in the database to our new supplier "Navacon Vertical".
UPDATE public.proyectos
SET 
  nombre = 'Sellado y limpieza ventanal · Navacon Vertical',
  pres = -3051.00,
  obs = 'Proveedor: Navacon Vertical (sustituye a Pinta Limpio). Presupuesto nuevo PTTO090A-2026 (3.051,00€ sin IVA, 3.356,10€ con 10% IVA). Factura y conciliación bancaria pendientes.'
WHERE nombre = 'Sellado y limpieza ventanal · Pinta Limpio' AND año = '2026';

-- If it wasn't there before, we upsert the new "Navacon Vertical" project to ensure it is in the database:
INSERT INTO public.proyectos (año, cat, nombre, pres, progreso, obs, banco_ref)
VALUES (
  '2026',
  'pendiente',
  'Sellado y limpieza ventanal · Navacon Vertical',
  -3051.00,
  0.00, -- Pending project
  'Proveedor: Navacon Vertical (sustituye a Pinta Limpio). Presupuesto nuevo PTTO090A-2026 (3.051,00€ sin IVA, 3.356,10€ con 10% IVA). Factura y conciliación bancaria pendientes.',
  NULL
)
ON CONFLICT (nombre, año) 
DO UPDATE SET 
  cat = EXCLUDED.cat,
  pres = EXCLUDED.pres,
  obs = EXCLUDED.obs,
  banco_ref = NULL; -- Keep bank references unlinked
