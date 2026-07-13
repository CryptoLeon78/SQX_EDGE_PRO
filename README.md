# SQX Edge Pro

**Aplicación Windows de escritorio para gestión de portafolios SQX, scoring de activos Edge y análisis de calidad de datos MT5.**

Integra Electron (UI nativa), FastAPI (backend cuantitativo) y SQLite (persistencia local) en una suite completa para traders algorítmicos.

---

## 📋 Requisitos Previos

| Componente | Versión | Verificar |
|-----------|---------|----------|
| **Windows** | 10 / 11 | `winver` |
| **Python** | 3.11+ | `python --version` |
| **Node.js** | 18+ LTS | `node --version` |
| **Git** | (opcional) | `git --version` |

---

## 🚀 Instalación y Ejecución

```powershell
cd 'C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO'
Set-ExecutionPolicy -Scope Process Bypass
.\run_dev.ps1
```

**Primera ejecución:** crea `backend\.venv`, instala dependencias Python (`pyproject.toml`) y ejecuta `npm install`.

## ✅ Validación de Inicio

```
✓ Backend conectado
✓ API: http://127.0.0.1:<puerto>
✓ Catálogo: 43 activos, 112 entradas Edge
✓ Snapshots MT5 cargados
✓ Migration: ok
```

Swagger UI disponible en `http://127.0.0.1:<puerto>/docs`.

---

## 🗺️ Estado del Proyecto — Roadmap

**Arquitectura:** Electron → FastAPI (127.0.0.1) → SQLite. El frontend nunca calcula reglas de negocio; todo scoring, rating y agregación vive en Python.

### ✅ Fase 0 — Fundaciones
Electron + FastAPI + SQLite, migraciones, `GET /api/health`, `catalog_seed.json` (33 activos base).

### ✅ Fase 1A — Catálogo persistente
Catálogo de activos en SQLite + endpoint `GET /api/assets`.

### ✅ Fase 1B — Motor de scoring Edge
Categorías Edge, entradas por activo/dirección, `calc_score()` Long/Short con semántica `++/+/~/-`, normalizador de símbolos (`SP500→US500`, `NDX→USTEC`, `GDAXI→GER40`), suite de tests unitarios completa.

### ✅ Fase 2A — Importador MT5 (backend)
- Parser CSV con detección de delimitador (TAB / coma / punto y coma)
- Validación estricta de columnas obligatorias y filas `Year = ALL`
- Normalización de símbolos y persistencia **inmutable** (nuevo snapshot, nunca sobrescribe)
- Soporte CSV con y sin columna `NegSpreadCount`
- **12 tests en verde**, validado contra exports reales AUDCAD y GBPUSD (incluye caso `MinSpread` horario negativo)

### ✅ Fase 2B — Vista funcional Calidad MT5
- Integración completa verificada: Electron + FastAPI + SQLite + Vista Calidad MT5
- Consumo de snapshots persistidos (sin recálculo en JavaScript)
- Navegación cruzada: panel "Por Activo" → scores Long/Short + último snapshot MT5 → "Ver calidad"
- Tabla anual y desglose por hora/sesión renderizados desde backend

### 🔄 Fase 2C — Importación nativa desde Electron *(EN PROGRESO)*
**Objetivo:** diálogo modal de importación con selector de archivos nativo y broker editable.

| Componente | Estado |
|---|---|
| Contrato `POST /api/import/mt5-csv` (`provider`, `stats_path`, `hourly_path`) | ✅ Definido |
| Campo Proveedor/Broker editable con `datalist` (sugerencias: MT5 local, Darwinex, IC Markets, Pepperstone) | 🔄 En diseño |
| Selector nativo Windows para CSV stats + CSV hourly | ⏳ Pendiente |
| Validación pre-importación (símbolo detectado, coincidencia de pareja, delimitador, errores) | ⏳ Pendiente |
| IPC aislado Electron ↔ backend | ⏳ Pendiente |
| Actualización automática de catálogo/snapshots/detalle tras importar | ⏳ Pendiente |

**Regla de diseño:** un cambio de proveedor crea un snapshot independiente (nunca fusiona ni sobrescribe). El selector mostrará `AUDCAD · Darwinex · 12 jul 2026, 17:08`.

### ⏳ Fase 3 — SQX Edge UI completa
Shell Electron con las 5 vistas funcionales (Dashboard, Top Picks, Por Categoría, Matriz Completa, Filtros Fase 2), drawer de detalle, score rings, sparklines, exportación CSV respetando filtros activos.

### ⏳ Fase 4 — Producción Windows
Diálogos nativos completos, logs y diagnóstico, backup automático pre-importación, empaquetado PyInstaller (`--onedir`) + electron-builder, instalador NSIS, smoke tests en VM limpia.

### ⏳ Fase 5 — Automatización SQX
Detector de instalaciones StrategyQuant X / SQCli, ejecución segura de comandos, importación de Databank exports, watch folders, auditoría y generación de paquetes de trabajo SQX.

> Detalle completo de cada fase, contratos API y decisiones técnicas en [`docs/PHASES.md`](docs/PHASES.md).

---

## 📁 Estructura del Proyecto

```
SQX_EDGE_PRO/
├── backend/                  # FastAPI + motor cuantitativo
│   ├── app/
│   │   ├── api/              # health, assets, quality, imports, exports...
│   │   ├── core/              # score_engine, quality_engine, normalizadores
│   │   ├── database/          # migraciones, sesión SQLite
│   │   ├── services/           # mt5_csv_importer, sqx_importer
│   │   └── main.py
│   ├── tests/
│   └── pyproject.toml
├── frontend/                  # HTML + JS vanilla (consumidor de API)
│   ├── index.html
│   ├── css/
│   └── js/
│       └── views/            # activos, top-picks, calidad-datos, imports...
├── desktop/                   # Electron shell
│   ├── main.js
│   ├── preload.js
│   ├── backend-manager.js
│   └── paths.js
├── docs/
│   ├── architecture.md
│   ├── data-contracts.md
│   └── PHASES.md              # roadmap detallado
├── package.json
├── .gitignore
├── run_dev.ps1
└── README.md
```

---

## 🔐 Seguridad y Privacidad

Nunca se commitean: `.env`, `data/`, `imports/`, `exports/`, `logs/`, `*.db`, `node_modules/`, `.venv/`. Ver `.gitignore` completo.

**Ubicaciones de datos:**

| Tipo | Ubicación |
|------|-----------|
| Repo (código) | `C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO` |
| Datos operativos | `%LOCALAPPDATA%\SQX Edge Pro\` |
| Base de datos | `%LOCALAPPDATA%\SQX Edge Pro\sqx_edge.db` |

---

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🐛 Troubleshooting

**Backend no inicia:**
```powershell
Remove-Item backend\.venv -Recurse -Force
.\run_dev.ps1
```

**Puerto en uso:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

## 🤝 Workflow de Desarrollo

- **`main`** → producción, solo cambios validados vía PR
- **`develop`** → rama base de desarrollo
- **`feature/*`** → una rama por incremento, merge a `develop` tras revisión
- **`hotfix/*`** → fix urgente, merge directo a `main` y `develop`

---

## 📜 Licencia

[Especifica tu licencia — MIT, GPL, Privada, etc.]
