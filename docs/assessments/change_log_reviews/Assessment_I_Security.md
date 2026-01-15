# Assessment I Results: Security & Input Validation

## Executive Summary

As a static site, the security surface is small. No secrets were found in the codebase. GitHub Actions secrets are used for Codecov, which is standard. Dependencies are the main vector; strict pinning is not fully enforced in `requirements.txt` (using `>=`), leaving a small window for supply chain attacks via updated packages.

## Top Risks

1.  **Dependency Supply Chain (Severity: LOW)**: `requirements.txt` uses `>=`.
2.  **Input Validation (Severity: LOW)**: `build-html.py` processes local files. If a malicious PR added a bad QMD, it could theoretically execute code during render (Quarto executes python chunks).
3.  **XSS (Severity: LOW)**: No user input forms. Content is static.

## Scorecard

| Category               | Score | Evidence                                           | Remediation                               |
| ---------------------- | ----- | -------------------------------------------------- | ----------------------------------------- |
| Secrets Management     | 10/10 | No secrets in repo.                                | N/A                                       |
| Dependency Security    | 8/10  | Standard pip usage.                                | Use hash-checking in requirements.        |
| Content Security       | 9/10  | Static content.                                    | N/A                                       |
| CI Security            | 10/10 | Standard Actions.                                  | N/A                                       |

**Weighted Score: 9.2/10**

## Refactoring Plan

**Quick Wins**
1.  **Pin Dependencies**: Convert `requirements.txt` to use exact versions `==` for stability and security.

**Strategic Fixes**
1.  **Dependabot**: Enable Dependabot to keep pinned versions up to date automatically.
