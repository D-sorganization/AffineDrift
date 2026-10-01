# Complete-State Technical Review

Issue #4756 extends epic #4009 and corpus review #4021. The full Chapter 3 source
was read and corrected. Prior companion findings are preserved in
`state-snapshot-prior-review.json`; this review does not complete the whole book
or re-audit every linked monograph.

## Scientific Decisions

1. **State, Parameters, and Observation.** Replaced the loaded-bow/decorative-cord
   comparison, which changes the physical system, with unresolved deformation of
   the same beam. Complete deformation determines strain energy for a fixed
   elastic law. A scalar modal observation can hide nonzero energy, but this is
   an abstract example, not a fitted shaft. Measurements and state are distinct.
2. **Evolution Contract.** State sufficiency is relative to a model, parameters,
   initial time, future inputs, and well-posed evolution. The scalar square-root
   ODE supplies an explicit nonuniqueness counterexample despite a single-valued
   right-hand side. Local Lipschitz continuity is sufficient, not necessary.
   Constraint consistency, contact modes, and event/reset rules are included
   where needed. Numerical disagreement can reflect more than missing state.
3. **Velocity Reversal.** Same configuration gives the same configuration-dependent
   inertia matrix. Standard quadratic convective forces are even under simultaneous
   reversal of every velocity, unlike momentum, fixed-torque power, and viscous
   resistance. Equal initial acceleration can coexist with different state
   derivatives and futures. Tests use the repository's physically consistent
   double-pendulum mass matrix and Christoffel factorization; a separate analytic
   expression checks the quadratic bias. Gravity projections, rather than an
   inertial gravity direction, change with posture.
4. **Memory and Preparation.** Pure delay needs relevant history or a declared
   approximation; it is not a first-order lag. A memoryless nonlinear map does
   not automatically add an independent state. Continuous preparation preserves
   state within each branch while allowing different states between branches;
   it need not reach equilibrium. This is distinct from matched-state torque
   interventions. Prior history need not remain an independent predictor once a
   sufficient state is fixed.
5. **Intervention Contract.** Pointwise contrasts remain defined for nonlinear
   controls, but additive attribution requires further structure. A product-control
   example demonstrates nonadditivity. Hold complete relevant state and other
   inputs fixed, distinguish open-loop programs from feedback policies, and
   separate commands, transmitted torque, steps, impulses, and state resets.
   Prescribed moving-base motion does not provide dynamic feedback by itself.
6. **Event Timing.** Event guards, directions, windows, missing crossings, and
   causal detection are part of the contract. Respective-event comparisons can
   include timing changes absent from fixed-time comparisons. A command labeled
   relative to future impact can be retrospective; a real-time policy needs an
   estimator or a causal trigger. State timing is not inherently more robust.
7. **Measurement and Presentation.** Sparse strain, kinematic, grip, and EMG
   observations do not automatically reconstruct a complete state. Uncertainty
   distributions depend on measurement models, excitation, parameters, and
   estimator assumptions. Clarified the scope of McPhee's review, pinned provider
   links, consolidated repeated arguments, and amended the schematic to include
   the model/input conditions for prediction.

## Provider and Literature Scope

Read the complete pinned matched-state ensemble chapter at UpstreamDrift revision
`85cce4d3307bb7ad3953d9fc6e583e370803515c`. It defines matched four-component states
for paired rigid double-pendulum commanded/zero-torque futures. The finite
preparation chapter at the same revision was previously read with its code and
stored arrays during issue #4753. Their contracts are contrasted here; no new
provider simulation or whole-monograph verification is claimed.

The [publisher record for McPhee (2022)](https://link.springer.com/article/10.1007/s12283-022-00387-0)
confirms the bibliographic identity and the abstract's scope: a review of golf
models and measurements. Only the abstract and record were accessed, not the
subscription full text. The chapter cites it as a survey, not evidence that a
particular measurement set is sufficient.

## Delegation and Adjudication

Supplied-text agy Gemini 3.8 Flash jobs supported the claim inventory, provider
contract inventory, test drafting, notation review, and a handoff checklist. Lead adjudication rejected:

- treating local Lipschitz continuity as necessary for uniqueness;
- claiming quaternion normalization automatically requires a DAE;
- inferring impacts or velocity jumps from a continuous dead-zone map;
- requiring equilibrium to carry finite preparation state without a reset;
- requiring control affineness merely to define a pointwise contrast;
- treating finite-grid agreement as proof of general numerical convergence;
- calling companion/technical-monograph chapter numbering a reference error;
- declaring transverse crossing necessary for every isolated event;
- using a constant scalar inertia with an arbitrary nonzero quadratic bias as a
  mechanically consistent rigid-body example.

The six local cases include the corrected schematic (failed before correction),
physical velocity-reversal parity, nonunique scalar evolution, pure-delay
history, incomplete modal observation, and nonlinear intervention nonadditivity.
They test the stated distinctions; they do not validate human biomechanics.

## Publication and Regression Results

The final 221-page companion PDF is byte-identical at canonical and public paths.
All Chapter 3 PDF pages 18–24 and boundaries 17/25 were visually reviewed. All three
display equations fit the 390px mobile viewport. Four viewport/theme publication
checks pass, with no serious or critical axe findings; 37 chapter math expressions
render without errors or page overflow. Twelve publication gates and the 654-source
title audit pass. Repository Ruff and Black (836 files), plus the CI-scoped mypy
check (94 files), pass.

The 63 affected checks pass. The full configured default pytest coverage run exits
zero, with 6,401 passing progress symbols and 29 reported skips; double-quiet output
suppresses the usual count/duration summary. Coverage is 78.9% for configured source
plus scripts and 93.0% for source alone. Rendering finished before regression and
no publication files were regenerated during it. Packaging-test outputs were
preserved under QA. These checks support the declared mathematical and publishing
contracts, not empirical human validation.

The Flash handoff draft wrongly classified pending full validation alongside
passed partial checks as contradictory; these are compatible workflow states.
Its phrase 'discrete state divergence' was rejected because differences between
prepared branches need not involve discrete jumps.
