# F-AD-013

**source_revision model authority is a constant compared to itself**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | governance | high | S | proposed |

**Locations:** `src/affine_control/ztcf_contract.py:14`, `src/affine_control/ztcf_contract.py:228`, `data/ztcf/planar_golf_forward_fixture_v2.json:9`

## Finding

- Severity: Low  - Category: governance
- Confidence: high
- Location: src/affine_control/ztcf_contract.py:14, 212-231; data/ztcf/planar_golf_forward_fixture_v2.json:9
- Evidence: `SUPPORTED_MODEL_REVISION = "9a809cbe…"` is compared against the fixture's `source_revision`; neither is
  compared to `golf_model.py`'s bytes or to the repo HEAD (the commit is not resolvable in the shallow clone).
  The *working* pin is `tests/fixtures/widgets/ztcf-explorer.parity.json::dependency_sha256` (verified matching).
- Failure scenario: edit `GolfModel.rigid_mass_matrix`; the ZTCF contract still "supports" revision 9a809cbe…;
  only the widget parity test notices, and its failure message talks about JS mirrors, not model authority.
- Proposed change: replace `source_revision` with `source_sha256` of `golf_model.py` and check it in
  `_build_supported_model`; or drop the field.
- Verification: mutate `golf_model.py`, run `tests/test_ztcf_intervention_contract.py` → fails with a model-authority message.
- Effort: S

## Draft Pull Request

**Title:** `fix(ztcf): pin model authority to golf_model.py bytes, not a constant`

### Why This Matters (The Pitch)

The ZTCF contract's model-authority check compares a constant to itself. `SUPPORTED_MODEL_REVISION` is checked against the fixture's `source_revision`, but neither is tied to the bytes of `golf_model.py` or to repo HEAD. Edit `GolfModel.rigid_mass_matrix` and the contract still happily supports the old revision; only the widget parity test notices, and its message talks about JS mirrors, not model authority. For a contract whose purpose is to say which model produced a result, that is a gap a reviewer can find. Replace `source_revision` with a `source_sha256` of `golf_model.py` checked in `_build_supported_model`, or drop the field. Small change, and the failure message finally names the real cause. Anyone editing the model gets told at once that the contract's authority has moved.

### Proposed PR Body

## Problem
`src/affine_control/ztcf_contract.py:14, 212-231` compares `SUPPORTED_MODEL_REVISION` to the fixture's `source_revision` (`data/ztcf/planar_golf_forward_fixture_v2.json:9`); neither is compared to `golf_model.py`'s bytes or repo HEAD. The working pin is `tests/fixtures/widgets/ztcf-explorer.parity.json::dependency_sha256`.

## Change
- [ ] Replace `source_revision` with `source_sha256` of `golf_model.py` and check it in `_build_supported_model`, or drop the field
- [ ] Update the fixture accordingly

## Verification
Mutate `golf_model.py` and run `tests/test_ztcf_intervention_contract.py`; it fails with a model-authority message.

## Risk and Rollback
Fixture schema change; revert the commit to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-013

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
