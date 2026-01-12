# Assessment F Results: Installation & Deployment

## Executive Summary

*   **Deployment Automation**: Excellent. `deploy.yml` handles GitHub Pages deployment automatically on push to `main`.
*   **Environment Reproducibility**: Weakness detected. `requirements.txt` exists but lacks version pinning (lockfile), meaning builds could break if dependencies update.
*   **Local Setup**: Straightforward (`pip install`, `quarto preview`), but relies on user having Python/Quarto installed. No Dockerfile provided for a hermetic environment.

## Scorecard

| Category              | Score | Evidence                                           | Remediation                     |
| --------------------- | ----- | -------------------------------------------------- | ------------------------------- |
| Automation            | 10/10 | Fully automated GH Pages deploy.                   | Keep it up.                     |
| Reproducibility       | 5/10  | No `requirements.lock`.                            | Add lockfile.                   |
| Containerization      | 0/10  | No Dockerfile.                                     | Add DevContainer/Dockerfile.    |
| Documentation         | 8/10  | Deployment is well-documented in guides.           | N/A                             |
| **Overall Score**     | **5.8/10** | **Strong Cloud Deploy, Weak Local Repro.**   |                                 |

## Top Risks

1.  **Dependency Drift (Severity: MAJOR)**: Without a lockfile, a new version of `pandas` or `numpy` could break the build or tools unexpectedly.
2.  **Environment Mismatch (Severity: MEDIUM)**: Developers on different OSs might face issues (Quarto version differences).

## Remediation

**48 Hours**
1.  **Generate Lockfile**: `pip-compile requirements.txt`.

**2 Weeks**
1.  **Add DevContainer**: VS Code `.devcontainer` configuration for instant onboarding.
