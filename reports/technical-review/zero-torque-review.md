# Zero-Torque Counterfactual Technical Review — #4427

## Scope and Central Argument

Complete reread and revision of the canonical zero-torque article and both
Chapter 6 editions, including examples, exercises, overview and contract.
The review separates five connected operations: defining the mechanical plant,
evaluating a same-state acceleration, integrating an input-removal branch,
resetting velocity, and estimating correction authority. Their shared equations
do not make their outputs interchangeable.

The reader can now follow the full chain from Cartesian COM motion to kinetic
energy, mass matrix, velocity/gravity bias, acceleration and recovered input.
That establishes the pointwise mechanics. A branch intervention then evolves
the complete declared state, which changes the subsequent drift. DCR compares
a projected magnitude with a bounded input effect; it omits direction and
horizon information needed for reachability. Measurement and physiological
claims require their own identification argument.

## Corrected Findings

| Finding                                   | Severity | Correction and Evidence                                                                                                                                                                                                                  |
| ----------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Inconsistent rigid mechanics              | P1       | Replace mixed pivot/COM inertias, missing parallel-axis terms, incomplete velocity bias, wrong cosine and sign-inconsistent solve with a uniform-rod derivation checked independently from COM Jacobians and potential-energy gradients. |
| Incorrect inverse input recovery          | P1       | Use the full coupled matrix. Explain why an inertial generalized-load component is different from an already computed inverse-dynamics input; subtracting retained load from the latter double counts it.                                |
| Pointwise/branch conflation               | P1       | The affine identity holds at every common state. Separated branches have a changed drift term; a nominal contribution integral is generally not a removed-input trajectory.                                                              |
| Incomplete state and constraint protocol  | P1       | Include internal-state dynamics, retained input policies, prescribed time dependence, coupled acceleration/reaction solve, contact feasibility and event definition.                                                                     |
| Infeasible or gravity-only velocity reset | P1       | Define the instantaneous ZVCF reset explicitly, retain surviving loads, and check velocity constraints and mode consistency. Resetting state is a different intervention from removing an input.                                         |
| Unqualified DCR and late authority        | P1       | Use an exact projected torque-box support value, rate-scaling example, direction counterexample and finite-horizon double-integrator bound. Remove empirical-looking torque ranges and unsupported late-swing conclusions.               |
| Numerical and measurement overreach       | P1       | Separate acceleration magnitude from stiffness; distinguish ground wrench from grip load, electrical activity from muscle-force identification, and exact-model intervention effects from model–human disagreement.                      |
| Inconsistent paired presentation          | P2       | Reconcile all mathematical expressions, replace the invented torque schematic with derived equations, specify exercise parameters, preserve section/equation targets and inspect print/mobile rendering.                                 |

## Independent Mechanics Checks

The two uniform rods have masses (2, 0.2) kg, lengths (0.4, 0.3) m, midpoint
COMs and COM inertias mL²/12. The base is fixed; gravity is downward; there is
no damping or contact. The first angle is counterclockwise from inertial +x;
the second is relative. At q=(45,70) degrees and v=(8,12) rad/s:

- M = [[0.15287515, 0.01010424], [0.01010424, 0.006]] kg·m².
- Velocity bias = (-3.78884065, 0.72168393) N·m.
- Gravity bias = (3.20524786, -0.12437655) N·m.
- Zero-input acceleration = (11.69948358, -119.25363140) rad/s².
- For a reference acceleration (2,8), recovered input =
  (-0.19700856, 0.66551586) N·m. Diagonal-only recovery fails closure.

Tests construct inertia independently from COM Jacobians, differentiate it to
recover Euler–Lagrange velocity bias, check the kinetic-energy power identity,
and differentiate potential energy for gravity. They also verify positive
inertia at multiple postures, inverse/forward closure, rate scaling, the exact
box bound by enumerating vertices, direction-dependent cancellation, an
infeasible moving-constraint reset, common-state subtraction after branch
separation, and a nonstiff constant-acceleration counterexample.

Ten mathematical checks passed before correction; a source regression failed
against the old printed example. All eleven checks then passed with both
corrected editions. Twelve existing contract checks preserve fixture replay
and rejection of unsupported engines, historical mixed-inertia revisions,
nonzero inputs and mismatched protocols.

The analytical two-rod example is not a newly registered ZTCF engine or a
published forward rollout. The rigid three-link v2 fixture, adapter, model,
schema and parameters remain unchanged. Its replay is a software regression,
not human, flexible-shaft or cross-engine validation.

## Adversarial Pass

Mass coupling changes recovered input even when one only cares about a single
coordinate. A zero-velocity reset can violate a moving support constraint.
Equal DCR values can permit or forbid drift cancellation depending on input
direction. Quadrupling velocity bias need not quadruple total drift because
gravity remains fixed and components can cancel. A large constant acceleration
need not contain a fast decaying mode. Each counterexample directly limits an
overgeneralization in the previous explanation.

An exact deterministic paired-model comparison isolates the stated model
intervention when all other protocols are held fixed. It does not automatically
identify an effect in a person. Net torque does not uniquely identify muscle
forces, co-contraction, activation, impedance or effort. Retained feedback and
open-loop replay define different experiments; fixed-time and impact-event
outputs also differ. No universal safe horizon, muscle capacity, late-swing
dominance, clinical effect or coaching prescription is established here.

## Sources and Access Limits

Existing Lynch2017 and Featherstone2008 entries support standard rigid-body
structure; neither bibliography was edited. Northwestern's official
[Chapter 8 overview](https://modernrobotics.northwestern.edu/chapters/chapter8/)
was inspected. An attempted individual video page was unavailable; this is not
a claim to have newly read either complete textbook. The worked derivation is
independently checked as described above.

The official [SUNDIALS v6.0.0 CVODE mathematical documentation, section 4.2](https://sundials.readthedocs.io/en/v6.0.0/cvode/Mathematics_link.html)
was read for the stiffness distinction. No new CVODE execution or parity test
was performed. Unsupported empirical torque ranges and the passive-force
isolation assertion formerly attached to Nesbit/MacKenzie citations were
removed; those papers are not newly certified by this review.

## Rendering and Provenance

The accompanying render-verification JSON records the isolated real-preamble
print build, paired mathematics, public-route browser cases and equation
inspection. Print contains nine pages including references. Long inline
expressions were moved into display math after visual inspection exposed a
narrow-screen readability issue that document-width checks alone did not find.
The standalone article reuses the existing overview/math styles and a small
page-local mobile-title and theme-aware overview-card rules. No frozen predecessor CSS was edited.

The obsolete torque timeline is removed; no external source reference to its
old figure label was found. Chapter section/equation labels and historical web
heading targets are retained. The canonical glossary anchor is made explicit
outside the callout because this Quarto version removes heading IDs inside
callout titles and rejects a `sec` cross-reference prefix on the callout itself.

The manifesto's model-conditioned intervention statement remains consistent
with the corrected canonical article. Its source is unchanged. A separate
dimensional error in its notation baseline is tracked in #4428 under #4063;
dependency carry-forward here is not a new acceptance of that entire page.
The inventory records a subsequent committed evidence checkpoint, not an
uncommitted working tree. Main merge and live publication are separate gates.
