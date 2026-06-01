from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze_snapshot
from .github import fetch_snapshot, load_applicant, load_evidence, load_snapshot
from .render import (
    action_plan,
    application_draft,
    codex_prompts,
    form_fields,
    maintenance_scorecard,
    readiness_check,
    report_to_json,
    report_to_markdown,
    submission_pack,
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        snapshot = _snapshot_from_args(args)
        report = analyze_snapshot(snapshot, stale_days=args.stale_days)
        applicant = load_applicant(args.applicant) if getattr(args, "applicant", None) else None

        if args.command == "audit":
            output = report_to_json(report) if args.format == "json" else report_to_markdown(report)
        elif args.command == "scorecard":
            output = maintenance_scorecard(report)
        elif args.command == "action-plan":
            output = action_plan(report)
        elif args.command == "application":
            output = application_draft(report, role=args.role, applicant=applicant)
        elif args.command == "codex-prompts":
            output = codex_prompts(report)
        elif args.command == "form-fields":
            output = form_fields(report, role=args.role, applicant=applicant)
        elif args.command == "submission-pack":
            output = submission_pack(report, role=args.role, applicant=applicant)
        elif args.command == "readiness":
            output = readiness_check(report, role=args.role)
        else:
            parser.error(f"Unknown command: {args.command}")
            return 2

        _write_output(output, args.output)
        return 0
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"oss-radar: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-radar",
        description="Generate evidence-based maintenance reports for GitHub repositories.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = _add_snapshot_args(subparsers.add_parser("audit", help="Generate a maintenance report."))
    audit.add_argument("--format", choices=["markdown", "json"], default="markdown")
    audit.add_argument("--output", type=Path, help="Write output to a file instead of stdout.")

    scorecard = _add_snapshot_args(
        subparsers.add_parser("scorecard", help="Generate a maintenance health scorecard.")
    )
    scorecard.add_argument("--output", type=Path, help="Write output to a file instead of stdout.")

    plan = _add_snapshot_args(
        subparsers.add_parser("action-plan", help="Generate a prioritized maintainer action plan.")
    )
    plan.add_argument("--output", type=Path, help="Write output to a file instead of stdout.")

    application = _add_snapshot_args(
        subparsers.add_parser("application", help="Draft truthful Codex for OSS application fields.")
    )
    application.add_argument("--role", choices=["primary", "core"], default="primary")
    application.add_argument("--output", type=Path, help="Write output to a file instead of stdout.")

    prompts = _add_snapshot_args(
        subparsers.add_parser("codex-prompts", help="Generate Codex prompts for maintainer workflows.")
    )
    prompts.add_argument("--output", type=Path, help="Write output to a file instead of stdout.")

    fields = _add_snapshot_args(
        subparsers.add_parser("form-fields", help="Generate copy-paste fields for the Codex for OSS form.")
    )
    fields.add_argument("--role", choices=["primary", "core"], default="primary")
    fields.add_argument("--output", type=Path, help="Write output to a file instead of stdout.")

    pack = _add_snapshot_args(
        subparsers.add_parser("submission-pack", help="Generate a combined Codex for OSS submission pack.")
    )
    pack.add_argument("--role", choices=["primary", "core"], default="primary")
    pack.add_argument("--output", type=Path, help="Write output to a file instead of stdout.")

    readiness = _add_snapshot_args(
        subparsers.add_parser("readiness", help="Run a conservative Codex for OSS readiness self-check.")
    )
    readiness.add_argument("--role", choices=["primary", "core"], default="primary")
    readiness.add_argument("--output", type=Path, help="Write output to a file instead of stdout.")

    return parser


def _add_snapshot_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--repo", help="GitHub repo as owner/name or https://github.com/owner/name.")
    source.add_argument("--fixture", type=Path, help="Path to a saved GitHub snapshot JSON file.")
    parser.add_argument("--evidence", type=Path, help="Path to optional adoption and maintainer evidence JSON.")
    parser.add_argument("--applicant", type=Path, help="Path to optional private applicant profile JSON.")
    parser.add_argument("--stale-days", type=int, default=30, help="Days without update before an issue is stale.")
    return parser


def _snapshot_from_args(args: argparse.Namespace):
    if args.fixture:
        snapshot = load_snapshot(args.fixture)
    else:
        snapshot = fetch_snapshot(args.repo)

    if args.evidence:
        snapshot = snapshot.with_evidence(load_evidence(args.evidence))
    return snapshot


def _write_output(value: str, output: Path | None) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(value, encoding="utf-8")
    else:
        print(value, end="")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
