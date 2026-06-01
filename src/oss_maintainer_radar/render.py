from __future__ import annotations

import json
import textwrap
from dataclasses import asdict

from .models import MaintainerReport, WorkItem


def report_to_json(report: MaintainerReport) -> str:
    return json.dumps(asdict(report), default=str, ensure_ascii=False, indent=2)


def report_to_markdown(report: MaintainerReport) -> str:
    repo = report.repository
    lines = [
        f"# Maintainer Radar: {repo.full_name}",
        "",
        f"Generated: {report.generated_at.isoformat()}",
        "",
        "## Repository",
        "",
        f"- URL: {repo.url or 'unknown'}",
        f"- Description: {repo.description or 'No description provided'}",
        f"- Stars: {repo.stars}",
        f"- Forks: {repo.forks}",
        f"- Default branch: {repo.default_branch}",
        f"- Archived: {'yes' if repo.archived else 'no'}",
        "",
        "## Workload",
        "",
        f"- Open issues in sample: {report.open_issue_count}",
        f"- Stale issues: {report.stale_issue_count}",
        f"- Open pull requests in sample: {report.open_pull_request_count}",
        f"- Pull requests awaiting attention: {report.stale_pull_request_count}",
        "",
        "## Label Mix",
        "",
    ]

    if report.label_counts:
        lines.extend(f"- {label}: {count}" for label, count in report.label_counts.items())
    else:
        lines.append("- No labels found in the open issue sample.")

    lines.extend(["", "## Stale Issues", ""])
    lines.extend(_work_items(report.stale_issues, "No stale issues found in the sample."))

    lines.extend(["", "## Pull Requests Awaiting Review", ""])
    lines.extend(_work_items(report.review_backlog, "No stale pull requests found in the sample."))

    lines.extend(["", "## Release Notes", ""])
    lines.extend(f"- {note}" for note in report.release_notes)

    lines.extend(["", "## Qualification Signals", ""])
    lines.extend(f"- {signal}" for signal in report.qualification_signals)

    lines.extend(["", "## Application Risks", ""])
    if report.risks:
        lines.extend(f"- {risk}" for risk in report.risks)
    else:
        lines.append("- No obvious application risk was detected in the sampled data.")

    return "\n".join(lines) + "\n"


def application_draft(report: MaintainerReport, *, role: str) -> str:
    qualifies = _fit_500(
        " ".join(
            [
                f"I am a {role} maintainer of {report.repository.full_name}.",
                f"The repo has {report.repository.stars} stars and {report.repository.forks} forks.",
                f"Current maintenance surface includes {_count(report.open_issue_count, 'open issue')} and {_count(report.open_pull_request_count, 'open pull request')} in the sampled data.",
                "The project benefits from evidence-based triage, review, release management, and quality work.",
            ]
        )
    )
    credits = _fit_500(
        "Use API credits for maintainer automation: summarize new issues, prepare PR review briefs, draft release notes from merged changes, route security-sensitive reports, and generate regression-risk checklists before releases. Outputs will be reviewed by maintainers before action."
    )
    anything_else = _fit_500(
        "All application claims should be checked against public GitHub data before submission. Do not claim adoption, permissions, or ecosystem impact that cannot be verified."
    )

    return textwrap.dedent(
        f"""\
        # Codex for Open Source Application Draft

        These drafts are intentionally conservative. Edit them before submitting.

        ## Describe Your Role

        {role.title()} maintainer. I triage issues, review pull requests, manage releases, and help preserve project quality.

        ## Why Does This Repository Qualify? (<=500 chars)

        {qualifies}

        ## How Will You Use API Credits? (<=500 chars)

        {credits}

        ## Anything Else? (<=500 chars)

        {anything_else}
        """
    )


def codex_prompts(report: MaintainerReport) -> str:
    repo = report.repository.full_name
    stale_list = "\n".join(f"- #{item.number}: {item.title}" for item in report.stale_issues[:10])
    review_list = "\n".join(f"- #{item.number}: {item.title}" for item in report.review_backlog[:10])

    return textwrap.dedent(
        f"""\
        # Codex Maintainer Prompts for {repo}

        ## Issue Triage

        Review these stale issues and propose labels, duplicate checks, and the next maintainer action. Keep the output evidence-based and avoid closing anything without a maintainer decision.

        {stale_list or "- No stale issues in the current sample."}

        ## Pull Request Review Brief

        For each PR, summarize likely review focus areas, missing tests, release-note impact, and security-sensitive changes to inspect.

        {review_list or "- No stale PRs in the current sample."}

        ## Release Readiness

        Build a release checklist from the latest merged PRs, open bug-labeled issues, changelog gaps, and test status. Flag blockers separately from nice-to-have cleanup.
        """
    )


def submission_pack(report: MaintainerReport, *, role: str) -> str:
    repo = report.repository
    lines = [
        "# Codex for Open Source Submission Pack",
        "",
        f"Repository: {repo.full_name}",
        f"Repository URL: {repo.url or 'unknown'}",
        f"Generated: {report.generated_at.isoformat()}",
        "",
        "## Before You Submit",
        "",
        "- Confirm your GitHub profile is public.",
        "- Confirm the repository is public.",
        f"- Confirm you are truly a {role} maintainer.",
        "- Replace fixture/sample data with a live `--repo owner/repo` run.",
        "- Fill in first name, last name, ChatGPT account email, and OpenAI organization ID yourself.",
        "- Do not claim usage, downloads, permissions, or ecosystem importance that the evidence does not support.",
        "",
        "## Application Draft",
        "",
        application_draft(report, role=role).strip(),
        "",
        "## Evidence Report",
        "",
        report_to_markdown(report).strip(),
        "",
        "## Codex Workflow Prompts",
        "",
        codex_prompts(report).strip(),
    ]
    return "\n".join(lines) + "\n"


def readiness_check(report: MaintainerReport, *, role: str) -> str:
    repo = report.repository
    checks = [
        _check(
            "Public repository URL",
            bool(repo.url.startswith("https://github.com/")),
            f"Repository URL is {repo.url or 'missing'}.",
            "Publish the repository on GitHub and rerun with `--repo owner/repo`.",
        ),
        _check(
            "Repository is active",
            not repo.archived,
            "Repository is not archived.",
            "Unarchive the repository or use an active project you maintain.",
        ),
        _check(
            "Maintainer role selected",
            role in {"primary", "core"},
            f"Role is {role} maintainer.",
            "Choose primary or core maintainer.",
        ),
        _check(
            "Adoption evidence",
            repo.stars >= 10 or repo.forks >= 3,
            f"Repository has {repo.stars} stars and {repo.forks} forks.",
            "Collect truthful usage evidence such as stars, forks, downloads, dependents, or ecosystem importance.",
        ),
        _check(
            "Maintenance workload evidence",
            report.open_issue_count > 0 or report.open_pull_request_count > 0,
            f"Sample has {_count(report.open_issue_count, 'open issue')} and {_count(report.open_pull_request_count, 'open pull request')}.",
            "A brand-new repo may not show ongoing triage or review work yet.",
        ),
        _check(
            "Review surface evidence",
            report.open_pull_request_count > 0 or report.stale_pull_request_count > 0,
            f"Sample has {_count(report.open_pull_request_count, 'open pull request')}.",
            "Show pull request review responsibilities from the public repository or existing project.",
        ),
        _check(
            "Release management evidence",
            report.latest_release is not None,
            f"Latest release is {report.latest_release.tag_name if report.latest_release else 'missing'}.",
            "Create public releases or explain another verifiable maintenance responsibility.",
        ),
        _check(
            "Application-risk review",
            not report.risks,
            "No obvious risks were detected in the sampled data.",
            "Review the risks below and edit application text conservatively.",
        ),
    ]

    lines = [
        f"# Codex for Open Source Readiness: {repo.full_name}",
        "",
        f"Generated: {report.generated_at.isoformat()}",
        "",
        "This is a self-check, not a guarantee of selection.",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- {check}" for check in checks)

    lines.extend(["", "## Current Risks", ""])
    if report.risks:
        lines.extend(f"- {risk}" for risk in report.risks)
    else:
        lines.append("- No obvious application risk was detected in the sampled data.")

    lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "- Run against the real public repository, not a fixture, before submitting.",
            "- Keep GitHub profile and repository visibility public.",
            "- Fill personal fields and OpenAI organization ID yourself.",
            "- Do not submit claims you cannot verify.",
        ]
    )
    return "\n".join(lines) + "\n"


def _work_items(items: tuple[WorkItem, ...], empty: str) -> list[str]:
    if not items:
        return [f"- {empty}"]
    return [
        f"- #{item.number} {item.title} ({item.age_days} days since update) {item.url}".rstrip()
        for item in items
    ]


def _fit_500(value: str) -> str:
    compact = " ".join(value.split())
    if len(compact) <= 500:
        return compact
    return compact[:497].rstrip() + "..."


def _count(value: int, label: str) -> str:
    suffix = "" if value == 1 else "s"
    return f"{value} {label}{suffix}"


def _check(name: str, passed: bool, success: str, failure: str) -> str:
    status = "PASS" if passed else "REVIEW"
    detail = success if passed else failure
    return f"[{status}] {name}: {detail}"
