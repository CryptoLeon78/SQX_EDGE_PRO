from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

VALID_DIRECTIONS = {"L", "S", "LS"}
VALID_RATINGS = {"++", "+", "-", "--"}
RATING_POINTS = {
    "++": 3,
    "+": 2,
    "-": 1,
    "--": 0,
}
MAX_CATEGORY_POINTS = 3
CATEGORY_COUNT = 7


@dataclass(frozen=True)
class ScoreResult:
    direction: str
    raw_points: int
    max_points: int
    score: float
    coverage: int
    category_count: int
    compatible_entries: int
    status: str


def entry_matches_direction(entry_direction: str, requested_direction: str) -> bool:
    if entry_direction not in VALID_DIRECTIONS:
        raise ValueError(f"Dirección inválida: {entry_direction}")
    if requested_direction not in {"L", "S"}:
        raise ValueError(f"Dirección solicitada inválida: {requested_direction}")
    return entry_direction == "LS" or entry_direction == requested_direction


def rating_points(rating: str) -> int:
    if rating not in VALID_RATINGS:
        raise ValueError(f"Rating inválido: {rating}")
    return RATING_POINTS[rating]


def calculate_asset_score(
    entries: Iterable[dict],
    direction: str,
    category_count: int = CATEGORY_COUNT,
) -> ScoreResult:
    if direction not in {"L", "S"}:
        raise ValueError("La dirección debe ser L o S.")
    if category_count < 1:
        raise ValueError("category_count debe ser mayor que cero.")

    best_by_category: dict[str, int] = {}
    compatible_entries = 0

    for entry in entries:
        if not entry.get("enabled", True):
            continue
        if not entry_matches_direction(entry["direction"], direction):
            continue

        compatible_entries += 1
        category = entry["category_code"]
        points = rating_points(entry["rating"])
        best_by_category[category] = max(best_by_category.get(category, 0), points)

    raw_points = sum(best_by_category.values())
    max_points = category_count * MAX_CATEGORY_POINTS
    coverage = len(best_by_category)
    score = round((raw_points / max_points) * 100, 1)

    return ScoreResult(
        direction=direction,
        raw_points=raw_points,
        max_points=max_points,
        score=score,
        coverage=coverage,
        category_count=category_count,
        compatible_entries=compatible_entries,
        status="classified" if coverage else "unclassified",
    )
