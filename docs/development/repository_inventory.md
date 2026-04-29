# Repository Inventory

## Inventory Map

AffineDrift is organized around research content, website assets, executable
tooling, and validation tests:

- `articles/`, `books/`, `pages/`, `resources/`, and `models/` hold the
  Quarto source surfaces rendered into the public site.
- `src/` contains Python packages for affine-control, tangent-model, analysis,
  and repository-quality helpers.
- `js/`, `css/`, `static/`, and root web assets support the generated website.
- `.github/workflows/` contains workflow definitions only; human-facing workflow
  documentation is tracked through this development inventory and `SPEC.md`.
- `tests/` contains pytest, Jest, and Playwright coverage for code, content, and
  site smoke checks.

## Implementation Status

The repository keeps active implementation in the core Python packages, Quarto
source tree, and website asset pipeline. CI validates source freshness, content
structure, JavaScript behavior, Playwright smoke coverage, and SPEC updates.

## Known Gaps

Some development tracking documents are intentionally high-level and reference
the open issue backlog instead of duplicating issue bodies. Quarto rendering
still depends on the CI runner toolchain for full website validation.

## Maintenance Note

Update this inventory when a primary source directory, package boundary, or
workflow documentation location changes. Workflow-directory documentation should
not be kept as a loose Markdown file inside `.github/workflows/`, because that
directory is reserved for executable workflow definitions.
