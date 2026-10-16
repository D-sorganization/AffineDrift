# F-AD-015

**Gravity constant defined six times, bypassing src.core.constants**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | hygiene | high | S | proposed |

**Locations:** `src/affine_control/ztcf_contract.py:12`, `src/affine_control/golf_model.py:35`, `src/affine_control/rnea.py:36`, `src/affine_control/ideomotor_demo.py:18`, `src/golf_simulation/round_simulator.py:43`, `src/core/constants.py:108`

## Finding

- Severity: Low  - Category: hygiene
- Confidence: high
- Location: src/affine_control/ztcf_contract.py:12; src/affine_control/golf_model.py:35; src/affine_control/rnea.py:36; src/affine_control/ideomotor_demo.py:18; src/golf_simulation/round_simulator.py:43; src/core/constants.py:108; js/ztcf-explorer.js:15; js/drift-control-sandbox.js:15
- Evidence: all `9.81`; `constants.py:1-6` says it exists "to collect magic numbers previously scattered".
  `ztcf_contract.py:13` bakes the value into a protocol string (`"uniform gravity at 9.81 m/s^2"`) that is
  then compared by equality (line 260).
- Failure scenario: someone "corrects" one copy to 9.80665; the contract string no longer matches, widget parity
  breaks, and the JS mirror disagrees with Python by 0.03 %.
- Proposed change: import from `src.core.constants`; generate the JS constant into `*-data.js` like the arm viewer does.
- Verification: `grep -rn "9\.81" src js | wc -l` → 1 (constants.py).
- Effort: S

## Draft Pull Request

**Title:** `refactor(constants): use src.core.constants for gravity everywhere`

### Why This Matters (The Pitch)

Gravity is defined as 9.81 in six places while `src/core/constants.py` exists to collect exactly this kind of scattered number. One value is baked into a protocol string compared by equality, so a well-meaning change to 9.80665 in one file breaks widget parity, and the JS mirror would then disagree with Python by 0.03 %. Import the constant and generate the JS value into the `*-data.js` files the way the arm viewer already does.

### Proposed PR Body

## Problem
Gravity `9.81` is defined in `src/affine_control/ztcf_contract.py:12`, `golf_model.py:35`, `rnea.py:36`, `ideomotor_demo.py:18`, `src/golf_simulation/round_simulator.py:43`, `src/core/constants.py:108`, `js/ztcf-explorer.js:15` and `js/drift-control-sandbox.js:15`. `ztcf_contract.py:13` embeds it in a protocol string compared by equality at line 260.

## Change
- [ ] Import gravity from `src.core.constants` in the Python modules
- [ ] Generate the JS constant into `*-data.js` like the arm viewer

## Verification
`grep -rn "9\.81" src js | wc -l` returns 1 (constants.py).

## Risk and Rollback
Values are unchanged, so behavior is identical; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-015


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
