# F-AD-035

**LQR convergence uses an absolute 1e-14 tolerance on S**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | numerics | medium | S | proposed |

**Locations:** `src/affine_control/lqr.py:31`, `src/affine_control/lqr.py:139`

## Finding

- Severity: Low  - Category: numerics
- Confidence: medium
- Location: src/affine_control/lqr.py:31, 139
- Evidence: `np.max(np.abs(s_next - s)) < 1e-14` — for a textbook problem with `‖S‖≈1` fine; for `Q=diag(1e3)` the
  fixed-point iteration will chatter at ~1e-13 and raise "did not converge" after 10,000 iterations.
- Proposed change: `tol * max(1.0, np.max(np.abs(s)))`, or use `scipy.linalg.solve_discrete_are` as oracle in tests.
- Effort: S

## Draft Pull Request

**Title:** `fix(lqr): scale Riccati convergence tolerance to the magnitude of S`

### Why This Matters (The Pitch)

An absolute 1e-14 tolerance on S works for unit-scale problems but chatters near 1e-13 for something like Q=diag(1e3), then raises a spurious "did not converge". Use a relative tolerance, or SciPy's discrete ARE solver as a test oracle.

### Proposed PR Body

## Problem
`src/affine_control/lqr.py:31, 139` tests `np.max(np.abs(s_next - s)) < 1e-14`.

## Change
- [ ] Use `tol * max(1.0, np.max(np.abs(s)))`
- [ ] Optionally use `scipy.linalg.solve_discrete_are` as an oracle in tests

## Verification
A test with `Q=diag(1e3)` converges and matches the oracle.

## Risk and Rollback
Slightly looser absolute stopping point on large-scale problems; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-035


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
