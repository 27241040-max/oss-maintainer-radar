from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .models import ApplicantProfile, Evidence, RepoSnapshot


GITHUB_API = "https://api.github.com"


def load_snapshot(path: str | Path) -> RepoSnapshot:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return RepoSnapshot.from_payload(payload)


def load_evidence(path: str | Path) -> Evidence:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return Evidence.from_payload(payload)


def load_applicant(path: str | Path) -> ApplicantProfile:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return ApplicantProfile.from_payload(payload)


def fetch_snapshot(repo: str, *, token: str | None = None, per_page: int = 100) -> RepoSnapshot:
    owner, name = parse_repo_ref(repo)
    auth_token = token or os.environ.get("GITHUB_TOKEN")
    repository = _github_get(f"/repos/{owner}/{name}", auth_token)
    issues = _github_get(
        f"/repos/{owner}/{name}/issues?state=all&sort=updated&direction=desc&per_page={per_page}",
        auth_token,
    )
    pulls = _github_get(
        f"/repos/{owner}/{name}/pulls?state=all&sort=updated&direction=desc&per_page={per_page}",
        auth_token,
    )
    releases = _github_get(f"/repos/{owner}/{name}/releases?per_page=20", auth_token)

    return RepoSnapshot.from_payload(
        {
            "repository": repository,
            "issues": issues,
            "pull_requests": pulls,
            "releases": releases,
        }
    )


def parse_repo_ref(value: str) -> tuple[str, str]:
    cleaned = value.strip()
    if cleaned.startswith("https://"):
        parsed = urllib.parse.urlparse(cleaned)
        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if parsed.netloc != "github.com" or len(parts) < 2:
            raise ValueError(f"Unsupported GitHub repository URL: {value}")
        return parts[0], re.sub(r"\.git$", "", parts[1])

    parts = cleaned.split("/")
    if len(parts) == 2 and all(parts):
        return parts[0], re.sub(r"\.git$", "", parts[1])

    raise ValueError("Use owner/repo or https://github.com/owner/repo")


def _github_get(path: str, token: str | None) -> Any:
    request = urllib.request.Request(
        f"{GITHUB_API}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "oss-maintainer-radar",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return _github_get_with_fallback(path, token, f"GitHub API request failed with {exc.code}: {detail}", exc)
    except urllib.error.URLError as exc:
        return _github_get_with_fallback(path, token, f"GitHub API request failed: {exc.reason}", exc)


def _github_get_with_fallback(path: str, token: str | None, message: str, cause: Exception) -> Any:
    try:
        return _github_get_with_gh(path, token)
    except RuntimeError as fallback_exc:
        raise RuntimeError(f"{message}; gh api fallback failed: {fallback_exc}") from cause


def _github_get_with_gh(path: str, token: str | None) -> Any:
    env = os.environ.copy()
    if token and "GITHUB_TOKEN" not in env and "GH_TOKEN" not in env:
        env["GITHUB_TOKEN"] = token

    try:
        completed = subprocess.run(
            ["gh", "api", path],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("GitHub CLI `gh` is not installed") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("GitHub CLI `gh api` timed out") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise RuntimeError(detail)

    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GitHub CLI `gh api` returned invalid JSON") from exc
