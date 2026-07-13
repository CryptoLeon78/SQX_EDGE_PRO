Sí: hacemos **solo SQX Edge Pro**, diseñado desde el inicio como aplicación Windows instalable y compilable a `.exe`. La arquitectura correcta es **Electron + FastAPI/Python + SQLite**, no Streamlit ni un HTML standalone: así tendrás interfaz de escritorio real, selectores nativos de archivos/rutas, backend cuantitativo reutilizable y una ruta limpia a instalador Windows. [perplexity](https://www.perplexity.ai/search/0bb42daf-d4c1-4a17-aad2-1fe8f3d56adc)

## Arquitectura objetivo

```text
SQX Edge Pro.exe
│
├── Electron shell
│   ├── Ventana nativa Windows
│   ├── UI HTML / CSS / JavaScript
│   ├── Diálogos nativos: abrir CSV, SQB, JSON, carpetas
│   ├── Gestión de menú, icono, actualizaciones y logs
│   └── Arranque/parada controlada del backend Python
│
├── Backend Python local
│   ├── FastAPI en 127.0.0.1 con puerto dinámico
│   ├── Motor SQX Edge: catálogo, ratings, scoring y filtros
│   ├── Importadores CSV de MT5 / SQX
│   ├── Integración futura con SQCli
│   ├── SQLite como fuente persistente
│   └── Exportaciones CSV, JSON y packs de auditoría
│
└── Datos locales
    ├── sqx_edge.db
    ├── imports/
    ├── exports/
    ├── profiles/
    ├── logs/
    └── backups/
```

Electron resuelve lo que un navegador puro no puede hacer bien: seleccionar rutas reales de Windows, crear archivos en ubicaciones elegidas por el usuario, ejecutar el backend local y empaquetar la experiencia como escritorio. Es además una línea que ya has elegido para proyectos que combinan UI HTML y Python local. [perplexity](https://www.perplexity.ai/search/0bb42daf-d4c1-4a17-aad2-1fe8f3d56adc)

## Decisión tecnológica

| Área | Decisión | Motivo |
|---|---|---|
| Aplicación escritorio | Electron | Integración Windows, `.exe`, diálogos nativos y shell estable |
| Interfaz | HTML, CSS, JavaScript ES6 modular | Ligera, rápida y sin dependencia de frameworks |
| API local | FastAPI | Tipado, documentación automática, pruebas y extensibilidad |
| Motor cuantitativo | Python | Reutiliza tus scripts, importadores y lógica de métricas |
| Base de datos | SQLite | Portable, sin servidor, fácil de respaldar y empaquetar |
| ORM | SQLAlchemy | Migraciones, modelos claros y consultas mantenibles |
| Validación | Pydantic | Contratos consistentes entre UI, API, CSV y base de datos |
| Distribución Python | PyInstaller `--onedir` | Más fiable que `--onefile` para dependencias cuantitativas |
| Instalador | electron-builder + NSIS | Instalador Windows, icono, accesos directos y desinstalación |

FastAPI permite que el frontend y el motor de cálculo evolucionen independientemente; SQLite aporta edición escalable, histórico y persistencia robusta, que ya has identificado como necesaria en aplicaciones operativas con múltiples cambios y reglas. [perplexity](https://www.perplexity.ai/search/4909ecdf-cd2b-4c56-a744-d6d7c1daa793)

## Principio fundamental

**El frontend no calcula decisiones cuantitativas.** Solo pide datos y los representa.

```text
UI Electron
   │
   ├── GET /api/assets
   ├── GET /api/assets/{id}/detail
   ├── GET /api/top-picks?direction=L
   ├── GET /api/matrix?type=Forex&rating=+
   ├── POST /api/import/mt5-csv
   ├── POST /api/import/sqx-export
   ├── POST /api/export/matrix-csv
   └── POST /api/quality/recalculate
   │
FastAPI
   │
   ├── score_engine.py
   ├── phase2_filters.py
   ├── quality_engine.py
   ├── mt5_csv_importer.py
   ├── sqx_importer.py
   └── SQLite
```

Esto evita duplicar fórmulas entre JavaScript y Python, mantiene el scoring testeable y permite reutilizar el mismo motor en automatizaciones futuras, CLI, SQCli o procesos batch. Tu objetivo previo de reutilizar scripts Python existentes desde una interfaz HTML encaja exactamente con esta separación. [perplexity](https://www.perplexity.ai/search/4909ecdf-cd2b-4c56-a744-d6d7c1daa793)

## Estructura del repositorio

```text
SQX_EDGE_PRO/
│
├── README.md
├── .gitignore
├── pyproject.toml
├── package.json
├── electron-builder.yml
├── build.ps1
├── run_dev.ps1
├── build_release.ps1
│
├── desktop/
│   ├── main.js
│   ├── preload.js
│   ├── backend-manager.js
│   ├── menu.js
│   ├── paths.js
│   └── assets/
│       └── sqx-edge.ico
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   ├── tokens.css
│   │   ├── app.css
│   │   ├── controls.css
│   │   ├── tables.css
│   │   └── views.css
│   └── js/
│       ├── app.js
│       ├── api-client.js
│       ├── app-state.js
│       ├── navigation.js
│       ├── ui/
│       │   ├── components.js
│       │   ├── score-ring.js
│       │   ├── sparkline.js
│       │   └── csv-download.js
│       └── views/
│           ├── activos.js
│           ├── top-picks.js
│           ├── categorias.js
│           ├── filtros-fase2.js
│           ├── matriz.js
│           ├── calidad-datos.js
│           ├── imports.js
│           └── settings.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   │
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── assets.py
│   │   │   ├── categories.py
│   │   │   ├── top_picks.py
│   │   │   ├── matrix.py
│   │   │   ├── quality.py
│   │   │   ├── imports.py
│   │   │   ├── exports.py
│   │   │   ├── profiles.py
│   │   │   └── sqcli.py
│   │   │
│   │   ├── core/
│   │   │   ├── enums.py
│   │   │   ├── constants.py
│   │   │   ├── models.py
│   │   │   ├── score_engine.py
│   │   │   ├── edge_catalog.py
│   │   │   ├── phase2_engine.py
│   │   │   ├── quality_engine.py
│   │   │   └── symbol_normalizer.py
│   │   │
│   │   ├── database/
│   │   │   ├── session.py
│   │   │   ├── schema.py
│   │   │   ├── migrations.py
│   │   │   └── repositories/
│   │   │       ├── asset_repository.py
│   │   │       ├── quality_repository.py
│   │   │       ├── import_repository.py
│   │   │       └── profile_repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── mt5_csv_importer.py
│   │   │   ├── sqx_databank_importer.py
│   │   │   ├── data_quality_service.py
│   │   │   ├── export_service.py
│   │   │   ├── backup_service.py
│   │   │   ├── sqcli_service.py
│   │   │   └── watch_folder_service.py
│   │   │
│   │   └── resources/
│   │       ├── catalog_seed.json
│   │       ├── phase2_defaults.json
│   │       ├── symbol_aliases.json
│   │       └── quality_thresholds.json
│   │
│   └── tests/
│       ├── test_scoring.py
│       ├── test_direction_semantics.py
│       ├── test_catalog_seed.py
│       ├── test_mt5_csv_importer.py
│       ├── test_quality_engine.py
│       └── test_exports.py
│
├── mt5/
│   └── DataQualityAnalyzer_v15.mq5
│
├── docs/
│   ├── architecture.md
│   ├── data-contracts.md
│   ├── mt5-import-guide.md
│   ├── sqcli-integration.md
│   └── build-release.md
│
└── installer/
    ├── license.txt
    └── installer_notes.md
```

## Modelo de datos

El modelo debe distinguir tres fuentes de verdad:

1. **Catálogo Edge:** reglas estratégicas, categorías, direcciones, ratings, TFs y razones.
2. **Calidad de datos:** resultado importado desde MT5 por broker, símbolo, rango temporal y fecha de importación.
3. **Perfil operativo:** configuración concreta que une catálogo, broker, aliases, filtros fase 2 y decisiones de uso.

```text
Asset
├── EURUSD
├── asset_type = Forex
├── subtype = Major
└── EdgeEntry[]
    ├── category = tendencia
    ├── direction = L/S
    ├── rating = ++
    ├── timeframes = H1, H4, D1
    └── why = ...
    
QualitySnapshot
├── provider = Darwinex
├── raw_symbol = EURUSD
├── canonical_asset_id = EURUSD
├── imported_at = ...
├── analysis_from = ...
├── analysis_to = ...
├── gaps_pct
├── spikes_pct
├── bad_ohlc_pct
├── total_ticks
├── current_spread
└── yearly/hourly spread stats

OperationalProfile
├── name = Darwinex H1 Production
├── provider = Darwinex
├── asset universe = ...
├── quality constraints = ...
├── phase 2 thresholds = ...
└── selected strategy families = ...
```

El EA actual ya es una fuente sólida para los `QualitySnapshot`: calcula calidad de velas, gaps, spikes, Bad OHLC, spread actual, percentiles por año y distribución horaria por sesión; también excluye spreads invertidos de las métricas para no contaminar los percentiles. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/155971156/3150e9b7-27a2-4d9e-85a6-24adeea252a6/DataQualityAnalyzer_v15.mq5?AWSAccessKeyId=ASIA2F3EMEYE5HAGSQHR&Signature=i5cuyC75%2Fmxh99oceEDPDvq%2Bu%2BY%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEB4aCXVzLWVhc3QtMSJHMEUCIAiAGrXu2D2CbIadVmZSxrRZ%2BePP2vjlgOpd3dGScd4WAiEAljwVJzn611XJrT0M9g4JjxCO2OtcVnICOOZkCVkUD1wq%2FAQI5v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDI21KCkpGSnmGaUrYirQBNYaPSatytEgm9MJUloU41jA7Sklir48bMKK95IWA7p1AST%2BHLyNTIJPpOHlu3yMlU3jRNH%2B5NOVze230aMDC1IZAeYUoyqLz4fGeVFpMp4FNet2ZIe4Tuuol0ALr3fmQhhNBgbnu6XNSB%2Fsn3Jh1IrwA5qHcE7n%2BayKQ0zD90mDG9eOvUUqdn659DXwCExFJuMXwAbMoONNOkYPCugFnh6SCJTp78wNXh%2BQIJ1sRXnStePKAuTDX5I6y762XEu8suqGFD%2FS7jMrZkVVdYHf3Ffi17btpTwdUlW0dNqAJfUXaG0JUIN%2F9LxMc8g17L31Chv1POL61lWbbgqUKyXoSyHXmlCtakczA5TAGm3ZIESIQAR4QD21IGLCA1aQMrmsjNRULSM5OCIEIHGXRa1TH3Qwz%2BRAYNyN%2Flu5GTdtuGTawNIvSNG25qPfvKyohJDzwMEjCDJ%2FpuFCbt5bWSYCjRqQnPOQM84NklRCnrvEN4%2F8SBN6VWzHZFjWz9v1142tVnVZqpo1ZeYZQ6jn3RhJJfxO8MnvXF1kYNWp3XVXtEhDi%2FsUkoS0%2FW4HjadqhnY1BUevW5ZZQA1F9e9fx%2FIb2Prdu04e59TFO0F%2FdgHOJkf7u%2FabaapzmnMpeDNd3NCObAjaFnNk%2FuDq8vqzVGnMH8AOuwdFcXq7xBwCu%2FeFRhqRfNM4cOing2v5SgsTwTr7OF3k%2F5u6Byal%2BEt7MLQ62cPwl0c1rZ%2FDTTSxnc%2BOEhkQwR9%2FutNty0YOXuqdoJE%2FSLnMlZux24AwhuRTjDd0Pqow76nO0gY6mAEiIaCBQMxo47YeobRyXH2qwAGNyu2jAhzqkfgQ5EBhd%2F9rbVCNMAInVk%2BIxhC0RLiFlmLoEIbYohTnWXXSYpqGeAHOlTVVrao6w3nDvcf7ZoFZdsn1xDIT9d7AMvDLFnXje9FL%2B%2B3XtDDXTm73c33ChBdCKOiFi%2BYoRiJ8EGhu4yOeHBz7uScUdrxeOajb1vJqDTm49ZxOXw%3D%3D&Expires=1783866050)

## Integración con Data Quality

El archivo `DataQualityAnalyzer_v15.mq5` no se “convierte” a Python ni se embebe como código de aplicación. Permanece como parte de `mt5/`, se instala o copia a MT5 y produce los CSV que importará SQX Edge Pro. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/155971156/3150e9b7-27a2-4d9e-85a6-24adeea252a6/DataQualityAnalyzer_v15.mq5?AWSAccessKeyId=ASIA2F3EMEYE5HAGSQHR&Signature=i5cuyC75%2Fmxh99oceEDPDvq%2Bu%2BY%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEB4aCXVzLWVhc3QtMSJHMEUCIAiAGrXu2D2CbIadVmZSxrRZ%2BePP2vjlgOpd3dGScd4WAiEAljwVJzn611XJrT0M9g4JjxCO2OtcVnICOOZkCVkUD1wq%2FAQI5v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDI21KCkpGSnmGaUrYirQBNYaPSatytEgm9MJUloU41jA7Sklir48bMKK95IWA7p1AST%2BHLyNTIJPpOHlu3yMlU3jRNH%2B5NOVze230aMDC1IZAeYUoyqLz4fGeVFpMp4FNet2ZIe4Tuuol0ALr3fmQhhNBgbnu6XNSB%2Fsn3Jh1IrwA5qHcE7n%2BayKQ0zD90mDG9eOvUUqdn659DXwCExFJuMXwAbMoONNOkYPCugFnh6SCJTp78wNXh%2BQIJ1sRXnStePKAuTDX5I6y762XEu8suqGFD%2FS7jMrZkVVdYHf3Ffi17btpTwdUlW0dNqAJfUXaG0JUIN%2F9LxMc8g17L31Chv1POL61lWbbgqUKyXoSyHXmlCtakczA5TAGm3ZIESIQAR4QD21IGLCA1aQMrmsjNRULSM5OCIEIHGXRa1TH3Qwz%2BRAYNyN%2Flu5GTdtuGTawNIvSNG25qPfvKyohJDzwMEjCDJ%2FpuFCbt5bWSYCjRqQnPOQM84NklRCnrvEN4%2F8SBN6VWzHZFjWz9v1142tVnVZqpo1ZeYZQ6jn3RhJJfxO8MnvXF1kYNWp3XVXtEhDi%2FsUkoS0%2FW4HjadqhnY1BUevW5ZZQA1F9e9fx%2FIb2Prdu04e59TFO0F%2FdgHOJkf7u%2FabaapzmnMpeDNd3NCObAjaFnNk%2FuDq8vqzVGnMH8AOuwdFcXq7xBwCu%2FeFRhqRfNM4cOing2v5SgsTwTr7OF3k%2F5u6Byal%2BEt7MLQ62cPwl0c1rZ%2FDTTSxnc%2BOEhkQwR9%2FutNty0YOXuqdoJE%2FSLnMlZux24AwhuRTjDd0Pqow76nO0gY6mAEiIaCBQMxo47YeobRyXH2qwAGNyu2jAhzqkfgQ5EBhd%2F9rbVCNMAInVk%2BIxhC0RLiFlmLoEIbYohTnWXXSYpqGeAHOlTVVrao6w3nDvcf7ZoFZdsn1xDIT9d7AMvDLFnXje9FL%2B%2B3XtDDXTm73c33ChBdCKOiFi%2BYoRiJ8EGhu4yOeHBz7uScUdrxeOajb1vJqDTm49ZxOXw%3D%3D&Expires=1783866050)

Flujo operativo:

```text
MT5 + DataQualityAnalyzer
        │
        ├── SpreadStats_*.csv
        └── SpreadHourly_*.csv
                │
                ▼
       SQX Edge Pro → Importar calidad MT5
                │
                ▼
      Validación + normalización del símbolo
                │
                ▼
        SQLite + snapshot inmutable
                │
                ▼
  Calidad de datos / Matriz / Filtros de operación
```

El importador debe seguir aceptando CSV delimitados por tabulador, coma o punto y coma, ya que la lógica actual contempla los tres formatos y MetaTrader puede usar TAB con `FILE_CSV`. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/155971156/e4fa7f5f-4783-497c-a879-e5a0b85c8496/sqx_monitor_v8-2.html?AWSAccessKeyId=ASIA2F3EMEYE5HAGSQHR&Signature=RoQJoniyc8xPh1jO8%2FxtV%2F34a9I%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEB4aCXVzLWVhc3QtMSJHMEUCIAiAGrXu2D2CbIadVmZSxrRZ%2BePP2vjlgOpd3dGScd4WAiEAljwVJzn611XJrT0M9g4JjxCO2OtcVnICOOZkCVkUD1wq%2FAQI5v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARABGgw2OTk3NTMzMDk3MDUiDI21KCkpGSnmGaUrYirQBNYaPSatytEgm9MJUloU41jA7Sklir48bMKK95IWA7p1AST%2BHLyNTIJPpOHlu3yMlU3jRNH%2B5NOVze230aMDC1IZAeYUoyqLz4fGeVFpMp4FNet2ZIe4Tuuol0ALr3fmQhhNBgbnu6XNSB%2Fsn3Jh1IrwA5qHcE7n%2BayKQ0zD90mDG9eOvUUqdn659DXwCExFJuMXwAbMoONNOkYPCugFnh6SCJTp78wNXh%2BQIJ1sRXnStePKAuTDX5I6y762XEu8suqGFD%2FS7jMrZkVVdYHf3Ffi17btpTwdUlW0dNqAJfUXaG0JUIN%2F9LxMc8g17L31Chv1POL61lWbbgqUKyXoSyHXmlCtakczA5TAGm3ZIESIQAR4QD21IGLCA1aQMrmsjNRULSM5OCIEIHGXRa1TH3Qwz%2BRAYNyN%2Flu5GTdtuGTawNIvSNG25qPfvKyohJDzwMEjCDJ%2FpuFCbt5bWSYCjRqQnPOQM84NklRCnrvEN4%2F8SBN6VWzHZFjWz9v1142tVnVZqpo1ZeYZQ6jn3RhJJfxO8MnvXF1kYNWp3XVXtEhDi%2FsUkoS0%2FW4HjadqhnY1BUevW5ZZQA1F9e9fx%2FIb2Prdu04e59TFO0F%2FdgHOJkf7u%2FabaapzmnMpeDNd3NCObAjaFnNk%2FuDq8vqzVGnMH8AOuwdFcXq7xBwCu%2FeFRhqRfNM4cOing2v5SgsTwTr7OF3k%2F5u6Byal%2BEt7MLQ62cPwl0c1rZ%2FDTTSxnc%2BOEhkQwR9%2FutNty0YOXuqdoJE%2FSLnMlZux24AwhuRTjDd0Pqow76nO0gY6mAEiIaCBQMxo47YeobRyXH2qwAGNyu2jAhzqkfgQ5EBhd%2F9rbVCNMAInVk%2BIxhC0RLiFlmLoEIbYohTnWXXSYpqGeAHOlTVVrao6w3nDvcf7ZoFZdsn1xDIT9d7AMvDLFnXje9FL%2B%2B3XtDDXTm73c33ChBdCKOiFi%2BYoRiJ8EGhu4yOeHBz7uScUdrxeOajb1vJqDTm49ZxOXw%3D%3D&Expires=1783866050)

## Módulos de la interfaz

La primera versión Pro tendrá estas áreas:

| Módulo | Finalidad |
|---|---|
| **Dashboard SQX Edge** | KPIs globales, score medio, mejores activos, alertas |
| **Por Activo** | Grid, score, ratings, detalle y calidad asociada |
| **Top Picks** | Ranking Long/Short y prioridades |
| **Por Categoría** | Indicadores por clase, TF, rating y dirección |
| **Matriz Completa** | Heatmap activo × dirección × categoría |
| **Filtros Fase 2** | ADX, ATR, Choppiness, Hurst, KER y volumen |
| **Calidad MT5** | Instrumentos, spread, percentiles, quality checks, sesiones |
| **Importaciones** | CSV MT5, exports SQX, JSON y logs de validación |
| **Perfiles** | Broker, cuentas, aliases, spreads y presets |
| **Automatización SQX** | Detección de SQCli, rutas, ejecución y auditoría futura |
| **Configuración** | Rutas, backups, UI, umbrales y comportamiento de importación |

La UI seguirá usando el diseño oscuro SQX Edge, pero sus datos procederán de la API local, no de objetos JavaScript embebidos.

## Camino de compilación

La aplicación final se construirá en dos pasos:

```text
1. Python backend
   └── PyInstaller --onedir
       └── backend/dist/sqx-edge-api/sqx-edge-api.exe

2. Desktop shell
   └── electron-builder
       └── release/SQX Edge Pro Setup.exe
```

Elegiría `--onedir` y no `--onefile` para el backend: permite inspeccionar errores, gestionar recursos y manejar con más fiabilidad dependencias científicas o de análisis que previsiblemente crecerán en tu stack. Esa estrategia ya ha sido la recomendada para distribuir herramientas Python complejas a usuarios sin entorno local. [perplexity](https://www.perplexity.ai/search/a8ec35bb-59b5-45d8-9f32-82ef3487e23d)

En producción, Electron localizará el ejecutable del backend dentro de sus `resources`, arrancará FastAPI solo en `127.0.0.1`, esperará a `GET /api/health`, abrirá la ventana principal y cerrará el proceso hijo al salir.

## Fases de implementación

### Fase 0: Fundaciones

- Crear repositorio Git y estructura inicial.
- Configurar entorno Python, Node/Electron y scripts PowerShell.
- Definir `catalog_seed.json` con los 33 activos, 7 categorías, ratings, TFs, razones y direcciones.
- Crear SQLite con migraciones.
- Implementar endpoint `GET /api/health`.

### Fase 1: Motor cuantitativo

- Modelos Pydantic y SQLAlchemy.
- `calc_score(asset, dir_filter)` con semántica exacta para `L`, `S` y `L/S`.
- Score normalizado, estrellas, filtros de ratings y rankings.
- Tests unitarios obligatorios para `++`, `+`, `~`, `-`, direcciones y categorías vacías.
- Normalizador de símbolos: `SP500 -> US500`, `NDX -> USTEC`, `GDAXI -> GER40`.

### Fase 2: Calidad MT5

- Importador de CSV anual y horario.
- Detección de delimitador TAB/coma/punto y coma.
- Validación de columnas, rangos y datos corruptos.
- Almacenamiento histórico por `snapshot`.
- Vista Calidad MT5 que sustituya funcionalmente al monitor HTML actual.

### Fase 3: SQX Edge UI

- Shell Electron funcional.
- Dashboard y las cinco vistas funcionales.
- Drawer de detalle, score rings, sparklines, matrices y filtros.
- Exportación CSV desde API para respetar filtros activos.
- Persistencia de preferencias visuales y filtros mediante SQLite o preferencias Electron.

### Fase 4: Producción Windows

- Diálogos nativos para archivos, carpetas, base de datos, exportaciones y backups.
- Logs legibles y pantalla de diagnóstico.
- Backup automático de SQLite antes de importaciones masivas.
- Empaquetado PyInstaller + electron-builder.
- Instalador NSIS, icono, acceso directo, desinstalador.
- Smoke tests desde una máquina limpia o VM Windows.

### Fase 5: Automatización SQX

- Detector de instalaciones StrategyQuant X y SQCli.
- Registro de rutas por perfil.
- Ejecución segura de comandos SQCli.
- Importación de Databank exports.
- Watch folders para importaciones MT5/SQX automáticas.
- Auditoría y generación de paquetes de trabajo SQX.

La aplicación debe seguir funcionando en modo manual aunque SQCli no exista, y activar automatización solo cuando se detecte y valide su ruta. Esto respeta el planteamiento de integración progresiva entre SQX, Python, MT5 y una UI guiada. [perplexity](https://www.perplexity.ai/search/1e030ac6-c0b2-4daf-9502-1fff73ece187)

## Decisión de inicio

El primer entregable no será el dashboard visual completo. Será una **vertical slice funcional**:

```text
Electron abre
    ↓
Python backend arranca
    ↓
SQLite se inicializa
    ↓
Se carga el catálogo de 33 activos
    ↓
Vista Por Activo consume /api/assets
    ↓
Click en EURUSD muestra score y detalle
    ↓
Se importa un CSV del EA
    ↓
El snapshot de calidad queda persistido
    ↓
La vista Calidad MT5 lo muestra
```

Si esta cadena funciona, el resto de tabs son extensiones de una base estable. Si empezamos por los cinco dashboards a la vez, terminaremos con una UI atractiva pero sin arquitectura fiable detrás.