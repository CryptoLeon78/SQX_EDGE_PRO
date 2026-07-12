# SQX Edge Pro

Aplicación Windows de escritorio para catálogo SQX Edge, perfiles operativos y calidad de datos de MT5.

## Arquitectura

- Electron: shell de escritorio, menú y diálogos nativos
- FastAPI: API local en 127.0.0.1
- SQLite: persistencia local fuera del repositorio
- Python: motor cuantitativo, importadores y exportaciones

## Ubicaciones

Repositorio de desarrollo:

```text
C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO
```

Datos operativos de desarrollo y producción:

```text
%LOCALAPPDATA%\SQX Edge Pro\
```

La base de datos se crea en:

```text
%LOCALAPPDATA%\SQX Edge Pro\sqx_edge.db
```

## Requisitos

- Windows 10/11
- Python 3.11 o 3.12 disponible como `python`
- Node.js LTS 20 o posterior disponible como `node` y `npm`
- Git opcional, pero recomendado

## Arranque

Desde PowerShell:

```powershell
Set-Location 'C:\BOTS\Versiones\Config y spreads ACTIVOS\SQX_EDGE_PRO'
Set-ExecutionPolicy -Scope Process Bypass
.\run_dev.ps1
```

En el primer lanzamiento el script crea `backend\.venv`, instala las dependencias Python y ejecuta `npm install`.

## Validación

La ventana debe mostrar:

- Backend conectado
- API URL con `127.0.0.1`
- Ruta de datos de usuario
- Ruta SQLite
- Estado de migración `ok`

También puedes abrir `http://127.0.0.1:<puerto>/docs` durante la ejecución para consultar OpenAPI.

## Fase actual

Fase 0: Electron, FastAPI, SQLite, migración inicial, health check y catálogo seed mínimo.
