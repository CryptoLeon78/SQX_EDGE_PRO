import json
import sqlite3
from typing import Any


class AssetRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

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
            GROUP BY
                a.id, a.name, a.asset_type, a.subtype,
                a.enabled, a.catalog_version
            ORDER BY a.asset_type, a.id
        """

        rows = self.connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]

    def get_asset(self, asset_id: str) -> dict[str, Any] | None:
        asset = self.connection.execute(
            """
            SELECT id, name, asset_type, subtype, enabled, catalog_version
            FROM assets
            WHERE id = ?
            """,
            (asset_id.upper(),),
        ).fetchone()

        if asset is None:
            return None

        edges = self.connection.execute(
            """
            SELECT id, category, direction, rating, timeframes_json, why, enabled
            FROM edge_entries
            WHERE asset_id = ?
            ORDER BY category, direction, rating
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
