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

## Sample code

The sample Python package under `src/secure_api/` contains simple security-focused helpers (for example, secret redaction). It is intentionally minimal so the focus stays on CI security gates.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env       # optional local env values for experiments
pytest -q
bandit -r src -c pyproject.toml
pip install pip-audit && pip-audit -r requirements.txt
```

## Demonstrating “detect → fix → remediate”

Because this workflow scans **full git history**, a committed secret pattern can keep failing later runs on that same branch even after deletion.

Use this exact flow (matches how this repo is being demonstrated):

1. **Detect:** Create and push a branch named `demo-detect` with a demo file containing a detectable fake secret pattern.
2. **Show detection:** Confirm the Gitleaks job fails in Actions.
3. **Fix:** Delete the demo file and commit the removal.
4. **Important behavior:** The `demo-detect` PR will still fail because full-history scanning still includes the earlier leaked commit.
5. **Pass (operational remediation):** Open a clean branch from `main` (without leaked commit history) and show checks passing there.
6. **Cleanup:** Delete demo branches after presentation.

Live demo commands:

```bash
# Detect
git checkout main
git pull
git checkout -b demo-detect
printf "AWS_SECRET_ACCESS_KEY_EXAMPLE=ABCD1234EFGH5678IJKL9012MNOP3456QRST7890\n" > demo-secret.txt
git add demo-secret.txt
git commit -m "demo: add detectable secret pattern"
git push -u origin demo-detect

# Fix on same branch
rm demo-secret.txt
git add -u
git commit -m "demo: remove fake secret"
git push

# Note: this branch will still fail due to full-history scanning.

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

### If you must make the same branch pass

Yes, rewriting history can fix this case, because it removes the leaked commit itself from the branch history scanned by Gitleaks.

```bash
# Remove demo file from all history (example)
git filter-repo --path demo-secret.txt --invert-paths
git push --force --all
git push --force --tags
```

Notes:
- Use history rewrite only when you really need to preserve that same branch/PR path.
- Teammates must re-sync (re-clone or reset) after force-pushed history.
- If any real secret was exposed, rotate/revoke it immediately.

Always rotate immediately if a real secret is ever exposed, and use **GitHub Actions [encrypted secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)** or your platform secret store for runtime values.

## GitHub setup

1. Create a repository on GitHub and push this project.
2. Ensure **Actions** are enabled (repository **Settings → Actions**).
3. Optional: add repository secrets if you later add deploy/runtime jobs that require them.

## Requirements

- Python **3.11+** (CI uses 3.12)

