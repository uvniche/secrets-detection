# Secrets Detection & Security Scanning - DevSecOps CI/CD

This repository demonstrates a **GitHub Actions** pipeline that runs on every push and pull request to `main` / `master`. It fails the workflow when leaked secrets, high-severity dependency issues, or critical/high filesystem findings are detected.

## What runs in CI


| Job                 | Tool                                             | Purpose                                                                         |
| ------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| **Secrets scan**    | [Gitleaks](https://github.com/gitleaks/gitleaks) | Detects API keys, tokens, and other secrets in git history                      |
| **Python security** | [Bandit](https://github.com/PyCQA/bandit)        | Static analysis for common Python security mistakes                             |
| **Dependencies**    | [pip-audit](https://pypi.org/project/pip-audit/) | Reports known vulnerabilities in pinned dependencies                            |
| **Tests**           | pytest                                           | Unit tests for local security helpers                                           |
| **Filesystem scan** | [Trivy](https://github.com/aquasecurity/trivy)   | Scans the repository filesystem for OS/library CVEs (CRITICAL/HIGH, fixed only) |


Workflow file: `[.github/workflows/security-ci.yml](.github/workflows/security-ci.yml)`.

The Gitleaks job installs the [official CLI](https://github.com/gitleaks/gitleaks) and scans the full git history. It avoids `[gitleaks/gitleaks-action](https://github.com/gitleaks/gitleaks-action)`’s default push range (`before^..after`), which breaks when the push’s `before` commit is the **root** commit—`before^` does not exist, so Git reports `unknown revision` and the action exits with an error even when no leaks are found.

## Local

Run these macOS commands from the repository root.

### 1) Setup (one-time)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env       # optional local env values for experiments
```

### 2) Local equivalent of CI Job: `gitleaks` (secrets scan)

Purpose: detect committed secrets/tokens in repository history.

```bash
gitleaks detect --source . --redact --verbose --exit-code 2
```

### 3) Local equivalent of CI Job: `python-security`

Purpose: run tests + Python static analysis + dependency audit.

```bash
pytest -q
bandit -r src -c pyproject.toml
pip-audit -r requirements.txt --desc
```

### 4) Local equivalent of CI Job: `trivy` (filesystem CVE scan)

Purpose: scan repo filesystem for CRITICAL/HIGH vulnerabilities.

```bash
trivy fs --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 .
```

### Notes for local runs

- `gitleaks` and `trivy` commands require those CLIs to be installed locally.
- In GitHub Actions, installation/execution is handled by the workflow jobs.

## GitHub Demo

This section demonstrates GitHub Actions detection behavior using a fake secret pattern.  
It is separate from normal local development usage.

1. **Detection setup:** Create and push the `demo-detect` branch with a test file that contains a known fake secret pattern.
2. **CI verification:** Verify that the Gitleaks check fails in GitHub Actions for the demo branch.
3. **Clean-branch validation:** Create a fresh branch from `main` with no demo leak history and verify that checks pass.
4. **Cleanup:** Remove the temporary demo branches after validation is complete.

Demo commands:

```bash
# Detect
git checkout main
git pull
git checkout -b demo-detect
printf "AWS_SECRET_ACCESS_KEY_EXAMPLE=ABCD1234EFGH5678IJKL9012MNOP3456QRST7890\n" > demo-secret.txt
git add demo-secret.txt
git commit -m "demo: add detectable secret pattern"
git push -u origin demo-detect

# Pass from clean branch
git checkout main
git pull
git checkout -b demo-clean-pass
git push -u origin demo-clean-pass

# Cleanup
git checkout main
git branch -D demo-detect demo-clean-pass
git push origin --delete demo-detect demo-clean-pass
```

Always rotate immediately if a real secret is ever exposed, and use **GitHub Actions [encrypted secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)** or your platform secret store for runtime values.

## Requirements

- Python **3.11+** (CI uses 3.12)

