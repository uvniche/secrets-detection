# Secrets detection (Python + GitHub)

Uses [Yelp detect-secrets](https://github.com/Yelp/detect-secrets) locally and in GitHub Actions. New findings compared to `.secrets.baseline` fail CI.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### First-time baseline (or after you intentionally add a non-secret)

```bash
detect-secrets scan --all-files > .secrets.baseline
detect-secrets audit .secrets.baseline   # mark real secrets vs false positives
```

### Scan (CI-equivalent)

```bash
detect-secrets scan --baseline .secrets.baseline
```

### Pre-commit (optional)

```bash
pre-commit install
```

## GitHub

Push this repo and enable Actions. The workflow runs on PRs and on `main`/`master`.

If you add a **real** secret to history, rotate it and use `git filter-repo` or similar—scanning does not undo exposure.
