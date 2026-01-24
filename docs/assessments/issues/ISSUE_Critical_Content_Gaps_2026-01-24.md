---
title: Critical User-Facing Content Gaps
labels: incomplete-implementation, critical, content
---

# Critical User-Facing Content Gaps

The Completist Audit (2026-01-24) identified several user-facing pages with explicit "Coming Soon" placeholders, indicating missing functionality and content that blocks the user experience.

## Affected Pages

1.  **Tools (`tools.qmd`)**
    *   **Unit Converter**: Marked "Coming Soon".
    *   **RRT Path Planner**: Marked "Coming Soon".
    *   **Solar System Model**: Marked "Coming Soon".
    *   **Interactive Games**: Marked "Coming Soon".

2.  **Contact (`contact.qmd`)**
    *   **Social Links**: Twitter/X and LinkedIn links are placeholders marked "(Coming Soon)".

3.  **Daydreams & Doodles (`daydreams-doodles.qmd`)**
    *   **Future Projects**: Section lists unimplemented tools.

## Action Required
*   **Decision**: Either implement the missing features/content or hide these sections/pages from the public navigation until they are ready.
*   **Placeholder Images**: Replace generic `book_placeholder.svg` and `placeholder.svg` in `resources-*.qmd` with actual asset images or better fallback logic.
