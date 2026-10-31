# Humanoid Expansion Audience Brief

Phase 0 planning deliverable for #5177 and #5172. This brief does not authorize
article production, dataset use, or site implementation.

## Audiences and Reader Outcomes

| Audience | Starting Point | Reader Outcome | Evidence to Provide |
| --- | --- | --- | --- |
| Learners moving into robotics | Linear algebra and introductory mechanics; unfamiliar with spatial notation | Follow a wrench or twist between frames and reproduce a small worked example | Prerequisite links, frame and unit definitions, derivation, runnable example |
| Practitioners comparing engines | Experience with at least one simulator | Compare MuJoCo, Drake, Pinocchio, and MJX under the same declared assumptions | Engine versions, common inputs, solver settings, measured errors and limitations |
| Researchers seeking reproducibility | Multibody dynamics and numerical methods | Reproduce and challenge a cross-validated result | Provenance, accessible artifacts, uncertainty, falsifiers and independent validation |

These audiences describe reader intent. Use the existing `audience-level` field
for technical depth; do not create a second depth taxonomy.

## Content Principles

- Use screw theory and Lie groups as the shared language across the planned
  cross-engine parity, contact/ground-reaction wrench, and whole-body MPC series.
- Declare frames, units, boundary conditions and model assumptions before results.
- Distinguish an analytical identity, a simulation result and an experimental claim.
- Show a reproducible example before scaling to a whole-body model. A missing
  backend or unavailable dataset is an explicit dependency, never a parity result.
- Follow the [editorial style guide](../development/editorial-style-guide.md).
  Keep model boundaries in the established “What This Shows / What It Does Not
  Show” block and preserve the existing evidence and publication gates.
- Reference the rights ledger before choosing data. A planning reference does not
  clear a licence or permit downloading, redistribution, or publication.

## Hand-Off to AffineDrift UX Overhaul (#5171)

Issue #5171 owns site information architecture and presentation. Its implementers
should consume this audience brief and the [metadata contract](content-metadata-schema.md)
when deciding how readers find prerequisites, series and engine comparisons.
Do not duplicate navigation, filter, layout or search design in #5177.

The contract describes planning records only. Any later ingestion into article
front matter must extend the established schema and validator deliberately;
this phase adds no site integration. The three launch outlines belong to #5178,
the reuse map to #5175, and dataset clearance to the #5176 rights ledger.
