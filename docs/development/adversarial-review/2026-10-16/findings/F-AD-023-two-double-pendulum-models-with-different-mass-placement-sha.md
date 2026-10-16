# F-AD-023

**Two double-pendulum models with different mass placement share a function name**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | correctness | high | S | proposed |

**Locations:** `src/affine_control/dynamics.py:145`, `src/tools/rl_funnel_dynamics.py:22`, `src/tools/rl_funnel_dynamics.py:64`, `tests/test_critical_physics_fixes.py:36`

## Finding

- Severity: Medium  - Category: correctness / architecture
- Confidence: high
- Location: src/affine_control/dynamics.py:145-164; src/tools/rl_funnel_dynamics.py:22, 44-73; tests/test_critical_physics_fixes.py:36-41; js/drift-control-sandbox.js:15
- Evidence: `double_pendulum_mass_matrix(q, m1, m2, l1, l2)` (point masses at link midpoints, `m1/4`) vs
  `double_pendulum_mass_matrix(th1, th2)` (point masses at link ends, `(m1+m2)L1²`); both absolute angles, both
  correct for *their* model (verified), but a reader of "the double pendulum" in Volume I ch7 vs the RL-funnel
  chapter is looking at different physics with the same name and no cross-reference.
- Failure scenario: an agent "deduplicates" them (the DRY mandate tells it to) and picks one; half the worked
  examples silently change.
- Proposed change: rename the tool-side one `end_mass_double_pendulum_mass_matrix` (or parametrize mass fraction
  `c∈{0.5,1.0}` in the canonical one and derive both); document the convention in NOTATION.md.
- Verification: a test asserting the two agree when the canonical model is given `com_fraction=1.0` and `m1→4m1`.
- Effort: S

## Draft Pull Request

**Title:** `refactor(dynamics): disambiguate the two double-pendulum mass matrices`

### Why This Matters (The Pitch)

Two functions named `double_pendulum_mass_matrix` model different physics. One puts point masses at link midpoints, the other at link ends. Both are correct for their own model, but a reader of the double pendulum in Volume I chapter 7 versus the RL-funnel chapter is looking at different systems with no cross-reference. The repo's own DRY mandate invites an agent to "deduplicate" them and silently change half the worked examples. Rename the tool-side function or parametrize mass placement in the canonical one, document the convention in NOTATION.md, and add a test that the two agree under the right parameters. That removes a trap for readers and for future refactors, and keeps the textbook examples stable when someone next runs a deduplication pass.

### Proposed PR Body

## Problem
`src/affine_control/dynamics.py:145-164` defines `double_pendulum_mass_matrix(q, m1, m2, l1, l2)` with point masses at link midpoints (`m1/4`); `src/tools/rl_funnel_dynamics.py:22, 44-73` defines `double_pendulum_mass_matrix(th1, th2)` with end masses (`(m1+m2)L1^2`). `tests/test_critical_physics_fixes.py:36-41` and `js/drift-control-sandbox.js:15` relate.

## Change
- [ ] Rename the tool-side function to `end_mass_double_pendulum_mass_matrix`, or parametrize `com_fraction` in the canonical one and derive both
- [ ] Document the convention in `NOTATION.md`

## Verification
A test asserting the two agree when the canonical model is given `com_fraction=1.0` and `m1 -> 4m1`.

## Risk and Rollback
Rename touches callers in the RL-funnel tooling; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-023


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
