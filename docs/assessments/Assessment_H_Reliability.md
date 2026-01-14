# Assessment H Results: Reliability & Error Handling

## Executive Summary

The repository relies on strict CI gates ("Quality Gate") to ensure reliability. The `check_site_health.py` script is a robust mechanism for detecting broken links and orphans, acting as a reliability backstop. Error handling in scripts is basic (print and exit) but appropriate for build tools.

## Top Risks

1.  **Build Fragility (Severity: MEDIUM)**: If a single file in the hardcoded list is missing, `build-html.py` likely crashes or halts deployment.
2.  **Silent Failures (Severity: LOW)**: Some CI steps use `continue-on-error: true` (e.g., `website-lint`), potentially hiding degrading quality.
3.  **Link Rot (Severity: LOW)**: External links are checked? `check_site_health.py` explicitly skips external links.

## Scorecard

| Category               | Score | Evidence                                           | Remediation                               |
| ---------------------- | ----- | -------------------------------------------------- | ----------------------------------------- |
| Error Recovery         | 7/10  | Scripts fail fast (good), but messages basic.      | Improve error logging.                    |
| Integrity Checks       | 9/10  | `check_site_health.py` is excellent.               | Add external link checking.               |
| CI reliability         | 8/10  | `continue-on-error` reduces strictness.            | Remove where possible.                    |
| Monitorability         | N/A   | Static site, monitored via GH Actions status.      | N/A                                       |

**Weighted Score: 8/10**

## Refactoring Plan

**Quick Wins**
1.  **External Link Check**: Add a flag or separate tool to check external links periodically (weekly), not on every push (too slow/flaky).
2.  **Strict Linting**: Remove `continue-on-error` from CSS/HTML linting once clean.

**Strategic Fixes**
1.  **Robust Build Script**: Refactor `build-html.py` to handle missing files gracefully (warn instead of crash) or fail with very specific "Action Required" messages.
