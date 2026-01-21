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

## Issue 3: Medium Severity Finding in tools/verify_images.py
- **Title**: SECURITY: Medium Severity Finding in tools/verify_images.py
- **Labels**: `security`, `jules:sentinel`
- **Body**:
  Bandit found B310: Audit url open for permitted schemes.
  Location: `tools/verify_images.py:57`

  **Note**: This matches a policy exception for verification tools but requires periodic review to ensure it remains safe.
