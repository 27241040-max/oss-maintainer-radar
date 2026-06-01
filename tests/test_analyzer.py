from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from oss_maintainer_radar.analyzer import analyze_snapshot
from oss_maintainer_radar.github import load_applicant, load_evidence, load_snapshot, parse_repo_ref
from oss_maintainer_radar.models import RepoSnapshot


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

    def test_release_note_groups_are_deterministic_from_labels_and_titles(self) -> None:
        snapshot = RepoSnapshot.from_payload(
            {
                "repository": {
                    "full_name": "example/repo",
                    "html_url": "https://github.com/example/repo",
                },
                "pull_requests": [
                    {"number": 1, "title": "Patch auth token handling", "state": "closed", "labels": []},
                    {"number": 2, "title": "Fix crash on empty config", "state": "closed", "labels": []},
                    {"number": 3, "title": "Improve README setup guide", "state": "closed", "labels": []},
                    {"number": 4, "title": "Bump actions/checkout from 4 to 6", "state": "closed", "labels": []},
                    {"number": 5, "title": "Refresh CI workflow", "state": "closed", "labels": []},
                    {"number": 6, "title": "Add compact mode", "state": "closed", "labels": []},
                    {"number": 7, "title": "Open review remains excluded", "state": "open", "labels": []},
                ],
            }
        )

        report = analyze_snapshot(snapshot)
        groups = {group.category: [item.number for item in group.pull_requests] for group in report.release_note_groups}

        self.assertEqual(groups["Security-sensitive changes"], [1])
        self.assertEqual(groups["Bug fixes"], [2])
        self.assertEqual(groups["Documentation"], [3])
        self.assertEqual(groups["Dependencies"], [4])
        self.assertEqual(groups["Maintenance"], [5])
        self.assertEqual(groups["Other changes"], [6])
        self.assertNotIn(7, [number for numbers in groups.values() for number in numbers])

    def test_release_note_groups_normalize_common_label_aliases_without_rewriting_labels(self) -> None:
        snapshot = RepoSnapshot.from_payload(
            {
                "repository": {
                    "full_name": "example/repo",
                    "html_url": "https://github.com/example/repo",
                },
                "issues": [
                    {
                        "number": 10,
                        "title": "Crash in config loader",
                        "state": "open",
                        "labels": [{"name": "type: bug"}],
                    }
                ],
                "pull_requests": [
                    {"number": 1, "title": "Harden token storage", "state": "closed", "labels": [{"name": "security-review"}]},
                    {"number": 2, "title": "Repair config loader", "state": "closed", "labels": [{"name": "type: bug"}]},
                    {"number": 3, "title": "Clarify install path", "state": "closed", "labels": [{"name": "area/docs"}]},
                    {"number": 4, "title": "Upgrade action pins", "state": "closed", "labels": [{"name": "dependencies"}]},
                    {"number": 5, "title": "Refresh workflows", "state": "closed", "labels": [{"name": "chore"}]},
                ],
            }
        )

        report = analyze_snapshot(snapshot)
        groups = {group.category: group.pull_requests for group in report.release_note_groups}

        self.assertEqual([item.number for item in groups["Security-sensitive changes"]], [1])
        self.assertEqual([item.number for item in groups["Bug fixes"]], [2])
        self.assertEqual([item.number for item in groups["Documentation"]], [3])
        self.assertEqual([item.number for item in groups["Dependencies"]], [4])
        self.assertEqual([item.number for item in groups["Maintenance"]], [5])
        self.assertEqual(groups["Bug fixes"][0].labels, ("type: bug",))
        self.assertTrue(any("open bug-labeled issue" in note for note in report.release_notes))

    def test_since_filters_release_window_evidence(self) -> None:
        snapshot = load_snapshot(FIXTURE)
        report = analyze_snapshot(
            snapshot,
            now=datetime(2026, 6, 1, tzinfo=timezone.utc),
            stale_days=30,
            since=datetime(2026, 5, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(report.window_start, datetime(2026, 5, 1, tzinfo=timezone.utc))
        self.assertEqual(report.open_issue_count, 1)
        self.assertEqual(report.stale_issue_count, 0)
        self.assertEqual(report.sampled_pull_request_count, 1)
        self.assertEqual(report.open_pull_request_count, 1)
        self.assertIsNone(report.latest_release)
        self.assertTrue(any("No release sample" in risk for risk in report.risks))

    def test_since_can_produce_empty_window(self) -> None:
        snapshot = load_snapshot(FIXTURE)
        report = analyze_snapshot(
            snapshot,
            now=datetime(2026, 6, 1, tzinfo=timezone.utc),
            stale_days=30,
            since=datetime(2026, 6, 2, tzinfo=timezone.utc),
        )

        self.assertEqual(report.open_issue_count, 0)
        self.assertEqual(report.sampled_pull_request_count, 0)
        self.assertIsNone(report.latest_release)
        self.assertTrue(any("No pull request sample" in risk for risk in report.risks))

    def test_load_applicant_profile(self) -> None:
        applicant = load_applicant(APPLICANT_FIXTURE)

        self.assertEqual(applicant.first_name, "Jane")
        self.assertEqual(applicant.github_username, "jane-maintainer")
        self.assertEqual(applicant.interest, "API credits")


if __name__ == "__main__":
    unittest.main()
