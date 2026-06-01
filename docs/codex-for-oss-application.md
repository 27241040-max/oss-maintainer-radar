# Codex for Open Source Application Checklist

This checklist helps maintainers prepare a truthful application for the Codex
for Open Source program.

For the final publish-and-submit handoff checklist, see
`docs/final-submission-checklist.md`.

## Program Fit

The public program pages say reviewers look for:

- maintainers of active open-source projects
- meaningful usage, broad adoption, or clear ecosystem importance
- evidence of active maintenance such as review, triage, release management, and quality work
- accurate and complete information about the applicant, repository, and role

The terms also say submitting an application does not guarantee selection.
False, misleading, or incomplete information can lead to rejection or revocation.

## Fields To Prepare

Required fields:

- first name
- last name
- email for the ChatGPT account
- public GitHub username
- public GitHub repository URL
- maintainer role: primary or core maintainer
- why the repository qualifies, 500 characters max
- interest: Codex Security and/or API credits
- OpenAI organization ID
- how API credits will be used, 500 characters max

Optional:

- anything else reviewers should know, 500 characters max

## How To Use This Repository

Run:

```bash
oss-radar audit --repo owner/repo --output reports/owner-repo.md
oss-radar application --repo owner/repo --role primary --output reports/application.md
oss-radar form-fields --repo owner/repo --role primary --output reports/form-fields.md
oss-radar codex-prompts --repo owner/repo --output reports/codex-prompts.md
oss-radar readiness --repo owner/repo --role primary --output reports/readiness.md
```

For downloads, dependents, or ecosystem importance that GitHub does not expose,
create a JSON evidence file and pass `--evidence evidence.json`. Only include
claims that have public source URLs.

For private applicant fields, copy `examples/applicant.example.json` to ignored
`applicant.json`, edit it locally, and pass `--applicant applicant.json`.

For live `--repo` audits, the CLI uses direct GitHub API requests first. If
local TLS certificate configuration blocks those requests, it falls back to
`gh api` when the GitHub CLI is installed and authenticated.

Then check every generated claim:

- Do you actually have maintainer permissions?
- Is the repository public?
- Are stars, forks, issues, PRs, releases, and downloads current?
- Do additional evidence claims include source URLs?
- Can you explain why the project matters without exaggerating?
- Are API-credit plans limited to the project you maintain?

## Suggested API Credit Use

Use credits for core maintainer work:

- summarize new issue batches for triage
- prepare PR review briefs with risk and test focus
- draft release notes from merged changes
- produce regression-risk checklists before release
- route security-sensitive reports for careful human review

All generated outputs should be reviewed by maintainers before action.
