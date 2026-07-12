from fastapi import APIRouter, HTTPException, Query

from app.database.migrations import connect, migrate
from app.repositories.asset_repository import AssetRepository

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("")
def list_assets(
    enabled_only: bool = Query(default=False),
) -> dict:
    migrate()
    with connect() as connection:
        repository = AssetRepository(connection)
        assets = repository.list_assets(enabled_only=enabled_only)

    return {
        "count": len(assets),
        "assets": assets,
    }


@router.get("/{asset_id}")
def get_asset(asset_id: str) -> dict:
    migrate()
    with connect() as connection:
        repository = AssetRepository(connection)
        asset = repository.get_asset(asset_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Activo no encontrado: {asset_id.upper()}",
        )

    return asset
