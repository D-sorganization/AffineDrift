---
title: Visible "Coming Soon" Placeholders
labels: incomplete-implementation, critical, content
assignee: unassigned
status: open
---

# Visible "Coming Soon" Placeholders on User-Facing Pages

## Description
The Completist Audit identified several pages with explicit "Coming Soon" placeholders that are visible to end users.

## Locations
- **`tools.qmd`**: "Coming Soon" placeholders for:
    - Unit Converter
    - RRT Path Planner
    - Solar System Model
    - Games
- **`contact.qmd`**: "Coming Soon" status on social media links (Twitter/X, LinkedIn).
- **`daydreams-doodles.qmd`**: Multiple "Coming Soon" resource types.

## Remediation
- **Short-term**: Comment out or hide these sections using CSS (`display: none`) or Quarto conditional inclusion (`::: {.content-hidden}`) if the features are not ready.
- **Long-term**: Implement the missing tools and content.
