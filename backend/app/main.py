from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assets import router as assets_router
from app.api.health import router as health_router
from app.config import APP_NAME, APP_VERSION, ensure_data_directories
from app.database.migrations import migrate


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "file://"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(assets_router)


@app.get("/")
def root() -> dict:
    return {"service": APP_NAME, "docs": "/docs"}
