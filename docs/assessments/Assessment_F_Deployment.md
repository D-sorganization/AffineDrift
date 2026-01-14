# Assessment F Results: Installation & Deployment

## Executive Summary

Deployment is handled via GitHub Actions (`deploy-website.yml`), which is standard and reliable. Installation logic relies on `requirements.txt` and `package.json`. The recent failure to run tests locally due to missing `numpy` suggests that the installation instructions or dependency files might need a refresh or strict version pinning is interfering with local environments.

## Top Risks

1.  **Dependency Definition (Severity: HIGH)**: `numpy` is needed for tests but was not present in the environment despite `requirements.txt`.
2.  **CI/Local Parity (Severity: MEDIUM)**: CI installs dependencies successfully, but local replication failed.
3.  **Version Pinning (Severity: MEDIUM)**: `requirements.txt` has loose pinning (`>=`) which is good for libraries but risky for applications (reproducibility).

## Scorecard

| Category               | Score | Evidence                                           | Remediation                               |
| ---------------------- | ----- | -------------------------------------------------- | ----------------------------------------- |
| Install Reliability    | 6/10  | Local install failed to provide `numpy`.           | specific `pip install` check.             |
| CI/CD Pipeline         | 10/10 | GitHub Actions are comprehensive.                  | N/A                                       |
| Deployment Automation  | 10/10 | Fully automated on push to main.                   | N/A                                       |
| Environment Definition | 8/10  | `requirements.txt` and `package.json` present.     | Lock files (poetry.lock) recommended.     |

**Weighted Score: 8.5/10**

## Refactoring Plan

**Quick Wins**
1.  **Verify Requirements**: Ensure `requirements.txt` is complete and formatted correctly (remove large gaps).
2.  **Add Setup Script**: A simple `setup.sh` that runs `pip install -r requirements.txt && npm install` would help.

**Strategic Fixes**
1.  **Dependency Locking**: Switch to `uv` or `poetry` to generate a lock file, ensuring CI and local environments are identical.
