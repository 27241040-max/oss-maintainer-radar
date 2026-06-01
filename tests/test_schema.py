from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from oss_maintainer_radar.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "sample_github_payload.json"
SCHEMA = ROOT / "schemas" / "maintainer-report.schema.json"


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
            schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
            payload = json.loads(output.read_text(encoding="utf-8"))
            validate_schema(schema, payload, schema)
            self.assertEqual(payload["schema_version"], "1.2")
            self.assertIn("scorecard", payload)
            self.assertIn("release_note_groups", payload)
            self.assertIn("release_count", payload)
            self.assertGreater(payload["scorecard"]["total"], 0)


def validate_schema(schema: dict[str, Any], value: Any, root: dict[str, Any], path: str = "$") -> None:
    if "$ref" in schema:
        validate_schema(resolve_ref(schema["$ref"], root), value, root, path)
        return

    if "anyOf" in schema:
        errors: list[AssertionError] = []
        for option in schema["anyOf"]:
            try:
                validate_schema(option, value, root, path)
                return
            except AssertionError as exc:
                errors.append(exc)
        raise AssertionError(f"{path} did not match any schema option: {errors}")

    if "const" in schema:
        assert value == schema["const"], f"{path} expected {schema['const']!r}, got {value!r}"

    expected_type = schema.get("type")
    if expected_type is not None:
        assert json_type_matches(value, expected_type), f"{path} expected {expected_type}, got {type(value).__name__}"

    if isinstance(value, int) and not isinstance(value, bool) and "minimum" in schema:
        assert value >= schema["minimum"], f"{path} expected minimum {schema['minimum']}, got {value}"

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            assert key in value, f"{path} missing required key {key}"
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                validate_schema(properties[key], child, root, child_path)
            elif isinstance(schema.get("additionalProperties"), dict):
                validate_schema(schema["additionalProperties"], child, root, child_path)
            else:
                assert schema.get("additionalProperties", True), f"{child_path} is not allowed"

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            validate_schema(schema["items"], item, root, f"{path}[{index}]")


def resolve_ref(ref: str, root: dict[str, Any]) -> dict[str, Any]:
    prefix = "#/$defs/"
    if not ref.startswith(prefix):
        raise AssertionError(f"unsupported schema ref: {ref}")
    return root["$defs"][ref[len(prefix):]]


def json_type_matches(value: Any, expected_type: str | list[str]) -> bool:
    if isinstance(expected_type, list):
        return any(json_type_matches(value, item) for item in expected_type)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    raise AssertionError(f"unsupported JSON schema type: {expected_type}")


if __name__ == "__main__":
    unittest.main()
