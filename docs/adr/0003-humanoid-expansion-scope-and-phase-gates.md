# 0003. Humanoid Expansion Scope and Phase Gates

## Status

Proposed for #5174 under the deferred, planning-only epic #5172.
Dieter's approval is the phase-0 exit gate. This record does not supply that
approval or authorize implementation, publication or artifact use.

## Context

A humanoid expansion can connect the existing multibody and control material
without creating a second simulation authority. Planning must separate the
educational scope from computational qualification, artifact rights and delivery
approval. The project charter excludes replacing reusable Tools kernels or
UpstreamDrift's executable studies.

## Decision

### Initial Pillars

The proposed scope has three initial pillars:

1. **Cross-engine parity:** explain comparable model assumptions, coordinates,
   units, fixtures and error budgets using qualified upstream comparisons.
   Numerical agreement is not physical validation.
2. **Whole-body dynamics, contact and locomotion:** explain articulated models,
   constraints, contact assumptions, balance and gait using evidence with explicit
   applicability limits.
3. **Trajectory optimisation and MPC:** explain objectives, constraints, horizons
   and controller assumptions through reproducible upstream results.

Screw theory and Lie groups provide the common thread: coordinate frames, rigid
transforms, twists and wrenches connect geometry to dynamics and control. Their
notation and conventions must remain consistent across the three pillars.

### Responsibility Boundary

AffineDrift is presentation-only for this expansion: it owns pedagogy, sanitized
visualization and immutable evidence projections; heavy dynamics remain in UpstreamDrift.
Reusable kernels and interchange contracts remain with their upstream owners.
Do not copy solver implementations or import cross-repository Python runtime code.

This extends the publication boundary in
[ADR-0001](0001-markerless-mocap-publication-boundary.md), whose original scope is
markerless mocap; it does not reclassify that ADR as a humanoid validation result.
The [project charter](../project/CHARTER.md) likewise keeps executable studies
outside AffineDrift. Every public result must identify its qualified upstream
revision, assumptions and claim class; missing evidence remains unavailable.

### Non-Goals and Deferred Topics

Phase 0 produces planning documents only. It does not add humanoid runtime code,
site navigation, articles, robot deployment or a new asset registry. It does not
qualify hardware safety, clinical performance, general-purpose autonomy or
physical human/robot parity.

Defer hardware integration, sim-to-real claims, imitation/foundation-model
training and unreviewed model or dataset adoption. Revisit each through a scoped
proposal with evidence, rights review and explicit owner approval; listing a
topic here does not authorize it.

### Delivery Process

Use small PRs to `main`, each independently reviewable and below the fleet size
cap. Unfinished implementation stays behind default-off feature flags.
Research-only branches are never shipped; accepted findings must be recast as
bounded, tested changes against current `main` after the relevant phase gate.
Do not stack delivery on unmerged prerequisites or publish speculative results.

### Phase Gates

- **Phase 0 — Planning:** assemble this ADR, the upstream reuse map, rights ledger,
  audience/metadata brief and launch outlines (#5175–#5178). Reconcile every
  proposed artifact against a recorded rights decision; held or rejected assets
  remain excluded. Record open questions and deferred claims.
  Dieter's approval is the phase-0 exit gate; merged planning documents alone
  do not open phase 1.
- **Phase 1 — Qualified Foundations:** after approval, complete pillar 1's
  prerequisites: D-sorganization/UpstreamDrift#13789 and the MJX benchmark work
  (including UpstreamDrift #13786). Require protected, revision-pinned evidence,
  explicit model/coordinate contracts and bounded comparison criteria before
  presenting parity claims. This ADR does not assert those prerequisites are done.
- **Phase 2 — Bounded Educational Delivery:** deliver approved slices across the
  three pillars only with qualified upstream evidence, approved artifact use,
  reproducibility checks and reviewed notation. Keep incomplete work disabled;
  demonstrate each slice's acceptance before enabling it.
- **Later Expansion:** hardware, additional datasets and deferred topics need
  separate scope and gate decisions. No automatic progression follows from
  merging a phase or closing an issue.

## Consequences

The series gains a common conceptual spine and an explicit computational owner.
Delivery can proceed in small increments after approval without shipping research
branches or duplicating dynamics. It must wait when prerequisite evidence, rights
decisions or owner approval are missing. No licence approval, parity validation,
new site structure or implementation is claimed by this planning record.
