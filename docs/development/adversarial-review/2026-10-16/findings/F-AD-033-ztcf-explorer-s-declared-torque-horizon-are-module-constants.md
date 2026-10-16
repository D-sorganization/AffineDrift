# F-AD-033

**ZTCF explorer's declared torque/horizon are module constants, not part of the intervention record**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | governance | medium | S | proposed |

**Locations:** `src/affine_control/ztcf_explorer.py:55`, `src/affine_control/ztcf_explorer.py:57`, `src/affine_control/ztcf_contract.py:256`

## Finding

- Severity: Low  - Category: governance
- Confidence: medium
- Location: src/affine_control/ztcf_explorer.py:55-58, 139-163; src/affine_control/ztcf_contract.py:256
- Evidence: `DECLARED_TORQUE = (40.0, 15.0, 3.0)`, `HORIZON = 0.2`, `STEPS = 200` live in code; `branch_intervention`
  writes a `ZTCFIntervention` whose `retained.controls` must be empty and which therefore cannot record the torque
  the *actual* branch used. The record "replays" but does not describe the comparison.
- Proposed change: add an `ActualBranch` sub-record (torque, horizon, steps, solver) to the explorer output and to
  the parity fixture; or store the comparison in a separate `BranchComparison` model.
- Effort: S

## Draft Pull Request

**Title:** `feat(ztcf): record actual-branch torque and horizon in explorer output`

### Why This Matters (The Pitch)

The explorer's declared torque, horizon and step count live as module constants, so the record it writes replays but does not describe the comparison it made. Add an `ActualBranch` sub-record or a separate `BranchComparison` model, and carry it into the parity fixture.

### Proposed PR Body

## Problem
`src/affine_control/ztcf_explorer.py:55-58, 139-163` holds `DECLARED_TORQUE = (40.0, 15.0, 3.0)`, `HORIZON = 0.2` and `STEPS = 200` in code; `branch_intervention` writes a `ZTCFIntervention` whose `retained.controls` must be empty (`src/affine_control/ztcf_contract.py:256`).

## Change
- [ ] Add an `ActualBranch` sub-record (torque, horizon, steps, solver) to the explorer output and parity fixture, or store it in a separate `BranchComparison` model

## Verification
Parity fixtures regenerate and the Python and JS tests still agree.

## Risk and Rollback
Schema addition; fixture digests change. Revert to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-033

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
