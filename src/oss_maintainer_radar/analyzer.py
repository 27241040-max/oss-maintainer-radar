from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from .models import MaintainerReport, Release, RepoSnapshot, WorkItem


def analyze_snapshot(
    snapshot: RepoSnapshot,
    *,
    now: datetime | None = None,
    stale_days: int = 30,
) -> MaintainerReport:
    generated_at = now or datetime.now(timezone.utc)
    open_issues = [issue for issue in snapshot.issues if issue.state == "open"]
    open_prs = [pr for pr in snapshot.pull_requests if pr.state == "open" and not pr.draft]

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
    latest_release = _latest_release(snapshot.releases)

    return MaintainerReport(
        repository=snapshot.repository,
        generated_at=generated_at,
        open_issue_count=len(open_issues),
        stale_issue_count=len(stale_issues),
        open_pull_request_count=len(open_prs),
        stale_pull_request_count=len(review_backlog),
        label_counts=dict(label_counts.most_common()),
        stale_issues=stale_issues,
        review_backlog=review_backlog,
        latest_release=latest_release,
        release_notes=_release_notes(snapshot, latest_release),
        qualification_signals=_qualification_signals(snapshot),
        risks=_risks(snapshot),
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
        if issue.state == "open" and any(label.lower() == "bug" for label in issue.labels)
    )
    if open_bug_count:
        notes.append(f"{open_bug_count} open bug-labeled issue(s) may affect release readiness.")

    return tuple(notes)


def _qualification_signals(snapshot: RepoSnapshot) -> tuple[str, ...]:
    repo = snapshot.repository
    signals = [
        f"{repo.full_name} is public at {repo.url or 'an unspecified URL'}.",
        f"Repository signals: {repo.stars} stars, {repo.forks} forks, {repo.open_issues} open GitHub issues.",
    ]

    if repo.stars >= 100 or repo.forks >= 20:
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
    risks: list[str] = []
    if repo.archived:
        risks.append("Repository is archived, which conflicts with active-maintenance expectations.")
    if repo.stars < 10 and repo.forks < 3:
        risks.append("Low public adoption may weaken a Codex for OSS application.")
    if not snapshot.pull_requests:
        risks.append("No pull request sample was found; review workload evidence may be weak.")
    if not snapshot.releases:
        risks.append("No release sample was found; release-management evidence may be weak.")
    return tuple(risks)

