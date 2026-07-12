# Arquitectura — SQX Edge Pro

## Fase 0

La aplicación se ejecuta en dos procesos:

```text
Electron
  └─ inicia FastAPI como proceso hijo local
       └─ inicializa SQLite y expone /api/health
```

## Seguridad de la UI

Electron usa `contextIsolation: true`, `sandbox: true` y `nodeIntegration: false`. La interfaz no accede directamente a Node, al sistema de archivos ni al backend de Python; solo recibe datos autorizados a través de `preload.js`.

## Datos persistentes

El código se ejecuta desde el repositorio en desarrollo o desde `resources` en la versión compilada. Los datos del usuario no se almacenan junto al ejecutable.

```text
%LOCALAPPDATA%\SQX Edge Pro\
├── sqx_edge.db
├── imports\
├── exports\
├── profiles\
├── logs\
└── backups\
```

## Próximo incremento

Fase 1 añadirá modelos, catálogo persistente, endpoint `/api/assets` y el motor de scoring.
