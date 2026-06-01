# Contributing

Thanks for helping improve OSS Maintainer Radar.

## Principles

- Prefer evidence from public repository data.
- Do not add features that encourage inflated adoption or maintainer claims.
- Keep the CLI usable without mandatory third-party services.
- Add tests for analyzer, renderer, and CLI behavior.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests
```

## Pull Requests

Please include:

- a short description of the maintainer problem being solved
- tests or fixture updates for behavior changes
- before/after output examples for renderer changes
