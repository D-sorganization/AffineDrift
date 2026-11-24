# Humanoid Expansion: UpstreamDrift Reuse Map

Phase 0 planning for #5172 and #5175. This map grants no permission to build
anything and makes no parity claim beyond the evidence it cites. Paths are in
`D-sorganization/UpstreamDrift` (UD), read from `main` on 2026-11-06. Nothing
here was executed to produce it: "validation evidence" means evidence that
already exists in UD, and "not yet validated" means this map found none that
covers the claim.

## Boundary

[ADR 0003](../adr/0003-humanoid-expansion-scope-and-phase-gates.md) and
[ADR 0001](../adr/0001-markerless-mocap-publication-boundary.md) keep AffineDrift
(AD) presentation-only. Heavy dynamics, contact solves and optimisation stay in
UD. AD consumes UD outputs (reports, receipts, figures' source data) and does
not import or re-implement UD solvers. A row below is a candidate for AD to
read an output from, never for AD to run.

## Reuse Rows

Each checklist item must be ticked with a link to the evidence before a row is
relied on. An unticked item means the row is not yet usable for that purpose.

### 1. Cross-Engine Parity Harness and Benchmarks

| Field | Entry |
| --- | --- |
| Provides | A specification and verifier for running one fitted torque profile through Simscape, MuJoCo, Pinocchio and Drake, plus per-engine replay overlays. |
| Where in UD | `docs/development/cross_engine_parity/CROSS_ENGINE_GOLF_EQUIVALENCE_SPEC.md`; `docs/development/full_body_models/evidence/fb6_parity/verify_cross_engine_parity.py`; epic UD#13789. |
| Contract | Inputs are a canonical model definition and a polynomial torque profile; the outputs are per-engine trajectories compared against the oracle. Units and tolerances are defined in the spec, not restated here. |
| Existing evidence | The fb6 parity replays under `evidence/fb6_parity/replays/` (overlay files for Drake, MuJoCo and Pinocchio at one commit hash). |
| Gaps | UD#13789 (sensitivity-aware parity for the 3-DOF swing model) is open, so the epic as a whole is not validated. The existing evidence is golf-swing specific; **nothing here is validated for a humanoid model.** |

- [ ] Contract (inputs, outputs, units, preconditions) read from the spec and linked
- [ ] Evidence receipt for the exact commit linked
- [ ] UD#13789 closed, or the row restricted to what is already receipted
- [ ] Humanoid applicability shown, not assumed

### 2. Screw / Wrench Math Utilities

| Field | Entry |
| --- | --- |
| Provides | A spatial wrench type with a declared frame, application point, sign convention and SI units; transforms to a new frame and point; joint-torque and world-frame wrench conversions. |
| Where in UD | `src/shared/python/motion_matching/force_torque.py` (`SpatialWrench`, `transform_wrench`); `src/shared/python/force_overlay/conversions.py` (`joint_torque_wrench`, `world_wrench_from_local`, `move_wrench_point`). |
| Contract | Every wrench states its application frame and point and uses SI units; `application_frame` must be a non-empty string; vectors are validated as finite 3-vectors. Preconditions on rotation matrices are in the module, not restated here. |
| Existing evidence | Unit tests exist under UD `tests/`; this map did not run them. |
| Gaps | No evidence found that these utilities are validated for floating-base humanoid kinematics or for Lie-group (SE(3)) composition beyond single rigid-body transforms. Treat as **not yet validated** for the screw-theory pillar. |

- [ ] Contract read from the module docstrings and linked
- [ ] Passing test run for a named commit linked
- [ ] SE(3) composition and sign conventions checked against the pillar-3 outline
- [ ] Humanoid applicability shown, not assumed

### 3. Optimizer Backend Registry (UD ADR-0050)

| Field | Entry |
| --- | --- |
| Provides | One registry that records which optimisation backends exist, which problem class each serves and whether each is importable, replacing a string compare in the optimiser. |
| Where in UD | `src/shared/python/optimization/backend_registry.py`; decision in `docs/adr/0050-optimizer-backend-registry-and-bioptim.md` (Accepted, 2026-09-08); `tests/unit/optimization/test_backend_registry.py`. |
| Contract | A backend is looked up by name; unknown names keep the previous behaviour. The ADR records that several backends need conda-forge packages and are not pip-installable, which constrains where AD could ever run them. |
| Existing evidence | ADR-0050 and its registry tests. |
| Gaps | The registry describes the seven-DOF swing optimisation. **No evidence found for humanoid-scale problems.** Some backends were recorded as physically wrong in the ADR's context (placeholder inertials, no between-node dynamics); whether those were fixed is for the ADR's follow-up issues to show, not this map. |

- [ ] Registry contract and the current backend list linked
- [ ] The ADR's follow-up issues (#9755, #9756) read and their status recorded
- [ ] Humanoid-scale applicability shown, not assumed

### 4. Replay Benchmarks

| Field | Entry |
| --- | --- |
| Provides | Head-to-head optimiser benchmarks that rescore every candidate through one shared simulator replay, with receipts. |
| Where in UD | `scripts/benchmark_mjx_knot_solvers.py`; `docs/development/full_body_models/evidence/mjx_benchmark_lbfgs60/REPORT.md` (generated from receipts); related UD#13786 (closed). |
| Contract | Reports carry provenance (commit, interpreter and package versions, host) and state their solver choices and promotion rule. Numbers come from receipts. |
| Existing evidence | The linked REPORT.md for captures `driver` and `iron`. |
| Gaps | Two golf captures on one host. **Not validated** for other models, hosts or humanoid motion. The report's own incumbent receipts were reused from an earlier commit, which the report discloses; AD must repeat that disclosure if it cites numbers. |

- [ ] Report and receipts for the cited commit linked
- [ ] Provenance block copied with any figure that cites it
- [ ] UD#13789 / MJX prerequisites closed before any pillar-1 parity claim
- [ ] Humanoid applicability shown, not assumed

## Confirmation

- Heavy dynamics stay in UD; AD consumes outputs only (ADR 0003, ADR 0001).
- Every row above is marked not yet validated for humanoid use.
- No row asserts that UD#13789 or the MJX benchmark work is complete.
- Approval of this map is Dieter's phase-0 call; merging it does not supply it.
