# F-AD-029

**Dead physics constants with undocumented provenance**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | hygiene | high | S | proposed |

**Locations:** `src/core/constants.py:114`, `src/core/constants.py:117`, `src/golf_simulation/putting.py:22`

## Finding

- Severity: Low  - Category: hygiene
- Confidence: high
- Location: src/core/constants.py:114-118; src/golf_simulation/putting.py:22-30
- Evidence: `HOLE_CAPTURE_SPEED_MS = 1.5` and `STIMPMETER_CALIBRATION_FACTOR = 1.285` are imported nowhere;
  `putting.py:22-30` derives deceleration from first principles (`1.83²/(2·stimp·0.3048)`) instead. 1.285 has no
  citation; "Physics constants are not overridable — the speed of light is not a config option" (constants.py:19)
  is undercut by a magic calibration factor with no source.
- Proposed change: delete both or cite (Penner 2002 for hole capture ≈ 1.31 m/s on a flat green).
- Effort: S

## Draft Pull Request

**Title:** `chore(constants): delete or cite two unused physics constants`

### Why This Matters (The Pitch)

`HOLE_CAPTURE_SPEED_MS` and `STIMPMETER_CALIBRATION_FACTOR` are imported nowhere, and 1.285 has no citation in a file that says physics constants are not configurable. Delete them or cite a source.

### Proposed PR Body

## Problem
`src/core/constants.py:114-118` defines both constants; `src/golf_simulation/putting.py:22-30` derives deceleration from first principles instead.

## Change
- [ ] Delete both constants, or add a citation (the finding suggests Penner 2002 for hole capture)

## Verification
Grep confirms no importers; tests still pass.

## Risk and Rollback
Unused code; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-029


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
