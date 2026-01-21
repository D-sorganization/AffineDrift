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

## Issue 3: Migrate Jules Agents to CLI v0.1.x API
- **Title**: CRITICAL: Migrate Jules Agents to CLI v0.1.x API
- **Labels**: `jules:code-quality`, `critical`, `maintenance`
- **Body**:
  Key maintenance workflows are explicitly disabled because they rely on an outdated Jules CLI API.
  - `Jules-Tech-Custodian.yml`: "Jules Integration (Disabled - API Migration Required)"
  - `Jules-Conflict-Fix.yml`: "Jules CLI integration disabled pending API migration"

  This causes the "Control Tower" automation to fail silently or warn without performing necessary maintenance.

  **Action**: Update the workflows to use the new Jules CLI v0.1.x API syntax (e.g., `jules new`, `jules remote`) as noted in the TODO comments.
