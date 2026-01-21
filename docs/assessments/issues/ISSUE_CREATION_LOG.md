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

## Issue 3: Misleading Commit & Committed Artifacts
- **Title**: CRITICAL: Misleading Commit Message & Artifacts in Repo
- **Labels**: `jules:code-quality`, `critical`, `integrity`
- **Body**:
  Commit `8c8a930` ("fix(ci): repair remaining yaml indentation issues") contains unrelated feature work and build artifacts.

  **Violations:**
  1. **Misleading Message:** Claims CI fix, adds `grip_angle_simulator.html`.
  2. **Artifacts:** `workflow_runs_affine.txt` (50KB log) committed to root.

  **Action**:
  1. Remove `workflow_runs_affine.txt`.
  2. Revert or split `8c8a930`.
  3. Ensure commits match their descriptions.
