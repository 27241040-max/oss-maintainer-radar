# Scheduled Maintainer Workflow

This workflow shows how a maintainer can use OSS Maintainer Radar as a weekly
evidence brief. It uses the same reusable Action that this repository runs in
`.github/workflows/maintainer-radar.yml`.

Generated reports are inputs for human review. They should not be treated as
approval, rejection, release, or application decisions on their own.

## Setup

Add a workflow like this to the repository you maintain:

```yaml
name: Maintainer Radar

on:
  workflow_dispatch:
    inputs:
      target_repo:
        description: Repository to audit, such as owner/repo
        required: false
      stale_days:
        description: Days without updates before work is stale
        required: false
        default: "30"
      since:
        description: Optional ISO release-window start
        required: false
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
      - uses: 27241040-max/oss-maintainer-radar@v0.8.0
        with:
          target_repo: ${{ inputs.target_repo || github.repository }}
          stale_days: ${{ inputs.stale_days || '30' }}
          since: ${{ inputs.since }}
          github_token: ${{ github.token }}
          output_dir: reports
      - uses: actions/upload-artifact@v7
        with:
          name: maintainer-radar-report
          path: reports/
```

The scheduled run gives maintainers a recurring baseline. The manual
`workflow_dispatch` run is useful before releases, after large dependency
updates, or when preparing a focused release-window report with `since`.

## Run And Download

From the GitHub UI:

1. Open **Actions**.
2. Select **Maintainer Radar**.
3. Select **Run workflow**.
4. Leave `target_repo` blank for the current repository, or enter another
   public repository you maintain.
5. Download the `maintainer-radar-report` artifact when the run finishes.

From the GitHub CLI:

```bash
gh workflow run "Maintainer Radar" \
  --repo owner/repo \
  -f target_repo=owner/repo \
  -f stale_days=30 \
  -f since=2026-06-01

gh run list --repo owner/repo --workflow "Maintainer Radar" --limit 3
gh run download RUN_ID --repo owner/repo --name maintainer-radar-report --dir reports/latest
```

The artifact contains:

- `maintainer-radar.md`: human-readable workload and evidence report
- `maintainer-radar.json`: machine-readable report following the schema
- `scorecard.md`: maintenance health scorecard
- `action-plan.md`: prioritized checklist
- `codex-prompts.md`: prompts for maintainer-reviewed Codex sessions

## Save And Compare Artifacts

Keep downloaded JSON reports in dated folders:

```bash
gh run download RUN_ID --repo owner/repo --name maintainer-radar-report --dir reports/2026-06-01
gh run download NEXT_RUN_ID --repo owner/repo --name maintainer-radar-report --dir reports/2026-06-08

oss-radar trend \
  reports/2026-06-01/maintainer-radar-report/maintainer-radar.json \
  reports/2026-06-08/maintainer-radar-report/maintainer-radar.json
```

Use trend reports to compare open issues, stale issues, review backlog, release
count, risk count, and scorecard score. Treat every change as a prompt for
maintainer review, not as an automated project-health prediction.

## Weekly Triage Loop

Use `maintainer-radar.md` first. It is the source brief for the rest of the
workflow.

1. Review **Stale Issues**.
   - If an issue is still reproducible, add the next concrete question or owner.
   - If an issue lacks required information, ask for that information and label
     it clearly.
   - If an issue cannot be reproduced and has gone quiet, close it with a short
     explanation.
2. Review **Pull Requests Awaiting Review**.
   - Assign a reviewer when the PR is actionable.
   - Ask for tests or scope reduction when the report suggests release risk.
   - Defer or close inactive PRs only after a maintainer review.
3. Review **Release Notes**.
   - Copy recent completed PR titles into a changelog draft.
   - Use release-note groups as deterministic buckets for bug fixes, docs,
     dependencies, security-sensitive changes, maintenance, and other changes.
   - Treat normalized labels as grouping hints only; keep original labels in
     maintainer comments and changelog evidence.
   - Check bug-labeled issues before creating a release.
   - Use `--since` to keep release notes tied to the current release window.
4. Review `scorecard.md` and `action-plan.md`.
   - Treat low adoption, missing releases, or weak review surface as risk notes.
   - Convert the action plan into issues only when the work is real and scoped.
5. Use `codex-prompts.md` for assisted review.
   - Paste a prompt into Codex with the relevant issue, PR, or release context.
   - Keep generated summaries as drafts until a maintainer checks them.

## Example Maintainer Decisions

Use a small decision log after each scheduled run:

```text
Run:
Artifact:
Window start:

Stale issues:
- Decision:
- Follow-up issue/comment:

Review backlog:
- Decision:
- Reviewer or next action:

Release notes:
- Completed PRs considered:
- Release-note groups checked:
- Changelog entries needed:

Evidence notes:
- Public metrics checked:
- Claims to avoid:
Trend notes:
- JSON reports compared:
- Changes requiring maintainer review:
```

Example outcomes:

- Stale issues found: ask for reproduction details, add a triage label, or close
  with a clear maintainer note.
- Review backlog found: assign a reviewer, request tests, or split the PR before
  release.
- Recent completed PRs found: draft changelog entries and check whether the next
  release should mention migration, security, or regression risk.
- Low adoption signals found: keep application and README language conservative.

## Evidence Boundaries

Do not turn scheduled reports into adoption claims. A report can show public
repository activity, open work, release history, and maintainer process. It does
not prove downloads, dependents, ecosystem importance, or selection for any
program unless those facts have separate public sources.
