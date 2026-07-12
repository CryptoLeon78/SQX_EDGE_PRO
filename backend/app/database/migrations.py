import json
import sqlite3
from pathlib import Path
from typing import Any

from app.config import DATABASE_PATH, ensure_data_directories

SCHEMA_VERSION = 2
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
    # utf-8-sig admite UTF-8 sin BOM y UTF-8 con BOM generado por PowerShell.
    with CATALOG_SEED_PATH.open(encoding="utf-8-sig") as file:
        return json.load(file)


def seed_catalog(connection: sqlite3.Connection) -> int:
    seed = load_catalog_seed()
    assets = seed.get("assets", [])

    for asset in assets:
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
                seed.get("catalog_version", "0.1.0"),
            ),
        )

    return len(assets)


def migrate() -> int:
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )

        current_version = get_schema_version(connection)

        if current_version < 1:
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
                INSERT INTO schema_migrations(version, applied_at)
                VALUES (1, datetime('now'))
                """
            )
            current_version = 1

        if current_version < 2:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    subtype TEXT,
                    enabled INTEGER NOT NULL DEFAULT 1
                        CHECK(enabled IN (0, 1)),
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
                    enabled INTEGER NOT NULL DEFAULT 1
                        CHECK(enabled IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(asset_id, category, direction, rating),
                    FOREIGN KEY(asset_id) REFERENCES assets(id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                INSERT INTO schema_migrations(version, applied_at)
                VALUES (2, datetime('now'))
                """
            )

        seed_catalog(connection)
        connection.commit()
        return SCHEMA_VERSION
