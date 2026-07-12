from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.migrations import connect, migrate
from app.repositories.quality_repository import QualityRepository
from app.services.mt5_csv_importer import Mt5CsvValidationError, parse_mt5_quality

router = APIRouter(prefix="/api/import", tags=["imports"])


class Mt5QualityImportRequest(BaseModel):
    stats_path: str = Field(min_length=1)
    hourly_path: str | None = None
    provider: str = Field(default="Local MT5", min_length=1, max_length=120)


@router.post("/mt5-quality")
def import_mt5_quality(request: Mt5QualityImportRequest) -> dict:
    try:
        parsed = parse_mt5_quality(
            stats_path=request.stats_path,
            hourly_path=request.hourly_path,
        )
    except Mt5CsvValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    migrate()
    with connect() as connection:
        asset_exists = connection.execute(
            "SELECT 1 FROM assets WHERE id = ?",
            (parsed.canonical_asset_id,),
        ).fetchone()

        if asset_exists is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"El símbolo '{parsed.raw_symbol}' se normalizó como "
                    f"'{parsed.canonical_asset_id}', pero no existe en el catálogo."
                ),
            )

        repository = QualityRepository(connection)
        snapshot_id = repository.create_snapshot(
            parsed=parsed,
            provider=request.provider.strip(),
            source_stats_name=request.stats_path.split("\\")[-1].split("/")[-1],
            source_hourly_name=(
                request.hourly_path.split("\\")[-1].split("/")[-1]
                if request.hourly_path else None
            ),
        )
        connection.commit()

    return {
        "snapshot_id": snapshot_id,
        "provider": request.provider.strip(),
        "raw_symbol": parsed.raw_symbol,
        "canonical_asset_id": parsed.canonical_asset_id,
        "annual_rows": len([row for row in parsed.stats_rows if row["year"] is not None]),
        "hourly_rows": len(parsed.hourly_rows),
        "message": "Snapshot de calidad MT5 importado correctamente.",
    }
