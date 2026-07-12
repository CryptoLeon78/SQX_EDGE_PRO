from __future__ import annotations

ALIASES = {
    "SP500": "US500",
    "US500": "US500",
    "NDX": "USTEC",
    "NAS100": "USTEC",
    "USTEC": "USTEC",
    "GDAXI": "GER40",
    "GER40": "GER40",
    "XAUUSD": "XAUUSD",
}


def normalize_symbol(raw_symbol: str) -> str:
    normalized = (raw_symbol or "").strip().upper().replace(" ", "")
    if not normalized:
        raise ValueError("El símbolo está vacío.")

    return ALIASES.get(normalized, normalized)
