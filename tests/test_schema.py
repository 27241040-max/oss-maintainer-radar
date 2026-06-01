from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from oss_maintainer_radar.cli import main
from oss_maintainer_radar.schema_validation import SchemaValidationError, load_report_schema, validate_schema


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "sample_github_payload.json"
SCHEMA = ROOT / "schemas" / "maintainer-report.schema.json"
PACKAGE_SCHEMA = ROOT / "src" / "oss_maintainer_radar" / "schemas" / "maintainer-report.schema.json"
TREND_SCHEMA = ROOT / "schemas" / "trend-report.schema.json"
PACKAGE_TREND_SCHEMA = ROOT / "src" / "oss_maintainer_radar" / "schemas" / "trend-report.schema.json"


class SchemaTests(unittest.TestCase):
    def test_fixture_json_report_matches_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            status = main(
                [
                    "audit",
                    "--fixture",
                    str(FIXTURE),
                    "--format",
                    "json",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            schema = load_report_schema(SCHEMA)
            payload = json.loads(output.read_text(encoding="utf-8"))
            validate_schema(schema, payload, schema)
            self.assertEqual(payload["schema_version"], "1.2")
            self.assertIn("scorecard", payload)
            self.assertIn("release_note_groups", payload)
            self.assertIn("release_count", payload)
            self.assertGreater(payload["scorecard"]["total"], 0)

    def test_packaged_schema_matches_repository_schema(self) -> None:
        repository_schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        package_schema = json.loads(PACKAGE_SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(package_schema, repository_schema)

    def test_generated_trend_json_matches_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            trend = Path(tmp) / "trend.json"

            first_status = main(
                [
                    "audit",
                    "--fixture",
                    str(FIXTURE),
                    "--format",
                    "json",
                    "--output",
                    str(first),
                ]
            )
            latest_status = main(
                [
                    "audit",
                    "--fixture",
                    str(FIXTURE),
                    "--format",
                    "json",
                    "--output",
                    str(latest),
                ]
            )
            trend_status = main(["trend", str(first), str(latest), "--format", "json", "--output", str(trend)])

            self.assertEqual(first_status, 0)
            self.assertEqual(latest_status, 0)
            self.assertEqual(trend_status, 0)
            schema = load_report_schema(TREND_SCHEMA)
            payload = json.loads(trend.read_text(encoding="utf-8"))
            validate_schema(schema, payload, schema)
            self.assertEqual(payload["reports_compared"], 2)

    def test_packaged_trend_schema_matches_repository_schema(self) -> None:
        repository_schema = json.loads(TREND_SCHEMA.read_text(encoding="utf-8"))
        package_schema = json.loads(PACKAGE_TREND_SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(package_schema, repository_schema)

    def test_schema_enum_rejects_unknown_value(self) -> None:
        schema = {"type": "string", "enum": ["improved", "unchanged", "worsened"]}

        with self.assertRaisesRegex(SchemaValidationError, "expected one of"):
            validate_schema(schema, "unknown", schema)


if __name__ == "__main__":
    unittest.main()
