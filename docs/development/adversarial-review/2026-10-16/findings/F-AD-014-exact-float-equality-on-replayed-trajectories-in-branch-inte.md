# F-AD-014

**Exact float equality on replayed trajectories in branch_intervention**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | numerics | medium | S | proposed |

**Locations:** `src/affine_control/ztcf_explorer.py:161`, `tests/test_ztcf_intervention_contract.py:63`

## Finding

- Severity: Low  - Category: numerics
- Confidence: medium
- Location: src/affine_control/ztcf_explorer.py:161; tests/test_ztcf_intervention_contract.py:63-67
- Evidence: `if execute_ztcf_intervention(intervention) != intervention.expected: raise ValueError(...)` compares
  pydantic models holding floats produced by `np.linalg.solve`.
- Failure scenario: works today because both sides run the same code in-process; breaks the moment the branch
  record is loaded from JSON written by a different BLAS/platform, or `expected` is rounded for publication.
  The contract test itself uses `abs=1e-10` — the two disagree on what "replays" means.
- Proposed change: compare with `integration.absolute_tolerance` (the field already exists).
- Verification: round `expected` to 12 digits in a test and assert `branch_intervention` still accepts it.
- Effort: S

## Draft Pull Request

**Title:** `fix(ztcf): compare replayed branch trajectories with declared tolerance`

### Why This Matters (The Pitch)

A replay check that uses exact float equality works today only because both sides run the same code in one process. Load the branch record from JSON written on another platform, or round `expected` for publication, and `branch_intervention` rejects a perfectly good trajectory. The contract test already uses `abs=1e-10`, so the code and its own test disagree about what "replays" means. The integration settings already carry an `absolute_tolerance` field. Use it.

### Proposed PR Body

## Problem
`src/affine_control/ztcf_explorer.py:161` raises if `execute_ztcf_intervention(intervention) != intervention.expected`, an exact comparison of floats from `np.linalg.solve`; `tests/test_ztcf_intervention_contract.py:63-67` uses `abs=1e-10`.

## Change
- [ ] Compare against `integration.absolute_tolerance` instead of `!=`

## Verification
Round `expected` to 12 digits in a test and assert `branch_intervention` still accepts it.

## Risk and Rollback
Slightly looser acceptance, bounded by the declared tolerance; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-014


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
