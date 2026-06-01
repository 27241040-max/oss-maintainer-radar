# Codex for Open Source Submission Pack

Use this page after the project is published as a public GitHub repository.

## Required User-Specific Values

- First name:
- Last name:
- ChatGPT account email:
- GitHub username:
- Public repository URL:
- Maintainer role: primary maintainer or core maintainer
- OpenAI organization ID:
- Interest: Codex Security, API credits, or both

## Repository Evidence To Collect

Run:

```bash
oss-radar audit --repo owner/repo --output reports/application-evidence.md
oss-radar application --repo owner/repo --role primary --output reports/application-draft.md
oss-radar submission-pack --repo owner/repo --role primary --output reports/submission-pack.md
oss-radar readiness --repo owner/repo --role primary --output reports/readiness.md
```

If you have verified evidence outside GitHub stars and forks, create an evidence
file:

```json
{
  "monthly_downloads": 5200,
  "dependents": 18,
  "ecosystem_importance": "Used by maintainers to prepare issue triage and release readiness notes.",
  "maintainer_responsibilities": ["Review pull requests", "Triage issues"],
  "usage_notes": ["Replace sample values with current public metrics."],
  "source_urls": ["https://github.com/owner/repo"]
}
```

Then pass it to the commands:

```bash
oss-radar submission-pack --repo owner/repo --evidence evidence.json --role primary --output reports/submission-pack.md
oss-radar readiness --repo owner/repo --evidence evidence.json --role primary --output reports/readiness.md
```

Then confirm:

- the repository is public
- your GitHub profile is public
- stars, forks, issues, pull requests, releases, and downloads are current
- additional evidence includes public source URLs
- your maintainer role is true and verifiable
- your API-credit plan is limited to repositories you own or are authorized to maintain

## Draft: Why This Repository Qualifies

Replace this with the output from `reports/application-draft.md`, then edit it
so every claim is accurate.

## Draft: How API Credits Will Be Used

Use credits for maintainer automation: summarize new issues, prepare PR review
briefs, draft release notes from merged changes, route security-sensitive
reports, and generate regression-risk checklists before releases. Maintainers
will review outputs before taking action.

## Final Honesty Check

Do not submit claims about broad adoption, downloads, maintainership, security
need, or ecosystem importance unless you can verify them from public evidence
or your actual repository permissions.
