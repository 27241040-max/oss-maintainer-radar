# Package Release Notes

OSS Maintainer Radar can be built as a standard Python source distribution and
wheel. Publishing to a package registry is optional; the GitHub repository is
enough for normal open-source collaboration.

## Build Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m build
```

For the full maintainer check, including tests, CLI smoke tests, source
distribution inspection, wheel installation, and entry-point verification:

```bash
python scripts/verify.py
```

Expected artifacts:

- `dist/oss_maintainer_radar-0.13.0.tar.gz`
- `dist/oss_maintainer_radar-0.13.0-py3-none-any.whl`

The source distribution includes docs, examples, schemas, tests, and project
policy files through `MANIFEST.in`.
It also includes `examples/applicant.example.json` as a safe template; real
`applicant.json` files are intentionally ignored by Git.

## Verify The Wheel

```bash
python3 -m venv /tmp/oss-radar-wheel-check
/tmp/oss-radar-wheel-check/bin/python -m pip install dist/oss_maintainer_radar-0.13.0-py3-none-any.whl
/tmp/oss-radar-wheel-check/bin/oss-radar --help
```

## Before Publishing

- Confirm the public GitHub repository URL is real.
- Update `pyproject.toml` project URLs after the repository exists.
- Run `python -m unittest discover -s tests`.
- Run `python -m build`.
- Run `oss-radar readiness --repo owner/repo --role primary`.
