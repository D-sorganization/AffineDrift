# Site-Surface Provenance and Evidence Reconciliation — #4429

## Scope and Intent

This review reconciles the historical provenance of canonical site-surface audit evidence
documented in issue #4429 and recorded in
`reports/technical-review/zero-torque-dependency-carry-forward.json`.

During the #4427 zero-torque evidence refresh, comparison against historical commits
identified that eleven canonical source files (`pages/about.qmd`, `pages/book-reviews.qmd`,
`pages/collaborate.qmd`, `pages/contact.qmd`, `pages/daydreams-doodles.qmd`,
`pages/development-roadmap.qmd`, `pages/notation.qmd`, `pages/overview.qmd`,
`pages/tangent-hyperplanes.qmd`, `pages/technology.qmd`, and `pages/tools.qmd`) differed in
exact bytes from their declared initial review commit `0d2bd503a226cbbf7da1e87ce558952efe797d33`.
In addition, `ad-finding-notation-render-integrity` bound a test symbol
(`tests/test_responsive_layout_contract.py::test_dense_tables_scroll_without_collapsing_long_cells_to_fragments`)
introduced after `0d2bd503a`.

The separate manifesto notation correction completed under #4428 at checkpoint
`2250d07fc564a70525224d6b2d2765385448bd55` and the homepage review at
`dab057d47ce072b44c08dee101d1aac7fee542c1` are preserved without alteration.

## Audit of Intervening Diffs

All git commits modifying the eleven canonical source routes between baseline commit
`0d2bd503a226cbbf7da1e87ce558952efe797d33` and HEAD were examined in detail:

1. `f287ce6a` — `[TRUST-AUDIT-10] Audit Homepage and Site-Level Trust Surfaces (#4066)`
2. `1e5725de` — `docs(content): wire lateral links into Build-section pages (#3902) (#4269)`
3. `c088f9d0` — `docs(content): add series navigation sidebars and wire tangent-space cluster (#3904) (#4271)`
4. `4c46ea5a` — `build(links): site link gate + controlled category vocabulary (#3898, #3899) (#4302)`
5. `93291cec` — `fix(linking): wire reference cluster cross-article links (closes #3900) (#4364)`
6. `63d98d19` — `docs(link-gate): burn down link-gate baseline by 31 entries (#4408) (#4410)`

Across all eleven files, the net diff consists of 107 added lines containing exclusively:

- YAML frontmatter categorization: `categories: [site-information]`, `[reference]`,
  `[tangent-space]`, `[technology]`, `[tools]`, and `[creative]`.
- Editorial navigation footers: `## Related Articles` and `## Geometry Companion Articles`
  linking relative companion articles to burn down link-gate baseline entries.

Zero lines of scientific prose, physical derivations, mathematical formulas, upstream
contract boundaries, or authority claims were modified, added, or deleted.

## Claim Re-Review and Evidence Binding

Because all substantive prose and mathematical declarations are unchanged, all claims
classified in `data/trust/site_trust_surface_audit.json` remain accurate and bounded:

- Authority limits, assumptions, boundaries, and falsifiers for each route remain valid.
- The canonical sources reached their current stable byte content at commit
  `63d98d19203049d3f52d44d071862fcbb1685147`.
- Source revisions are updated to `63d98d19203049d3f52d44d071862fcbb1685147` to bind exact
  committed bytes.
- Render revisions remain preserved at `0d2bd503a226cbbf7da1e87ce558952efe797d33`, maintaining
  the record of initial responsive layout and multi-browser rendering qualification.
- Finding verification commits are updated to `63d98d19203049d3f52d44d071862fcbb1685147`.
  For `ad-finding-notation-render-integrity`, the test symbol
  `tests/test_responsive_layout_contract.py::test_dense_tables_scroll_without_collapsing_long_cells_to_fragments`
  (added in `c1963cf0` and symbol-bound in `57d53c65`) is present, passes, and matches the
  exact SHA-256 digest at `63d98d19203049d3f52d44d071862fcbb1685147`.

## Summary of Reconciled Routes

| Route                             | Source Path                     | Reconciled Source Revision | Preserved Render Revision | Finding IDs                                                                                        |
| --------------------------------- | ------------------------------- | -------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------- |
| `/`                               | `index.qmd`                     | `dab057d4...` (preserved)  | `dab057d4...`             | `ad-finding-home-readiness-amplification`                                                          |
| `/pages/about.html`               | `pages/about.qmd`               | `63d98d19...`              | `0d2bd503...`             | `ad-finding-about-authority-boundary`                                                              |
| `/pages/book-reviews.html`        | `pages/book-reviews.qmd`        | `63d98d19...`              | `0d2bd503...`             | `ad-finding-book-reviews-active-state`                                                             |
| `/pages/collaborate.html`         | `pages/collaborate.qmd`         | `63d98d19...`              | `0d2bd503...`             | `ad-finding-collaboration-promises`                                                                |
| `/pages/contact.html`             | `pages/contact.qmd`             | `63d98d19...`              | `0d2bd503...`             | `ad-finding-contact-channel-contract`                                                              |
| `/pages/daydreams-doodles.html`   | `pages/daydreams-doodles.qmd`   | `63d98d19...`              | `0d2bd503...`             | `ad-finding-daydreams-analogy-authority`                                                           |
| `/pages/development-roadmap.html` | `pages/development-roadmap.qmd` | `63d98d19...`              | `0d2bd503...`             | `ad-finding-roadmap-stale-readiness`                                                               |
| `/pages/drifter-manifesto.html`   | `pages/drifter-manifesto.qmd`   | `2250d07f...` (#4428)      | `2250d07f...`             | 5 findings (preserved)                                                                             |
| `/pages/notation.html`            | `pages/notation.qmd`            | `63d98d19...`              | `0d2bd503...`             | `ad-finding-notation-authority-limit`, `ad-finding-notation-render-integrity`                      |
| `/pages/overview.html`            | `pages/overview.qmd`            | `63d98d19...`              | `0d2bd503...`             | `ad-finding-overview-upstream-contract`, `ad-finding-overview-python-support-boundary`             |
| `/pages/tangent-hyperplanes.html` | `pages/tangent-hyperplanes.qmd` | `63d98d19...`              | `0d2bd503...`             | `ad-finding-tangent-locality-readiness`, `ad-finding-tangent-reference-completeness-amplification` |
| `/pages/technology.html`          | `pages/technology.qmd`          | `63d98d19...`              | `0d2bd503...`             | `ad-finding-technology-summary-amplification`                                                      |
| `/pages/tools.html`               | `pages/tools.qmd`               | `63d98d19...`              | `0d2bd503...`             | `ad-finding-tools-capability-overreach`                                                            |
