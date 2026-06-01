# Final Codex for Open Source Submission Checklist

Use this page after the repository is public. It separates what this project can
generate from the private or account-specific values that only the applicant
can provide.

## Publish The Repository

Required before generating final evidence:

- publish this repository as public
- keep the GitHub profile public
- confirm the public repository URL
- wait for GitHub Actions to run at least once
- run the Maintainer Radar workflow manually if you want a public artifact

Suggested repository:

```text
https://github.com/27241040-max/oss-maintainer-radar
```

## Generate Final Files

After publishing:

```bash
python scripts/verify.py
oss-radar readiness --repo 27241040-max/oss-maintainer-radar --role primary --output reports/readiness.md
oss-radar form-fields --repo 27241040-max/oss-maintainer-radar --role primary --output reports/form-fields.md
oss-radar submission-pack --repo 27241040-max/oss-maintainer-radar --role primary --output reports/submission-pack.md
```

To prefill private applicant fields locally:

```bash
cp examples/applicant.example.json applicant.json
```

Edit `applicant.json`, then pass it to form-field and submission-pack commands:

```bash
oss-radar form-fields --repo 27241040-max/oss-maintainer-radar --applicant applicant.json --role primary --output reports/form-fields.md
oss-radar submission-pack --repo 27241040-max/oss-maintainer-radar --applicant applicant.json --role primary --output reports/submission-pack.md
```

`applicant.json` is ignored by Git.

If you have verified public evidence such as downloads or dependents:

```bash
oss-radar readiness --repo 27241040-max/oss-maintainer-radar --evidence evidence.json --role primary --output reports/readiness.md
oss-radar form-fields --repo 27241040-max/oss-maintainer-radar --evidence evidence.json --applicant applicant.json --role primary --output reports/form-fields.md
oss-radar submission-pack --repo 27241040-max/oss-maintainer-radar --evidence evidence.json --applicant applicant.json --role primary --output reports/submission-pack.md
```

Only use `--evidence` after replacing sample values with truthful values and
public source URLs.

## Form Fields You Must Provide

The tool cannot know these values:

- first name
- last name
- email associated with the ChatGPT account
- public GitHub username
- OpenAI organization ID
- whether you want Codex Security, API credits, or both

## Fields The Tool Can Draft

Use `reports/form-fields.md` for:

- public GitHub repository URL
- maintainer role wording
- why the repository qualifies, 500 characters max
- how API credits will be used, 500 characters max
- optional anything-else field, 500 characters max

## Honesty Review

Before submitting:

- every claim about stars, forks, downloads, dependents, or ecosystem importance has a public source
- the repository is actually public
- the GitHub profile is public
- the selected maintainer role is true
- `reports/readiness.md` has no unexpected REVIEW item
- API credits are described for maintainer automation, release workflows, pull request review, or other core OSS work
- no generated text claims selection is guaranteed

## Known Limitation

A newly created repository may not yet show meaningful usage, broad adoption, or
active maintenance evidence. In that case, use this project as a real OSS
starting point, but consider applying with an existing active project you already
maintain if you have one.
