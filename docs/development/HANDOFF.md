# Implementation Handoff

Keep this file current and concise. Replace instructional placeholders; do not append an unbounded transcript.

## Identity

- Repository: `D-sorganization/AffineDrift`
- Working directory: `C:/tmp/AD_w3904`
- Branch: `claude/issue-3904-series-nav` (based on `origin/main` @ `1ce02d7`)
- Baseline commit: `1ce02d7ae4d916d4c598b62be78cefa83452aaa7`
- Implementation commit: `f094080234cc5cc59c186c891b37ab08cd5426bb` (resolve with `git rev-parse HEAD` if amended)
- Pull request: `not created` (opened against `main` immediately after push)
- Governing issue/epic: `#3904` (part of epic `#3896`, Cross-Article Linking)

## Objective and Status

- Objective: Add Quarto sidebar groups for the theory series, tangent series, and Geometry of Motion volumes (prev/next + breadcrumbs); wire the four isolated geometry articles into the tangent-space cluster; chain `appendix-applications` and `affine-nature-golf-swing` into the theory-core sequence.
- Status: `ready for review`
- Completed: three series sidebars (`theory-nav`, `tangent-nav`, `geometry-motion-nav`) added to `_quarto.yml`; canonical `## Related Articles` on all four geometry articles; return links from tangent parts 1–7 to the hub and geometry articles; hub lists the four geometry companions; theory chain links (Part 5 → appendix-applications → monograph) plus sidebar ordering; new contract test `tests/test_series_navigation.py` (60 cases).
- Remaining: Merge; CI render is the only unexercised surface (Quarto not installed locally).

## Files and Decisions

- Files changed:
  - `_quarto.yml` — three series sidebar groups (each page in exactly one ordered group)
  - `articles/superposition.qmd`, `articles/null-space-constraint-jacobian.qmd`, `articles/force-mobility-matrices.qmd`, `articles/degrees-of-freedom-and-dimensionality.qmd` — canonical Related Articles (force-mobility's "Related Concepts" callout converted to the linked canonical form; its unlinked `.qmd` text mentions replaced by real page links)
  - `pages/tangent-hyperplanes.qmd` — new "Geometry Companion Articles" list linking the four articles
  - `articles/tangent-hyperplanes-series/part-1..7-*.qmd` — Related Articles returning to the hub and geometry articles
  - `articles/theory-part5.qmd`, `articles/appendix-applications.qmd`, `articles/affine-nature-golf-swing.qmd` — chain links completing the theory sequence
  - `tests/test_series_navigation.py` — TDD contract test (RED 37 failed / 19 passed before implementation; 60 passed after)
- Key decisions:
  - Dedicated per-series sidebars instead of new sections inside the docked `books-nav`: sidebar membership is what drives Quarto prev/next and breadcrumb derivation, and series-scoped sidebars keep prev/next inside the reading order (a `books-nav` section would chain each series' first page to the previous section's last page).
  - `articles/The_Geometry_of_Motion/quarto/_quarto.yml` intentionally unchanged: it is a separate `type: book` project whose ordered `book.chapters` (index, volume0–2) already provide prev/next inside the book render; adding the volumes again there would duplicate the group. The main-site render of the volume pages is covered by `geometry-motion-nav` in the root `_quarto.yml`.
  - Canonical component mirrored from `articles/theory-part1.qmd`: `## Related Articles` + `::: {.callout-note}` `## See Also` bulleted markdown links (no include exists for this pattern).
  - `articles/degrees-of-freedom-and-dimensionality.qmd` Related Articles is composed with sibling PR #4265 (issue #3901): that PR's five bullet links are included verbatim in the same callout, so both PRs can merge without losing either side's links.
  - `scripts/link-checker.py` intentionally untouched (owned by open PR #4268).
- User-owned or unrelated worktree changes: `none observed`

## Validation

- `python -m pytest tests/test_series_navigation.py` — 60 passed
- `python -m pytest tests/test_books_navigation.py tests/test_navbar_ia.py` — 27 passed
- `python -m ruff check tests/test_series_navigation.py && python -m black --check --line-length 100 tests/test_series_navigation.py` — pass
- `python scripts/check_quarto_xrefs.py` — 568 targets, 27 references, all resolved
- `yaml.safe_load(_quarto.yml)` — parses; sidebars `[books-nav, theory-nav, tangent-nav, geometry-motion-nav]`
- Inline link audit over all 14 touched content files — 0 broken relative `.html` targets; outbound counts in Related Articles: superposition 5, null-space 5, force-mobility 6, degrees-of-freedom 9; non-hub inbound per geometry article: 6 / 3 / 6 / 4
- `python scripts/check_title_case.py` — 627 files, all titles title case
- Not run locally: Quarto render (Quarto not installed in this environment); CI renders the site.

## Blockers and Risks

- Blockers: `none`
- Risks/assumptions: PR #4265 targets `staging` and this PR targets `main`; the composed callout makes their link sets union-clean. `docs/development/HANDOFF.md` is newly created here; PR #4265 also creates one on its branch, so the later merge may need to keep both handoff sections.

## Next Steps

1. Open PR to `main` (`Fixes #3904`) and monitor the CI render once.
2. After merge, spot-check prev/next and breadcrumbs on one page per series in the deployed site.

## Change Log

- `SELF` — Initial handoff for issue #3904: series sidebars, tangent-cluster wiring, and theory-chain links implemented and validated.