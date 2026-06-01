# Trend JSON Dashboard Example

`oss-radar trend --format json` is meant for small dashboards and maintainer
review tools that should not parse Markdown or CSV.

Always validate trend JSON before ingestion:

```bash
oss-radar trend \
  reports/week-1/maintainer-radar.json \
  reports/week-2/maintainer-radar.json \
  --format json \
  --output reports/trend-summary.json

oss-radar validate-report reports/trend-summary.json --schema trend
```

After validation, the dependency-free example script can print metric rows and
warnings:

```bash
python examples/trend_dashboard.py reports/trend-summary.json
```

Example output:

```text
Maintainer Trend Dashboard: owner/repo
Reports compared: 2

Warnings:
- none

Metrics:
Metric | First | Latest | Delta | Direction
--- | ---: | ---: | ---: | ---
Open issues | 8 | 4 | -4 | improved
Release count | 1 | 2 | +1 | improved

Review boundaries:
- Treat increases or decreases as prompts for maintainer review, not automated decisions.
```

The dashboard output is a review aid. It should help maintainers notice changes
in issue load, review backlog, releases, risk count, and scorecard score. It is
not an automated project-health score, adoption claim, or selection decision.
