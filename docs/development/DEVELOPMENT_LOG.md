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

- **State:** in_review
- **Owner:** claude (wave-3 agent W3_3901)
- **Issue:** `#3901` (epic `#3896`)
- **PR:** not created (opens against `staging` immediately after push)
- **Branch:** `claude/issue-3901-motor-control-cluster`
- **Paths:** `articles/ideomotor-theory-and-predictive-brain.qmd`, `articles/passive-distributed-control.qmd`, `articles/degrees-of-freedom-and-dimensionality.qmd`, `articles/nonlinear-control-insights.qmd`, `books/human-motor-control.qmd`, `books/biomechanics-biology-to-systems.qmd`, `articles/The_Physics_of_Golf/quarto/ch27_passive_distributed_control.qmd`
- **Started:** 2026-09-07
- **Last verified:** 2026-09-07 (`SELF`)
- **Summary:** Adding the canonical Related Articles component to the six zero-outbound-link motor-control pages, linking both ways between `passive-distributed-control.qmd` and Physics of Golf ch27, and converting the unlinked theory Part 1/2/3/5 references in `nonlinear-control-insights.qmd` to real page links. All 106 relative link targets verified to exist in the worktree.
- **Next step:** Merge the PR, then swap the `resources/resources-books.html#biomechanics` link for `resources/learning-path-biomechanics.html` once the learning-path pages land on `staging`.

## Shipped (Last 90 Days)

## Archive