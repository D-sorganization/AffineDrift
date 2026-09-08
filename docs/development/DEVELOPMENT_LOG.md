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

### DL-#3899 · Site Link Quality Gate (include-aware links, path style, related coverage, orphans)

- **State:** in_review
- **Owner:** W3_3899 (claude)
- **Issue:** #3899 (C3 of epic #3896)
- **PR:** #4268 (open against `staging`)
- **Paths:** `src/tools/check_links.py`, `src/tools/utils/link_checks.py`, `src/tools/utils/site_config_utils.py`, `src/tools/utils/link_utils.py`, `config/link_checker_budget.json`, `docs/LINK-CHECKER.md`, `.github/workflows/ci-standard.yml`, `docs/development/QUALITY_GATES_POLICY.md`, `tests/tools/test_link_checks.py`, `articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.qmd`
- **Started:** 2026-09-08
- **Last verified:** 2026-09-08 (`SELF`)
- **Summary:** Extends the existing link checker with source-level checks (include-aware internal link resolution, page-link path style, Related-Articles coverage, orphan detection), wired into `ci-standard.yml` with baselines budgeted in `config/link_checker_budget.json` and exit codes documented in `docs/LINK-CHECKER.md`.
- **Next step:** Merge once protected checks pass (closes #3899).

## Shipped (Last 90 Days)

## Archive