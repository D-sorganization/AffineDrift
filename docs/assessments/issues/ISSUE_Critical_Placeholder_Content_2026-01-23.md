---
title: "Critical Incomplete: Visible Placeholder Content"
labels: incomplete-implementation, critical
---
# Critical Incomplete: Visible Placeholder Content on Website

**Priority**: High
**Status**: Open

## Description
User-facing pages contain visible "Coming Soon" placeholders and dead links (`#`), which degrade the user experience and give an unfinished impression.

## Locations
1. **`tools.qmd`**: 5 tools and 4 resource types marked "Coming Soon".
2. **`daydreams-doodles.qmd`**: 4 items marked "Coming Soon".
3. **`contact.qmd`**: Social media links (Twitter/X, LinkedIn) are "Coming Soon" with `#` hrefs.

## Remediation
- **Short Term**: Comment out these sections in the Quarto `.qmd` files so they do not render.
- **Long Term**: Implement the content or remove the placeholders entirely if not planned for immediate release.
