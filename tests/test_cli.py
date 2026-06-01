from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from oss_maintainer_radar.cli import main
from oss_maintainer_radar.analyzer import analyze_snapshot
from oss_maintainer_radar.github import load_snapshot
from oss_maintainer_radar.render import application_draft


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "sample_github_payload.json"


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
            self.assertIn("Evidence Report", text)
            self.assertIn("Codex Workflow Prompts", text)


if __name__ == "__main__":
    unittest.main()
