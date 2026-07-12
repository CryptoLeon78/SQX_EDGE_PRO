from pathlib import Path
import os

APP_NAME = "SQX Edge Pro"
APP_SLUG = "sqx-edge-pro"
APP_VERSION = "0.1.0"

LOCAL_APP_DATA = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
DATA_DIR = LOCAL_APP_DATA / APP_NAME
DATABASE_PATH = DATA_DIR / "sqx_edge.db"
IMPORTS_DIR = DATA_DIR / "imports"
EXPORTS_DIR = DATA_DIR / "exports"
PROFILES_DIR = DATA_DIR / "profiles"
LOGS_DIR = DATA_DIR / "logs"
BACKUPS_DIR = DATA_DIR / "backups"

def ensure_data_directories() -> None:
    for directory in (
        DATA_DIR,
        IMPORTS_DIR,
        EXPORTS_DIR,
        PROFILES_DIR,
        LOGS_DIR,
        BACKUPS_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)
