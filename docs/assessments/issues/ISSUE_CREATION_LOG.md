# Issue Creation Log

The following issues would be created based on assessment grades below 5.

## Issue 1: Critical Low Test Coverage
- **Title**: CRITICAL: Low Test Coverage (2/10)
- **Labels**: `jules:assessment`, `needs-attention`, `priority:critical`
- **Body**:
  Test coverage is critically low at 18%.
  - `build-html.py`: 0%
  - `tools/code_quality_check.py`: 0%

  **Action**: Create tests for these critical scripts immediately.

## Issue 2: User-Visible Placeholder Content
- **Title**: CRITICAL: User-Visible Placeholders on Production Site
- **Labels**: `incomplete-implementation`, `critical`, `quality-control`
- **Body**:
  Multiple user-facing pages contain "Coming Soon" placeholders which degrade the user experience.
  - `tools.qmd`: Multiple tool sections.
  - `daydreams-doodles.qmd`: Resource cards.
  - `contact.qmd`: Social media links.

  **Action**: Hide these sections or implement the missing features.

## 2026-01-21 - Completist Audit Findings

### Issue 1: User-Visible Placeholders and Broken Links
**Title:** Incomplete Implementation: Critical User-Facing Placeholders
**Labels:** incomplete-implementation, critical
**Body:**
The Completist audit has identified visible placeholder content that degrades the user experience on the live site.

**Locations:**
- `tools.qmd`: Multiple "Coming Soon" sections and empty links.
- `contact.qmd`: Twitter/X and LinkedIn links are placeholders (`#`).
- `daydreams-doodles.qmd`: "Coming Soon" spans.
- `resources-videos.qmd`: Missing video ID for Channel Preview.

**Action Required:**
Replace "Coming Soon" placeholders with actual content or remove the sections until content is ready. Update social links in `contact.qmd`.

### Issue 2: Jules CLI API Migration Gaps
**Title:** Feature Gap: Update Workflows for Jules CLI v0.1.x
**Labels:** incomplete-implementation, maintenance
**Body:**
TODOs indicate that workflow files have not been updated for the Jules CLI v0.1.x API changes.

**Locations:**
- `.github/workflows/Jules-Tech-Custodian.yml`
- `.github/workflows/Jules-Conflict-Fix.yml`

**Action Required:**
Migrate the CLI commands to match the new API specification to ensure bot functionality.
