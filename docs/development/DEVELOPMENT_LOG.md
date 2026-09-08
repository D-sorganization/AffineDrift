# Development Log — AffineDrift

State table for every feature in flight in this repository. Update entries
**in place**; never append dated sections. One entry per feature, from proposal
to ship. See the `development-logs` section of `AGENTS.md` for the binding rules
and `shared_scripts/development_log.py` for the validator.

- **Portfolio:** infra
- **WIP limit:** 3
- **Last audited:** 2026-09-08 by W3_3899

## States

`proposed` → `in_progress` → `in_review` → `shipped`, with `parked` reachable
from any live state and `abandoned` from `parked`. `shipped` never returns to
`in_progress`; open a new entry instead.

## Active

### DL-#3899 · Site Link Quality Gate (include-aware links, path style, related coverage, orphans)

- **State:** in_review
- **Owner:** W3_3899 (claude)
- **Issue:** #3899 (C3 of epic #3896)
- **PR:** not created (branch `claude/issue-3899-link-checker`; PR opens against `staging` right after the implementation commit)
- **Paths:** `src/tools/check_links.py`, `src/tools/utils/link_checks.py`, `src/tools/utils/site_config_utils.py`, `src/tools/utils/link_utils.py`, `config/link_checker_budget.json`, `docs/LINK-CHECKER.md`, `.github/workflows/ci-standard.yml`, `docs/development/QUALITY_GATES_POLICY.md`, `tests/tools/test_link_checks.py`, `articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.qmd`
- **Started:** 2026-09-08
- **Last verified:** 2026-09-08 (`SELF`)
- **Summary:** Extends the existing link checker with source-level checks (include-aware internal link resolution, page-link path style, Related-Articles coverage, orphan detection), wired into `ci-standard.yml` with baselines budgeted in `config/link_checker_budget.json` and exit codes documented in `docs/LINK-CHECKER.md`.
- **Next step:** Merge after PR #4265 lands, rebasing over `origin/staging` and union-resolving the new HANDOFF/DEVELOPMENT_LOG files.

## Shipped (Last 90 Days)

### DL-#3906 · Monograph figure-path defects — Remove Before Populating

- **State:** shipped
- **Owner:** claude
- **Issue:** #3906 (closed)
- **Paths:** `articles/proximal_distal_energy_transfer/**` (removed on staging in `0d3db91`)
- **Started:** 2026-08-21
- **Last verified:** 2026-09-08 (`SELF`)
- **Summary:** The 22 unresolvable monograph figure references shipped in ch03b/c/d; the chapters were subsequently removed from staging. The include-aware internal-link check from DL-#3899 now guards this defect class with fixture regression tests.

## Archive

Older entries live in `DEVELOPMENT_LOG_ARCHIVE_<year>.md`.

## Field Reference

- **State:** lifecycle position (see States).
- **Owner:** agent id responsible for the next action.
- **Issue/PR:** GitHub references; `not created` before the PR exists.
- **Paths:** repo globs this entry governs; refresh `Last verified` when these change.
- **Last verified:** date (`commit sha`) of the last validation that exercised the Paths.
- **Next step:** exactly one concrete, executable action — never a status report.