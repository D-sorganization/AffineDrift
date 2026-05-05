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

## Public-Facing Source Boundaries

Public research and article content should be edited in canonical Quarto,
Markdown, TeX, or asset sources that are intentionally part of the published
site or book pipeline:

- Public article and book sources belong under `articles/`, `books/`, `pages/`,
  and `resources/` only when they are meant to be reader-facing research
  content.
- Retained review notes, PR instructions, automation summaries, audit reports,
  and dated editorial reports are process artifacts. Keep new process artifacts
  under `docs/development/`, `docs/process/`, `reports/`, or `assessments/`
  according to audience and retention purpose, not inside primary public
  article paths.
- Generated website output belongs under `docs/` when produced by the site
  build. Generated source-adjacent HTML, LaTeX byproducts, cache files, or
  critique dumps should not be introduced beside canonical article sources
  unless the generated file is deliberately retained as a provenance artifact
  and documented here.
- PR and review instruction files must not be linked from `_quarto.yml`,
  `resources/articles.qmd`, learning paths, or public landing pages unless they
  have first been rewritten as public provenance or methodology content.

## Review and Generated Artifact Classification

The following tracked artifacts are retained for provenance or development
history, but they are not primary public article surfaces:

| Path | Classification | Retention policy |
| --- | --- | --- |
| `AffineDrift_Content_Review_Instructions.docx` | Internal process | Retain as source-bound review guidance until replaced by a Markdown process document. Do not link from public navigation. |
| `articles/PR_INDUCED_ACCELERATION.md` | Internal process | Treat as PR-specific development notes for induced-acceleration work. Future updates should move or supersede this under `docs/process/` before public linking. |
| `articles/The_Physics_of_Golf/PR_GUIDANCE.md` | Internal process | Retain as golf-series PR guidance, separate from reader-facing Physics of Golf chapters. Do not add to public article indexes. |
| `articles/The_Physics_of_Golf/PR_INSTRUCTIONS.md` | Internal process | Retain as implementation instructions only. Do not link from public golf research navigation. |
| `articles/The_Geometry_of_Motion/PR_INSTRUCTIONS.md` | Internal process | Retain as Geometry of Motion implementation instructions only. Prefer `docs/process/` for future instruction updates. |
| `articles/Tangent Hyperplane Articles/Advanced/Contraction_Tangent_CRITIC.qmd` | Public provenance | Canonical Quarto source for the critic/provenance page when the critique is intentionally published. Keep it source-authored and cite its role from public indexes only when curated. |
| `articles/Tangent Hyperplane Articles/Advanced/Contraction_Tangent_CRITIC.md` | Public provenance | Markdown companion/provenance copy. Keep only while it has source-review value; avoid treating it as the canonical page when a `.qmd` exists. |
| `articles/Tangent Hyperplane Articles/Advanced/Contraction_Tangent_CRITIC.html` | Generated output | Generated critique output beside source content. Do not edit by hand or link as canonical source; prefer regenerating from `.qmd` or moving generated output to `docs/` in a future cleanup. |
| `articles/Tangent Hyperplane Articles/Advanced/Hybrid_Tangent_CRITIC.md` and `.qmd` | Public provenance | Retain only as curated critique/provenance material. The `.qmd` source is preferred for publication. |
| `articles/Tangent Hyperplane Articles/Advanced/Residual-Aware_Control_CRITIC.md` and `.qmd` | Public provenance | Retain only as curated critique/provenance material. The `.qmd` source is preferred for publication. |
| `reports/textbook_editorial_review_2026-04-*.md` | Internal process | Dated automation/editorial reports. Retain in `reports/` for audit history; do not surface as public research content without an edited summary page. |

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

When adding or retaining process artifacts, update the classification table
above and verify that public navigation does not expose PR instructions, stale
review dumps, or generated HTML as primary research content.
