# Changelog

All notable changes to OSS Maintainer Radar are documented here.

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
