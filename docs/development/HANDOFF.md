# Implementation Handoff

Keep this file current and concise. Replace instructional placeholders; do not append an unbounded transcript.

## Identity

- Repository: `D-sorganization/AffineDrift`
- Working directory: `C:/tmp/AD_w3901`
- Branch: `claude/issue-3901-motor-control-cluster` (based on `origin/staging` @ `f6adaa2`)
- Baseline commit: `f6adaa29277708b8b16a7a59b6cf4a9bbdcf50f5`
- Implementation commit: `SELF` — the commit containing this update; resolve with `git rev-parse HEAD`
- Pull request: `not created` (opened against `staging` immediately after push)
- Governing issue/epic: `#3901` (part of epic `#3896`, Cross-Article Linking)

## Objective and Status

- Objective: Wire the motor-control/neuro content cluster (6 pages with zero outbound links) with a canonical Related Articles component, an explicit standalone-article ↔ book-chapter relation, and resolved theory-part links.
- Status: `ready for review`
- Completed: All six cluster pages carry a `## Related Articles` callout (≥5 outbound links each); `articles/passive-distributed-control.qmd` ↔ `articles/The_Physics_of_Golf/quarto/ch27_passive_distributed_control.qmd` link both ways; `articles/nonlinear-control-insights.qmd` "Related Theoretical Sections" Part 1/2/3/5 entries are real page links.
- Remaining: Merge; add `resources/learning-path-biomechanics.qmd` links once the learning-path pages exist on `staging` (they are on `main` only, see Risks).

## Files and Decisions

- Files changed:
  - `articles/ideomotor-theory-and-predictive-brain.qmd` — Related Articles (cluster, PoG ch24–26, Volume IV book page)
  - `articles/passive-distributed-control.qmd` — Related Articles (PoG ch27 counterpart, intentional-constraint-collapse, cluster, Volume III, Reference Books)
  - `articles/degrees-of-freedom-and-dimensionality.qmd` — Related Articles (cluster, PoG ch25, Volume IV)
  - `articles/nonlinear-control-insights.qmd` — Related Theoretical Sections converted to real links (theory-part1/2/3/5.html); Related Articles added
  - `books/human-motor-control.qmd` — Related Articles (article companions for its ch1/2/5/6/7, PoG ch24–26, Volume III)
  - `books/biomechanics-biology-to-systems.qmd` — Related Articles (cluster, PoG ch26, Volume IV)
  - `articles/The_Physics_of_Golf/quarto/ch27_passive_distributed_control.qmd` — Companion Article callout linking back to the standalone article (reciprocal of the article→chapter link)
- Key decisions:
  - Canonical component mirrored from `articles/theory-part1.qmd`: `## Related Articles` + `::: {.callout-note}` `## See Also` bulleted markdown links. No new include was introduced (the site has no shared related-articles include; DRY handled by copying the exact existing markup pattern).
  - Theory Parts 1/2/3/5 use resolved page links (`theory-partN.html`) rather than `@sec-` cross-page refs, matching `articles/zero-torque-counterfactual.qmd` practice and avoiding cross-page crossref fragility.
  - `resources/learning-path-biomechanics.qmd` (named in the issue) does NOT exist on `staging` — it exists on `main` (added in `0d3db91`). Linking it would 404 the staging build, so `resources/resources-books.html#biomechanics` (existing, anchor verified) is used as the biomechanics resource target instead.
  - `scripts/link-checker.py` intentionally untouched (owned by a sibling agent).
- User-owned or unrelated worktree changes: `none observed`

## Validation

- Inline Python link audit (ad-hoc, not committed) over the 7 changed files — 106 relative links checked; every `.html` target resolves to an existing `.qmd` source in the worktree; `#biomechanics` anchor present in `resources/resources-books.qmd`. Result: `ALL TARGETS EXIST`.
- Outbound relative links per page: ideomotor 7, passive-distributed-control 6, degrees-of-freedom 5, nonlinear-control-insights 8, human-motor-control 7, biomechanics 5 (issue gate: ≥3 each). Inbound from non-hub content pages: every cluster page ≥2.
- Not run locally: Quarto render (Quarto not installed in this environment); CI renders the site.

## Blockers and Risks

- Blockers: `none`
- Risks/assumptions: learning-path links deferred until `resources/learning-path-*.qmd` land on `staging`; the staging/main divergence is documented in the PR body.

## Next Steps

1. Open PR to `staging` (`Fixes #3901`) and monitor CI render once.
2. After the learning-path pages merge to `staging`, swap the Reference Books link in `articles/passive-distributed-control.qmd` for `resources/learning-path-biomechanics.html`.

## Change Log

- `SELF` — Initial handoff for issue #3901: motor-control cluster cross-linking wired and verified.