# GitHub Action Usage

OSS Maintainer Radar can run as a reusable GitHub Action in any public
repository that wants scheduled maintainer reports.

## Example

```yaml
name: Maintainer Radar

on:
  workflow_dispatch:
  schedule:
    - cron: "17 8 * * 1"

permissions:
  contents: read

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - uses: 27241040-max/oss-maintainer-radar@v0.3.0
        with:
          github_token: ${{ github.token }}
          output_dir: reports
      - uses: actions/upload-artifact@v7
        with:
          name: maintainer-radar-report
          path: reports/
```

The action writes:

- `reports/maintainer-radar.md`
- `reports/scorecard.md`
- `reports/action-plan.md`
- `reports/codex-prompts.md`

## Inputs

- `target_repo`: repository to audit, such as `owner/repo`; defaults to the current repository.
- `stale_days`: days without updates before an issue is considered stale; defaults to `30`.
- `output_dir`: directory for generated files; defaults to `reports`.
- `github_token`: optional token for GitHub API rate limits.

## Maintainer Review

Generated reports are evidence briefs, not automated decisions. Maintainers
should review issue triage, PR review notes, release notes, and application
claims before acting on them.
