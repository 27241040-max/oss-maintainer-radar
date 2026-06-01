from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .models import RepoSnapshot
from .models import Evidence


GITHUB_API = "https://api.github.com"


def load_snapshot(path: str | Path) -> RepoSnapshot:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return RepoSnapshot.from_payload(payload)


def load_evidence(path: str | Path) -> Evidence:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return Evidence.from_payload(payload)


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
        raise RuntimeError(f"GitHub API request failed with {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc
