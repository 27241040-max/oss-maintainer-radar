from __future__ import annotations

import json
import textwrap
from dataclasses import asdict

from .models import ApplicantProfile, MaintainerReport, WorkItem


def report_to_json(report: MaintainerReport) -> str:
    return json.dumps(report_to_dict(report), ensure_ascii=False, indent=2)


def report_to_dict(report: MaintainerReport) -> dict:
    data = asdict(report)
    data["schema_version"] = "1.1"
    data["generated_at"] = report.generated_at.isoformat()
    data["window_start"] = report.window_start.isoformat() if report.window_start else None
    if report.latest_release and data["latest_release"]:
        data["latest_release"]["published_at"] = (
            report.latest_release.published_at.isoformat()
            if report.latest_release.published_at
            else None
        )
    data["scorecard"] = _scorecard_dict(report)
    return data


def report_to_markdown(report: MaintainerReport) -> str:
    repo = report.repository
    lines = [
        f"# Maintainer Radar: {repo.full_name}",
        "",
        f"Generated: {report.generated_at.isoformat()}",
        f"Window start: {report.window_start.isoformat() if report.window_start else 'not set'}",
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
        "## Additional Evidence",
        "",
    ]

    lines.extend(_evidence_lines(report))
    lines.extend(
        [
            "",
            "## Workload",
            "",
            f"- Open issues in sample: {report.open_issue_count}",
            f"- Stale issues: {report.stale_issue_count}",
            f"- Pull requests in sample: {report.sampled_pull_request_count}",
            f"- Open pull requests in sample: {report.open_pull_request_count}",
            f"- Pull requests awaiting attention: {report.stale_pull_request_count}",
            "",
            "## Label Mix",
            "",
        ]
    )

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
    lines.extend(["", "## Release Note Groups", ""])
    lines.extend(_release_note_group_lines(report))

    lines.extend(["", "## Qualification Signals", ""])
    lines.extend(f"- {signal}" for signal in report.qualification_signals)

    lines.extend(["", "## Application Risks", ""])
    if report.risks:
        lines.extend(f"- {risk}" for risk in report.risks)
    else:
        lines.append("- No obvious application risk was detected in the sampled data.")

    return "\n".join(lines) + "\n"


def application_draft(report: MaintainerReport, *, role: str, applicant: ApplicantProfile | None = None) -> str:
    fields = form_field_values(report, role=role, applicant=applicant)

    return textwrap.dedent(
        f"""\
        # Codex for Open Source Application Draft

        These drafts are intentionally conservative. Edit them before submitting.

        ## Describe Your Role

        {fields["Describe your role"]}

        ## Why Does This Repository Qualify? (<=500 chars)

        {fields["Why does this repository qualify?"]}

        ## How Will You Use API Credits? (<=500 chars)

        {fields["How will you use API credits?"]}

        ## Anything Else? (<=500 chars)

        {fields["Anything else?"]}
        """
    )


def form_field_values(
    report: MaintainerReport,
    *,
    role: str,
    applicant: ApplicantProfile | None = None,
) -> dict[str, str]:
    applicant = applicant or ApplicantProfile()
    evidence_clauses = _application_evidence_clauses(report)
    release_clauses = _application_release_clauses(report)
    qualifies = _fit_500(
        " ".join(
            [
                f"I am a {role} maintainer of {report.repository.full_name}.",
                f"The repo has {report.repository.stars} stars and {report.repository.forks} forks.",
                *evidence_clauses,
                *release_clauses,
                f"Current maintenance surface includes {_count(report.open_issue_count, 'open issue')} and {_count(report.sampled_pull_request_count, 'sampled pull request')}.",
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

    return {
        "First name": _manual(applicant.first_name),
        "Last name": _manual(applicant.last_name),
        "Email associated with your ChatGPT account": _manual(applicant.chatgpt_email),
        "Public GitHub username": _manual(applicant.github_username),
        "Public GitHub repository URL": report.repository.url or "<publish repository first>",
        "Maintainer role": f"{role} maintainer",
        "Describe your role": f"{role.title()} maintainer. I triage issues, review pull requests, manage releases, and help preserve project quality.",
        "Why does this repository qualify?": qualifies,
        "Interest": applicant.interest or "API credits",
        "OpenAI organization ID": _manual(applicant.openai_org_id),
        "How will you use API credits?": credits,
        "Anything else?": anything_else,
    }


def form_fields(
    report: MaintainerReport,
    *,
    role: str,
    applicant: ApplicantProfile | None = None,
) -> str:
    fields = form_field_values(report, role=role, applicant=applicant)
    limited_fields = {
        "Why does this repository qualify?",
        "How will you use API credits?",
        "Anything else?",
    }

    lines = [
        "# Codex for Open Source Form Fields",
        "",
        "Review every field before submitting. This output does not guarantee selection.",
        "",
    ]

    for label, value in fields.items():
        lines.extend([f"## {label}", "", value])
        if label in limited_fields:
            lines.append("")
            lines.append(f"Character count: {len(value)}/500")
        lines.append("")

    lines.extend(
        [
            "## Before Submit",
            "",
            "- Replace every `<fill manually>` value.",
            "- Rerun against the live public repository, not a fixture.",
            "- Check readiness output for REVIEW items.",
            "- Confirm source URLs for any manual evidence.",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


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

        Build a release checklist from the release-note groups, open bug-labeled issues, changelog gaps, and test status. Flag blockers separately from nice-to-have cleanup, and do not infer impact beyond labels, titles, and code context.
        """
    )


def maintenance_scorecard(report: MaintainerReport) -> str:
    scorecard = _scorecard_dict(report)
    repo = report.repository

    lines = [
        f"# Maintenance Scorecard: {repo.full_name}",
        "",
        f"Generated: {report.generated_at.isoformat()}",
        f"Window start: {report.window_start.isoformat() if report.window_start else 'not set'}",
        "",
        f"Score: {scorecard['score']}/{scorecard['total']}",
        "",
        "## Dimensions",
        "",
    ]
    lines.extend(
        f"- {item['name']}: {item['points']}/{item['max_points']} - {item['detail']}"
        for item in scorecard["dimensions"]
    )

    lines.extend(["", "## Notes", ""])
    if report.risks:
        lines.extend(f"- {risk}" for risk in report.risks)
    else:
        lines.append("- No obvious maintenance risk was detected in the sampled data.")

    return "\n".join(lines) + "\n"


def action_plan(report: MaintainerReport) -> str:
    repo = report.repository
    immediate = _immediate_actions(report)
    weekly = _weekly_actions(report)
    evidence = _evidence_actions(report)

    lines = [
        f"# Maintainer Action Plan: {repo.full_name}",
        "",
        f"Generated: {report.generated_at.isoformat()}",
        f"Window start: {report.window_start.isoformat() if report.window_start else 'not set'}",
        "",
        "## Immediate",
        "",
    ]
    lines.extend(immediate)
    lines.extend(["", "## This Week", ""])
    lines.extend(weekly)
    lines.extend(["", "## Evidence To Keep Current", ""])
    lines.extend(evidence)

    return "\n".join(lines) + "\n"


def submission_pack(
    report: MaintainerReport,
    *,
    role: str,
    applicant: ApplicantProfile | None = None,
) -> str:
    repo = report.repository
    lines = [
        "# Codex for Open Source Submission Pack",
        "",
        f"Repository: {repo.full_name}",
        f"Repository URL: {repo.url or 'unknown'}",
        f"Generated: {report.generated_at.isoformat()}",
        f"Window start: {report.window_start.isoformat() if report.window_start else 'not set'}",
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
        application_draft(report, role=role, applicant=applicant).strip(),
        "",
        "## Form Fields",
        "",
        form_fields(report, role=role, applicant=applicant).strip(),
        "",
        "## Evidence Report",
        "",
        report_to_markdown(report).strip(),
        "",
        "## Maintenance Scorecard",
        "",
        maintenance_scorecard(report).strip(),
        "",
        "## Maintainer Action Plan",
        "",
        action_plan(report).strip(),
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
            repo.stars >= 10 or repo.forks >= 3 or report.evidence.has_adoption_signal(),
            _adoption_success(report),
            "Collect truthful usage evidence such as stars, forks, downloads, dependents, or ecosystem importance.",
        ),
        _check(
            "Evidence sources",
            not report.evidence.has_adoption_signal() or bool(report.evidence.source_urls),
            "Additional evidence includes source URLs.",
            "Add source URLs for downloads, dependents, or ecosystem-importance claims.",
        ),
        _check(
            "Maintenance workload evidence",
            report.open_issue_count > 0 or report.sampled_pull_request_count > 0,
            f"Sample has {_count(report.open_issue_count, 'open issue')} and {_count(report.sampled_pull_request_count, 'pull request')}.",
            "A brand-new repo may not show ongoing triage or review work yet.",
        ),
        _check(
            "Review surface evidence",
            report.sampled_pull_request_count > 0,
            f"Sample has {_count(report.sampled_pull_request_count, 'pull request')}.",
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


def _evidence_lines(report: MaintainerReport) -> list[str]:
    evidence = report.evidence
    lines: list[str] = []
    if evidence.monthly_downloads is not None:
        lines.append(f"- Monthly downloads: {evidence.monthly_downloads}")
    if evidence.dependents is not None:
        lines.append(f"- Dependents: {evidence.dependents}")
    if evidence.ecosystem_importance:
        lines.append(f"- Ecosystem importance: {evidence.ecosystem_importance}")
    lines.extend(f"- Maintainer responsibility: {item}" for item in evidence.maintainer_responsibilities)
    lines.extend(f"- Usage note: {item}" for item in evidence.usage_notes)
    lines.extend(f"- Source: {item}" for item in evidence.source_urls)
    if not lines:
        lines.append("- No additional evidence file was provided.")
    return lines


def _application_evidence_clauses(report: MaintainerReport) -> list[str]:
    evidence = report.evidence
    clauses: list[str] = []
    if evidence.monthly_downloads is not None:
        clauses.append(f"It has about {evidence.monthly_downloads} monthly downloads.")
    if evidence.dependents is not None:
        clauses.append(f"It has {evidence.dependents} dependents.")
    if evidence.ecosystem_importance:
        clauses.append(evidence.ecosystem_importance)
    return clauses


def _application_release_clauses(report: MaintainerReport) -> list[str]:
    if not report.latest_release:
        return []
    return [f"Latest release is {report.latest_release.tag_name}."]


def _score_dimensions(report: MaintainerReport) -> list[tuple[str, int, int, str]]:
    repo = report.repository
    adoption = repo.stars >= 10 or repo.forks >= 3 or report.evidence.has_adoption_signal()
    has_workload = report.open_issue_count > 0 or report.sampled_pull_request_count > 0
    risk_penalty = min(20, len(report.risks) * 5)

    return [
        (
            "Repository availability",
            20 if repo.url.startswith("https://github.com/") and not repo.archived else 0,
            20,
            "Public GitHub repository is active."
            if repo.url.startswith("https://github.com/") and not repo.archived
            else "Repository should be public on GitHub and not archived.",
        ),
        (
            "Adoption signal",
            20 if adoption else 0,
            20,
            _adoption_success(report) if adoption else "Public adoption evidence is still weak.",
        ),
        (
            "Maintenance surface",
            20 if has_workload else 0,
            20,
            f"Sample has {_count(report.open_issue_count, 'open issue')} and {_count(report.sampled_pull_request_count, 'pull request')}."
            if has_workload
            else "No open issue or pull request surface was found in the sample.",
        ),
        (
            "Release practice",
            20 if report.latest_release else 0,
            20,
            f"Latest release is {report.latest_release.tag_name}."
            if report.latest_release
            else "No public release was found in the sample.",
        ),
        (
            "Risk posture",
            max(0, 20 - risk_penalty),
            20,
            "No obvious risks were detected." if not report.risks else f"{len(report.risks)} risk item(s) need review.",
        ),
    ]


def _scorecard_dict(report: MaintainerReport) -> dict:
    dimensions = _score_dimensions(report)
    return {
        "score": sum(points for _, points, _, _ in dimensions),
        "total": sum(max_points for _, _, max_points, _ in dimensions),
        "risk_count": len(report.risks),
        "dimensions": [
            {
                "name": name,
                "points": points,
                "max_points": max_points,
                "detail": detail,
            }
            for name, points, max_points, detail in dimensions
        ],
    }


def _immediate_actions(report: MaintainerReport) -> list[str]:
    actions: list[str] = []
    repo = report.repository
    if not repo.url.startswith("https://github.com/"):
        actions.append("- Publish the repository on GitHub before using public maintainer evidence.")
    if repo.archived:
        actions.append("- Unarchive the repository or choose an active project.")
    if not report.latest_release:
        actions.append("- Publish a first release with installation notes and changelog entries.")
    if report.stale_pull_request_count:
        actions.append(f"- Review {_count(report.stale_pull_request_count, 'pull request')} waiting for attention.")
    if report.stale_issue_count:
        actions.append(f"- Triage {_count(report.stale_issue_count, 'stale issue')} and record the next maintainer action.")
    if not actions:
        actions.append("- No urgent repository hygiene action was found in this sample.")
    return actions


def _weekly_actions(report: MaintainerReport) -> list[str]:
    actions = [
        f"- Review the current sample of {_count(report.open_pull_request_count, 'open pull request')}.",
        f"- Triage the current sample of {_count(report.open_issue_count, 'open issue')}.",
        "- Keep release notes tied to merged changes and public tags.",
    ]
    completed_pr_count = max(0, report.sampled_pull_request_count - report.open_pull_request_count)
    if completed_pr_count:
        actions.append(f"- Review {_count(completed_pr_count, 'completed pull request')} for release-note impact.")
    if report.release_note_groups:
        groups = ", ".join(group.category for group in report.release_note_groups[:5])
        actions.append(f"- Draft release notes from deterministic groups: {groups}.")
    if report.label_counts:
        top_labels = ", ".join(list(report.label_counts)[:5])
        actions.append(f"- Watch high-volume labels: {top_labels}.")
    return actions


def _evidence_actions(report: MaintainerReport) -> list[str]:
    actions = [
        "- Keep stars, forks, releases, issues, and pull requests publicly visible.",
        "- Add external usage evidence only when it has a source URL.",
    ]
    if report.repository.stars < 10 and report.repository.forks < 3 and not report.evidence.has_adoption_signal():
        actions.append("- Collect real adoption evidence before making ecosystem-impact claims.")
    return actions


def _adoption_success(report: MaintainerReport) -> str:
    parts = [f"{report.repository.stars} stars", f"{report.repository.forks} forks"]
    if report.evidence.monthly_downloads is not None:
        parts.append(f"{report.evidence.monthly_downloads} monthly downloads")
    if report.evidence.dependents is not None:
        parts.append(f"{report.evidence.dependents} dependents")
    if report.evidence.ecosystem_importance:
        parts.append("ecosystem-importance notes")
    return "Repository has " + ", ".join(parts) + "."


def _work_items(items: tuple[WorkItem, ...], empty: str) -> list[str]:
    if not items:
        return [f"- {empty}"]
    return [
        f"- #{item.number} {item.title} ({item.age_days} days since update) {item.url}".rstrip()
        for item in items
    ]


def _release_note_group_lines(report: MaintainerReport) -> list[str]:
    if not report.release_note_groups:
        return ["- No completed pull requests were available for release-note grouping."]

    lines: list[str] = []
    for group in report.release_note_groups:
        lines.append(f"- {group.category}")
        for item in group.pull_requests[:5]:
            label_text = f" [{', '.join(item.labels)}]" if item.labels else ""
            lines.append(f"  - #{item.number} {item.title}{label_text} {item.url}".rstrip())
    return lines


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


def _manual(value: str) -> str:
    return value if value else "<fill manually>"
