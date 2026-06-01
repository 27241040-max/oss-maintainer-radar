from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import re

from .models import (
    MaintainerReport,
    PullRequest,
    Release,
    ReleaseNoteGroup,
    ReleaseNoteItem,
    RepoSnapshot,
    WorkItem,
)


def analyze_snapshot(
    snapshot: RepoSnapshot,
    *,
    now: datetime | None = None,
    stale_days: int = 30,
    since: datetime | None = None,
) -> MaintainerReport:
    generated_at = now or datetime.now(timezone.utc)
    filtered_snapshot = _filter_snapshot(snapshot, since)
    open_issues = [issue for issue in filtered_snapshot.issues if issue.state == "open"]
    open_prs = [pr for pr in filtered_snapshot.pull_requests if pr.state == "open" and not pr.draft]

    stale_issues = tuple(
        WorkItem(
            number=issue.number,
            title=issue.title,
            url=issue.url,
            age_days=_age_days(issue.updated_at, generated_at),
            labels=issue.labels,
        )
        for issue in open_issues
        if _age_days(issue.updated_at, generated_at) >= stale_days
    )

    review_backlog = tuple(
        WorkItem(
            number=pr.number,
            title=pr.title,
            url=pr.url,
            age_days=_age_days(pr.updated_at, generated_at),
            labels=pr.labels,
        )
        for pr in open_prs
        if _age_days(pr.updated_at, generated_at) >= max(2, stale_days // 10)
    )

    label_counts = Counter(label for issue in open_issues for label in issue.labels)
    latest_release = _latest_release(filtered_snapshot.releases)

    return MaintainerReport(
        repository=filtered_snapshot.repository,
        generated_at=generated_at,
        window_start=since,
        open_issue_count=len(open_issues),
        stale_issue_count=len(stale_issues),
        sampled_pull_request_count=len(filtered_snapshot.pull_requests),
        open_pull_request_count=len(open_prs),
        stale_pull_request_count=len(review_backlog),
        label_counts=dict(label_counts.most_common()),
        stale_issues=stale_issues,
        review_backlog=review_backlog,
        latest_release=latest_release,
        release_notes=_release_notes(filtered_snapshot, latest_release),
        release_note_groups=_release_note_groups(filtered_snapshot),
        qualification_signals=_qualification_signals(filtered_snapshot),
        risks=_risks(filtered_snapshot),
        evidence=filtered_snapshot.evidence,
    )


def _age_days(value: datetime | None, now: datetime) -> int:
    if value is None:
        return 0
    return max(0, (now - value).days)


def _latest_release(releases: tuple[Release, ...]) -> Release | None:
    published = [release for release in releases if release.published_at and not release.draft]
    if not published:
        return None
    return sorted(published, key=lambda release: release.published_at or datetime.min, reverse=True)[0]


def _filter_snapshot(snapshot: RepoSnapshot, since: datetime | None) -> RepoSnapshot:
    if since is None:
        return snapshot
    return RepoSnapshot(
        repository=snapshot.repository,
        issues=tuple(issue for issue in snapshot.issues if _in_window(issue.updated_at or issue.created_at, since)),
        pull_requests=tuple(
            pr for pr in snapshot.pull_requests if _in_window(pr.updated_at or pr.created_at, since)
        ),
        releases=tuple(release for release in snapshot.releases if _in_window(release.published_at, since)),
        evidence=snapshot.evidence,
    )


def _in_window(value: datetime | None, since: datetime) -> bool:
    if value is None:
        return False
    return value >= since


def _release_notes(snapshot: RepoSnapshot, latest_release: Release | None) -> tuple[str, ...]:
    notes: list[str] = []
    if latest_release:
        notes.append(f"Latest published release is {latest_release.tag_name}.")
    else:
        notes.append("No published release was found in the sampled data.")

    merged_or_closed_prs = [
        pr for pr in snapshot.pull_requests if pr.state in {"closed", "merged"}
    ]
    if merged_or_closed_prs:
        titles = ", ".join(f"#{pr.number} {pr.title}" for pr in merged_or_closed_prs[:5])
        notes.append(f"Recent completed pull requests to review for notes: {titles}.")

    open_bug_count = sum(
        1
        for issue in snapshot.issues
        if issue.state == "open" and _labels_include(issue.labels, {"bug", "bugfix", "defect", "regression"})
    )
    if open_bug_count:
        notes.append(f"{open_bug_count} open bug-labeled issue(s) may affect release readiness.")

    return tuple(notes)


def _release_note_groups(snapshot: RepoSnapshot) -> tuple[ReleaseNoteGroup, ...]:
    grouped: dict[str, list[ReleaseNoteItem]] = {category: [] for category in _RELEASE_NOTE_CATEGORY_ORDER}
    for pr in snapshot.pull_requests:
        if pr.state not in {"closed", "merged"}:
            continue
        grouped[_release_note_category(pr)].append(
            ReleaseNoteItem(
                number=pr.number,
                title=pr.title,
                url=pr.url,
                labels=pr.labels,
            )
        )

    return tuple(
        ReleaseNoteGroup(category=category, pull_requests=tuple(items))
        for category, items in grouped.items()
        if items
    )


_RELEASE_NOTE_CATEGORY_ORDER = (
    "Security-sensitive changes",
    "Bug fixes",
    "Documentation",
    "Dependencies",
    "Maintenance",
    "Other changes",
)


def _release_note_category(pr: PullRequest) -> str:
    label_tokens = _label_tokens(pr.labels)
    title_tokens = _text_tokens(pr.title)
    words = label_tokens | title_tokens

    if words & {"security", "vulnerability", "cve", "auth", "secret"}:
        return "Security-sensitive changes"
    if words & {"bug", "bugfix", "defect", "regression", "fix", "fixed", "failure", "error", "crash", "broken"}:
        return "Bug fixes"
    if words & {"documentation", "docs", "doc", "readme", "guide"}:
        return "Documentation"
    if words & {"dependencies", "dependency", "deps", "dependabot", "bump", "upgrade"}:
        return "Dependencies"
    if words & {
        "maintenance",
        "chore",
        "ci",
        "workflow",
        "build",
        "release",
        "refactor",
        "test",
        "tests",
        "cleanup",
    }:
        return "Maintenance"
    return "Other changes"


def _labels_include(labels: tuple[str, ...], aliases: set[str]) -> bool:
    return bool(_label_tokens(labels) & aliases)


def _label_tokens(labels: tuple[str, ...]) -> set[str]:
    tokens: set[str] = set()
    for label in labels:
        normalized = " ".join(_text_tokens(label))
        if normalized:
            tokens.add(normalized)
        tokens.update(_text_tokens(label))
    return tokens


def _text_tokens(value: str) -> set[str]:
    return {part for part in re.split(r"[^a-z0-9]+", value.lower()) if part}


def _qualification_signals(snapshot: RepoSnapshot) -> tuple[str, ...]:
    repo = snapshot.repository
    evidence = snapshot.evidence
    signals = [
        f"{repo.full_name} is public at {repo.url or 'an unspecified URL'}.",
        f"Repository signals: {repo.stars} stars, {repo.forks} forks, {repo.open_issues} open GitHub issues.",
    ]

    if evidence.monthly_downloads is not None:
        signals.append(f"Additional evidence: {evidence.monthly_downloads} monthly downloads.")
    if evidence.dependents is not None:
        signals.append(f"Additional evidence: {evidence.dependents} dependents.")
    if evidence.ecosystem_importance:
        signals.append(f"Ecosystem importance: {evidence.ecosystem_importance}")

    if repo.stars >= 100 or repo.forks >= 20 or evidence.has_adoption_signal():
        signals.append("The repository shows visible adoption signals.")
    else:
        signals.append("Adoption signals are still early; do not overstate usage.")

    if snapshot.pull_requests:
        signals.append(f"Sample includes {len(snapshot.pull_requests)} pull request(s), showing active review surface.")

    if snapshot.releases:
        signals.append(f"Sample includes {len(snapshot.releases)} release record(s), showing release management surface.")

    return tuple(signals)


def _risks(snapshot: RepoSnapshot) -> tuple[str, ...]:
    repo = snapshot.repository
    evidence = snapshot.evidence
    risks: list[str] = []
    if repo.archived:
        risks.append("Repository is archived, which conflicts with active-maintenance expectations.")
    if repo.stars < 10 and repo.forks < 3 and not evidence.has_adoption_signal():
        risks.append("Low public adoption may weaken a Codex for OSS application.")
    if evidence.has_adoption_signal() and not evidence.source_urls:
        risks.append("Additional adoption evidence should include source URLs before submission.")
    if not snapshot.pull_requests:
        risks.append("No pull request sample was found; review workload evidence may be weak.")
    if not snapshot.releases:
        risks.append("No release sample was found; release-management evidence may be weak.")
    return tuple(risks)
