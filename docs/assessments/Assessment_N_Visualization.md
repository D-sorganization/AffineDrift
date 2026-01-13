# Assessment N Results: Visualization & Math

## Executive Summary

*   **Math Rendering**: Uses MathJax via Quarto. Consistency seems high based on `Assessment_A` feedback (though `Assessment_A` noted broken delimiters in `index.qmd`).
*   **Figures**: Uses standard Markdown images. Lightbox improves usability.
*   **Interactive Viz**: Some mentions of Simulink/Matlab, but web-based interactive viz (e.g. JS plotting) seems limited or absent.

## Top Risks

1.  **Broken Math Delimiters (Severity: HIGH)**: As noted, `index.qmd` might have `$ ... $` vs `\( ... \)` issues.
2.  **Mobile Math (Severity: MEDIUM)**: Long equations on mobile need scroll overflow handling (Quarto usually handles this, but needs verification).

## Scorecard

| Category             | Score | Evidence                                  | Remediation                     |
| -------------------- | ----- | ----------------------------------------- | ------------------------------- |
| Math Typesetting     | 8/10  | Mostly standard, some syntax errors.      | Fix delimiters.                 |
| Image Quality        | 8/10  | Good use of figures.                      | N/A                             |
| Interactivity        | 5/10  | Static images mostly.                     | Add Plotly/JS plots.            |

**Weighted Score: 7.0/10**

## Refactoring Plan

1.  **Fix Delimiters**: Run a regex search for `$$` vs `\[` and standardise.
2.  **Overflow Check**: Add CSS rule `.math-display { overflow-x: auto; }` if not present.
