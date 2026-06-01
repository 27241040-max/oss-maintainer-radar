from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
