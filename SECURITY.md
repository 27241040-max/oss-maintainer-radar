# Security Policy

## Supported Versions

The project is currently pre-1.0. Security fixes are accepted on `main`.

## Reporting a Vulnerability

Please open a private security advisory on GitHub if the repository is hosted
there. If private advisories are unavailable, contact the maintainer listed in
the repository profile.

## Data Handling

OSS Maintainer Radar reads public GitHub repository data and optional local JSON
fixtures. It does not require secrets. If `GITHUB_TOKEN` is present, it is used
only as an HTTP authorization header for GitHub API rate limits and is never
printed.

