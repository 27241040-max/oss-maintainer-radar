# OSS Maintainer Radar

OSS Maintainer Radar is a small, dependency-free CLI for open-source maintainers
who need an evidence-based view of repository health before triage, review, and
release work.

It reads GitHub repository data from a public repo or a saved JSON snapshot,
then produces:

- a maintainer workload report
- stale issue and pull request signals
- release-readiness notes
- a truthful Codex for Open Source application draft with 500-character fields
- Codex task prompts maintainers can paste into their normal review workflow

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

Generate an application draft:

```bash
oss-radar application --fixture examples/sample_github_payload.json --role primary
```

Generate Codex prompts for maintainer workflows:

```bash
oss-radar codex-prompts --fixture examples/sample_github_payload.json
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

If you have a `GITHUB_TOKEN`, the CLI will use it for higher rate limits. The
token is never printed.

## Output Formats

Markdown is the default:

```bash
oss-radar audit --fixture examples/sample_github_payload.json --format markdown
```

JSON is available for automation:

```bash
oss-radar audit --fixture examples/sample_github_payload.json --format json
```

## Codex for Open Source Notes

The Codex for Open Source program is for maintainers of active public
open-source projects. A brand-new repository may be useful, but it may not show
the usage or ecosystem importance reviewers look for yet.

Use this tool to prepare an accurate application:

1. Run `oss-radar audit` on the repository you actually maintain.
2. Check whether the evidence supports your claims.
3. Edit the generated text so every statement is true.
4. Submit only public repositories and roles you can verify.

For one combined file, run `oss-radar submission-pack --repo owner/repo --role primary`.
For copy-paste fields, run `oss-radar form-fields --repo owner/repo --role primary`.
For a risk-oriented self-check, run `oss-radar readiness --repo owner/repo --role primary`.
If you have verified downloads, dependents, or ecosystem-importance evidence, put it in a JSON file shaped like `examples/evidence.json` and pass `--evidence path/to/evidence.json`.

See [docs/codex-for-oss-application.md](docs/codex-for-oss-application.md) for
a field-by-field checklist.

See [docs/submission-pack.md](docs/submission-pack.md) for a submission prep
template and [docs/github-actions.md](docs/github-actions.md) for a scheduled
maintainer automation example.
See [docs/package-release.md](docs/package-release.md) for package build checks.

## Maintainer Automation Ideas

OSS Maintainer Radar is designed to support workflows where API credits could
help with:

- issue triage summaries
- pull request review briefs
- release-note drafting
- regression-risk checklists
- security-review routing

The current CLI keeps these workflows deterministic and local. The generated
Codex prompts make it easy to add AI assistance without hiding the evidence.

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
