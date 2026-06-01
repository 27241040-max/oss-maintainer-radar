# Maintainer Workflows

OSS Maintainer Radar supports repeatable maintenance loops that can be run
locally, in CI, or before a release.

## Weekly Triage

```bash
oss-radar audit --repo owner/repo --output reports/weekly-triage.md
```

Use the report to:

- identify stale issues
- find bug-labeled issues that may block releases
- decide which PRs need reviewer attention
- keep public maintenance notes grounded in repository evidence

## Health Scorecard

```bash
oss-radar scorecard --repo owner/repo --output reports/scorecard.md
```

Use the scorecard to:

- spot weak areas before a release
- compare public adoption, review surface, and release practice
- keep risk notes separate from roadmap ambitions

## Maintainer Action Plan

```bash
oss-radar action-plan --repo owner/repo --output reports/action-plan.md
```

Use the action plan to:

- identify urgent hygiene work
- convert stale review and triage signals into a weekly checklist
- keep evidence collection honest and source-backed

## Pull Request Review Prep

```bash
oss-radar codex-prompts --repo owner/repo --output reports/review-prompts.md
```

Paste the generated prompt into Codex with the relevant PR diff. Ask for:

- likely regression areas
- missing tests
- release-note impact
- security-sensitive code paths

## Release Readiness

```bash
oss-radar audit --repo owner/repo --stale-days 14 --output reports/release-readiness.md
```

Before publishing:

- inspect open bug-labeled issues
- check stale PRs that may contain release blockers
- review deterministic release-note groups produced from completed PR labels and titles
- remember that label aliases are normalized for grouping, but original labels remain in output
- review recent completed PRs for changelog entries
- keep release notes separate from unverifiable marketing claims

## Release Windows

```bash
oss-radar scorecard --repo owner/repo --since 2026-05-01 --output reports/may-scorecard.md
```

Use release-window filters to:

- focus scorecards on work updated after a release branch opened
- keep stale issue and PR counts tied to a specific milestone
- compare current release work against the full repository report

## Trend Reports

```bash
oss-radar audit --repo owner/repo --format json --output reports/week-1.json
oss-radar audit --repo owner/repo --format json --output reports/week-2.json
oss-radar validate-report reports/week-1.json reports/week-2.json
oss-radar trend reports/week-1.json reports/week-2.json --output reports/trend.md
```

Use trend reports to:

- validate saved reports before comparing them
- compare saved reports from the same repository
- review changes in open issues, stale issues, review backlog, releases, risks, and scorecard score
- avoid turning trend deltas into adoption or ecosystem-importance claims
