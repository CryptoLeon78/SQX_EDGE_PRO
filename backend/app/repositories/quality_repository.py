from __future__ import annotations

import sqlite3
from typing import Any

from app.services.mt5_csv_importer import ParsedMt5Quality


class QualityRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def create_snapshot(
        self,
        parsed: ParsedMt5Quality,
        provider: str,
        source_stats_name: str,
        source_hourly_name: str | None,
    ) -> int:
        summary = parsed.summary
        cursor = self.connection.execute(
            """
            INSERT INTO quality_snapshots (
                provider, raw_symbol, canonical_asset_id,
                source_stats_name, source_hourly_name,
                current_spread, avg_spread, p50, p75, p90, p99,
                min_spread, max_spread, mode_spread, samples_count,
                neg_spread_count, pip_tick_size, point_value_usd,
                pip_tick_step, order_size_step, tick_value, point
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                provider,
                parsed.raw_symbol,
                parsed.canonical_asset_id,
                source_stats_name,
                source_hourly_name,
                summary["current_spread"],
                summary["avg_spread"],
                summary["p50"],
                summary["p75"],
                summary["p90"],
                summary["p99"],
                summary["min_spread"],
                summary["max_spread"],
                summary["mode_spread"],
                summary["samples_count"],
                summary["neg_spread_count"],
                summary["pip_tick_size"],
                summary["point_value_usd"],
                summary["pip_tick_step"],
                summary["order_size_step"],
                summary["tick_value"],
                summary["point"],
            ),
        )
        snapshot_id = int(cursor.lastrowid)

        for row in parsed.stats_rows:
            if row["year"] is None:
                continue
            self.connection.execute(
                """
                INSERT INTO quality_spread_years (
                    snapshot_id, year, avg_spread, p50, p75, p90, p99,
                    min_spread, max_spread, mode_spread, samples_count,
                    neg_spread_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    row["year"],
                    row["avg_spread"],
                    row["p50"],
                    row["p75"],
                    row["p90"],
                    row["p99"],
                    row["min_spread"],
                    row["max_spread"],
                    row["mode_spread"],
                    row["samples_count"],
                    row["neg_spread_count"],
                ),
            )

        for row in parsed.hourly_rows:
            self.connection.execute(
                """
                INSERT INTO quality_spread_hours (
                    snapshot_id, hour, session, avg_spread, p50, p75, p90, p99,
                    min_spread, max_spread, mode_spread, samples_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    row["hour"],
                    row["session"],
                    row["avg_spread"],
                    row["p50"],
                    row["p75"],
                    row["p90"],
                    row["p99"],
                    row["min_spread"],
                    row["max_spread"],
                    row["mode_spread"],
                    row["samples_count"],
                ),
            )

        return snapshot_id

    def list_snapshots(self, asset_id: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT
                id, provider, raw_symbol, canonical_asset_id, imported_at,
                current_spread, avg_spread, p50, p75, p90, p99,
                samples_count, neg_spread_count,
                source_stats_name, source_hourly_name
            FROM quality_snapshots
        """
        parameters: list[Any] = []

        if asset_id:
            query += " WHERE canonical_asset_id = ?"
            parameters.append(asset_id.upper())

        query += " ORDER BY imported_at DESC, id DESC"
        rows = self.connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]

    def get_snapshot(self, snapshot_id: int) -> dict[str, Any] | None:
        snapshot = self.connection.execute(
            "SELECT * FROM quality_snapshots WHERE id = ?",
            (snapshot_id,),
        ).fetchone()
        if snapshot is None:
            return None

        years = self.connection.execute(
            """
            SELECT year, avg_spread, p50, p75, p90, p99, min_spread,
                   max_spread, mode_spread, samples_count, neg_spread_count
            FROM quality_spread_years
            WHERE snapshot_id = ?
            ORDER BY year
            """,
            (snapshot_id,),
        ).fetchall()

        hours = self.connection.execute(
            """
            SELECT hour, session, avg_spread, p50, p75, p90, p99, min_spread,
                   max_spread, mode_spread, samples_count
            FROM quality_spread_hours
            WHERE snapshot_id = ?
            ORDER BY hour
            """,
            (snapshot_id,),
        ).fetchall()

        result = dict(snapshot)
        result["years"] = [dict(row) for row in years]
        result["hours"] = [dict(row) for row in hours]
        return result

    def list_providers(self) -> list[str]:
        rows = self.connection.execute(
            "SELECT DISTINCT provider FROM quality_snapshots WHERE TRIM(provider) <> '' ORDER BY provider COLLATE NOCASE"
        ).fetchall()
        return [str(row["provider"]) for row in rows]
