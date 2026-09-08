# Development Log — AffineDrift

State table for every feature in flight in this repository. Update entries
**in place**; never append dated sections. One entry per feature, from proposal
to ship.

- **Portfolio:** `golf`
- **WIP limit:** `8`
- **Last audited:** `2026-09-07` by `claude`

## States

`proposed` → `in_progress` → `in_review` → `shipped`, with `parked` reachable
from any live state and `abandoned` from `parked`. `shipped` never returns to
`in_progress`; open a new entry instead.

## Active

### DL-#3901 · Wire motor-control/neuro content cluster cross-links

- **State:** shipped (PR #4265 squash-merged to staging 2026-09-08)
- **Owner:** claude (wave-3 agent W3_3901)
- **Issue:** `#3901` (epic `#3896`)
- **PR:** not created (opens against `staging` immediately after push)
- **Branch:** `claude/issue-3901-motor-control-cluster`
- **Paths:** `articles/ideomotor-theory-and-predictive-brain.qmd`, `articles/passive-distributed-control.qmd`, `articles/degrees-of-freedom-and-dimensionality.qmd`, `articles/nonlinear-control-insights.qmd`, `books/human-motor-control.qmd`, `books/biomechanics-biology-to-systems.qmd`, `articles/The_Physics_of_Golf/quarto/ch27_passive_distributed_control.qmd`
- **Started:** 2026-09-07
- **Last verified:** 2026-09-07 (`SELF`)
- **Summary:** Adding the canonical Related Articles component to the six zero-outbound-link motor-control pages, linking both ways between `passive-distributed-control.qmd` and Physics of Golf ch27, and converting the unlinked theory Part 1/2/3/5 references in `nonlinear-control-insights.qmd` to real page links. All 106 relative link targets verified to exist in the worktree.
- **Next step:** Merge the PR, then swap the `resources/resources-books.html#biomechanics` link for `resources/learning-path-biomechanics.html` once the learning-path pages land on `staging`.

### DL-#3900 · Wire the reference cluster cross-links

- **State:** in_review
- **Owner:** claude (W6 session)
- **Issue:** `#3900` (epic `#3896`)
- **PR:** [#4266](https://github.com/D-sorganization/AffineDrift/pull/4266) (against `staging`)
- **Branch:** `claude/issue-3905-reference-cluster`
- **Paths:** `articles/lagrangian-reference.qmd`, `articles/screw-theory-reference.qmd`, `articles/rotation-representations-reference.qmd`, `pages/notation-conventions.qmd`, `articles/The_Physics_of_Golf/quarto/glossary.qmd`, `articles/theory-part1.qmd`, `articles/drifter-manifesto.qmd`, `articles/force-mobility-matrices.qmd`, `articles/null-space-constraint-jacobian.qmd`, `articles/The_Geometry_of_Motion/quarto/vol0_ch11_lagrangian_mechanics.qmd`, `articles/The_Physics_of_Golf/quarto/ch02..ch31`
- **Started:** 2026-09-08
- **Summary:** Added the canonical Related Articles callout to the five reference-cluster pages with inbound links from ten consumer pages so every reference page has >= 3 outbound and >= 3 inbound (non-hub) edges. All relative link targets verified in the worktree.
- **Next step:** Merge the PR (protected merge closes #3900 via `Fixes #3900`).

## Shipped (Last 90 Days)

## Archive