# Assessment H Results: Reliability

## Executive Summary

*   **Build Reliability**: The build relies on `build-html.py`, which is custom code. If this script has bugs, the site build fails.
*   **External Dependencies**: `requirements.txt` is the main source of fragility.
*   **Uptime**: GitHub Pages provides high uptime (99.9%+).

## Top Risks

1.  **Custom Build Logic (Severity: MEDIUM)**: `build-html.py` parsing logic (regex/string manipulation) is less robust than standard Quarto rendering.
2.  **Dependency Drift (Severity: MEDIUM)**: Lack of lockfile.
3.  **Third-Party Assets (Severity: LOW)**: If MathJax CDN goes down (unlikely), math breaks.

## Scorecard

| Category             | Score | Evidence                                  | Remediation                     |
| -------------------- | ----- | ----------------------------------------- | ------------------------------- |
| Build Stability      | 7/10  | Custom script introduces risk.            | Unit test `build-html.py`.      |
| Infrastructure       | 10/10 | GitHub Pages.                             | N/A                             |
| Dependency Mgmt      | 6/10  | No lockfile.                              | Add lockfile.                   |

**Weighted Score: 7.6/10**

## Refactoring Plan

1.  **Test Build Script**: Add unit tests for `build-html.py` specifically testing edge cases in HTML extraction.
2.  **Pin Dependencies**: Use `pip-compile` to lock dependencies.
