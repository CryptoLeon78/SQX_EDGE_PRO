from fastapi import APIRouter, HTTPException, Query

from app.database.migrations import connect
from app.repositories.asset_repository import AssetRepository

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("")
def list_assets(enabled_only: bool = Query(default=False)) -> dict:
    with connect() as connection:
        repository = AssetRepository(connection)
        assets = repository.list_assets(enabled_only=enabled_only)
        categories = repository.list_categories()

    return {
        "count": len(assets),
        "category_count": len(categories),
        "assets": assets,
    }


@router.get("/categories/list")
def list_categories() -> dict:
    with connect() as connection:
        categories = AssetRepository(connection).list_categories()
    return {"count": len(categories), "categories": categories}


@router.get("/{asset_id}/score")
def get_asset_score(
    asset_id: str,
    direction: str = Query(pattern="^(L|S)$"),
) -> dict:
    with connect() as connection:
        score = AssetRepository(connection).get_score(
            asset_id=asset_id,
            direction=direction,
        )

    if score is None:
        raise HTTPException(
            status_code=404,
            detail=f"Activo no encontrado: {asset_id.upper()}",
        )
    return score


@router.get("/{asset_id}")
def get_asset(asset_id: str) -> dict:
    with connect() as connection:
        asset = AssetRepository(connection).get_asset(asset_id)

    if asset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Activo no encontrado: {asset_id.upper()}",
        )
    return asset
