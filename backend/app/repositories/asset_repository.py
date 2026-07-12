import json
import sqlite3
from typing import Any

from app.core.score_engine import calculate_asset_score


class AssetRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def category_count(self) -> int:
        row = self.connection.execute(
            "SELECT COUNT(*) AS count FROM edge_categories WHERE enabled = 1"
        ).fetchone()
        return int(row["count"])

    def list_assets(self, enabled_only: bool = False) -> list[dict[str, Any]]:
        query = """
            SELECT
                a.id,
                a.name,
                a.asset_type,
                a.subtype,
                a.enabled,
                a.catalog_version,
                COUNT(e.id) AS edge_count
            FROM assets a
            LEFT JOIN edge_entries e
                ON e.asset_id = a.id AND e.enabled = 1
        """
        parameters: list[Any] = []

        if enabled_only:
            query += " WHERE a.enabled = ?"
            parameters.append(1)

        query += """
            GROUP BY a.id, a.name, a.asset_type, a.subtype, a.enabled, a.catalog_version
            ORDER BY a.asset_type, a.id
        """

        rows = self.connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]

    def list_categories(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT code, name, description, sort_order, indicator_count, enabled
            FROM edge_categories
            ORDER BY sort_order
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def get_asset(self, asset_id: str) -> dict[str, Any] | None:
        asset = self.connection.execute(
            """
            SELECT id, name, asset_type, subtype, enabled, catalog_version
            FROM assets WHERE id = ?
            """,
            (asset_id.upper(),),
        ).fetchone()

        if asset is None:
            return None

        edges = self.connection.execute(
            """
            SELECT
                e.id,
                e.category AS category_code,
                c.name AS category_name,
                c.sort_order AS category_order,
                e.direction,
                e.rating,
                e.timeframes_json,
                e.why,
                e.enabled
            FROM edge_entries e
            JOIN edge_categories c ON c.code = e.category
            WHERE e.asset_id = ?
            ORDER BY c.sort_order, e.direction, e.rating DESC
            """,
            (asset_id.upper(),),
        ).fetchall()

        result = dict(asset)
        result["edges"] = [
            {
                **dict(edge),
                "timeframes": json.loads(edge["timeframes_json"]),
            }
            for edge in edges
        ]
        result["edge_count"] = len(result["edges"])
        return result

    def get_score(self, asset_id: str, direction: str) -> dict[str, Any] | None:
        asset = self.get_asset(asset_id)
        if asset is None:
            return None

        result = calculate_asset_score(
            entries=asset["edges"],
            direction=direction,
            category_count=self.category_count(),
        )

        return {
            "asset_id": asset["id"],
            "direction": result.direction,
            "raw_points": result.raw_points,
            "max_points": result.max_points,
            "score": result.score,
            "coverage": result.coverage,
            "category_count": result.category_count,
            "compatible_entries": result.compatible_entries,
            "status": result.status,
        }
