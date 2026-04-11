# DevSecOps CI/CD — Python secrets detection and security scanning

This repository demonstrates a **GitHub Actions** pipeline that runs on every push and pull request to `main` / `master`. It fails the workflow when leaked secrets, high‑severity dependency issues, or critical/high container findings are detected.

## What runs in CI

| Job | Tool | Purpose |
|-----|------|--------|
| **Secrets scan** | [Gitleaks](https://github.com/gitleaks/gitleaks) | Detects API keys, tokens, and other secrets in git history |
| **Python security** | [Bandit](https://github.com/PyCQA/bandit) | Static analysis for common Python security mistakes |
| **Dependencies** | [pip-audit](https://pypi.org/project/pip-audit/) | Reports known vulnerabilities in pinned dependencies |
| **Tests** | pytest | Basic API tests |
| **Filesystem & image** | [Trivy](https://github.com/aquasecurity/trivy) | Scans the repo and the built Docker image for OS/library CVEs (CRITICAL/HIGH, fixed only) |

Workflow file: [`.github/workflows/security-ci.yml`](.github/workflows/security-ci.yml).

The Gitleaks job installs the [official CLI](https://github.com/gitleaks/gitleaks) and scans the full git history. It avoids [`gitleaks/gitleaks-action`](https://github.com/gitleaks/gitleaks-action)’s default push range (`before^..after`), which breaks when the push’s `before` commit is the **root** commit—`before^` does not exist, so Git reports `unknown revision` and the action exits with an error even when no leaks are found.

## Sample application

A minimal [FastAPI](https://fastapi.tiangolo.com/) service under `src/secure_api/` loads configuration with **Pydantic Settings** from the environment (`API_KEY`, etc.). There are **no secrets in source control** — only `.env.example` with empty placeholders.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env       # set API_KEY locally if you want /protected
pytest -q
bandit -r src -c pyproject.toml
pip install pip-audit && pip-audit -r requirements.txt
uvicorn secure_api.main:app --reload --app-dir src
```

## Docker

The image runs `apt-get upgrade` during build so the Debian/OpenSSL layer matches published security fixes (otherwise Trivy can fail on **fixed** HIGH CVEs that are not yet in the slim base tag).

```bash
docker build -t secure-api-demo .
docker run --rm -e API_KEY=dev-secret -p 8000:8000 secure-api-demo
```

## Demonstrating “detect → fix → pass”

1. **Trigger a failure:** Commit a realistic secret pattern (e.g. a fake `AWS_SECRET_ACCESS_KEY=...` in a tracked file). Push a branch and open a PR — **Gitleaks** should fail.
2. **Fix:** Remove the secret, rotate any real credential that was ever exposed, and use **GitHub Actions [encrypted secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)** or your platform’s secret store; load them at runtime as environment variables (as this app does with `API_KEY`).
3. **Verify:** Push again — the pipeline should go green.

## GitHub setup

1. Create a repository on GitHub and push this project.
2. Ensure **Actions** are enabled (repository **Settings → Actions**).
3. Optional: add a repository secret named `API_KEY` if you later add a deploy job that needs it.

## Requirements

- Python **3.11+** (CI uses 3.12)
- Docker (for local image builds; CI uses Docker for Trivy image scan)
