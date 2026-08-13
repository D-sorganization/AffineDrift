# Terminology Decision Record

## Status and Scope

**Status:** Ratified for AffineDrift and the conforming UpstreamDrift research
profile under AffineDrift epic #3834.

This record resolves the seven semantic decisions identified by the repository
audit. `NOTATION.md` is the normative definition. This record preserves the
reasoning, rejected alternatives, migration rules, and falsification
boundaries.

## Decision 7: One Canonical Home

**Decision:** `NOTATION.md` is the single normative home for published
control-affine terminology. Articles may explain or specialize a definition,
but may not declare an incompatible local definition canonical. Code and data
schemas must identify the construction they implement.

**Reasoning:** A blocklist or a self-declaring article cannot close the loop
between a term, its mathematical type, and CI. The authority therefore exposes
a machine-readable table that the positive terminology gate parses.

## Decision 2: Complete Effective-Plant Drift

**Decision:** Drift is the complete autonomous vector field of the declared
effective plant. It includes all retained state-dependent inertial,
gravitational, elastic, dissipative, shaft, and compatible constraint/contact
terms. Reduced inventories are named model specializations.

**Energy consequence:** A ZTCF trajectory conserves mechanical energy only
when the declared drift is conservative, unforced, time invariant, and free of
dissipation and nonconservative contact work. With damping or drag,
$\dot E\leq0$ only when the retained dissipative law guarantees that sign.

**Rejected:** Defining drift globally as Coriolis plus gravity. That definition
silently excludes features that the flexible and biological models retain.

## Decision 1: Preserve the Four-Construction ZTCF Family

**Decision:** Retain pointwise sample, stitched pointwise trace, forward
trajectory, and achieved-state branched trajectory. Require the construction
qualifier on first use.

**Reasoning:** These constructions answer different questions and are already
implemented. Narrowing ZTCF to trajectory-only would hide valuable pointwise
attribution instead of making its limitations explicit.

**Boundary:** Only forward and branched constructions test persistence after
control removal. Pointwise and stitched constructions support same-state
attribution only.

## Decision 3: Zero Declared Control Is Not No Muscle

**Decision:** ZTCF zeros the declared applied generalized-control channel while
holding the declared effective plant fixed. It does not imply zero muscle
activation, EMG, co-contraction, reflex activity, or biological effort.

**Reasoning:** Impedance can remain in a frozen effective plant and biological
activation is not identifiable from generalized mechanics alone.

## Decision 4: ZVCF Is an Instantaneous Acceleration

**Decision:** ZVCF is the zero-velocity, zero-control drift acceleration at a
fixed configuration and declared internal state. It is not a state, generalized
torque, or releasable trajectory.

**Migration:** A control-preserving zero-velocity evaluation is renamed
**zero-velocity control-preserved acceleration**. A force-space image is named
**ZVCF generalized-force representation**. Neither may use bare ZVCF as though
it were the canonical object.

## Decision 5: One DCR Expansion and One Comparable Space

**Decision:** DCR expands to **Drift-Control Ratio**. Its numerator and
denominator must occupy the same acceleration or task-projected space, under a
declared metric and admissible control set. The denominator is bounded control
authority, not an unlabeled realized input.

**Rejected:** Full-state norms that mix coordinate and velocity units;
unweighted cross-space torque/acceleration ratios; and “Drift-to-Control Ratio”
as a competing expansion.

**Aerodynamic collision:** DgCR remains **Drag-Curve Ratio**.

## Decision 6: Symbol Convention

**Decision:** Use $f(x)$ for drift, uppercase $G(x)$ for the input map,
lowercase $g(q)$ for gravity generalized force, and $u$ for the declared control
input.

**Reasoning:** This matches a common control-affine convention while preventing
one letter from denoting both gravity and input inside a document.

## Enforcement Decision

The terminology gate must:

1. parse canonical entries from `NOTATION.md`;
2. reject unknown explicit expansions, not merely listed known mistakes;
3. require a construction qualifier on first ZTCF use;
4. enforce ZVCF, DCR, and DgCR positive forms; and
5. fail closed when any enforced acronym lacks an authority entry.

Historical quotations may remain only through the existing explicit baseline.

## Cross-Repository Conformance

AffineDrift owns the public semantic authority. UpstreamDrift owns executable
model contracts. Its conforming profile must preserve these meanings while
adding implementation-specific details such as coordinates, units, contact
mode, tolerances, and provenance. An implementation profile may narrow a model
inventory, but may not redefine the object.

## Falsification and Reporting Boundary

Every numerical counterfactual report must state the construction, zeroed
channel, retained plant terms, initial or achieved state, coordinate/frame
convention, and horizon. Any DCR report must additionally state $W$,
$\mathcal U(x)$, $\varepsilon$, and sensitivity to those choices. None of these
mechanical quantities alone establishes muscle recruitment or a universal golf
strategy.
