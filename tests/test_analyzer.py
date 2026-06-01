from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from oss_maintainer_radar.analyzer import analyze_snapshot
from oss_maintainer_radar.github import load_applicant, load_evidence, load_snapshot, parse_repo_ref


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "sample_github_payload.json"
NEW_PROJECT_FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "new_project_payload.json"
EVIDENCE_FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "evidence.json"
APPLICANT_FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "applicant.example.json"


class AnalyzerTests(unittest.TestCase):
    def test_analyze_snapshot_computes_workload(self) -> None:
        snapshot = load_snapshot(FIXTURE)
        report = analyze_snapshot(
            snapshot,
            now=datetime(2026, 6, 1, tzinfo=timezone.utc),
            stale_days=30,
        )

        self.assertEqual(report.repository.full_name, "example/oss-maintainer-radar")
        self.assertEqual(report.open_issue_count, 2)
        self.assertEqual(report.stale_issue_count, 1)
        self.assertEqual(report.sampled_pull_request_count, 2)
        self.assertEqual(report.open_pull_request_count, 1)
        self.assertEqual(report.stale_pull_request_count, 1)
        self.assertIn("documentation", report.label_counts)
        self.assertIn("bug", report.label_counts)
        self.assertTrue(any("visible adoption" in signal for signal in report.qualification_signals))

    def test_parse_repo_ref_accepts_common_forms(self) -> None:
        self.assertEqual(parse_repo_ref("owner/repo"), ("owner", "repo"))
        self.assertEqual(parse_repo_ref("https://github.com/owner/repo"), ("owner", "repo"))
        self.assertEqual(parse_repo_ref("https://github.com/owner/repo.git"), ("owner", "repo"))

    def test_parse_repo_ref_rejects_unknown_hosts(self) -> None:
        with self.assertRaises(ValueError):
            parse_repo_ref("https://example.com/owner/repo")

    def test_new_project_reports_weak_application_evidence(self) -> None:
        snapshot = load_snapshot(NEW_PROJECT_FIXTURE)
        report = analyze_snapshot(
            snapshot,
            now=datetime(2026, 6, 1, tzinfo=timezone.utc),
            stale_days=30,
        )

        self.assertTrue(any("early" in signal for signal in report.qualification_signals))
        self.assertTrue(any("Low public adoption" in risk for risk in report.risks))
        self.assertTrue(any("No pull request" in risk for risk in report.risks))

    def test_manual_evidence_counts_as_adoption_signal(self) -> None:
        snapshot = load_snapshot(NEW_PROJECT_FIXTURE).with_evidence(load_evidence(EVIDENCE_FIXTURE))
        report = analyze_snapshot(
            snapshot,
            now=datetime(2026, 6, 1, tzinfo=timezone.utc),
            stale_days=30,
        )

        self.assertEqual(report.evidence.monthly_downloads, 5200)
        self.assertTrue(any("5200 monthly downloads" in signal for signal in report.qualification_signals))
        self.assertFalse(any("Low public adoption" in risk for risk in report.risks))

    def test_load_applicant_profile(self) -> None:
        applicant = load_applicant(APPLICANT_FIXTURE)

        self.assertEqual(applicant.first_name, "Jane")
        self.assertEqual(applicant.github_username, "jane-maintainer")
        self.assertEqual(applicant.interest, "API credits")


if __name__ == "__main__":
    unittest.main()
