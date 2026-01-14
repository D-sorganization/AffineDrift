# Assessment L Results: Maintainability

## Executive Summary

*   **Codebase Size**: Manageable. Clearly separated concerns (Content vs. Code).
*   **Complexity**: `build-html.py` is the most complex piece of "infra" code. `script.js` is clean but growing.
*   **Tech Debt**: `tools/` directory clutter is the main debt.

## Top Risks

1.  **Bus Factor on Build Script (Severity: MEDIUM)**: Custom build logic.
2.  **CSS Specificity (Severity: LOW)**: `styles.css` has some `!important` overrides which can make maintenance hard.

## Scorecard

| Category             | Score | Evidence                                  | Remediation                     |
| -------------------- | ----- | ----------------------------------------- | ------------------------------- |
| Code Complexity      | 8/10  | Mostly low.                               | Simplify `build-html.py`.       |
| Tech Debt            | 7/10  | `tools/` organization.                    | Group tools.                    |
| Documentation        | 8/10  | Good docs help maintenance.               | N/A                             |

**Weighted Score: 7.6/10**

## Refactoring Plan

1.  **Refactor CSS**: Review `!important` usage and try to use specificity instead.
2.  **Comment Build Script**: Ensure `build-html.py` is heavily commented explaining *why* it extracts HTML manually.
