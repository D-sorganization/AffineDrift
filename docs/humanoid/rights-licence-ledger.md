# Humanoid Expansion Rights and Licence Ledger

Phase 0 planning for #5172 and #5176. This ledger grants no permission to use
an artifact. Nothing is used before a decision is recorded for the exact
artifact version and intended use. No datasets or models are fetched here.

## Ledger Template and Initial Reviews

Copy a row for each concrete model, dataset, sub-dataset or other artifact.
Replace the candidate version with an immutable release, revision or identifier
before review. Collection-level entries below do not approve their members.

| Artifact                         | Version                                    | Licence                                                | Intended Use                                                                     | Reviewer   | Decision |
| -------------------------------- | ------------------------------------------ | ------------------------------------------------------ | -------------------------------------------------------------------------------- | ---------- | -------- |
| MuJoCo Menagerie models          | Not selected; pin each model revision      | Review per model; licences vary                        | Candidate model illustrations and cross-engine comparisons; scope to be reviewed | Unassigned | PENDING  |
| Unitree robot models (URDF/MJCF) | Not selected; pin each model revision      | Pending review per model and included asset            | Candidate robot geometry for educational comparisons; scope to be reviewed       | Unassigned | PENDING  |
| Open X-Embodiment                | Not selected; pin each sub-dataset version | Pending review per sub-dataset                         | Candidate trajectory examples; scope to be reviewed                              | Unassigned | PENDING  |
| LeRobot datasets/models          | Not selected; pin each artifact revision   | Pending review per artifact                            | Candidate dataset/model examples; scope to be reviewed                           | Unassigned | PENDING  |
| AMASS                            | Not selected                               | Terms not reviewed; no licence interpretation recorded | No use while on hold; proposed use must be specified for review                  | Unassigned | ON-HOLD  |
| MuJoCo engine | Not selected; pin release and artifact set | Pending review of selected release and redistributed artifacts | Parity benchmarks, contact comparisons and simulated MPC replay | Unassigned | PENDING |
| Drake engine | Not selected; pin release and artifact set | Pending review of selected release and redistributed artifacts | Parity benchmarks, contact comparisons and simulated MPC replay | Unassigned | PENDING |
| Pinocchio engine | Not selected; pin release and artifact set | Pending review of selected release and redistributed artifacts | Parity comparisons, wrench transforms and dynamics cross-checks | Unassigned | PENDING |
| MJX engine | Not selected; pin release and artifact set | Pending review of selected release and redistributed artifacts | Batched parity and throughput examples; no agreement result asserted | Unassigned | PENDING |
| Synthetic benchmark inputs and output traces | Not selected; pin authored inputs, model and outputs | Pending review of authorship and all included model assets | Reproduce the proposed cross-engine comparison | Unassigned | PENDING |
| Synthetic contact traces | Not selected; pin authored traces, model and outputs | Pending review of authorship and all included model assets | Check transforms and balance with known inputs | Unassigned | PENDING |
| Synthetic target trajectories | Not selected; pin authored targets, model and replay outputs | Pending review of authorship and all included model assets | Reproducible minimal controller examples | Unassigned | PENDING |
| Any future measured force-plate data | No dataset selected | Pending review of a named dataset, consent and permitted derived outputs | Candidate model-observation comparisons; no data collection authorized | Unassigned | PENDING |

## Outline Candidate Reconciliation

The additional rows above record candidates from the three #5178
[launch outlines](outlines/). They do not select an engine release or dataset.
Grouped engine mentions in an outline resolve to a separate `engine` row for
each named engine; the MuJoCo engine is distinct from the Menagerie model
collection. Synthetic inputs also need review of authorship, included model
assets and derived outputs; the word "synthetic" grants no clearance.

These entries make the remaining reviews visible, not complete. Replace each
planning placeholder with its exact version and intended-use evidence before
any decision to use it. Every additional row remains PENDING with an unassigned
reviewer. The original five candidates and AMASS's ON-HOLD status are unchanged;
phase-0 exit still requires Dieter's approval.

## Decision Evidence

For each review, record the artifact row identifier, exact version, authoritative
terms link and review date, intended use (including redistribution or derived
outputs), named reviewer, decision rationale and applicable restrictions. Link
that record from the decision cell. A missing version, reviewer or evidence
record keeps the decision PENDING; it must not be treated as approval.

Possible review outcomes are APPROVED for the documented use only, REJECTED,
PENDING or ON-HOLD. A changed artifact version or intended use requires a new
review. Never infer a member's licence from its collection or project name.

## AMASS Hold and Phase-0 Exit

AMASS remains ON-HOLD until its terms are reviewed against a specific intended
use and a decision is recorded. This document does not interpret AMASS terms.

Before phase-0 exit, reconcile every artifact referenced by the series outlines
with this ledger: each must have an exact version and an evidence-backed
decision. Pending candidates cannot be used. Rejected and held artifacts stay
excluded from use; substitute an approved artifact or defer the affected work.
This initial template does not establish that the outlines are reconciled or
that phase 0 is complete. Dieter's approval remains the phase-0 exit gate.
