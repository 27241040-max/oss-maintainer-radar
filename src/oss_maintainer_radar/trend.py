from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def trend_report(paths: list[Path]) -> str:
    if len(paths) < 2:
        raise ValueError("trend requires at least two JSON report files")

    snapshots = [_load_trend_snapshot(path) for path in paths]
    repository = snapshots[-1]["repository"]

    lines = [
        f"# Maintainer Trend Report: {repository}",
        "",
        f"Reports compared: {len(snapshots)}",
        "",
        "This report compares saved JSON reports. It does not predict project health.",
        "",
        "## Snapshots",
        "",
    ]
    for snapshot in snapshots:
        lines.append(
            "- {path}: generated {generated_at}, score {score}, open issues {open_issues}, "
            "stale issues {stale_issues}, review backlog {review_backlog}, releases {release_count}, risks {risk_count}".format(
                **snapshot
            )
        )

    lines.extend(["", "## Changes", ""])
    first = snapshots[0]
    latest = snapshots[-1]
    metrics = [
        ("Open issues", "open_issues", "lower"),
        ("Stale issues", "stale_issues", "lower"),
        ("Review backlog", "review_backlog", "lower"),
        ("Release count", "release_count", "higher"),
        ("Risk count", "risk_count", "lower"),
        ("Scorecard score", "score", "higher"),
    ]
    for name, key, preferred in metrics:
        lines.append(f"- {name}: {_change_line(first[key], latest[key], preferred)}")

    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            "- Compare reports generated from the same repository and similar windows when possible.",
            "- Treat increases or decreases as prompts for maintainer review, not automated decisions.",
            "- Do not turn trend changes into adoption, ecosystem-importance, or selection claims.",
        ]
    )
    return "\n".join(lines) + "\n"


def _load_trend_snapshot(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    repository = payload.get("repository") or {}
    scorecard = payload.get("scorecard") or {}

    return {
        "path": str(path),
        "repository": str(repository.get("full_name") or "unknown/unknown"),
        "generated_at": str(payload.get("generated_at") or "unknown"),
        "open_issues": _int_field(payload, "open_issue_count"),
        "stale_issues": _int_field(payload, "stale_issue_count"),
        "review_backlog": _int_field(payload, "stale_pull_request_count"),
        "release_count": _int_field(payload, "release_count"),
        "risk_count": _int_field(payload, "risks", list_count=True),
        "score": int(scorecard.get("score") or 0),
    }


def _int_field(payload: dict[str, Any], key: str, *, list_count: bool = False) -> int:
    value = payload.get(key)
    if list_count:
        return len(value) if isinstance(value, list) else 0
    if value in (None, ""):
        return 0
    return int(value)


def _change_line(first: int, latest: int, preferred: str) -> str:
    delta = latest - first
    if delta == 0:
        direction = "unchanged"
    elif (preferred == "lower" and delta < 0) or (preferred == "higher" and delta > 0):
        direction = "improved"
    else:
        direction = "worsened"

    signed = f"+{delta}" if delta > 0 else str(delta)
    return f"{first} -> {latest} ({signed}, {direction})"
