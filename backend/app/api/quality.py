from fastapi import APIRouter, HTTPException, Query

from app.database.migrations import connect, migrate
from app.repositories.quality_repository import QualityRepository

router = APIRouter(prefix="/api/quality", tags=["quality"])


@router.get("")
def list_quality_snapshots(
    asset_id: str | None = Query(default=None),
) -> dict:
    migrate()
    with connect() as connection:
        snapshots = QualityRepository(connection).list_snapshots(asset_id=asset_id)
    return {"count": len(snapshots), "snapshots": snapshots}


@router.get("/{snapshot_id}")
def get_quality_snapshot(snapshot_id: int) -> dict:
    migrate()
    with connect() as connection:
        snapshot = QualityRepository(connection).get_snapshot(snapshot_id)

    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail=f"Snapshot de calidad no encontrado: {snapshot_id}",
        )
    return snapshot
