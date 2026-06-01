# Roadmap

OSS Maintainer Radar should stay useful to maintainers without encouraging
inflated claims.

## Shipped

- Dependency-free CLI reports, scorecards, action plans, readiness checks, and
  Codex prompt packs.
- Conservative Codex for Open Source form-field drafts with character counts.
- Reusable GitHub Action with scheduled report artifacts.
- JSON Schema for machine-readable report output.
- Release-window filtering with `--since`.
- Live repository audit fallback through `gh api` when local TLS transport
  fails.
- Scheduled maintainer workflow documentation for weekly triage and release
  preparation.
- Trend reports across saved snapshots, including Markdown, CSV, and JSON.
- Schema validation for maintainer report JSON and trend JSON outputs.
- Dependency-free trend JSON dashboard example for integration review.

## Near Term

- Add an optional trend JSON schema compatibility note for future schema
  versions.
- Add a small regression-risk prompt template for release reviews.

## Later

- Add an optional OpenAI-powered summarizer that consumes the deterministic
  report and produces maintainer-reviewed drafts.
- Add GitHub App packaging for teams that want deeper scheduled triage.

## Non-Goals

- Fabricating adoption or ecosystem importance claims.
- Taking automated maintainer actions without human review.
- Requiring secrets for basic local reporting.
