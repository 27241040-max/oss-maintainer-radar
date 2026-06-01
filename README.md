# OSS Maintainer Radar

OSS Maintainer Radar is a small, dependency-free CLI for open-source maintainers
who need an evidence-based view of repository health before triage, review, and
release work.

It reads GitHub repository data from a public repo or a saved JSON snapshot,
then produces:

- a maintainer workload report
- a maintenance health scorecard
- a prioritized maintainer action plan
- stale issue and pull request signals
- release-readiness notes
- deterministic release-note groups from completed pull request labels and titles
- normalized common maintainer labels while preserving original label text
- local JSON report validation against the published report schema
- Markdown and CSV trend summaries across saved reports
- Codex task prompts maintainers can paste into their normal review workflow
- optional Codex for Open Source form-field drafts for projects that already
  have truthful public evidence

The project intentionally avoids fabricating adoption claims. If a repository
does not yet have meaningful usage, the report says so.

## Why This Exists

Maintainers often spend more time collecting context than acting on it. This
tool turns public repository signals into a concise working brief so maintainers
can focus Codex, reviewers, and contributors on the next useful action.

## Install

From a checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

No runtime dependencies are required.

## Quick Start

Run against the included fixture:

```bash
oss-radar audit --fixture examples/sample_github_payload.json
```

Generate a maintenance scorecard:

```bash
oss-radar scorecard --fixture examples/sample_github_payload.json
```

Generate a prioritized action plan:

```bash
oss-radar action-plan --fixture examples/sample_github_payload.json
```

Generate Codex prompts for maintainer workflows:

```bash
oss-radar codex-prompts --fixture examples/sample_github_payload.json
```

Compare saved JSON reports over time:

```bash
oss-radar audit --repo owner/repo --format json --output reports/week-1.json
oss-radar audit --repo owner/repo --format json --output reports/week-2.json
oss-radar validate-report reports/week-1.json reports/week-2.json
oss-radar trend reports/week-1.json reports/week-2.json
oss-radar trend reports/week-1.json reports/week-2.json --format csv --output reports/trend.csv
```

Create a combined submission pack:

```bash
oss-radar submission-pack --fixture examples/sample_github_payload.json --role primary --output reports/submission-pack.md
```

Generate copy-paste form fields with character counts:

```bash
oss-radar form-fields --fixture examples/sample_github_payload.json --role primary
```

Add manually verified evidence such as downloads, dependents, or ecosystem notes:

```bash
oss-radar submission-pack \
  --fixture examples/sample_github_payload.json \
  --evidence examples/evidence.json \
  --role primary \
  --output reports/submission-pack.md
```

Fill private form fields from a local file that should not be committed:

```bash
cp examples/applicant.example.json applicant.json
oss-radar form-fields \
  --fixture examples/sample_github_payload.json \
  --applicant applicant.json \
  --role primary
```

Run a conservative readiness self-check:

```bash
oss-radar readiness --fixture examples/new_project_payload.json --role primary
```

Check how the tool treats a brand-new project with little public evidence:

```bash
oss-radar audit --fixture examples/new_project_payload.json
```

Fetch a public GitHub repository and audit it:

```bash
oss-radar audit --repo psf/requests
```

If direct Python GitHub API requests fail because of local TLS certificate
configuration, the CLI automatically tries `gh api` when the GitHub CLI is
installed and authenticated.

Limit a report to a release window:

```bash
oss-radar scorecard --repo psf/requests --since 2026-05-01
```

If you have a `GITHUB_TOKEN`, the CLI will use it for higher rate limits. The
token is never printed.

## GitHub Action

Use OSS Maintainer Radar directly in another repository:

```yaml
- uses: 27241040-max/oss-maintainer-radar@v0.10.0
  with:
    github_token: ${{ github.token }}
    output_dir: reports
```

See [docs/action-usage.md](docs/action-usage.md) for a complete scheduled
workflow example.

## Output Formats

Markdown is the default:

```bash
oss-radar audit --fixture examples/sample_github_payload.json --format markdown
```

JSON is available for automation:

```bash
oss-radar audit --fixture examples/sample_github_payload.json --format json
```

Validate saved JSON before trend analysis or downstream automation:

```bash
oss-radar validate-report reports/maintainer-radar.json
```

## Codex for Open Source Notes

The Codex for Open Source program is for maintainers of active public
open-source projects. A brand-new repository may be useful, but it may not show
the usage or ecosystem importance reviewers look for yet.

This project is a maintainer operations tool first. Its application helpers are
only an appendix for accurate form filling:

1. Run `oss-radar audit` on the repository you actually maintain.
2. Check whether the evidence supports your claims.
3. Edit the generated text so every statement is true.
4. Submit only public repositories and roles you can verify.

For one combined file, run `oss-radar submission-pack --repo owner/repo --role primary`.
For copy-paste fields, run `oss-radar form-fields --repo owner/repo --role primary`.
For a risk-oriented self-check, run `oss-radar readiness --repo owner/repo --role primary`.
If you have verified downloads, dependents, or ecosystem-importance evidence, put it in a JSON file shaped like `examples/evidence.json` and pass `--evidence path/to/evidence.json`.
If you want to prefill private form fields locally, copy `examples/applicant.example.json` to ignored `applicant.json` and pass `--applicant applicant.json`.

See [docs/codex-for-oss-application.md](docs/codex-for-oss-application.md) for
a field-by-field checklist.

See [docs/submission-pack.md](docs/submission-pack.md) for a submission prep
template and [docs/github-actions.md](docs/github-actions.md) for a scheduled
maintainer automation example.
See [docs/action-usage.md](docs/action-usage.md) for reusable GitHub Action
setup.
See [docs/scheduled-maintainer-workflow.md](docs/scheduled-maintainer-workflow.md)
for an end-to-end weekly workflow using scheduled report artifacts.
See [schemas/maintainer-report.schema.json](schemas/maintainer-report.schema.json)
for the machine-readable report schema. The current schema version is `1.2`.
See [docs/package-release.md](docs/package-release.md) for package build checks.
See [docs/examples/self-scorecard.md](docs/examples/self-scorecard.md) and
[docs/examples/self-action-plan.md](docs/examples/self-action-plan.md) for
reports generated from this repository itself.
See [docs/final-submission-checklist.md](docs/final-submission-checklist.md)
for the last-mile publish and form-filling checklist.

## Maintainer Automation Ideas

OSS Maintainer Radar is designed to support workflows where API credits could
help with:

- issue triage summaries
- pull request review briefs
- release-note drafting
- deterministic release-note grouping
- trend reports across saved JSON snapshots
- CSV summaries for spreadsheet or dashboard review
- schema validation for downloaded workflow artifacts
- regression-risk checklists
- security-review routing

The current CLI and Action keep these workflows deterministic. Release-window
filtering, normalized label grouping, and generated Codex prompts make it easy
to add AI assistance without hiding the evidence.

## Development

Run tests:

```bash
python -m unittest discover -s tests
```

Run the full local verification suite:

```bash
python scripts/verify.py
```

Build distribution artifacts:

```bash
python -m pip install -e ".[dev]"
python -m build
```

Run the CLI without installing:

```bash
PYTHONPATH=src python3 -m oss_maintainer_radar.cli audit --fixture examples/sample_github_payload.json
```

## Contributing

Contributions are welcome. Please start with
[CONTRIBUTING.md](CONTRIBUTING.md) and keep outputs evidence-based.

## License

MIT
