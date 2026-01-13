# Assessment F Results: Deployment

## Executive Summary

*   **GitHub Pages**: Deployment is handled via standard `deploy.yml`, using the `actions/upload-pages-artifact` workflow. This is the gold standard for this stack.
*   **Build Artifacts**: The site builds to a `docs/` (or `_site/`) directory which is then uploaded.
*   **Environment consistency**: The workflow installs Python dependencies and sets up the environment before building.

## Top Risks

1.  **Build Failures (Severity: LOW)**: If `build-html.py` fails, deployment stops (good).
2.  **Environment Drift (Severity: LOW)**: As noted in Hygiene, lack of lockfile could cause build to break if a dep updates.

## Scorecard

| Category             | Score | Evidence                                  | Remediation                     |
| -------------------- | ----- | ----------------------------------------- | ------------------------------- |
| Automation           | 10/10 | Fully automated on push to main.          | N/A                             |
| Reliability          | 9/10  | Standard Actions used.                    | Add Lockfile.                   |
| Speed                | 9/10  | Fast build (mostly text processing).      | N/A                             |
| Rollback             | 8/10  | Git revert + push redeploys old version.  | N/A                             |

**Weighted Score: 9.0/10**

## Refactoring Plan

1.  **Lockfile**: Add `requirements.lock` to `deploy.yml` installation step (`pip install -r requirements.lock`) to ensure the build environment is identical to dev.
