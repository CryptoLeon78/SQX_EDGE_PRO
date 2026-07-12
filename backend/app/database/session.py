import sqlite3
from app.config import DATABASE_PATH, ensure_data_directories

SCHEMA_VERSION = 1

def connect() -> sqlite3.Connection:
    ensure_data_directories()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection
