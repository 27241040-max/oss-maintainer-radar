from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from oss_maintainer_radar.cli import main
from oss_maintainer_radar.analyzer import analyze_snapshot
from oss_maintainer_radar.github import load_snapshot
from oss_maintainer_radar.render import application_draft


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "sample_github_payload.json"
EVIDENCE_FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "evidence.json"
APPLICANT_FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "applicant.example.json"


class CliTests(unittest.TestCase):
    def test_audit_writes_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.md"
            status = main(["audit", "--fixture", str(FIXTURE), "--output", str(output)])

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("# Maintainer Radar", text)
            self.assertIn("Qualification Signals", text)
            self.assertIn("Release Note Groups", text)

    def test_application_writes_conservative_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "application.md"
            status = main(
                [
                    "application",
                    "--fixture",
                    str(FIXTURE),
                    "--role",
                    "core",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Codex for Open Source Application Draft", text)
            self.assertIn("Core maintainer", text)
            self.assertIn("Do not claim adoption", text)

    def test_application_fields_fit_form_limits(self) -> None:
        snapshot = load_snapshot(FIXTURE)
        report = analyze_snapshot(snapshot)
        draft = application_draft(report, role="primary")
        sections = draft.split("## ")
        limited_sections = [
            section
            for section in sections
            if "(<=500 chars)" in section
        ]

        self.assertEqual(len(limited_sections), 3)
        for section in limited_sections:
            value = section.split("\n\n", 1)[1].strip()
            self.assertLessEqual(len(value), 500)

    def test_submission_pack_combines_required_materials(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "submission-pack.md"
            status = main(
                [
                    "submission-pack",
                    "--fixture",
                    str(FIXTURE),
                    "--role",
                    "primary",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# Codex for Open Source Submission Pack"))
            self.assertIn("Codex for Open Source Submission Pack", text)
            self.assertIn("Application Draft", text)
            self.assertIn("Form Fields", text)
            self.assertIn("Evidence Report", text)
            self.assertIn("Maintenance Scorecard", text)
            self.assertIn("Maintainer Action Plan", text)
            self.assertIn("Codex Workflow Prompts", text)

    def test_form_fields_include_character_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "form-fields.md"
            status = main(
                [
                    "form-fields",
                    "--fixture",
                    str(FIXTURE),
                    "--role",
                    "primary",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Codex for Open Source Form Fields", text)
            self.assertIn("## Public GitHub repository URL", text)
            self.assertIn("Latest release is v0.1.0.", text)
            self.assertIn("Character count:", text)
            self.assertIn("<fill manually>", text)

    def test_scorecard_reports_maintenance_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "scorecard.md"
            status = main(
                [
                    "scorecard",
                    "--fixture",
                    str(FIXTURE),
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("# Maintenance Scorecard", text)
            self.assertIn("Score:", text)
            self.assertIn("pull requests", text)
            self.assertIn("Release practice", text)

    def test_action_plan_reports_prioritized_work(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "action-plan.md"
            status = main(
                [
                    "action-plan",
                    "--fixture",
                    str(FIXTURE),
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("# Maintainer Action Plan", text)
            self.assertIn("## Immediate", text)
            self.assertIn("completed pull request", text)
            self.assertIn("deterministic groups", text)
            self.assertIn("## Evidence To Keep Current", text)

    def test_form_fields_can_use_applicant_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "form-fields.md"
            status = main(
                [
                    "form-fields",
                    "--fixture",
                    str(FIXTURE),
                    "--applicant",
                    str(APPLICANT_FIXTURE),
                    "--role",
                    "primary",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Jane", text)
            self.assertIn("jane@example.com", text)
            self.assertIn("jane-maintainer", text)
            self.assertIn("org_...", text)

    def test_readiness_flags_review_items_for_new_projects(self) -> None:
        fixture = Path(__file__).resolve().parents[1] / "examples" / "new_project_payload.json"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "readiness.md"
            status = main(
                [
                    "readiness",
                    "--fixture",
                    str(fixture),
                    "--role",
                    "primary",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Codex for Open Source Readiness", text)
            self.assertIn("[REVIEW] Adoption evidence", text)
            self.assertIn("not a guarantee", text)

    def test_since_option_limits_report_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.md"
            status = main(
                [
                    "audit",
                    "--fixture",
                    str(FIXTURE),
                    "--since",
                    "2026-05-01",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Window start: 2026-05-01T00:00:00+00:00", text)
            self.assertIn("Open issues in sample: 1", text)
            self.assertIn("Pull requests in sample: 1", text)

    def test_submission_pack_includes_manual_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "submission-pack.md"
            status = main(
                [
                    "submission-pack",
                    "--fixture",
                    str(FIXTURE),
                    "--evidence",
                    str(EVIDENCE_FIXTURE),
                    "--role",
                    "primary",
                    "--output",
                    str(output),
                ]
            )

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Monthly downloads: 5200", text)
            self.assertIn("It has about 5200 monthly downloads.", text)

    def test_trend_reports_improving_saved_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            output = Path(tmp) / "trend.md"
            _write_report(first, open_issues=8, stale_issues=3, review_backlog=2, releases=1, risks=2, score=55)
            _write_report(latest, open_issues=4, stale_issues=1, review_backlog=0, releases=2, risks=1, score=75)

            status = main(["trend", str(first), str(latest), "--output", str(output)])

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("# Maintainer Trend Report", text)
            self.assertIn("Open issues: 8 -> 4 (-4, improved)", text)
            self.assertIn("Review backlog: 2 -> 0 (-2, improved)", text)
            self.assertIn("Release count: 1 -> 2 (+1, improved)", text)
            self.assertIn("Scorecard score: 55 -> 75 (+20, improved)", text)
            self.assertIn("does not predict project health", text)
            self.assertNotIn("## Warnings", text)

    def test_trend_reports_worsening_saved_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            _write_report(first, open_issues=2, stale_issues=0, review_backlog=0, releases=2, risks=0, score=90)
            _write_report(latest, open_issues=5, stale_issues=2, review_backlog=1, releases=2, risks=2, score=65)

            output = Path(tmp) / "trend.md"
            status = main(["trend", str(first), str(latest), "--output", str(output)])

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Open issues: 2 -> 5 (+3, worsened)", text)
            self.assertIn("Stale issues: 0 -> 2 (+2, worsened)", text)
            self.assertIn("Risk count: 0 -> 2 (+2, worsened)", text)
            self.assertIn("Scorecard score: 90 -> 65 (-25, worsened)", text)

    def test_trend_csv_reports_improving_saved_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            output = Path(tmp) / "trend.csv"
            _write_report(first, open_issues=8, stale_issues=3, review_backlog=2, releases=1, risks=2, score=55)
            _write_report(latest, open_issues=4, stale_issues=1, review_backlog=0, releases=2, risks=1, score=75)

            status = main(["trend", str(first), str(latest), "--format", "csv", "--output", str(output)])

            self.assertEqual(status, 0)
            rows = list(csv.DictReader(output.read_text(encoding="utf-8").splitlines()))
            self.assertEqual(len(rows), 6)
            self.assertEqual(
                rows[0],
                {
                    "repository": "example/repo",
                    "first_snapshot": str(first),
                    "latest_snapshot": str(latest),
                    "metric_name": "Open issues",
                    "first_value": "8",
                    "latest_value": "4",
                    "delta": "-4",
                    "direction": "improved",
                    "warnings": "",
                },
            )
            release_row = rows[3]
            self.assertEqual(release_row["metric_name"], "Release count")
            self.assertEqual(release_row["delta"], "1")
            self.assertEqual(release_row["direction"], "improved")

    def test_trend_csv_reports_worsening_saved_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            output = Path(tmp) / "trend.csv"
            _write_report(first, open_issues=2, stale_issues=0, review_backlog=0, releases=2, risks=0, score=90)
            _write_report(latest, open_issues=5, stale_issues=2, review_backlog=1, releases=2, risks=2, score=65)

            status = main(["trend", str(first), str(latest), "--format", "csv", "--output", str(output)])

            self.assertEqual(status, 0)
            rows = {row["metric_name"]: row for row in csv.DictReader(output.read_text(encoding="utf-8").splitlines())}
            self.assertEqual(rows["Open issues"]["delta"], "3")
            self.assertEqual(rows["Open issues"]["direction"], "worsened")
            self.assertEqual(rows["Release count"]["delta"], "0")
            self.assertEqual(rows["Release count"]["direction"], "unchanged")
            self.assertEqual(rows["Scorecard score"]["delta"], "-25")
            self.assertEqual(rows["Scorecard score"]["direction"], "worsened")

    def test_trend_json_reports_matching_saved_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            output = Path(tmp) / "trend.json"
            _write_report(first, open_issues=8, stale_issues=3, review_backlog=2, releases=1, risks=2, score=55)
            _write_report(latest, open_issues=4, stale_issues=1, review_backlog=0, releases=2, risks=1, score=75)

            status = main(["trend", str(first), str(latest), "--format", "json", "--output", str(output)])

            self.assertEqual(status, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["repository"], "example/repo")
            self.assertEqual(payload["reports_compared"], 2)
            self.assertEqual(payload["first_snapshot"], str(first))
            self.assertEqual(payload["latest_snapshot"], str(latest))
            self.assertEqual(payload["warnings"], [])
            self.assertEqual(payload["metrics"][0]["metric_name"], "Open issues")
            self.assertEqual(payload["metrics"][0]["delta"], -4)
            self.assertEqual(payload["metrics"][0]["direction"], "improved")
            self.assertIn("not automated decisions", payload["boundaries"][1])

    def test_trend_warns_on_repository_and_schema_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            output = Path(tmp) / "trend.md"
            _write_report(
                first,
                repository="example/first",
                schema_version="1.1",
                open_issues=8,
                stale_issues=3,
                review_backlog=2,
                releases=1,
                risks=2,
                score=55,
            )
            _write_report(
                latest,
                repository="example/latest",
                schema_version="1.2",
                open_issues=4,
                stale_issues=1,
                review_backlog=0,
                releases=2,
                risks=1,
                score=75,
            )

            status = main(["trend", str(first), str(latest), "--output", str(output)])

            self.assertEqual(status, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("## Warnings", text)
            self.assertIn("different repositories: example/first, example/latest", text)
            self.assertIn("different schema versions: 1.1, 1.2", text)
            self.assertIn("Open issues: 8 -> 4 (-4, improved)", text)

    def test_trend_csv_includes_warning_column_for_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            output = Path(tmp) / "trend.csv"
            _write_report(
                first,
                repository="example/first",
                schema_version="1.1",
                open_issues=8,
                stale_issues=3,
                review_backlog=2,
                releases=1,
                risks=2,
                score=55,
            )
            _write_report(
                latest,
                repository="example/latest",
                schema_version="1.2",
                open_issues=4,
                stale_issues=1,
                review_backlog=0,
                releases=2,
                risks=1,
                score=75,
            )

            status = main(["trend", str(first), str(latest), "--format", "csv", "--output", str(output)])

            self.assertEqual(status, 0)
            rows = list(csv.DictReader(output.read_text(encoding="utf-8").splitlines()))
            self.assertEqual(len(rows), 6)
            warning = rows[0]["warnings"]
            self.assertIn("different repositories: example/first, example/latest", warning)
            self.assertIn("different schema versions: 1.1, 1.2", warning)
            self.assertTrue(all(row["warnings"] == warning for row in rows))

    def test_trend_json_includes_warnings_for_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            output = Path(tmp) / "trend.json"
            _write_report(
                first,
                repository="example/first",
                schema_version="1.1",
                open_issues=8,
                stale_issues=3,
                review_backlog=2,
                releases=1,
                risks=2,
                score=55,
            )
            _write_report(
                latest,
                repository="example/latest",
                schema_version="1.2",
                open_issues=4,
                stale_issues=1,
                review_backlog=0,
                releases=2,
                risks=1,
                score=75,
            )

            status = main(["trend", str(first), str(latest), "--format", "json", "--output", str(output)])

            self.assertEqual(status, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["repository"], "example/latest")
            self.assertIn("different repositories: example/first, example/latest", payload["warnings"][0])
            self.assertIn("different schema versions: 1.1, 1.2", payload["warnings"][1])
            self.assertEqual(payload["metrics"][0]["direction"], "improved")

    def test_validate_report_passes_generated_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            summary = Path(tmp) / "validation.txt"
            audit_status = main(
                [
                    "audit",
                    "--fixture",
                    str(FIXTURE),
                    "--format",
                    "json",
                    "--output",
                    str(report),
                ]
            )

            status = main(["validate-report", str(report), "--output", str(summary)])

            self.assertEqual(audit_status, 0)
            self.assertEqual(status, 0)
            text = summary.read_text(encoding="utf-8")
            self.assertIn(f"PASS {report}", text)
            self.assertIn("schemas/maintainer-report.schema.json", text)

    def test_validate_report_accepts_named_trend_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            latest = Path(tmp) / "latest.json"
            trend = Path(tmp) / "trend.json"
            summary = Path(tmp) / "validation.txt"
            _write_report(first, open_issues=2, stale_issues=0, review_backlog=0, releases=1, risks=1, score=70)
            _write_report(latest, open_issues=1, stale_issues=0, review_backlog=0, releases=2, risks=0, score=85)
            trend_status = main(["trend", str(first), str(latest), "--format", "json", "--output", str(trend)])

            validation_status = main(["validate-report", str(trend), "--schema", "trend", "--output", str(summary)])

            self.assertEqual(trend_status, 0)
            self.assertEqual(validation_status, 0)
            text = summary.read_text(encoding="utf-8")
            self.assertIn(f"PASS {trend}", text)
            self.assertIn("schemas/trend-report.schema.json", text)

    def test_validate_report_fails_invalid_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            invalid = Path(tmp) / "invalid.json"
            summary = Path(tmp) / "validation.txt"
            status = main(
                [
                    "audit",
                    "--fixture",
                    str(FIXTURE),
                    "--format",
                    "json",
                    "--output",
                    str(report),
                ]
            )
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload.pop("schema_version")
            invalid.write_text(json.dumps(payload), encoding="utf-8")

            validation_status = main(["validate-report", str(invalid), "--output", str(summary)])

            self.assertEqual(status, 0)
            self.assertEqual(validation_status, 1)
            text = summary.read_text(encoding="utf-8")
            self.assertIn(f"FAIL {invalid}", text)
            self.assertIn("missing required key schema_version", text)


def _write_report(
    path: Path,
    *,
    repository: str = "example/repo",
    schema_version: str = "1.2",
    open_issues: int,
    stale_issues: int,
    review_backlog: int,
    releases: int,
    risks: int,
    score: int,
) -> None:
    payload = {
        "schema_version": schema_version,
        "repository": {"full_name": repository},
        "generated_at": path.stem,
        "open_issue_count": open_issues,
        "stale_issue_count": stale_issues,
        "stale_pull_request_count": review_backlog,
        "release_count": releases,
        "risks": ["risk"] * risks,
        "scorecard": {"score": score},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
