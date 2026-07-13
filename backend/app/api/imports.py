from pathlib import Path
import shutil

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.database.migrations import connect, migrate
from app.repositories.quality_repository import QualityRepository
from app.services.mt5_csv_importer import Mt5CsvValidationError, parse_mt5_quality
from app.services.mt5_import_archive import archive_mt5_csvs

router = APIRouter(prefix="/api/import", tags=["imports"])


class Mt5CsvImportRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=100)
    stats_path: str = Field(min_length=1)
    hourly_path: str = Field(min_length=1)

    @field_validator("provider")
    @classmethod
    def provider_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El proveedor / broker es obligatorio.")
        return value


def _import(payload: Mt5CsvImportRequest) -> dict:
    try:
        parsed = parse_mt5_quality(payload.stats_path, payload.hourly_path)
    except Mt5CsvValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    migrate()
    archive_dir = stats_archive = hourly_archive = None
    try:
        archive_dir, stats_archive, hourly_archive = archive_mt5_csvs(
            payload.stats_path, payload.hourly_path, parsed.raw_symbol, payload.provider
        )
        with connect() as connection:
            exists = connection.execute("SELECT 1 FROM assets WHERE id = ?", (parsed.canonical_asset_id,)).fetchone()
            if exists is None:
                raise HTTPException(status_code=422, detail=f"El símbolo '{parsed.raw_symbol}' se normalizó como '{parsed.canonical_asset_id}', pero no existe en el catálogo.")
            snapshot_id = QualityRepository(connection).create_snapshot(
                parsed=parsed,
                provider=payload.provider,
                source_stats_name=str(stats_archive),
                source_hourly_name=str(hourly_archive),
            )
            connection.commit()
    except HTTPException:
        if archive_dir: shutil.rmtree(archive_dir, ignore_errors=True)
        raise
    except Exception as error:
        if archive_dir: shutil.rmtree(archive_dir, ignore_errors=True)
        raise HTTPException(status_code=422, detail=f"No se pudo importar el snapshot: {error}") from error

    return {"snapshot_id": snapshot_id, "provider": payload.provider, "raw_symbol": parsed.raw_symbol, "canonical_asset_id": parsed.canonical_asset_id, "annual_rows": len([r for r in parsed.stats_rows if r["year"] is not None]), "hourly_rows": len(parsed.hourly_rows), "archive_path": str(archive_dir), "message": f"Snapshot {parsed.canonical_asset_id} · {payload.provider} importado correctamente."}


@router.post("/mt5-csv", status_code=201)
def import_mt5_csv(payload: Mt5CsvImportRequest) -> dict:
    return _import(payload)


@router.post("/mt5-quality", status_code=201, deprecated=True)
def import_mt5_quality_legacy(payload: Mt5CsvImportRequest) -> dict:
    return _import(payload)
