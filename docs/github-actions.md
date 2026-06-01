# GitHub Actions Automation

The repository includes `.github/workflows/maintainer-radar.yml` as an example
maintainer automation workflow. It uses the reusable action defined in
`action.yml`, so the project continuously exercises the same interface that
other repositories can use.

It can:

- run every Monday
- run manually with a `target_repo` input
- generate a maintainer report
- generate a machine-readable JSON report
- generate deterministic release-note groups from completed PR labels and titles
- normalize common label aliases for grouping while preserving original labels
- generate a scorecard and action plan
- generate Codex prompts for triage, review, and release readiness
- upload the generated files as a workflow artifact
- provide JSON artifacts that can be validated with `oss-radar validate-report`
- provide JSON artifacts that can be compared later with `oss-radar trend`
- provide CSV trend rows for spreadsheet or dashboard review
- provide JSON trend rows for dashboard integrations
- warn when trend inputs mix repositories or schema versions

The workflow uses `GITHUB_TOKEN` only for GitHub API rate limits. It does not
print the token or commit generated reports back to the repository.

See [action-usage.md](action-usage.md) for the reusable Action interface,
[scheduled-maintainer-workflow.md](scheduled-maintainer-workflow.md) for an
end-to-end maintainer loop, and
[../schemas/maintainer-report.schema.json](../schemas/maintainer-report.schema.json)
for the JSON report schema.

## Manual Run

In GitHub:

1. Open the repository Actions tab.
2. Choose **Maintainer Radar**.
3. Click **Run workflow**.
4. Set `target_repo` to `owner/repo`, or leave it blank to audit the current repository.
5. Download the `maintainer-radar-report` artifact after the run finishes.

## API Credit Fit

This workflow demonstrates the type of maintainer automation the Codex for Open
Source program describes: triage support, review preparation, release workflow
support, and core OSS maintenance. If you apply for API credits, explain how
credits would enhance these workflows while keeping maintainer review in the
loop.
