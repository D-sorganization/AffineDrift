# Completist Audit Report - 2026-01-26

## Executive Summary
This audit confirms a **Critical Deployment Failure** where the `startup-launcher.js` feature, while present in the source tree, is excluded from the build artifacts, resulting in 404 errors on the live site. Additionally, user-facing "Coming Soon" placeholders remain prominent on key pages, and several content gaps (missing book covers) persist. The previously flagged disabled workflows appear to have been removed from the repository.

## 1. Critical Incomplete (Blocking)
*   **Deployment Failure (High Severity):**
    *   The files `src/js/startup-launcher.js` and `src/css/startup-launcher.css` exist in the source tree.
    *   `_quarto.yml` references `/js/startup-launcher.js` in the `include-in-header` section.
    *   However, `src/js/startup-launcher.js` is **not** listed in the `resources` section of `_quarto.yml`, nor is there a configuration to copy it to the root `js/` directory in the output.
    *   **Impact:** Users encounter 404 errors for the startup script, breaking the intended splash screen experience.

*   **Visible Placeholder Content:**
    *   `tools.qmd`: Contains multiple "Coming Soon" placeholders for tools (Unit Converter, RRT Path Planner, Solar System Model, Games).
    *   `contact.qmd`: "Coming Soon" status on social media links (Twitter/X, LinkedIn).
    *   `daydreams-doodles.qmd`: Multiple "Coming Soon" resource types.
    *   `archive/handcrafted-site/wrist-universal-joint.html`: Contains explicit TODO comments and placeholder text for a Streamlit URL.

## 2. Feature Gaps
*   **Missing Book Covers:**
    *   `resources-books.qmd` (and generated HTML): Extensively uses `static/images/book_placeholder.svg` instead of actual book covers. This degrades the visual quality of the resources section.

## 3. Content Gaps (Website Specific)
*   **Researcher Profiles:**
    *   `resources-researchers.qmd`: Uses `placeholder.svg` for several researcher profiles where images are missing.

## 4. Technical Debt
*   **Swallowed Exceptions:**
    *   `scripts/assess_repo.py`: Contains `pass` statements in exception blocks, which may mask errors during repository assessment.
*   **Missing/Deleted Workflows:**
    *   Input data flagged `Jules-Conflict-Fix.yml` and `Jules-Tech-Custodian.yml` as disabled with TODOs. These files are no longer present in `.github/workflows/`, suggesting they have been deleted but not fully cleaned up from tracking or are pending migration.

## 5. Recommendations
1.  **Fix Deployment:** Explicitly add `src/js/startup-launcher.js` to the `resources` list in `_quarto.yml` or configure a pre-build step to copy it to `docs/js/`.
2.  **Resolve Placeholders:** Remove "Coming Soon" links from `contact.qmd` if they are not imminent. For `tools.qmd`, consider hiding the "Coming Soon" sections until the tools are ready for at least a beta release.
3.  **Content Update:** Acquire and add missing book cover images to `static/images/` and update `resources-books.qmd`.
