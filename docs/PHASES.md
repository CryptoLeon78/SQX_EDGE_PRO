# Roadmap Técnico — SQX Edge Pro

Estado consolidado y detalle de implementación por fase. Este documento se actualiza al cerrar o iniciar cada fase.

**Principio arquitectónico invariante:** el frontend (Electron/JS) nunca calcula reglas de negocio. Todo scoring, rating, agregación y validación vive en el backend Python (FastAPI). El frontend solo pide datos vía API y los representa.

---

## ✅ Fase 0 — Fundaciones
**Estado: Cerrada**

- Repositorio Git + estructura inicial (`desktop/`, `frontend/`, `backend/`, `docs/`)
- Entorno Python + Node/Electron + scripts PowerShell (`run_dev.ps1`)
- `catalog_seed.json`: 33 activos, 7 categorías, ratings, TFs, razones, direcciones
- SQLite con sistema de migraciones
- Endpoint `GET /api/health`

---

## ✅ Fase 1A — Catálogo de activos persistente
**Estado: Cerrada**

- Migración de `catalog_seed.json` a modelos SQLAlchemy + SQLite
- Endpoint `GET /api/assets`

## ✅ Fase 1B — Motor de scoring Edge
**Estado: Cerrada**

- Modelos Pydantic + SQLAlchemy para categorías Edge y entradas por activo/dirección
- `calc_score(asset, dir_filter)` con semántica exacta para `L`, `S`, `L/S`
- Score normalizado, estrellas, filtros de ratings y rankings
- Normalizador de símbolos: `SP500 → US500`, `NDX → USTEC`, `GDAXI → GER40`
- Tests unitarios obligatorios: `++`, `+`, `~`, `-`, todas direcciones, categorías vacías

**Resultado:** 43 activos en catálogo, 112 entradas Edge activas.

---

## ✅ Fase 2A — Importador MT5 (backend)
**Estado: Cerrada — 12 tests en verde**

### Input del EA (`DataQualityAnalyzer_v15.mq5`)
- **CSV anual de spreads:** símbolo, año, spread medio, percentiles P50/P75/P90/P99, mínimo, máximo, moda, nº muestras, spreads invertidos, propiedades estáticas del instrumento
- **CSV horario:** hora, sesión, percentiles equivalentes

### Alcance implementado
- Detección de delimitador: TAB, coma, punto y coma
- Parseo de filas anuales + fila global `Year = ALL` (fuente de percentiles agregados — **no se promedian percentiles anuales**, el EA ya los recalcula sobre histograma combinado)
- Validación estricta de columnas obligatorias
- Normalizador de aliases inicial (extensible por perfil): `SP500→US500`, `NDX→USTEC`, `GDAXI→GER40`
- Persistencia **inmutable**: cada importación crea un `QualitySnapshot` nuevo, nunca sobrescribe
- Listado de snapshots + detalle del último snapshot por activo
- Compatibilidad con CSV con y sin columna `NegSpreadCount` (retrocompatibilidad con versiones previas del EA)
- Importación manual (sin selector nativo aún — eso es Fase 2C)

### Validación real
- Exports reales de **AUDCAD** y **GBPUSD**
- Caso extremo cubierto: `MinSpread` horario negativo, normalizado sin contaminar métricas útiles

---

## ✅ Fase 2B — Vista funcional Calidad MT5
**Estado: Cerrada**

### Verificado en integración completa
- Cadena completa operativa: Electron → FastAPI → migración → SQLite → Vista Calidad MT5
- Estado confirmado: **43 activos, 112 entradas Edge, 2 snapshots MT5 cargados**
- Snapshot AUDCAD verificado: proveedor `MT5 local`, importado 12 jul 2026 17:08, 176.051.201 muestras
- Tabla anual + desglose hora/sesión renderizados **desde backend** (sin cálculo en JS)

### Navegación cruzada verificada
- Panel "Por Activo" → AUDCAD muestra scores Long/Short, 3 entradas estratégicas Edge, último snapshot MT5
- Acceso directo "Ver calidad" desde el panel de activo

---

## 🔄 Fase 2C — Importación nativa desde Electron
**Estado: En progreso**

### Objetivo
Reemplazar la importación manual (Fase 2A) por un flujo nativo: selector de archivos Windows + modal propio de la app, con campo de broker/proveedor editable desde el primer día.

### Decisión de diseño: campo Proveedor/Broker
No es una lista cerrada — es un campo editable con `datalist`:

| Campo | Comportamiento |
|---|---|
| **Proveedor / broker** | Obligatorio, editable, con sugerencias (`MT5 local`, `Darwinex`, `IC Markets`, `Pepperstone` + proveedores ya existentes en SQLite) |
| **CSV estadísticas** | Botón "Seleccionar" → diálogo nativo Windows |
| **CSV horario** | Botón "Seleccionar" → diálogo nativo Windows |
| **Validación** | Muestra símbolo detectado, coincidencia de pareja de archivos, delimitador, errores — antes de habilitar importación |
| **Importar snapshot** | Habilitado solo con proveedor + pareja de CSV válida |

### Reglas de persistencia (acordadas)
- El backend guarda el proveedor exactamente como se escribió (texto normalizado, ej. `Darwinex`)
- El selector de Calidad MT5 mostrará: `AUDCAD · Darwinex · 12 jul 2026, 17:08`
- Las sugerencias del `datalist` se construyen desde proveedores ya presentes en SQLite + valores iniciales fijos
- **Un cambio de broker crea un snapshot independiente** — nunca sobrescribe ni fusiona con snapshots de otro proveedor
- Los CSV del EA no incluyen campo broker — debe venir siempre de la importación (input del usuario)

### Contrato API definido
```json
POST /api/import/mt5-csv
{
  "provider": "Darwinex",
  "stats_path": "C:\\ruta\\AUDCAD_spread_stats_2026.07.10.csv",
  "hourly_path": "C:\\ruta\\AUDCAD_spread_hourly_2026.07.10.csv"
}
```

### Checklist de implementación

| Tarea | Estado |
|---|---|
| Contrato `POST /api/import/mt5-csv` | ✅ Definido |
| Endpoint backend: validación previa (símbolo, pareja, delimitador) | 🔄 En desarrollo |
| Endpoint backend: import + creación de snapshot con `provider` | 🔄 En desarrollo |
| Modal frontend con campo Proveedor (`datalist`) | ⏳ Pendiente |
| IPC aislado Electron (`preload.js`) para diálogo nativo de archivos | ⏳ Pendiente |
| Validación de pareja `*_spread_stats_*.csv` + `*_spread_hourly_*.csv` | ⏳ Pendiente |
| Actualización automática post-import: catálogo, lista de snapshots, detalle | ⏳ Pendiente |
| Tests de integración del flujo completo modal → IPC → API → SQLite | ⏳ Pendiente |

---

## ⏳ Fase 3 — SQX Edge UI completa
**Estado: Pendiente**

- Shell Electron funcional con las 5 vistas: Dashboard, Top Picks, Por Categoría, Matriz Completa, Filtros Fase 2
- Drawer de detalle, score rings, sparklines, heatmap matriz
- Exportación CSV desde API respetando filtros activos (no exportar desde estado JS local)
- Persistencia de preferencias visuales/filtros (SQLite o preferencias Electron)

---

## ⏳ Fase 4 — Producción Windows
**Estado: Pendiente**

- Diálogos nativos completos: archivos, carpetas, BD, exportaciones, backups
- Logs legibles + pantalla de diagnóstico
- Backup automático de SQLite antes de importaciones masivas
- Empaquetado: `PyInstaller --onedir` (backend) — se prefiere sobre `--onefile` por fiabilidad con dependencias científicas
- `electron-builder` + NSIS: instalador Windows, icono, accesos directos, desinstalador
- Smoke tests desde VM Windows limpia

**Camino de compilación:**
```
1. Python backend → PyInstaller --onedir → backend/dist/sqx-edge-api/sqx-edge-api.exe
2. Desktop shell → electron-builder → release/SQX Edge Pro Setup.exe
```

En producción, Electron localiza el ejecutable del backend en `resources`, arranca FastAPI solo en `127.0.0.1`, espera `GET /api/health`, abre la ventana principal, y cierra el proceso hijo al salir.

---

## ⏳ Fase 5 — Automatización SQX
**Estado: Pendiente**

- Detector de instalaciones StrategyQuant X y SQCli
- Registro de rutas por perfil
- Ejecución segura de comandos SQCli
- Importación de Databank exports
- Watch folders para importaciones MT5/SQX automáticas
- Auditoría y generación de paquetes de trabajo SQX

**Principio de integración progresiva:** la app debe funcionar en modo manual aunque SQCli no exista; la automatización se activa solo cuando se detecta y valida su ruta.

---

## Decisiones técnicas de referencia

| Área | Decisión | Motivo |
|---|---|---|
| App escritorio | Electron | `.exe`, diálogos nativos, shell estable |
| Interfaz | HTML/CSS/JS ES6 modular | Ligera, sin dependencia de frameworks |
| API local | FastAPI | Tipado, docs automática, testeable |
| Motor cuantitativo | Python | Reutiliza scripts/importadores existentes |
| Base de datos | SQLite | Portable, sin servidor, fácil backup |
| ORM | SQLAlchemy | Migraciones, modelos, queries mantenibles |
| Validación | Pydantic | Contratos consistentes UI↔API↔CSV↔BD |
| Distribución Python | PyInstaller `--onedir` | Más fiable que `--onefile` para deps científicas |
| Instalador | electron-builder + NSIS | Instalador Windows completo |

## Vertical slice original (referencia de arranque del proyecto)

```
Electron abre → Python backend arranca → SQLite se inicializa
→ Catálogo de 33 activos cargado → Vista Por Activo consume /api/assets
→ Click EURUSD muestra score/detalle → Importa CSV del EA
→ Snapshot de calidad persistido → Vista Calidad MT5 lo muestra
```

Esta cadena mínima (ya validada y funcionando) es la base estable sobre la que se construyen el resto de módulos.
