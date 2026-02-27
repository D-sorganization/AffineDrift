# Volume I Consolidation Audit

## Scope

This audit supports issue `#1289` by comparing the duplicate Volume I manuscript trees:

- `articles/textbook/`
- `articles/The_Geometry_of_Motion/Volume_I/`

## Findings

- Chapter filenames align 1:1 for `ch01` through `ch08`.
- `Volume_I/chapters/` includes additional support files (`further_reading.tex`, `glossary.tex`) not present in `articles/textbook/chapters/`.
- `Volume_I/main.tex` already uses the shared bibliography (`\bibliography{../geometry_of_motion}`).
- Chapter text differences existed between the duplicate trees and have been synchronized into `Volume_I/chapters/` from `articles/textbook/chapters/`.

## Consolidation Actions Applied

1. Synchronized `articles/textbook/chapters/ch*.tex` into `articles/The_Geometry_of_Motion/Volume_I/chapters/`.
2. Updated `books/tangent-space-methods.qmd` links and traceability notes to point at canonical `Volume_I` sources.
3. Added deprecation notice: `articles/textbook/README.md`.

## Remaining Follow-Up

- Remove or archive legacy transition artifacts in `articles/textbook/` once external links and automation no longer rely on them.
