from __future__ import annotations

import subprocess
import unittest
import urllib.error
from unittest.mock import patch

from oss_maintainer_radar.github import _github_get


class GithubTests(unittest.TestCase):
    @patch("oss_maintainer_radar.github.subprocess.run")
    @patch("oss_maintainer_radar.github.urllib.request.urlopen")
    def test_github_get_falls_back_to_gh_api_on_url_error(self, urlopen, run) -> None:
        urlopen.side_effect = urllib.error.URLError("certificate verify failed")
        run.return_value = subprocess.CompletedProcess(
            args=["gh", "api", "/repos/owner/repo"],
            returncode=0,
            stdout='{"full_name": "owner/repo"}',
            stderr="",
        )

        payload = _github_get("/repos/owner/repo", token=None)

        self.assertEqual(payload, {"full_name": "owner/repo"})
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], ["gh", "api", "/repos/owner/repo"])


if __name__ == "__main__":
    unittest.main()
