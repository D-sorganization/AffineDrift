# Series 2: Contact and Ground-Reaction Wrenches

Phase 0 outline for #5178, under #5172. No force estimates, datasets or
experimental validation are delivered here.

## Learning Goals

- Express contact forces and moments as a wrench with an explicit reference point.
- Separate measured ground reactions from model-dependent contact estimates.
- Check balance residuals and describe what a contact model cannot identify.

## Prerequisites

Statics, rigid-body dynamics, cross products, coordinate transforms and Series 1's
frame/unit contract. Learners need a worked wrench transform before whole-body
examples. #5177 owns the audience and metadata vocabulary when merged.

## Planned Articles

1. From Contact Forces to a Spatial Wrench
2. Moving the Ground-Reaction Reference Point
3. Contact Constraints and Whole-Body Balance Residuals
4. Comparing Contact Outputs Under Explicit Model Assumptions

## Engines and Datasets

The #5176 ledger, `docs/humanoid/rights-licence-ledger.md`, owns clearance.
Candidates below are **not cleared** by this outline; create or resolve exact
artifact rows before use, including use of engine outputs in published figures.

| Candidate | Intended Use | Required Ledger Row |
| --- | --- | --- |
| MuJoCo and Drake (one row each) | Contact simulations and comparison outputs | Engine/version, model and redistributed artifacts |
| Pinocchio | Wrench transforms and dynamics cross-checks | Engine/version and consumed model artifacts |
| Synthetic contact traces | Check transforms and balance with known inputs | Authored trace, model and derived outputs |
| Any future measured force-plate data | Compare a model with observations | Named dataset, consent/licence and permitted derived publication; no dataset selected |

## UpstreamDrift Dependencies

Consume #5175's screw/wrench math and parity/replay rows only after their
input frames, wrench ordering, units, reference points and validation gaps are
recorded. Pin exact output versions. UD produces dynamics and residuals; AD
renders and explains those outputs. A numerical consistency check must not be
presented as experimental validation of human contact forces.

## Common Thread

Use screw theory to transform wrenches and Lie groups to track contact frames.
The common frame convention connects this series to parity and whole-body MPC.

## Publication Gate

Later articles require Karl → Feynman → panel → Fleet-Critic → Dieter's sign-off.
Article PRs carry `do-not-merge`. #5174's ADR-0003 scope and phase decisions still
apply; this outline authorizes neither measurement collection nor article production.
