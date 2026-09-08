# Development Log — AffineDrift

State table for every feature in flight in this repository. Update
entries **in place**; never append dated sections. One entry per
feature, from proposal to ship. See the `development-logs` section of
`AGENTS.md` for the binding rules and
`shared_scripts/development_log.py` for the validator.

- **Portfolio:** personal
- **WIP limit:** 2
- **Last audited:** 2026-08-28 by bootstrap

## States

`proposed` → `in_progress` → `in_review` → `shipped`, with `parked`
reachable from any live state and `abandoned` from `parked`.
`shipped` never returns to `in_progress`; open a new entry instead.

## Active

### DL-#3904 · Series navigation and tangent-space cluster integration

- **State:** in_review
- **Owner:** claude (wave-8 agent W8_3904)
- **Issue:** `#3904` (epic `#3896`)
- **PR:** not created (opens against `main` immediately after push)
- **Branch:** `claude/issue-3904-series-nav`
- **Paths:** `_quarto.yml`, `pages/tangent-hyperplanes.qmd`,
  `articles/superposition.qmd`,
  `articles/null-space-constraint-jacobian.qmd`,
  `articles/force-mobility-matrices.qmd`,
  `articles/degrees-of-freedom-and-dimensionality.qmd`,
  `articles/tangent-hyperplanes-series/part-*.qmd`,
  `articles/theory-part5.qmd`, `articles/appendix-applications.qmd`,
  `articles/affine-nature-golf-swing.qmd`, `tests/test_series_navigation.py`
- **Started:** 2026-09-08
- **Last verified:** 2026-09-08 (`4ec3a19`)
- **Summary:** Added three series sidebar groups (theory, tangent-space,
  Geometry of Motion volumes) for prev/next and breadcrumbs; wired the four
  isolated geometry articles into the tangent-space cluster with the canonical
  Related Articles component and hub-side companion links; added return links
  from tangent parts 1–7; chained appendix-applications and
  affine-nature-golf-swing into the theory sequence. Contract test:
  60 passed. All relative link targets verified to exist.
- **Next step:** Merge the PR, then spot-check prev/next and breadcrumbs on
  one page per series in the deployed site.

### DL-0035 · Impact Dynamics and Acoustics Review

- **State:** in_review
- **Owner:** codex
- **Issue:** https://github.com/D-sorganization/AffineDrift/issues/4254
- **PR:** https://github.com/D-sorganization/AffineDrift/pull/4258
- **Branch:** docs/4253-impact-dynamics-acoustics
- **Paths:** `articles/technology-heavy-hit-impact-coupling.qmd`, `articles/_includes/impact-*.qmd`, `references/impact-acoustics.bib`, `docs/development/impact-acoustics/`, `tests/test_heavy_hit_evidence_boundaries.py`
- **Started:** 2026-09-07
- **Last verified:** 2026-09-07 (`cd0afdfa`)
- **Summary:** Corrected theory, source inventory and linked epics; publication regressions pass. Validation completed; PR #4258 in review; physical research remains open.

- **Next step:** Resolve protected PR #4258 review/check results, then follow the separately scoped research dependencies.

### DL-0001 · Audit Quality Fixes

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`ff8f89c2`)
- **Summary:** Seeded from local branch `audit/quality-fixes`, which is
  6 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0002 · Audit Webux Fixes

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`a8de0549`)
- **Summary:** Seeded from local branch `audit/webux-fixes`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0003 · Codex Fix Back To Top E2E

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`5ecf36da`)
- **Summary:** Seeded from local branch `codex/fix-back-to-top-e2e`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0004 · Codex Fix Deploy Runner Picker

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`e7e1052f`)
- **Summary:** Seeded from local branch `codex/fix-deploy-runner-picker`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0005 · Codex Fix Image Derivatives Main

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`eeaf1963`)
- **Summary:** Seeded from local branch `codex/fix-image-derivatives-main`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0006 · Codex Fix Local Guard Trigger

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`0e355770`)
- **Summary:** Seeded from local branch `codex/fix-local-guard-trigger`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0007 · Codex Issue 3230 Remaining Tests

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`8e0a1008`)
- **Summary:** Seeded from local branch `codex/issue-3230-remaining-tests`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0008 · Codex Issue 3230 Script Tests

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`0a826c32`)
- **Summary:** Seeded from local branch `codex/issue-3230-script-tests`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0009 · Codex Issue 3254 Sw Precache Cleanup

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`059a8608`)
- **Summary:** Seeded from local branch `codex/issue-3254-sw-precache-cleanup`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0010 · Codex Pr 3096 Accordion Aria

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`34fe1e83`)
- **Summary:** Seeded from local branch `codex/pr-3096-accordion-aria`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0011 · Codex Pr 3257 Current

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`ef70b175`)
- **Summary:** Seeded from local branch `codex/pr-3257-current`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0012 · Codex Pr 3257 Tail

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`14ee8c0e`)
- **Summary:** Seeded from local branch `codex/pr-3257-tail`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0013 · Codex Rl Funnel Facade Delegation

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`90f67166`)
- **Summary:** Seeded from local branch `codex/rl-funnel-facade-delegation`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0014 · Fix 3241 Spec

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`d4748e3d`)
- **Summary:** Seeded from local branch `fix/3241-spec`, which is
  7 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0015 · Fix Affinedrift Metrics Clobber 3273

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`ec259c52`)
- **Summary:** Seeded from local branch `fix/affinedrift-metrics-clobber-3273`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0016 · Fix Ball Flight Finite States 3285

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`5bacbca0`)
- **Summary:** Seeded from local branch `fix/ball-flight-finite-states-3285`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0017 · Fix Dbc Launch Conditions Finite States 3284 3285

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`0a461f82`)
- **Summary:** Seeded from local branch `fix/dbc-launch-conditions-finite-states-3284-3285`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0018 · Fix Dedup Escape Html 3291

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`ae1554b0`)
- **Summary:** Seeded from local branch `fix/dedup-escape-html-3291`, which is
  6 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0019 · Fix Exclude Internal Critic Docs 3913

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`1da2f4a2`)
- **Summary:** Seeded from local branch `fix/exclude-internal-critic-docs-3913`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0020 · Fix Golf Physics 3266 3271 3272

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`3d015a7e`)
- **Summary:** Seeded from local branch `fix/golf-physics-3266-3271-3272`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0021 · Fix Honest Unfinished Content 3918

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`fb59f8dd`)
- **Summary:** Seeded from local branch `fix/honest-unfinished-content-3918`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0022 · Fix Missing H1 Full Layout 3917

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`a338c479`)
- **Summary:** Seeded from local branch `fix/missing-h1-full-layout-3917`, which is
  1 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0023 · Fix Rotation Converter 3281 3282 3283

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`a7b810b4`)
- **Summary:** Seeded from local branch `fix/rotation-converter-3281-3282-3283`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0024 · Fix Round Simulator Tests 3293

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`6b1d3f2c`)
- **Summary:** Seeded from local branch `fix/round-simulator-tests-3293`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0025 · Fix Swing Optimizer Dt 3288

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`3626c44e`)
- **Summary:** Seeded from local branch `fix/swing-optimizer-dt-3288`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0026 · Fix Terrain Bounce Roll 3275

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`27f6adf3`)
- **Summary:** Seeded from local branch `fix/terrain-bounce-roll-3275`, which is
  3 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0027 · Issue 3221 Sw Networkfirst Local

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`e317d950`)
- **Summary:** Seeded from local branch `issue-3221-sw-networkfirst-local`, which is
  7 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0028 · Issue Golf Docs V1 Ci Fix

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`b776b73b`)
- **Summary:** Seeded from local branch `issue-golf-docs-v1-ci-fix`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0029 · Issue Mech Notation V1

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`e9d62a09`)
- **Summary:** Seeded from local branch `issue-mech-notation-v1`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0030 · Issue Sci V2

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`11a03223`)
- **Summary:** Seeded from local branch `issue-sci-v2`, which is
  6 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0031 · Issue Sec Audit V2

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`fb592f6a`)
- **Summary:** Seeded from local branch `issue-sec-audit-v2`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0032 · Issue Testing 3231 3230 3233 Local

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`3da4daca`)
- **Summary:** Seeded from local branch `issue-testing-3231-3230-3233-local`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0033 · Issue Webperf 3219 3221 3220 Local

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`938c260b`)
- **Summary:** Seeded from local branch `issue-webperf-3219-3221-3220-local`, which is
  4 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-0034 · Pr 3158 Palette

- **State:** parked
- **Owner:** unassigned
- **PR:** not created
- **Paths:** `.` — scope not yet narrowed; set real globs when
  this entry is reactivated.
- **Started:** 2026-08-28
- **Last verified:** 2026-08-28 (`0171a1d2`)
- **Summary:** Seeded from local branch `pr-3158-palette`, which is
  2 commit(s) ahead of the default branch with no
  development-log entry.
- **Parked:** 2026-08-28 — seeded during fleet rollout. Assign a
  governing issue and set `Paths` before moving this to a live
  state; a live entry without a real issue is orphaned by
  definition.

### DL-#3902 · Wire lateral links into Build pages: models, repositories, tools

- **State:** in_review
- **Owner:** claude (wave-6 agent W6_3902)
- **Issue:** `#3902` (epic `#3896`)
- **Branch:** `claude/issue-3902-models-lateral`
- **Paths:** `models/models.qmd`, `models/models-{simulink,mujoco,drake,pinocchio,pendulum,opensim,myosim}.qmd`, `repositories/*.qmd`, `pages/tools.qmd`, `articles/upstreamdrift-educational-integration.qmd`, `articles/rotation-converter.qmd`, `articles/proximal-distal-model-workbench.qmd`
- **Started:** 2026-09-07
- **Last verified:** 2026-09-07 (worktree `1ce02d7`)
- **Summary:** Added the canonical markdown `## Related Articles` component to all 8 `models/*.qmd` and all 6 `repositories/*.qmd` pages plus `pages/tools.qmd` and three isolated articles; 177 new relative markdown content links, every model↔repository pair bidirectional, every target verified to exist in the worktree. `articles/technology-heavy-hit-impact-coupling.qmd` deliberately untouched — PR #4267 (issue #3903) adds the model-interchange links there on its own branch.

- **Next step:** Merge alongside sibling wave PRs (#4265/#4266/#4267) and re-run `scripts/check_quarto_xrefs.py` on the integrated main.

## Shipped (Last 90 Days)

Entries stay here for 90 days after merge, then move to the archive.

## Archive

Older entries live in `DEVELOPMENT_LOG_ARCHIVE_<year>.md`.
