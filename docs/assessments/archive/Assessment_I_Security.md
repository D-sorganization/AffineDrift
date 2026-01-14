# Assessment I Results: Security

## Executive Summary

*   **Static Site Profile**: As a static site, the attack surface is minimal (no backend DB, no user auth).
*   **Dependency Risks**: The primary risk is compromised dependencies in the build chain or frontend assets.
*   **Secrets**: No secrets found in repo.

## Top Risks

1.  **Supply Chain (Severity: LOW)**: Unpinned dependencies in `requirements.txt`.
2.  **XSS (Severity: LOW)**: `script.js` manipulates DOM. If content source (`.qmd`) is compromised or allows raw HTML injection (via PRs), XSS is possible. But contributors are trusted.

## Scorecard

| Category             | Score | Evidence                                  | Remediation                     |
| -------------------- | ----- | ----------------------------------------- | ------------------------------- |
| Secrets Management   | 10/10 | None found.                               | N/A                             |
| Dep Vulnerabilities  | 8/10  | No lockfile to audit easily.              | Add lockfile + Dependabot.      |
| Input Validation     | 9/10  | Static content.                           | N/A                             |
| HTTPS/Headers        | 9/10  | GitHub Pages enforces HTTPS.              | N/A                             |

**Weighted Score: 9.0/10**

## Refactoring Plan

1.  **Dependabot**: Enable Dependabot for `pip` and `npm` (if `package.json` exists for dev tools) to catch vulnerabilities.
2.  **CSP**: Consider adding a Content Security Policy meta tag to `_quarto.yml` or the HTML template to restrict script sources.
