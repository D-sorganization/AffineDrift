# F-AD-008

**~9.7k LOC of fail-closed protocol declarations that validate prose for unrun experiments**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | architecture | high | L | proposed |

**Locations:** `src/affine_control/impedance_protocol.py:33`, `src/affine_control/impedance_protocol.py:105`, `src/affine_control/impedance_fixtures.py:57`, `src/affine_control/research_readiness/states.py:8`

## Finding

- Severity: Medium  - Category: architecture / governance
- Confidence: high
- Location: src/affine_control/impedance_protocol.py:33-48, 88-126; src/affine_control/impedance_fixtures.py:55-120; plus `hand_wrench_*`, `neural_timing_*`, `population_generalization*`, `equipment_response*`, `model_ladder*`, `impact_contact_{protocol,fixtures,uncertainty}`, `research_readiness/*`, `evidence_presentation/*`, `falsification_atlas/*`, `research_releases/*`, `historical_research/*`
- Evidence: 87 `__post_init__` validators; 162 `_require_text(...)`/"must be declared" calls, e.g.
  ```python
  SafetyEnvelope(device_id="simulated-torque-pulse-device/v1", device_revision="synthetic-feasibility-only",
                 hardware_stop="independent torque, displacement, and velocity interlock", ...)
  ```
  The validators check that strings are non-blank and floats are positive. `research_readiness/states.py:8-20`
  defines a 12-state lifecycle; the data shows 16 protocols at `simulation-ready`, none further.
- Failure scenario: 27 % of `src/` (and the coverage number) is dataclasses holding experiment-plan prose. It costs
  review time, inflates "coverage", and creates the impression of an experimental program. None of it can be wrong
  in a way a test could catch, so TDD on it is motion without progress.
- Why a newer engineer misses this: DbC says "validate inputs"; applied to prose it degenerates into checking
  that the prose exists. The right home for a protocol declaration is a JSON/YAML file validated by a schema
  (which this repo already has: `schemas/research-protocol-readiness-v1.schema.json`).
- Proposed change: move the declarations to `data/research_protocols/*.json` validated by the existing schemas;
  keep only the few functions that compute something (`impedance_protocol` regression matrices,
  `impact_contact_models` solvers). Expected deletion ≈ 7–8k LOC.
- Verification: `jsonschema` validation test per protocol file; coverage floor recomputed on what remains.
- Effort: L

## Draft Pull Request

**Title:** `refactor(protocols): move prose declarations to schema-validated JSON`

### Why This Matters (The Pitch)

About 9.7k lines, 27 % of src, hold experiment-plan prose in dataclasses with 87 validators that mostly check that strings are non-blank and floats are positive. The data shows sixteen protocols at `simulation-ready` and none further, so this is a large apparatus for experiments nobody has run. It costs review time, inflates the coverage number, and gives readers the impression of an experimental program that does not exist, which is a credibility risk in its own right. None of it can be wrong in a way a test could catch, so test-driven work on it is motion without progress. The repository already has the right home for it, `schemas/research-protocol-readiness-v1.schema.json`. Moving the declarations to JSON and keeping only the functions that compute something is expected to delete roughly 7 to 8k LOC. This is the biggest simplification on the list: less to clone, lint, read and defend, and a kernel that is visibly the substance of the repository. Effort is L, so schedule it deliberately.

### Proposed PR Body

## Problem
`src/affine_control/impedance_protocol.py:33-48, 88-126` and `impedance_fixtures.py:55-120`, plus the `hand_wrench_*`, `neural_timing_*`, `population_generalization*`, `equipment_response*`, `model_ladder*`, `research_readiness/`, `evidence_presentation/`, `falsification_atlas/`, `research_releases/` and `historical_research/` families, hold declarations as dataclasses with 87 `__post_init__` validators and 162 "must be declared" calls.

## Change
- [ ] Move declarations to `data/research_protocols/*.json` validated by the existing schemas
- [ ] Keep only functions that compute something (`impedance_protocol` regression matrices, `impact_contact_models` solvers)
- [ ] Delete the superseded dataclass modules (expected about 7-8k LOC)
- [ ] Recompute the coverage floor on what remains

## Verification
A `jsonschema` validation test per protocol file; coverage floor recomputed.

## Risk and Rollback
Large diff but mechanical; do it per family so any one can be reverted. Coverage percentage may move because denominator shrinks.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** Follow-ups: per-family follow-up PRs if this is split.

Refs: adversarial review 2026-10-16, F-AD-008


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._
