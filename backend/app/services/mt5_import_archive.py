from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.config import IMPORTS_DIR, ensure_data_directories


def _safe_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._") or "unknown"


def archive_mt5_csvs(
    stats_path: str | Path,
    hourly_path: str | Path | None,
    symbol: str,
    provider: str,
) -> tuple[Path, Path, Path | None]:
    """Copia los CSV al directorio de imports y devuelve (folder, stats_target, hourly_target).

    hourly_target es None si hourly_path es None.
    """
    ensure_data_directories()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    folder = IMPORTS_DIR / f"{stamp}_{_safe_component(symbol)}_{_safe_component(provider)}"
    folder.mkdir(parents=True, exist_ok=False)
    try:
        stats_target = folder / "stats.csv"
        shutil.copy2(stats_path, stats_target)

        hourly_target: Path | None = None
        if hourly_path is not None:
            hourly_target = folder / "hourly.csv"
            shutil.copy2(hourly_path, hourly_target)

        return folder, stats_target, hourly_target
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
