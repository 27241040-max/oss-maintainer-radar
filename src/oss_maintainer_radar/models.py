from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def parse_github_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


@dataclass(frozen=True)
class Repository:
    full_name: str
    url: str
    description: str = ""
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    default_branch: str = "main"
    archived: bool = False

    @classmethod
    def from_github(cls, payload: dict[str, Any]) -> "Repository":
        return cls(
            full_name=str(payload.get("full_name", "unknown/unknown")),
            url=str(payload.get("html_url", "")),
            description=str(payload.get("description") or ""),
            stars=int(payload.get("stargazers_count") or 0),
            forks=int(payload.get("forks_count") or 0),
            open_issues=int(payload.get("open_issues_count") or 0),
            default_branch=str(payload.get("default_branch") or "main"),
            archived=bool(payload.get("archived", False)),
        )


@dataclass(frozen=True)
class Issue:
    number: int
    title: str
    state: str
    url: str
    labels: tuple[str, ...] = ()
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_github(cls, payload: dict[str, Any]) -> "Issue":
        return cls(
            number=int(payload.get("number") or 0),
            title=str(payload.get("title") or ""),
            state=str(payload.get("state") or "open"),
            url=str(payload.get("html_url") or ""),
            labels=tuple(_label_names(payload.get("labels", []))),
            created_at=parse_github_datetime(payload.get("created_at")),
            updated_at=parse_github_datetime(payload.get("updated_at")),
        )


@dataclass(frozen=True)
class PullRequest:
    number: int
    title: str
    state: str
    url: str
    draft: bool = False
    labels: tuple[str, ...] = ()
    created_at: datetime | None = None
    updated_at: datetime | None = None
    requested_reviewers: tuple[str, ...] = ()

    @classmethod
    def from_github(cls, payload: dict[str, Any]) -> "PullRequest":
        return cls(
            number=int(payload.get("number") or 0),
            title=str(payload.get("title") or ""),
            state=str(payload.get("state") or "open"),
            url=str(payload.get("html_url") or ""),
            draft=bool(payload.get("draft", False)),
            labels=tuple(_label_names(payload.get("labels", []))),
            created_at=parse_github_datetime(payload.get("created_at")),
            updated_at=parse_github_datetime(payload.get("updated_at")),
            requested_reviewers=tuple(
                str(reviewer.get("login"))
                for reviewer in payload.get("requested_reviewers", [])
                if reviewer.get("login")
            ),
        )


@dataclass(frozen=True)
class Release:
    name: str
    tag_name: str
    url: str
    draft: bool = False
    prerelease: bool = False
    published_at: datetime | None = None

    @classmethod
    def from_github(cls, payload: dict[str, Any]) -> "Release":
        return cls(
            name=str(payload.get("name") or payload.get("tag_name") or ""),
            tag_name=str(payload.get("tag_name") or ""),
            url=str(payload.get("html_url") or ""),
            draft=bool(payload.get("draft", False)),
            prerelease=bool(payload.get("prerelease", False)),
            published_at=parse_github_datetime(payload.get("published_at")),
        )


@dataclass(frozen=True)
class RepoSnapshot:
    repository: Repository
    issues: tuple[Issue, ...] = ()
    pull_requests: tuple[PullRequest, ...] = ()
    releases: tuple[Release, ...] = ()
    evidence: "Evidence" = field(default_factory=lambda: Evidence())

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RepoSnapshot":
        repo_payload = payload.get("repository") or payload.get("repo") or {}
        issue_payloads = payload.get("issues", [])
        pull_payloads = payload.get("pull_requests") or payload.get("pulls") or []
        release_payloads = payload.get("releases", [])

        issues = [
            Issue.from_github(item)
            for item in issue_payloads
            if not item.get("pull_request")
        ]

        return cls(
            repository=Repository.from_github(repo_payload),
            issues=tuple(issues),
            pull_requests=tuple(PullRequest.from_github(item) for item in pull_payloads),
            releases=tuple(Release.from_github(item) for item in release_payloads),
            evidence=Evidence.from_payload(payload.get("evidence") or {}),
        )

    def with_evidence(self, evidence: "Evidence") -> "RepoSnapshot":
        return RepoSnapshot(
            repository=self.repository,
            issues=self.issues,
            pull_requests=self.pull_requests,
            releases=self.releases,
            evidence=evidence,
        )


@dataclass(frozen=True)
class Evidence:
    monthly_downloads: int | None = None
    dependents: int | None = None
    ecosystem_importance: str = ""
    maintainer_responsibilities: tuple[str, ...] = ()
    usage_notes: tuple[str, ...] = ()
    source_urls: tuple[str, ...] = ()

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Evidence":
        return cls(
            monthly_downloads=_optional_int(payload.get("monthly_downloads")),
            dependents=_optional_int(payload.get("dependents")),
            ecosystem_importance=str(payload.get("ecosystem_importance") or ""),
            maintainer_responsibilities=tuple(
                str(item) for item in payload.get("maintainer_responsibilities", []) if str(item).strip()
            ),
            usage_notes=tuple(str(item) for item in payload.get("usage_notes", []) if str(item).strip()),
            source_urls=tuple(str(item) for item in payload.get("source_urls", []) if str(item).strip()),
        )

    def has_adoption_signal(self) -> bool:
        return bool(
            (self.monthly_downloads and self.monthly_downloads > 0)
            or (self.dependents and self.dependents > 0)
            or self.ecosystem_importance.strip()
            or self.usage_notes
        )


@dataclass(frozen=True)
class ApplicantProfile:
    first_name: str = ""
    last_name: str = ""
    chatgpt_email: str = ""
    github_username: str = ""
    openai_org_id: str = ""
    interest: str = "API credits"

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ApplicantProfile":
        return cls(
            first_name=str(payload.get("first_name") or ""),
            last_name=str(payload.get("last_name") or ""),
            chatgpt_email=str(payload.get("chatgpt_email") or payload.get("email") or ""),
            github_username=str(payload.get("github_username") or ""),
            openai_org_id=str(payload.get("openai_org_id") or ""),
            interest=str(payload.get("interest") or "API credits"),
        )


@dataclass(frozen=True)
class WorkItem:
    number: int
    title: str
    url: str
    age_days: int
    labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class MaintainerReport:
    repository: Repository
    generated_at: datetime
    window_start: datetime | None
    open_issue_count: int
    stale_issue_count: int
    sampled_pull_request_count: int
    open_pull_request_count: int
    stale_pull_request_count: int
    label_counts: dict[str, int] = field(default_factory=dict)
    stale_issues: tuple[WorkItem, ...] = ()
    review_backlog: tuple[WorkItem, ...] = ()
    latest_release: Release | None = None
    release_notes: tuple[str, ...] = ()
    qualification_signals: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    evidence: Evidence = field(default_factory=Evidence)


def _label_names(labels: list[Any]) -> list[str]:
    names: list[str] = []
    for label in labels:
        if isinstance(label, str):
            names.append(label)
        elif isinstance(label, dict) and label.get("name"):
            names.append(str(label["name"]))
    return names


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)
