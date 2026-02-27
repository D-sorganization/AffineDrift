# Volume I Consolidation Audit

## Scope

This audit supports issue `#1289` by comparing the duplicate Volume I manuscript trees:

- `articles/textbook/`
- `articles/The_Geometry_of_Motion/Volume_I/`

## Findings

- Chapter filenames align 1:1 for `ch01` through `ch08`.
- `Volume_I/chapters/` includes additional support files (`further_reading.tex`, `glossary.tex`) not present in `articles/textbook/chapters/`.
- `Volume_I/main.tex` already uses the shared bibliography (`\bibliography{../geometry_of_motion}`).
- Chapter text differences exist between the duplicate trees and require controlled merge work because direct file replacement introduces LaTeX incompatibilities in CI.

## Consolidation Actions Applied

1. Updated `books/tangent-space-methods.qmd` links and traceability notes to point at canonical `Volume_I` sources.
2. Added deprecation notice: `articles/textbook/README.md`.
3. Added regression tests for canonical-path references and chapter coverage.

## Remaining Follow-Up

- Merge chapter-level content deltas from `articles/textbook/chapters/` into canonical `Volume_I/chapters/` in compile-safe increments.
- Remove or archive legacy transition artifacts in `articles/textbook/` once external links and automation no longer rely on them.
