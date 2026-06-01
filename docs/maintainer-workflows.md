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
- review recent completed PRs for changelog entries
- keep release notes separate from unverifiable marketing claims

