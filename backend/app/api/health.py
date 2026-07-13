from fastapi import APIRouter
from app.config import APP_NAME, APP_VERSION, DATA_DIR, DATABASE_PATH
from app.database.migrations import SCHEMA_VERSION

router = APIRouter(tags=["health"])

@router.get("/api/health")
def health() -> dict:
    schema_version = SCHEMA_VERSION
    return {
        "status": "ok",
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "schema_version": schema_version,
        "data_dir": str(DATA_DIR),
        "database_path": str(DATABASE_PATH),
    }
