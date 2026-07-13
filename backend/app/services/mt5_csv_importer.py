from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.symbol_normalizer import normalize_symbol

STATS_REQUIRED = {
    "Symbol", "Year", "AvgSpread", "P50", "P75", "P90", "P99",
    "MinSpread", "MaxSpread", "ModeSpread", "SamplesCount",
    "PipTickSize", "PointValueUSD", "PipTickStep", "OrderSizeStep",
    "TickValue", "Point", "CurrentSpread",
}

HOURLY_REQUIRED = {
    "Symbol", "Hour", "Session", "AvgSpread", "P50", "P75", "P90",
    "P99", "MinSpread", "MaxSpread", "ModeSpread", "SamplesCount",
}


class Mt5CsvValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedMt5Quality:
    raw_symbol: str
    canonical_asset_id: str
    stats_rows: list[dict[str, Any]]
    hourly_rows: list[dict[str, Any]]
    summary: dict[str, Any]


def detect_delimiter(content: str) -> str:
    first_line = next((line for line in content.splitlines() if line.strip()), "")
    counts = {delimiter: first_line.count(delimiter) for delimiter in ("\t", ";", ",")}
    delimiter, total = max(counts.items(), key=lambda item: item[1])
    if total < 1:
        raise Mt5CsvValidationError(
            "No se detectó delimitador válido. Se admite TAB, coma o punto y coma."
        )
    return delimiter


def read_csv_rows(path: str | Path) -> tuple[list[dict[str, str]], str]:
    source = Path(path)
    if not source.exists() or not source.is_file():
        raise Mt5CsvValidationError(f"Archivo no encontrado: {source}")
    if source.suffix.lower() != ".csv":
        raise Mt5CsvValidationError(f"El archivo debe tener extensión .csv: {source.name}")

    content = source.read_text(encoding="utf-8-sig")
    delimiter = detect_delimiter(content)
    reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

    if not reader.fieldnames:
        raise Mt5CsvValidationError("El CSV no contiene cabecera.")

    rows = [
        {str(key).strip(): (value or "").strip() for key, value in row.items()}
        for row in reader
        if any((value or "").strip() for value in row.values())
    ]

    if not rows:
        raise Mt5CsvValidationError("El CSV no contiene filas de datos.")

    return rows, delimiter


def require_columns(rows: list[dict[str, str]], required: set[str], file_label: str) -> None:
    found = set(rows[0].keys())
    missing = sorted(required - found)
    if missing:
        raise Mt5CsvValidationError(
            f"{file_label}: faltan columnas obligatorias: {', '.join(missing)}"
        )


def as_float(
    value: str,
    field: str,
    row_label: str,
    allow_negative: bool = False,
) -> float:
    if value == "":
        raise Mt5CsvValidationError(f"{row_label}: {field} no puede estar vacío.")
    try:
        number = float(value.replace(",", "."))
    except ValueError as error:
        raise Mt5CsvValidationError(
            f"{row_label}: {field} debe ser numérico; recibido '{value}'."
        ) from error

    if number < 0 and not allow_negative:
        raise Mt5CsvValidationError(f"{row_label}: {field} no puede ser negativo.")
    return number


def as_int(value: str, field: str, row_label: str) -> int:
    number = as_float(value, field, row_label)
    if not number.is_integer():
        raise Mt5CsvValidationError(f"{row_label}: {field} debe ser entero.")
    return int(number)


def parse_stats(path: str | Path) -> tuple[list[dict[str, Any]], str]:
    raw_rows, _ = read_csv_rows(path)
    require_columns(raw_rows, STATS_REQUIRED, "SpreadStats")

    symbols = {row["Symbol"].strip().upper() for row in raw_rows}
    if len(symbols) != 1 or "" in symbols:
        raise Mt5CsvValidationError("SpreadStats debe contener un único símbolo no vacío.")

    rows: list[dict[str, Any]] = []
    all_count = 0

    for row in raw_rows:
        year_raw = row["Year"].strip().upper()
        row_label = f"SpreadStats {row['Symbol']} {year_raw or '?'}"

        if year_raw == "ALL":
            year = None
            all_count += 1
        else:
            year = as_int(year_raw, "Year", row_label)
            if year < 2000 or year > 2100:
                raise Mt5CsvValidationError(f"{row_label}: Year fuera de rango.")

        parsed = {
            "year": year,
            "avg_spread": as_float(row["AvgSpread"], "AvgSpread", row_label),
            "p50": as_float(row["P50"], "P50", row_label),
            "p75": as_float(row["P75"], "P75", row_label),
            "p90": as_float(row["P90"], "P90", row_label),
            "p99": as_float(row["P99"], "P99", row_label),
            "min_spread": max(0.0, as_float(row["MinSpread"], "MinSpread", row_label, allow_negative=True)),
            "max_spread": as_float(row["MaxSpread"], "MaxSpread", row_label),
            "mode_spread": as_float(row["ModeSpread"], "ModeSpread", row_label),
            "samples_count": as_int(row["SamplesCount"], "SamplesCount", row_label),
            "neg_spread_count": as_int(row.get("NegSpreadCount", "0") or "0", "NegSpreadCount", row_label),
            "pip_tick_size": as_float(row["PipTickSize"], "PipTickSize", row_label),
            "point_value_usd": as_float(row["PointValueUSD"], "PointValueUSD", row_label),
            "pip_tick_step": as_float(row["PipTickStep"], "PipTickStep", row_label),
            "order_size_step": as_float(row["OrderSizeStep"], "OrderSizeStep", row_label),
            "tick_value": as_float(row["TickValue"], "TickValue", row_label),
            "point": as_float(row["Point"], "Point", row_label),
            "current_spread": (
                as_float(row["CurrentSpread"], "CurrentSpread", row_label)
                if row.get("CurrentSpread", "") != "" else None
            ),
        }

        if parsed["min_spread"] > parsed["max_spread"]:
            raise Mt5CsvValidationError(f"{row_label}: MinSpread no puede superar MaxSpread.")
        if not (parsed["min_spread"] <= parsed["p50"] <= parsed["p75"] <= parsed["p90"] <= parsed["p99"] <= parsed["max_spread"]):
            raise Mt5CsvValidationError(f"{row_label}: percentiles fuera de rango u orden.")
        if parsed["samples_count"] < 1:
            raise Mt5CsvValidationError(f"{row_label}: SamplesCount debe ser mayor que cero.")

        rows.append(parsed)

    if all_count != 1:
        raise Mt5CsvValidationError("SpreadStats debe contener exactamente una fila Year = ALL.")

    years = [row["year"] for row in rows if row["year"] is not None]
    if len(years) != len(set(years)):
        raise Mt5CsvValidationError("SpreadStats contiene años duplicados.")

    return rows, next(iter(symbols))


def parse_hourly(path: str | Path) -> tuple[list[dict[str, Any]], str]:
    raw_rows, _ = read_csv_rows(path)
    require_columns(raw_rows, HOURLY_REQUIRED, "SpreadHourly")

    symbols = {row["Symbol"].strip().upper() for row in raw_rows}
    if len(symbols) != 1 or "" in symbols:
        raise Mt5CsvValidationError("SpreadHourly debe contener un único símbolo no vacío.")

    rows: list[dict[str, Any]] = []
    hours: set[int] = set()

    for row in raw_rows:
        row_label = f"SpreadHourly {row['Symbol']} hora {row['Hour']}"
        hour = as_int(row["Hour"], "Hour", row_label)
        if hour < 0 or hour > 23:
            raise Mt5CsvValidationError(f"{row_label}: Hour debe estar entre 0 y 23.")
        if hour in hours:
            raise Mt5CsvValidationError(f"{row_label}: hora duplicada.")
        hours.add(hour)

        session = row["Session"].strip()
        if not session:
            raise Mt5CsvValidationError(f"{row_label}: Session no puede estar vacía.")

        parsed = {
            "hour": hour,
            "session": session,
            "avg_spread": as_float(row["AvgSpread"], "AvgSpread", row_label),
            "p50": as_float(row["P50"], "P50", row_label),
            "p75": as_float(row["P75"], "P75", row_label),
            "p90": as_float(row["P90"], "P90", row_label),
            "p99": as_float(row["P99"], "P99", row_label),
            "min_spread": max(0.0, as_float(row["MinSpread"], "MinSpread", row_label, allow_negative=True)),
            "max_spread": as_float(row["MaxSpread"], "MaxSpread", row_label),
            "mode_spread": as_float(row["ModeSpread"], "ModeSpread", row_label),
            "samples_count": as_int(row["SamplesCount"], "SamplesCount", row_label),
        }

        if parsed["min_spread"] > parsed["max_spread"]:
            raise Mt5CsvValidationError(f"{row_label}: MinSpread no puede superar MaxSpread.")
        if not (parsed["min_spread"] <= parsed["p50"] <= parsed["p75"] <= parsed["p90"] <= parsed["p99"] <= parsed["max_spread"]):
            raise Mt5CsvValidationError(f"{row_label}: percentiles fuera de rango u orden.")
        if parsed["samples_count"] < 1:
            raise Mt5CsvValidationError(f"{row_label}: SamplesCount debe ser mayor que cero.")

        rows.append(parsed)

    return sorted(rows, key=lambda item: item["hour"]), next(iter(symbols))


def parse_mt5_quality(
    stats_path: str | Path,
    hourly_path: str | Path | None = None,
) -> ParsedMt5Quality:
    stats_rows, stats_symbol = parse_stats(stats_path)
    hourly_rows: list[dict[str, Any]] = []

    if hourly_path:
        hourly_rows, hourly_symbol = parse_hourly(hourly_path)
        if hourly_symbol != stats_symbol:
            raise Mt5CsvValidationError(
                f"Los símbolos no coinciden: SpreadStats={stats_symbol}, "
                f"SpreadHourly={hourly_symbol}."
            )

    summary = next(row for row in stats_rows if row["year"] is None)
    return ParsedMt5Quality(
        raw_symbol=stats_symbol,
        canonical_asset_id=normalize_symbol(stats_symbol),
        stats_rows=stats_rows,
        hourly_rows=hourly_rows,
        summary=summary,
    )

