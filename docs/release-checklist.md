# Release Checklist

Use this checklist when preparing OSS Maintainer Radar releases.

## Before Release

- Run `python -m unittest discover -s tests`.
- Run `python scripts/verify.py`.
- Run `python -m build`.
- Run `oss-radar audit --fixture examples/sample_github_payload.json`.
- Review generated application text and confirm 500-character fields still fit.
- Update `CHANGELOG.md`.
- Confirm README examples still match the CLI.

## GitHub Release

- Tag the release, for example `v0.1.0`.
- Include the changelog summary.
- Link to maintainer workflow documentation.
- Note that generated application drafts must be edited for the applicant's real repository and role.

## After Release

- Run the Maintainer Radar GitHub Action against the public repository.
- Open issues for any follow-up improvements found during release review.
