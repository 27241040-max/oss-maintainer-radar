# Changelog

All notable changes to OSS Maintainer Radar are documented here.

## 0.13.0 - 2026-06-01

- Added `schemas/trend-report.schema.json` for `oss-radar trend --format json` output.
- Added named schema validation with `oss-radar validate-report trend.json --schema trend`.
- Added schema coverage for trend warnings, metric rows, integer deltas, and direction values.
- Included the trend schema in source distributions and wheels.
- Documented trend JSON validation before dashboard ingestion.

## 0.12.0 - 2026-06-01

- Added `oss-radar trend --format json` for dashboard-friendly trend output.
- Included compared report paths, warnings, metrics, deltas, directions, and review boundaries in trend JSON.
- Added JSON trend tests for matching inputs and repository/schema warning inputs.
- Documented saving JSON trend summaries next to workflow artifacts.

## 0.11.0 - 2026-06-01

- Added trend comparison warnings for reports from different repositories.
- Added trend comparison warnings for mixed `schema_version` values.
- Added a `warnings` column to CSV trend output.
- Documented that trend warnings are maintainer review prompts, not automated rejection.

## 0.10.0 - 2026-06-01

- Added CSV output for `oss-radar trend` with `--format csv`.
- Included repository, first snapshot, latest snapshot, metric name, values, delta, and direction in trend CSV rows.
- Added improving and worsening CSV trend tests.
- Documented saving CSV trend summaries next to downloaded workflow artifacts.

## 0.9.0 - 2026-06-01

- Added a `validate-report` command for checking generated JSON reports against `schemas/maintainer-report.schema.json`.
- Promoted the dependency-free JSON Schema subset validator from tests into reusable CLI code.
- Added pass/fail validation summaries for local report files.
- Documented validating downloaded workflow artifacts before using trend reports.

## 0.8.0 - 2026-06-01

- Added a `trend` command for comparing two or more saved JSON reports.
- Added `release_count` to maintainer reports and updated the report schema to `schema_version` 1.2.
- Added improving and worsening trend tests for open issues, stale issues, review backlog, releases, risk count, and scorecard score.
- Documented how scheduled workflow artifacts can be saved and compared over time.

## 0.7.0 - 2026-06-01

- Added deterministic label normalization for common maintainer labels before release-note grouping.
- Recognized aliases such as `type: bug`, `area/docs`, `security-review`, `dependencies`, and `chore`.
- Kept original labels unchanged in Markdown and JSON report output.
- Added tests for normalized label aliases and bug-labeled release readiness notes.

## 0.6.0 - 2026-06-01

- Added deterministic release-note grouping for completed pull requests using labels and titles only.
- Added `release_note_groups` to Markdown and JSON reports.
- Updated the report schema to `schema_version` 1.1.
- Added tests and workflow documentation for grouped release notes.

## 0.5.1 - 2026-06-01

- Added an optional `gh api` fallback when direct GitHub API requests fail because of local TLS or network transport issues.
- Added coverage for the GitHub CLI fallback path.
- Documented the fallback behavior for maintainers running live repository audits.

## 0.5.0 - 2026-06-01

- Added `--since` release-window filtering for issue, pull request, and release evidence.
- Added release-window support to the reusable GitHub Action.
- Added release-window metadata to Markdown and JSON reports.
- Added tests for populated and empty release windows.

## 0.4.0 - 2026-06-01

- Added a JSON Schema for machine-readable maintainer reports.
- Added scorecard data to JSON report output.
- Added machine-readable JSON report generation to the reusable GitHub Action.
- Documented the schema for downstream automation users.

## 0.3.0 - 2026-06-01

- Added a reusable composite GitHub Action for scheduled maintainer reports.
- Updated the bundled Maintainer Radar workflow to exercise the local action.
- Added GitHub Action usage documentation for downstream repositories.

## 0.2.1 - 2026-06-01

- Updated GitHub Actions workflow dependencies.
- Counted all sampled pull requests, not only currently open pull requests, in readiness and scorecard evidence.
- Added completed pull request follow-up guidance to action plans.

## 0.2.0 - 2026-06-01

- Added maintenance health scorecards for public repository checks.
- Added prioritized maintainer action plans for hygiene, weekly work, and evidence tracking.
- Added scorecard and action-plan sections to combined submission packs.
- Refocused README and maintainer workflow docs on the project as a general OSS maintenance tool.
- Included latest release evidence in conservative form-field drafts when available.

## 0.1.0 - 2026-06-01

- Added a dependency-free Python CLI for GitHub maintainer reports.
- Added Markdown and JSON report output.
- Added conservative Codex for Open Source application drafts.
- Added Codex prompt generation for triage, PR review, and release readiness.
- Added combined submission-pack generation for application prep.
- Added copy-paste form-field output with character counts.
- Added readiness self-checks for public evidence, maintenance surface, and application risks.
- Added optional JSON evidence files for downloads, dependents, ecosystem importance, and source URLs.
- Added package build documentation and CI package-build verification.
- Added a local verification script for tests, CLI smoke checks, sdist inspection, and wheel installation.
- Added a final submission checklist for public repo publishing and private form fields.
- Added local applicant profile JSON support for prefilled private form fields without committing personal data.
- Added tests, documentation, issue templates, CI, and maintainer automation workflow.
