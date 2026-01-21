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

## Issue 3: Persistent Low Test Coverage (Re-assessment)
- **Title**: CRITICAL: Test Coverage Dropped to ~6% (2/10)
- **Labels**: `jules:assessment`, `needs-attention`, `priority:critical`
- **Body**:
  Latest assessment indicates test coverage has dropped or was previously overestimated.
  - Estimated Coverage: ~6%
  - Critical gaps remain in build scripts and tools.

  **Action**: Prioritize unit tests for `tools/` directory.
