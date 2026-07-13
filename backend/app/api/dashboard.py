import csv
import io

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.database.migrations import connect
from app.repositories.asset_repository import AssetRepository

router = APIRouter(prefix="/api", tags=["dashboard"])


def _scores(connection, direction: str) -> list[dict]:
    repository = AssetRepository(connection)
    return [repository.get_score(asset["id"], direction) for asset in repository.list_assets(enabled_only=True)]


def _top_picks(connection, direction: str, limit: int) -> list[dict]:
    repository = AssetRepository(connection)
    rows = []
    for asset in repository.list_assets(enabled_only=True):
        score = repository.get_score(asset["id"], direction)
        rows.append({**asset, **score})
    return sorted(rows, key=lambda item: (-item["score"], -item["coverage"], item["id"]))[:limit]


@router.get("/dashboard")
def dashboard() -> dict:
    with connect() as connection:
        repository = AssetRepository(connection)
        assets = repository.list_assets(enabled_only=True)
        long_scores = _scores(connection, "L")
        short_scores = _scores(connection, "S")
        snapshots = connection.execute("SELECT COUNT(*) AS count FROM quality_snapshots").fetchone()["count"]
        category_count = repository.category_count()
    return {
        "asset_count": len(assets), "category_count": category_count, "quality_snapshot_count": snapshots,
        "long_average_score": round(sum(x["score"] for x in long_scores) / len(long_scores), 1) if long_scores else 0,
        "short_average_score": round(sum(x["score"] for x in short_scores) / len(short_scores), 1) if short_scores else 0,
        "long_classified_count": sum(x["status"] == "classified" for x in long_scores),
        "short_classified_count": sum(x["status"] == "classified" for x in short_scores),
        "top_long": _top_picks(connection, "L", 5), "top_short": _top_picks(connection, "S", 5),
    }


@router.get("/top-picks")
def top_picks(direction: str = Query("L", pattern="^(L|S)$"), limit: int = Query(20, ge=1, le=100)) -> dict:
    with connect() as connection:
        return {"direction": direction, "picks": _top_picks(connection, direction, limit)}


@router.get("/categories")
def category_summary() -> dict:
    with connect() as connection:
        repository = AssetRepository(connection)
        categories = repository.list_categories()
        rows = connection.execute("""SELECT category, direction, rating, COUNT(*) AS count FROM edge_entries WHERE enabled = 1 GROUP BY category, direction, rating""").fetchall()
    aggregate = {(row["category"], row["direction"], row["rating"]): row["count"] for row in rows}
    return {"categories": [{**category, "entries": sum(v for (code, _, _), v in aggregate.items() if code == category["code"]), "long_entries": sum(v for (code, direction, _), v in aggregate.items() if code == category["code"] and direction in ("L", "LS")), "short_entries": sum(v for (code, direction, _), v in aggregate.items() if code == category["code"] and direction in ("S", "LS"))} for category in categories]}


@router.get("/matrix")
def matrix(direction: str = Query("L", pattern="^(L|S)$")) -> dict:
    with connect() as connection:
        repository = AssetRepository(connection)
        assets = repository.list_assets(enabled_only=True)
        categories = repository.list_categories()
        entries = connection.execute("SELECT asset_id, category, direction, rating FROM edge_entries WHERE enabled = 1").fetchall()
    points = {"++": 3, "+": 2, "-": 1, "--": 0}
    values = {}
    for entry in entries:
        if entry["direction"] not in (direction, "LS"): continue
        key = (entry["asset_id"], entry["category"])
        values[key] = max(values.get(key, 0), points[entry["rating"]])
    return {"direction": direction, "categories": categories, "rows": [{"asset_id": asset["id"], "asset_name": asset["name"], "asset_type": asset["asset_type"], "values": {category["code"]: values.get((asset["id"], category["code"]), None) for category in categories}} for asset in assets]}


@router.get("/export/top-picks.csv")
def export_top_picks(direction: str = Query("L", pattern="^(L|S)$")):
    with connect() as connection: rows = _top_picks(connection, direction, 100)
    buffer = io.StringIO(); writer = csv.DictWriter(buffer, fieldnames=["id", "name", "asset_type", "subtype", "direction", "score", "coverage", "raw_points", "max_points", "status"]); writer.writeheader()
    for row in rows: writer.writerow({key: row.get(key) for key in writer.fieldnames})
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="top_picks_{direction}.csv"'})
