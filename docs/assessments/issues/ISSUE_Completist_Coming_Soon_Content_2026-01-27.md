---
title: "Critical Incomplete: Visible 'Coming Soon' Placeholders on User-Facing Pages"
labels: ["incomplete-implementation", "critical", "content-gap"]
date: "2026-01-27"
author: "Completist Agent"
---

# Critical Incomplete: Visible 'Coming Soon' Placeholders on User-Facing Pages

## Description
The Completist Audit (2026-01-27) identified several user-facing pages with explicit "Coming Soon" placeholders, indicating missing functionality and content that blocks the user experience. These placeholders are visible on deployed navigation paths and degrade the professional quality of the AffineDrift site.

## Affected Areas

### 1. Tools Section (`tools.qmd`)
The following tools are listed but marked as "Coming Soon":
*   **Unit Converter**
*   **RRT Path Planner**
*   **Solar System Model**
*   **Games**
*   **Control Theory & Simulation Tools** (placeholder text)
*   **General Purpose Calculators** (placeholder text)

### 2. Contact Page (`contact.qmd`)
Social media connectivity is broken:
*   **Twitter/X**: Link marked "(Coming Soon)" with `#` target.
*   **LinkedIn**: Link marked "(Coming Soon)" with `#` target.

### 3. Daydreams & Doodles (`daydreams-doodles.qmd`)
*   Multiple "Coming Soon" project entries.

### 4. Resource Placeholders
*   **`resources-books.qmd`**: Extensive reliance on `book_placeholder.svg`.
*   **`resources-researchers.qmd`**: Frequent fallback to `placeholder.svg` via `onerror` handlers.

## Impact
*   **User Frustration**: Users clicking on tools or contact links encounter dead ends.
*   **Trust**: Visible "Coming Soon" signs suggest an abandoned or unfinished project.
*   **Navigation**: Broken links negatively impact SEO and site health.

## Recommended Actions
1.  **Remove or Hide**: If the tools (Unit Converter, etc.) are not ready for release, remove their entries from `tools.qmd` entirely. Do not advertise broken features.
2.  **Fix Contact Links**: Add valid social media URLs or remove the links if the accounts do not exist.
3.  **Source Images**: Replace placeholder images in `resources-books.qmd` with valid book covers.
4.  **Audit Fallbacks**: Investigate why `resources-researchers.qmd` images are triggering `onerror` (broken upstream links?).

## Verification
After applying fixes, verify that no "Coming Soon" text is visible on the rendered pages and that all navigation links resolve to valid content.
