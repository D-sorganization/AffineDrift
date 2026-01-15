# Assessment A Results: Architecture & Implementation

## Executive Summary

The repository follows a standard "Static GitHub Pages + Quarto" architecture, which is appropriate for its research-heavy content. The separation of `docs/` (web root), `articles/` (content source), and `tools/` (maintenance) is logical. However, the `tools/` directory is cluttered, mixing scientific models (`wrist_universal_joint`) with site maintenance scripts (`check_site_health.py`). The build system relies on a custom `build-html.py` script with hardcoded file lists, which creates a maintenance bottleneck.

## Top 10 Risks

1.  **Tools Directory Cohesion (Severity: MEDIUM)**: `tools/` contains both scientific code and infrastructure scripts, complicating dependency management and onboarding.
2.  **Hardcoded Build Paths (Severity: MEDIUM)**: `build-html.py` requires manual updates to the file list for every new article, risking omitted pages.
3.  **Template Divergence (Severity: LOW)**: `docs/articles.html` acts as a master template but is disconnected from the Quarto build pipeline, requiring manual synchronization.
4.  **Config Complexity (Severity: LOW)**: `_quarto.yml` is large and monolithic, making it difficult to manage navigation changes.
5.  **Environment Fragility (Severity: MEDIUM)**: Local environment setup (e.g., `numpy` installation) has proven inconsistent, causing test failures.
6.  **Legacy Artifacts (Severity: LOW)**: `archive/` directories are present; while excluded from build, they clutter the file tree.
7.  **Data Documentation (Severity: LOW)**: The `data/` directory lacks a clear schema or documentation in `README.md`.
8.  **CSS Source Truth (Severity: LOW)**: Styles are present in both `styles.css` and `docs/styles.css`, leading to potential version skew.
9.  **Missing Component Library (Severity: LOW)**: No dedicated directory for reusable Quarto components or partials.
10. **Bus Factor (Custom Build) (Severity: MEDIUM)**: The custom logic in `build-html.py` for extracting HTML bodies is non-standard and requires specific knowledge to maintain.

## Scorecard

| Category                    | Score | Evidence                                                                 | Remediation                               |
| --------------------------- | ----- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Static Site Architecture    | 9/10  | Standard Quarto + GitHub Pages structure.                                | N/A                                       |
| Directory Organization      | 7/10  | `tools/` is mixed; `articles/` is flat.                                  | Reorganize `tools/` by function.          |
| Scalability                 | 6/10  | Hardcoded lists in build scripts limit scalability.                      | Implement glob-based file discovery.      |
| Extensibility               | 8/10  | Easy to add QMD content if build script is updated.                      | Automate build updates.                   |
| Infrastructure as Code      | 9/10  | `_quarto.yml` and workflows define the site well.                        | N/A                                       |
| Tech Stack Appropriateness  | 10/10 | Quarto is ideal for mathematical/scientific content.                     | N/A                                       |

**Weighted Score: 8.2/10**

## Refactoring Plan

**Quick Wins**
1.  **Clean `tools/`**: Move site maintenance scripts to `tools/maintenance/` or `scripts/` (if appropriate).
2.  **Document Build**: Add a "How to Add a New Article" section to `README.md` explicitly mentioning `build-html.py`.

**Strategic Fixes**
1.  **Automate Build Discovery**: Rewrite `build-html.py` to dynamically find `.qmd` files in `articles/`.
2.  **Unify Templates**: Investigate using Quarto's native `template` functionality to replace the `docs/articles.html` workaround.
