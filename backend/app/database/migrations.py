import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import DATABASE_PATH, ensure_data_directories

SCHEMA_VERSION = 3
RESOURCE_DIR = Path(__file__).resolve().parents[1] / "resources"
CATALOG_SEED_PATH = RESOURCE_DIR / "catalog_seed.json"


def connect() -> sqlite3.Connection:
    ensure_data_directories()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_schema_version(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
    ).fetchone()
    return int(row["version"])


def load_catalog_seed() -> dict[str, Any]:
    with CATALOG_SEED_PATH.open(encoding="utf-8-sig") as file:
        return json.load(file)


def create_base_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS application_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            subtype TEXT,
            enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0, 1)),
            catalog_version TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS edge_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id TEXT NOT NULL,
            category TEXT NOT NULL,
            direction TEXT NOT NULL CHECK(direction IN ('L', 'S', 'LS')),
            rating TEXT NOT NULL CHECK(rating IN ('++', '+', '-', '--')),
            timeframes_json TEXT NOT NULL DEFAULT '[]',
            why TEXT,
            enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(asset_id, category, direction, rating),
            FOREIGN KEY(asset_id) REFERENCES assets(id) ON DELETE CASCADE
        )
        """
    )


def create_edge_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS edge_categories (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            sort_order INTEGER NOT NULL UNIQUE,
            indicator_count INTEGER NOT NULL DEFAULT 0,
            enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0, 1))
        )
        """
    )


def seed_catalog(connection: sqlite3.Connection) -> None:
    seed = load_catalog_seed()

    for category in seed.get("categories", []):
        connection.execute(
            """
            INSERT INTO edge_categories (
                code, name, description, sort_order, indicator_count, enabled
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                name = excluded.name,
                description = excluded.description,
                sort_order = excluded.sort_order,
                indicator_count = excluded.indicator_count,
                enabled = excluded.enabled
            """,
            (
                category["code"],
                category["name"],
                category["description"],
                category["sort_order"],
                category["indicator_count"],
                1 if category.get("enabled", True) else 0,
            ),
        )

    for asset in seed.get("assets", []):
        connection.execute(
            """
            INSERT INTO assets (
                id, name, asset_type, subtype, enabled, catalog_version
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                asset_type = excluded.asset_type,
                subtype = excluded.subtype,
                enabled = excluded.enabled,
                catalog_version = excluded.catalog_version
            """,
            (
                asset["id"],
                asset["name"],
                asset["asset_type"],
                asset.get("subtype"),
                1 if asset.get("enabled", True) else 0,
                seed.get("catalog_version", "0.2.0"),
            ),
        )

        for edge in asset.get("edges", []):
            connection.execute(
                """
                INSERT INTO edge_entries (
                    asset_id, category, direction, rating,
                    timeframes_json, why, enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(asset_id, category, direction, rating) DO UPDATE SET
                    timeframes_json = excluded.timeframes_json,
                    why = excluded.why,
                    enabled = excluded.enabled,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    asset["id"],
                    edge["category"],
                    edge["direction"],
                    edge["rating"],
                    json.dumps(edge.get("timeframes", [])),
                    edge.get("why", ""),
                    1 if edge.get("enabled", True) else 0,
                ),
            )


def migrate() -> int:
    with connect() as connection:
        create_base_schema(connection)
        current_version = get_schema_version(connection)

        if current_version < 1:
            connection.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES (1, datetime('now'))"
            )

        if current_version < 2:
            connection.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES (2, datetime('now'))"
            )

        if current_version < 3:
            create_edge_schema(connection)
            connection.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES (3, datetime('now'))"
            )
        else:
            create_edge_schema(connection)

        seed_catalog(connection)
        connection.commit()
        return SCHEMA_VERSION
