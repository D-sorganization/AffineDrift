# Assessment A Results: Architecture & Implementation

## Executive Summary

*   **Context Alignment**: The repository correctly follows the "Static GitHub Pages + Quarto" model required for `AffineDrift.com`. This is a research website, not a "Tools Launcher" app (correcting previous assessment errors).
*   **Architecture Soundness**: The separation of `docs/` (web root), `articles/` (content source), and `tools/` (maintenance scripts) is logical and maintainable.
*   **Quarto Integration**: `_quarto.yml` is correctly configured for a custom website with specialized navigation and theming.
*   **Implementation Status**: The core website infrastructure is fully functional, with advanced features like "History Sidebar" and "ScrollSpy" implemented in vanilla JS.
*   **Tooling Organization**: While the website architecture is solid, the `tools/` directory contains a mix of "maintenance scripts" (e.g., `check_links.py`) and "scientific models" (e.g., `wrist_universal_joint/`) without clear delineation.

## Top 10 Risks

1.  **Tools/Content Mixing (Severity: MEDIUM)**: `tools/` is a flat list mixing CI scripts and scientific modeling code, making it harder to onboard new devs.
2.  **Legacy Artifacts (Severity: LOW)**: `archive/` folders exist but are correctly excluded from build.
3.  **Config Complexity (Severity: MEDIUM)**: `_quarto.yml` is quite large; splitting it might help if Quarto supported it (it does partially).
4.  **No "Modules" Directory (Severity: LOW)**: As per the template, a `modules/` or `components/` directory for shared Quarto snippets is missing; `articles/` does heavy lifting.
5.  **Hardcoded Paths (Severity: MEDIUM)**: `build-html.py` has a hardcoded list of QMD files, requiring manual updates for new pages.
6.  **CSS/JS Separation (Severity: LOW)**: `styles.css` and `script.js` are in `docs/` but also copied or managed via Quarto. The source of truth is slightly ambiguous (Edit source in root? Or `docs/`?).
7.  **Data Management (Severity: LOW)**: `data/` exists but usage isn't fully documented in `README`.
8.  **Template Divergence (Severity: LOW)**: The custom `docs/articles.html` template means global navigation changes require manual patching, not just YAML updates.
9.  **Python Version Pinning (Severity: LOW)**: CI uses specific Python versions, but `runtime.txt` or `.python-version` is missing for local dev (e.g. `pyenv`).
10. **Bus Factor (Severity: MEDIUM)**: The custom `build-html.py` logic is non-standard Quarto usage (extracting HTML bodies).

## Scorecard

| Category                    | Score | Evidence                                                                 | Remediation                               |
| --------------------------- | ----- | ------------------------------------------------------------------------ | ----------------------------------------- |
| Static Site Architecture    | 9/10  | Standard Quarto + GitHub Pages structure.                                | N/A                                       |
| Directory Organization      | 8/10  | Clear split of content vs. build artifacts.                              | Group `tools/` into subfolders.           |
| Scalability                 | 7/10  | Hardcoded file lists in build scripts limit scalability.                 | Make `build-html.py` scan directories.    |
| Extensibility               | 8/10  | Easy to add new QMD files (if added to build script).                    | Automate file discovery.                  |
| Infrastructure as Code      | 9/10  | `_quarto.yml` and workflows define the site.                             | N/A                                       |
| Tech Stack Appropriateness  | 10/10 | Quarto is ideal for this math-heavy content.                             | N/A                                       |

**Weighted Score: 8.5/10**

## Refactoring Plan

**Quick Wins**
1.  **Group Tools**: Move `check_*.py` into `tools/maintenance/` and `convert_*.py` into `tools/migration/`.
2.  **Document Build Process**: Clarify in `README` that `build-html.py` needs manual updates for new root files.

**Strategic Fixes**
1.  **Automate Build Discovery**: Rewrite `build-html.py` to glob `*.qmd` files instead of using a hardcoded list.
2.  **Standardize Tooling**: Convert `tools/` into a proper Python package or distinct folders to separate "Site Infra" from "Science Models".
