# Series 1: Humanoid Cross-Engine Parity

Phase 0 outline for #5178, under #5172. Titles and learning targets only;
no article draft or validated parity result is supplied.

## Learning Goals

- Distinguish agreement on a declared benchmark from general engine equivalence.
- Reproduce a frame, unit and solver contract before comparing outputs.
- Report tolerances, uncertainty and failures alongside successful comparisons.

## Prerequisites

Rigid-body transforms, Jacobians, numerical integration and basic test design.
Use #5177's audience brief and metadata contract when those documents land;
practitioners are the primary audience, with derivation links for learners.

## Planned Articles

1. A Common State, Frame and Unit Contract
2. One Benchmark Across MuJoCo, Drake and Pinocchio
3. MJX: Batch Throughput Versus Numerical Agreement
4. Reading a Cross-Engine Disagreement Without Hiding It

## Engines and Datasets

Each candidate below needs a row in `docs/humanoid/rights-licence-ledger.md`
(#5176), covering the exact version, artifacts and intended use. All selections
are **not cleared** in this outline; verify the ledger rather than inferring rights.

| Candidate | Intended Use | Required Ledger Row |
| --- | --- | --- |
| MuJoCo, Drake, Pinocchio, MJX (one row each) | Execute the same declared benchmark | Exact engine/version and any redistributed artifacts |
| Synthetic benchmark inputs and output traces | Reproduce the comparison | Exact authored inputs, models and output artifacts; no external motion data assumed |

## UpstreamDrift Dependencies

#5175 supplies the reuse map and contract-validation checklist. Its parity harness
and replay rows must identify input/output units, versions and actual evidence.
UD #13789 and the MJX benchmark work (including #13786) are references to check,
not proof of readiness or authorization to modify those issues. Heavy dynamics
stays in UD; AD consumes versioned outputs only. Missing evidence blocks results.

## Common Thread

Use screw theory for twists and wrenches and Lie groups for pose integration;
compare quantities only after mapping both engines to the same declared frame.

## Publication Gate

Later articles require Karl → Feynman → panel → Fleet-Critic → Dieter's sign-off.
Article PRs carry `do-not-merge`. Phase 0 outlines do not pass this gate or
replace the scope and phase decisions tracked by #5174 (ADR-0003).
