# Humanoid Expansion: Phase 0 Planning Index

Phase 0 planning artifacts for the humanoid expansion epic (#5172).

This expansion connects multibody dynamics, contact mechanics, and trajectory optimisation
for humanoid robotics while maintaining a strict presentation-only boundary for AffineDrift.
Heavy dynamics, contact solves, and numerical optimisations remain in UpstreamDrift.

All artifacts here are planning deliverables only and make no claim of implementation,
publication, or dataset clearance. Dieter's explicit approval is the Phase 0 exit gate
([ADR 0003](../adr/0003-humanoid-expansion-scope-and-phase-gates.md)). Merging planning
documents alone does not open Phase 1.

## Phase 0 Planning Artifacts

| Artifact | Issue | Description | Status / Gate |
| --- | --- | --- | --- |
| [ADR 0003: Scope and Phase Gates](../adr/0003-humanoid-expansion-scope-and-phase-gates.md) | #5174 | Defines three initial pillars, responsibility boundary, non-goals, and phase gates. | Proposed; Dieter's sign-off required for Phase 0 exit |
| [UpstreamDrift Reuse Map](upstream-reuse-map.md) | #5175 | Four scoped candidate components from UpstreamDrift with contracts, gaps, and unticked validation checklists. | Planning only; all rows unvalidated for humanoid use |
| [Rights & Licence Ledger](rights-licence-ledger.md) | #5176 | Review decisions and license clearance for models and datasets (e.g. MuJoCo Menagerie, Unitree, AMASS). | Fail-closed; AMASS ON-HOLD; models PENDING review |
| [Audience Brief](audience-brief.md) | #5177 | Target personas (Learners, Practitioners, Researchers), reader outcomes, and UX hand-off contract. | Planning deliverable for #5171 hand-off |
| [Content Metadata Schema](content-metadata-schema.md) | #5177 | Contract and schema specification for humanoid outline metadata, extending existing front-matter rules. | Planning contract; no automated article ingestion |
| [Launch Series Outlines](outlines/) | #5178 | Pedagogical outlines for initial pillars: [Series 01 (Cross-Engine Parity)](outlines/series-01-cross-engine-parity.md), [Series 02 (Contact GRF Wrenches)](outlines/series-02-contact-grf-wrenches.md), and [Series 03 (Whole-Body MPC)](outlines/series-03-whole-body-mpc.md). | Planning outlines; editorial and publication gates apply |

## Responsibility Boundary

As established in [ADR 0001](../adr/0001-markerless-mocap-publication-boundary.md) and
[ADR 0003](../adr/0003-humanoid-expansion-scope-and-phase-gates.md):
- AffineDrift is **presentation-only**: pedagogy, sanitized visualizations, and immutable evidence projections.
- UpstreamDrift owns **computational authority**: heavy dynamics, contact solvers, and trajectory optimisations.
- No solver code or cross-repo execution runtimes are duplicated or imported into AffineDrift.
