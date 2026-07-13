from pathlib import Path
import sys
import unittest
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.mt5_csv_importer import (
    Mt5CsvValidationError,
    parse_mt5_quality,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class Mt5CsvImporterTests(unittest.TestCase):
    def test_import_audcad_stats_and_hourly(self) -> None:
        parsed = parse_mt5_quality(
            FIXTURES / "AUDCAD_spread_stats.csv",
            FIXTURES / "AUDCAD_spread_hourly.csv",
        )

        self.assertEqual(parsed.raw_symbol, "AUDCAD")
        self.assertEqual(parsed.canonical_asset_id, "AUDCAD")
        self.assertEqual(len(parsed.stats_rows), 5)
        self.assertEqual(len(parsed.hourly_rows), 20)
        self.assertEqual(parsed.summary["year"], None)
        self.assertEqual(parsed.summary["avg_spread"], 10.2277)
        self.assertEqual(parsed.summary["current_spread"], 35.0)
        self.assertEqual(parsed.summary["samples_count"], 176051201)

    def test_import_gbpusd_stats_and_hourly(self) -> None:
        parsed = parse_mt5_quality(
            FIXTURES / "GBPUSD_spread_stats.csv",
            FIXTURES / "GBPUSD_spread_hourly.csv",
        )

        self.assertEqual(parsed.raw_symbol, "GBPUSD")
        self.assertEqual(parsed.canonical_asset_id, "GBPUSD")
        self.assertEqual(len(parsed.stats_rows), 10)
        self.assertGreater(len(parsed.hourly_rows), 0)
        hour_2 = next(row for row in parsed.hourly_rows if row["hour"] == 2)
        self.assertEqual(hour_2["min_spread"], 0.0)
        self.assertEqual(hour_2["p50"], 8.0)
        self.assertEqual(hour_2["p99"], 46.0)
        self.assertEqual(parsed.summary["year"], None)
        self.assertEqual(parsed.summary["avg_spread"], 6.4085)
        self.assertEqual(parsed.summary["current_spread"], 8.0)

    def test_tab_comma_and_semicolon_delimiters(self) -> None:
        source = (FIXTURES / "AUDCAD_spread_stats.csv").read_text(encoding="utf-8-sig")
        for delimiter in ("\t", ",", ";"):
            with self.subTest(delimiter=delimiter), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "stats.csv"
                path.write_text(source.replace("\t", delimiter), encoding="utf-8-sig")
                parsed = parse_mt5_quality(path)
                self.assertEqual(parsed.raw_symbol, "AUDCAD")

    def test_all_row_is_required_and_unique(self) -> None:
        source = (FIXTURES / "AUDCAD_spread_stats.csv").read_text(encoding="utf-8-sig")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "stats.csv"
            lines = source.splitlines()
            path.write_text("\n".join([lines[0]] + [line for line in lines[1:] if "\tALL\t" not in line]), encoding="utf-8")
            with self.assertRaises(Mt5CsvValidationError): parse_mt5_quality(path)
            path.write_text(source + "\n" + lines[1], encoding="utf-8")
            with self.assertRaises(Mt5CsvValidationError): parse_mt5_quality(path)

    def test_invalid_hour_samples_and_percentile_are_rejected(self) -> None:
        hourly = (FIXTURES / "AUDCAD_spread_hourly.csv").read_text(encoding="utf-8-sig")
        stats = FIXTURES / "AUDCAD_spread_stats.csv"
        for replacement in (("\t0\t", "\t24\t"), ("\t10221128\t", "\t0\t"), ("\t18\t", "\t-1\t")):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "hourly.csv"
                path.write_text(hourly.replace(*replacement, 1), encoding="utf-8")
                with self.assertRaises(Mt5CsvValidationError): parse_mt5_quality(stats, path)

    def test_symbols_must_match(self) -> None:
        with self.assertRaises(Mt5CsvValidationError):
            parse_mt5_quality(
                FIXTURES / "AUDCAD_spread_stats.csv",
                FIXTURES / "GBPUSD_spread_hourly.csv",
            )


if __name__ == "__main__":
    unittest.main()
