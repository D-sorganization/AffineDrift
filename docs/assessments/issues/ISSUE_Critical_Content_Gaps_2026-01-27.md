---
title: "Critical Incomplete: User-facing 'Under Development' & Placeholders"
labels: ["incomplete-implementation", "critical", "jules:completist"]
assignees: []
---

## Description
The Completist Audit (2026-01-27) identified several user-facing pages with "Under Development" sections and placeholder images, indicating missing functionality and content. These blocks interrupt the user experience and give the site an unfinished appearance.

## Affected Pages

### 1. Programs & Tools (`tools.qmd`)
*   **Additional Biomechanics Tools:** Section marked as "Under Development".
*   **Control Theory Simulation Suite:** Section marked as "Under Development".
*   **General Purpose Calculators:** Section marked as "Under Development".

### 2. Daydreams & Doodles (`daydreams-doodles.qmd`)
*   **Experimental Tools & Visualizations:** Section marked as "Future Projects" (Unit Converter, RRT Path Planner, Solar System Model, Games).

### 3. Resource Pages (`resources-*.qmd`)
*   **Books, Software, Researchers:** Multiple entries use placeholder images (`static/images/placeholder.svg` or `static/images/book_placeholder.svg`).

## Acceptance Criteria
- [ ] Remove or implement "Under Development" / "Future Projects" sections.
- [ ] Replace placeholder images with actual assets or remove the image element if not available.
- [ ] Ensure no user-visible placeholder text remains on the live site.

## Priority
**Critical** (Blocking User Experience)
