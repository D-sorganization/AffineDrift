---
title: Visible Content Gaps and Placeholders
labels: incomplete-implementation, content-gap, jules:completist
created_at: 2026-01-28
---

# User-Facing Content Gaps

## Description
Several pages on the public website contain explicit "Coming Soon" / "Under Development" sections or placeholder assets that degrade the user experience.

## Locations

### 1. Tools Page (`tools.qmd`)
- **Sections**:
    - "Additional Biomechanics Tools"
    - "Control Theory & Simulation Suite"
    - "Utility Tools"
- **Status**: Visible "Under Development" cards.

### 2. Daydreams & Doodles (`daydreams-doodles.qmd`)
- **Section**: "Future Projects"
- **Items**: Unit Converter, RRT Path Planner, Solar System Model.

### 3. Resources Books (`resources-books.qmd`)
- **Asset**: `static/images/book_placeholder.svg` used for multiple book covers.

## Action Items
1.  Comment out or remove "Under Development" sections from `.qmd` files until the tools are actually implemented.
2.  Replace placeholder book cover images with actual cover art or a more professional generic icon.
