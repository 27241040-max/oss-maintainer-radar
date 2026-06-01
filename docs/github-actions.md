# GitHub Actions Automation

The repository includes `.github/workflows/maintainer-radar.yml` as an example
maintainer automation workflow.

It can:

- run every Monday
- run manually with a `target_repo` input
- generate a maintainer report
- generate Codex prompts for triage, review, and release readiness
- upload the generated files as a workflow artifact

The workflow uses `GITHUB_TOKEN` only for GitHub API rate limits. It does not
print the token or commit generated reports back to the repository.

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

