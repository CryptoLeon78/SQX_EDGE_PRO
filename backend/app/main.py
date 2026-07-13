from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import assets, dashboard, health, imports, quality
from app.config import APP_NAME, APP_VERSION, ensure_data_directories
from app.database.migrations import SCHEMA_VERSION, migrate


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_data_directories()
    migrate()
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)

# allow_origins="*" es seguro aquí porque el backend escucha únicamente en
# 127.0.0.1 (loopback). Electron carga el frontend como file:// y envía
# origin: null, que no es reconocido por valores como "file://" o "http://localhost".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(assets.router)
app.include_router(imports.router)
app.include_router(quality.router)
app.include_router(dashboard.router)


@app.get("/")
def root() -> dict:
    return {"service": APP_NAME, "version": APP_VERSION, "schema_version": SCHEMA_VERSION, "docs": "/docs"}
