import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database.migrations import load_catalog_seed


class CatalogSeedTests(unittest.TestCase):
    def test_seed_has_unique_ids(self) -> None:
        seed = load_catalog_seed()
        asset_ids = [asset["id"] for asset in seed["assets"]]
        self.assertEqual(len(asset_ids), len(set(asset_ids)))

    def test_seed_assets_have_required_fields(self) -> None:
        seed = load_catalog_seed()
        for asset in seed["assets"]:
            self.assertTrue(asset["id"])
            self.assertTrue(asset["name"])
            self.assertTrue(asset["asset_type"])
            self.assertIn("enabled", asset)

    def test_seed_is_valid_json(self) -> None:
        seed_path = BACKEND_DIR / "app" / "resources" / "catalog_seed.json"
        with seed_path.open(encoding="utf-8-sig") as file:
            decoded = json.load(file)
        self.assertIn("assets", decoded)


if __name__ == "__main__":
    unittest.main()
