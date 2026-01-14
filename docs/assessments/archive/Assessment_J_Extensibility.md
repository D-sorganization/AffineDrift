# Assessment J Results: Extensibility

## Executive Summary

*   **Content Extensibility**: Adding new articles is relatively easy (add `.qmd`), but requires manual registration in the build script.
*   **Code Extensibility**: `tools/` scripts are largely standalone. Adding a new check or tool is easy but cluttering.
*   **Theme Extensibility**: CSS/JS are separate from content, allowing easy theming changes.

## Top Risks

1.  **Manual Registration (Severity: MEDIUM)**: New articles must be added to `build-html.py` list. This is an anti-pattern for extensibility.
2.  **Flat Tools Directory (Severity: LOW)**: As `tools/` grows, it becomes harder to find reusable components.

## Scorecard

| Category             | Score | Evidence                                  | Remediation                     |
| -------------------- | ----- | ----------------------------------------- | ------------------------------- |
| Content Scaling      | 7/10  | Manual steps required to add pages.       | Automate page discovery.        |
| Code Modularity      | 6/10  | Tools are scripts, not libraries.         | Refactor to package.            |
| Config Flexibility   | 8/10  | `_quarto.yml` handles most config.        | N/A                             |

**Weighted Score: 7.0/10**

## Refactoring Plan

1.  **Automate Discovery**: Modify `build-html.py` to scan for `.qmd` files recursively in `articles/` (or specified dirs) so new content is auto-detected.
