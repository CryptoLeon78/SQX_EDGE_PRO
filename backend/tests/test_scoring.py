from pathlib import Path
import json
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.core.score_engine import (
    calculate_asset_score,
    entry_matches_direction,
    rating_points,
)
from app.database.migrations import load_catalog_seed


class ScoreEngineTests(unittest.TestCase):
    def test_rating_points(self) -> None:
        self.assertEqual(rating_points("++"), 3)
        self.assertEqual(rating_points("+"), 2)
        self.assertEqual(rating_points("-"), 1)
        self.assertEqual(rating_points("--"), 0)

    def test_direction_semantics(self) -> None:
        self.assertTrue(entry_matches_direction("L", "L"))
        self.assertFalse(entry_matches_direction("L", "S"))
        self.assertTrue(entry_matches_direction("S", "S"))
        self.assertFalse(entry_matches_direction("S", "L"))
        self.assertTrue(entry_matches_direction("LS", "L"))
        self.assertTrue(entry_matches_direction("LS", "S"))

    def test_best_entry_per_category(self) -> None:
        entries = [
            {"category_code": "trend", "direction": "L", "rating": "+"},
            {"category_code": "trend", "direction": "LS", "rating": "++"},
            {"category_code": "momentum", "direction": "L", "rating": "-"},
        ]
        result = calculate_asset_score(entries, "L", category_count=7)
        self.assertEqual(result.raw_points, 4)
        self.assertEqual(result.coverage, 2)
        self.assertEqual(result.score, 19.0)

    def test_empty_categories_are_unclassified(self) -> None:
        result = calculate_asset_score([], "S", category_count=7)
        self.assertEqual(result.score, 0)
        self.assertEqual(result.coverage, 0)
        self.assertEqual(result.status, "unclassified")


class CatalogSeedTests(unittest.TestCase):
    def test_seed_is_valid_json(self) -> None:
        path = BACKEND_DIR / "app" / "resources" / "catalog_seed.json"
        with path.open(encoding="utf-8-sig") as file:
            seed = json.load(file)
        self.assertEqual(len(seed["categories"]), 7)

    def test_entries_reference_known_categories(self) -> None:
        seed = load_catalog_seed()
        categories = {item["code"] for item in seed["categories"]}
        for asset in seed["assets"]:
            for edge in asset.get("edges", []):
                self.assertIn(edge["category"], categories)


if __name__ == "__main__":
    unittest.main()
