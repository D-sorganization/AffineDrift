# F-AD-007

**Five copies of the same fixed-step RK4 loop**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | architecture | high | S | proposed |

**Locations:** `src/affine_control/dynamics.py:253`, `src/affine_control/golf_model.py:281`, `src/affine_control/ztcf_explorer.py:108`, `src/affine_control/ddp.py:267`, `src/affine_control/impact_contact_models.py:244`, `src/golf_simulation/ball_flight.py:380`

## Finding

- Severity: Medium  - Category: architecture
- Confidence: high
- Location: src/affine_control/dynamics.py:252-257; src/affine_control/golf_model.py:280-285; src/affine_control/ztcf_explorer.py:107-112; src/affine_control/ddp.py:267-271; src/affine_control/impact_contact_models.py:237-263; src/golf_simulation/ball_flight.py:364-385 (sixth, class method)
- Evidence: identical `k1..k4; state + dt/6*(k1+2k2+2k3+k4)` bodies; `ztcf_explorer._forced_acceleration`
  (86-89) also duplicates `GolfModel.forced_acceleration` (233-237).
- Failure scenario: the repo has a DRY gate (F-AD-019) that cannot see this; a fix to one (e.g. sampling
  clubhead speed at RK4 stages, adaptive step) silently diverges from the JS mirrors that port one of them.
- Why a newer engineer misses this: each was written by a different overnight agent in a different PR.
- Proposed change: one `src/core/integrators.py::rk4(f, x0, dt, steps, observe=None)` returning the sampled list;
  callers pass `derivative` and an `observe(state)` hook for clubhead speed.
- Verification: parity fixtures (`tests/fixtures/widgets/*.parity.json`) must still replay bit-for-bit.
- Effort: S

## Draft Pull Request

**Title:** `refactor(core): extract single rk4 integrator`

### Why This Matters (The Pitch)

Five copies of the same fixed-step RK4 loop live in the repository (a sixth is a class method in ball flight), written by different overnight agents in different PRs. In a project where Python-to-JS parity is the best thing it has, any fix to one copy, such as sampling clubhead speed at RK4 stages or adding an adaptive step, silently diverges from the others and from the JS mirrors that port one of them. The DRY gate cannot see this because it only greps a few files. The change is small: one `rk4(f, x0, dt, steps, observe=None)` in `src/core/integrators.py`, with an observe hook for clubhead speed, and the existing parity fixtures replaying bit-for-bit as the safety net. That makes the numerical core one definition to read, test and mirror, which is a reproducibility argument a reviewer can follow. It also removes roughly sixty lines.

### Proposed PR Body

## Problem
Identical `k1..k4; state + dt/6*(k1+2k2+2k3+k4)` loops sit in `src/affine_control/dynamics.py:252-257`, `golf_model.py:280-285`, `ztcf_explorer.py:107-112`, `ddp.py:267-271`, `impact_contact_models.py:237-263`, plus a class method in `src/golf_simulation/ball_flight.py:364-385`. `ztcf_explorer._forced_acceleration` (86-89) also duplicates `GolfModel.forced_acceleration` (233-237).

## Change
- [ ] Add `src/core/integrators.py::rk4(f, x0, dt, steps, observe=None)` returning the sampled list
- [ ] Switch callers to pass `derivative` and an `observe(state)` hook for clubhead speed
- [ ] Remove the duplicated `_forced_acceleration`

## Verification
Parity fixtures (`tests/fixtures/widgets/*.parity.json`) must still replay bit-for-bit.

## Risk and Rollback
Numerical results must be unchanged; any parity-fixture diff means the refactor is wrong. Revert the commit to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-007


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
