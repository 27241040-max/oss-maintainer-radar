from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_SCHEMA = Path("schemas") / "maintainer-report.schema.json"
TREND_SCHEMA = Path("schemas") / "trend-report.schema.json"
NAMED_SCHEMAS = {
    "maintainer": DEFAULT_SCHEMA,
    "report": DEFAULT_SCHEMA,
    "trend": TREND_SCHEMA,
}


class SchemaValidationError(ValueError):
    """Raised when a JSON report does not match the maintainer report schema."""


def validate_reports(report_paths: list[Path], schema_path: Path | None = None) -> tuple[str, bool]:
    resolved_schema_path = resolve_schema_path(schema_path)
    schema = load_report_schema(resolved_schema_path)
    lines: list[str] = []
    ok = True

    for report_path in report_paths:
        try:
            payload = _load_json(report_path)
            validate_schema(schema, payload, schema)
        except (OSError, json.JSONDecodeError, SchemaValidationError) as exc:
            ok = False
            lines.append(f"FAIL {report_path}: {exc}")
        else:
            lines.append(f"PASS {report_path}: matches {resolved_schema_path.as_posix()}")

    return "\n".join(lines) + "\n", ok


def load_report_schema(schema_path: Path | None = None) -> dict[str, Any]:
    path = resolve_schema_path(schema_path)
    return _load_json(path)


def resolve_schema_path(schema_path: Path | None = None) -> Path:
    if schema_path is None:
        return _find_schema(DEFAULT_SCHEMA)

    schema_name = schema_path.as_posix()
    if schema_name in NAMED_SCHEMAS:
        return _find_schema(NAMED_SCHEMAS[schema_name])

    return schema_path


def validate_schema(schema: dict[str, Any], value: Any, root: dict[str, Any], path: str = "$") -> None:
    if "$ref" in schema:
        validate_schema(_resolve_ref(schema["$ref"], root), value, root, path)
        return

    if "anyOf" in schema:
        errors: list[str] = []
        for option in schema["anyOf"]:
            try:
                validate_schema(option, value, root, path)
                return
            except SchemaValidationError as exc:
                errors.append(str(exc))
        raise SchemaValidationError(f"{path} did not match any schema option: {'; '.join(errors)}")

    if "const" in schema and value != schema["const"]:
        raise SchemaValidationError(f"{path} expected {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(repr(item) for item in schema["enum"])
        raise SchemaValidationError(f"{path} expected one of {allowed}, got {value!r}")

    expected_type = schema.get("type")
    if expected_type is not None and not _json_type_matches(value, expected_type):
        raise SchemaValidationError(f"{path} expected {_type_label(expected_type)}, got {_value_type(value)}")

    if isinstance(value, int) and not isinstance(value, bool) and "minimum" in schema:
        minimum = schema["minimum"]
        if value < minimum:
            raise SchemaValidationError(f"{path} expected minimum {minimum}, got {value}")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                raise SchemaValidationError(f"{path} missing required key {key}")
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                validate_schema(properties[key], child, root, child_path)
            elif isinstance(schema.get("additionalProperties"), dict):
                validate_schema(schema["additionalProperties"], child, root, child_path)
            elif not schema.get("additionalProperties", True):
                raise SchemaValidationError(f"{child_path} is not allowed")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise SchemaValidationError(f"{path} expected at least {schema['minItems']} items, got {len(value)}")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(schema["items"], item, root, f"{path}[{index}]")


def _find_schema(relative_schema: Path) -> Path:
    package_candidate = Path(__file__).resolve().parent / relative_schema
    if package_candidate.is_file():
        return package_candidate

    start = Path.cwd().resolve()
    for directory in (start, *start.parents):
        candidate = directory / relative_schema
        if candidate.is_file():
            return candidate

    package_root = Path(__file__).resolve().parents[2]
    candidate = package_root / relative_schema
    if candidate.is_file():
        return candidate

    raise FileNotFoundError(
        f"could not find {relative_schema.as_posix()}; run from a project checkout or pass --schema"
    )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"{path} does not exist") from exc
    except json.JSONDecodeError as exc:
        raise json.JSONDecodeError(f"{path}: {exc.msg}", exc.doc, exc.pos) from exc

    if not isinstance(payload, dict):
        raise SchemaValidationError(f"{path} must contain a JSON object")
    return payload


def _resolve_ref(ref: str, root: dict[str, Any]) -> dict[str, Any]:
    prefix = "#/$defs/"
    if not ref.startswith(prefix):
        raise SchemaValidationError(f"unsupported schema ref: {ref}")
    try:
        target = root["$defs"][ref[len(prefix):]]
    except KeyError as exc:
        raise SchemaValidationError(f"unknown schema ref: {ref}") from exc
    if not isinstance(target, dict):
        raise SchemaValidationError(f"schema ref is not an object: {ref}")
    return target


def _json_type_matches(value: Any, expected_type: str | list[str]) -> bool:
    if isinstance(expected_type, list):
        return any(_json_type_matches(value, item) for item in expected_type)
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
    raise SchemaValidationError(f"unsupported JSON schema type: {expected_type}")


def _type_label(expected_type: str | list[str]) -> str:
    if isinstance(expected_type, list):
        return " or ".join(expected_type)
    return expected_type


def _value_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__
