#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print a small dependency-free dashboard from oss-radar trend JSON."
    )
    parser.add_argument("trend_json", type=Path, help="Path from `oss-radar trend --format json`.")
    args = parser.parse_args(argv)

    try:
        payload = load_trend_json(args.trend_json)
        print(render_dashboard(payload), end="")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"trend-dashboard: {exc}", file=sys.stderr)
        return 1
    return 0


def load_trend_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")

    required = ["repository", "reports_compared", "warnings", "metrics", "boundaries"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"{path} is missing required key(s): {', '.join(missing)}")
    if not isinstance(payload["metrics"], list):
        raise ValueError(f"{path} metrics must be an array")
    return payload


def render_dashboard(payload: dict[str, Any]) -> str:
    lines = [
        f"Maintainer Trend Dashboard: {payload['repository']}",
        f"Reports compared: {payload['reports_compared']}",
        "",
    ]

    warnings = payload.get("warnings") or []
    lines.append("Warnings:")
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Metrics:",
            "Metric | First | Latest | Delta | Direction",
            "--- | ---: | ---: | ---: | ---",
        ]
    )
    for metric in payload["metrics"]:
        lines.append(_metric_row(metric))

    lines.extend(["", "Review boundaries:"])
    for boundary in payload.get("boundaries") or []:
        lines.append(f"- {boundary}")

    return "\n".join(lines) + "\n"


def _metric_row(metric: Any) -> str:
    if not isinstance(metric, dict):
        raise ValueError("metric row must be an object")

    name = str(metric.get("metric_name", "unknown"))
    first = _int_value(metric, "first_value")
    latest = _int_value(metric, "latest_value")
    delta = _int_value(metric, "delta")
    direction = str(metric.get("direction", "unknown"))
    return f"{name} | {first} | {latest} | {_signed(delta)} | {direction}"


def _int_value(metric: dict[str, Any], key: str) -> int:
    value = metric.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"metric {metric.get('metric_name', 'unknown')} has invalid {key}")
    return value


def _signed(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


if __name__ == "__main__":
    raise SystemExit(main())
