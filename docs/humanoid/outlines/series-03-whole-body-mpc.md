# Series 3: Whole-Body MPC in Practice

Phase 0 outline for #5178, under #5172. No controller implementation, stability
claim, performance benchmark or motion dataset is delivered.

## Learning Goals

- State an MPC horizon, objective, constraints and computational budget precisely.
- Distinguish feasibility and tracking performance from a stability guarantee.
- Reproduce failures as well as successes with versioned replay artifacts.

## Prerequisites

Optimization, constrained dynamics, numerical integration, Series 1's parity
contracts and Series 2's wrench conventions. Researchers need solver and replay
provenance; practitioners need a bounded minimal example before whole-body scale.
Use #5177's metadata fields once merged, without introducing another registry.

## Planned Articles

1. From a Whole-Body State to a Finite-Horizon Problem
2. Contact Wrench Constraints and Feasibility
3. Solver Selection, Timing Budgets and Failure Handling
4. Replaying Tracking Results Across Declared Engine Contracts

## Engines and Datasets

Resolve every candidate to `docs/humanoid/rights-licence-ledger.md` (#5176).
All are **not cleared** by this outline; a planning mention grants no data rights.

| Candidate | Intended Use | Required Ledger Row |
| --- | --- | --- |
| MuJoCo and Drake (one row each) | Simulated tracking and replay outputs | Engine/version, model and derived artifact rights |
| Pinocchio | Dynamics computations if supported by the validated reuse map | Engine/version and model artifacts |
| Synthetic target trajectories | Reproducible minimal controller examples | Authored targets, model and derived replay artifacts |
| AMASS | Possible later motion targets only | AMASS remains ON-HOLD; no download, processing or publication until owner clearance |

AMASS is excluded from selected inputs while ON-HOLD. Use no private motion
capture data or invented licence facts to fill the gap.

## UpstreamDrift Dependencies

#5175 owns the optimizer backend registry (UD ADR-0050), replay benchmarks,
screw/wrench utilities and their contract-validation checklist. Require evidence
for supported backends, units, failure statuses and timing provenance before
claiming a working controller. #5174's ADR-0003 governs phase transitions.
All heavy dynamics and optimization stay in UD; AD consumes outputs only.
Unknown or unvalidated capabilities remain explicitly blocked.

## Common Thread

Use Lie groups for pose errors and integration, and screw theory for twists,
wrenches and contact constraints. Preserve those conventions across all series.

## Publication Gate

Later articles require Karl → Feynman → panel → Fleet-Critic → Dieter's sign-off.
Article PRs carry `do-not-merge`. Outlines, synthetic examples and named engines
alone do not satisfy the publication gate or approve implementation.
