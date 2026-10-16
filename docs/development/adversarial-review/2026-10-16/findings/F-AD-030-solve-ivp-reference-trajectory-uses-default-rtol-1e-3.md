# F-AD-030

**solve_ivp reference trajectory uses default rtol=1e-3**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | numerics | high | S | proposed |

**Locations:** `src/tools/rl_funnel_dynamics.py:117`, `src/affine_control/series_elastic_demo.py:113`

## Finding

- Severity: Low  - Category: numerics
- Confidence: high
- Location: src/tools/rl_funnel_dynamics.py:117-123; src/affine_control/series_elastic_demo.py:113-115
- Evidence: `solve_ivp(double_pendulum_drift, t_span, x0, max_step=dt, dense_output=True)` — no `rtol/atol`; the
  default RK45 at 1e-3 relative on a chaotic double pendulum over seconds is not a "reference".
- Proposed change: `method="DOP853", rtol=1e-10, atol=1e-12` as `series_elastic_demo.py:113-115` already does.
- Effort: S

## Draft Pull Request

**Title:** `fix(numerics): tighten solve_ivp tolerances in RL-funnel reference`

### Why This Matters (The Pitch)

A "reference" chaotic double-pendulum trajectory is computed with default RK45 tolerances (rtol 1e-3). Use DOP853 with tight tolerances, as `series_elastic_demo.py` already does.

### Proposed PR Body

## Problem
`src/tools/rl_funnel_dynamics.py:117-123` calls `solve_ivp(double_pendulum_drift, t_span, x0, max_step=dt, dense_output=True)` with no `rtol/atol`; `src/affine_control/series_elastic_demo.py:113-115` uses tight tolerances.

## Change
- [ ] Pass `method="DOP853", rtol=1e-10, atol=1e-12`

## Verification
Compare the new trajectory against the old over the chapter's time span and update any dependent expectations.

## Risk and Rollback
Reference values may shift slightly; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-030


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
