from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectFileTests(unittest.TestCase):
    def test_action_metadata_exposes_maintainer_reports(self) -> None:
        text = (ROOT / "action.yml").read_text(encoding="utf-8")

        self.assertIn("using: composite", text)
        self.assertIn("target_repo:", text)
        self.assertIn("github_token:", text)
        self.assertIn("report_json_path:", text)
        self.assertIn("oss-radar audit", text)
        self.assertIn("--format json", text)
        self.assertIn("oss-radar scorecard", text)
        self.assertIn("oss-radar action-plan", text)
        self.assertIn("oss-radar codex-prompts", text)

    def test_scheduled_workflow_uses_local_action(self) -> None:
        text = (ROOT / ".github" / "workflows" / "maintainer-radar.yml").read_text(encoding="utf-8")

        self.assertIn("uses: ./", text)
        self.assertIn("target_repo: ${{ env.TARGET_REPO }}", text)
        self.assertIn("stale_days: ${{ env.STALE_DAYS }}", text)
        self.assertIn("path: reports/", text)

    def test_readme_documents_reusable_action(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("27241040-max/oss-maintainer-radar@v0.4.0", text)
        self.assertIn("docs/action-usage.md", text)
        self.assertIn("schemas/maintainer-report.schema.json", text)


if __name__ == "__main__":
    unittest.main()
