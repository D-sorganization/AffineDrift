# Assessment N Results: Visualization & Export

## Executive Summary

- **Plot Quality**: `matplotlib` plots in tools use custom styling (colors, grid) which is good.
- **Interactivity**: Streamlit provides interactivity. JS models provide real-time interactivity.
- **Accessibility**: Not explicitly coded (e.g. `aria-label` on canvas), but surrounding text helps.

## Top Visualization Risks

1.  **Accessibility (Severity: MEDIUM)**: Canvas-based visualizations (JS and PyPlot) are opaque to screen readers.

## Scorecard

| Category              | Score | Evidence                                                                 | Remediation                               |
| --------------------- | ----- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Plot Quality          | 9/10  | Clean, labelled, styled.                                                 | N/A                                       |
| Accessibility         | 5/10  | Standard canvas issues.                                                  | Add text descriptions/tables for data.    |
| Export Formats        | 8/10  | Streamlit allows saving images.                                          | N/A                                       |
| Interactivity         | 10/10 | Excellent usage of Streamlit/JS.                                         | N/A                                       |

**Weighted Score: 8.0/10**

## Refactoring Plan

**Quick Wins**
1.  **Alt Text**: Ensure static images in articles have alt text.

**Strategic Fixes**
1.  **Data Download**: Add "Download CSV" button to Streamlit apps for accessibility/reproducibility.
