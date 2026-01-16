# Assessment I Results: Security & Input Validation

## Executive Summary

- **Dependencies**: `requirements.txt` is used. No `pip-audit` in CI (based on workflow names).
- **Secrets**: No secrets found in code.
- **Input Validation**: `build-html.py` uses `html.escape` for title/description, which is good XSS prevention.
- **Unsafe Parsing**: `pickle` is not used. `yaml.safe_load` (implied via PyYAML usage) should be checked, but PyYAML's `load` is unsafe. `requirements.txt` has `PyYAML`. `build-html.py` uses regex, not yaml parser.

## Top Security Risks

1.  **Dependency Scanning (Severity: MEDIUM)**: No automated dependency scanning in CI.
2.  **Loose Dependencies (Severity: LOW)**: Supply chain risk.

## Scorecard

| Category                   | Score | Evidence                                                                 | Remediation                               |
| -------------------------- | ----- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Dependency Vulnerabilities | 8/10  | None obvious, but no auto-check.                                         | Add `pip-audit`.                          |
| Input Validation           | 9/10  | `html.escape` used.                                                      | N/A                                       |
| Secrets Exposure           | 10/10 | Clean.                                                                   | N/A                                       |
| Injection Vulnerabilities  | 9/10  | Static site, low risk.                                                   | N/A                                       |

**Weighted Score: 9.0/10**

## Refactoring Plan

**Quick Wins**
1.  **Add `pip-audit`**: Add a CI step to run `pip-audit`.

**Strategic Fixes**
1.  **Dependabot**: Enable Dependabot.
