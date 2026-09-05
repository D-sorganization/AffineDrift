# Technical Review: Mechanics, Control, and Impact

Date: 2026-09-05. Parent epic: [#4009](https://github.com/D-sorganization/AffineDrift/issues/4009).

## Argument Being Investigated

The golfer prepares and continually changes a coupled mechanical state. Geometry determines force transmission; inertia couples accelerations; activation and tissue mechanics determine forces and impedance; earlier work becomes kinetic and elastic energy; feedback and prediction manage deviations; impact selects which aspects of the delivered state matter. The useful research question is how those contributions interact under explicit constraints and measurable objectives.

A same-state affine partition is an algebraic tool. It does not independently identify muscle effort, intention, metabolic efficiency, or how the nervous system controls the swing. A forward counterfactual is a model intervention whose state evolves; it must declare its input, boundary conditions, starting state, and comparison event. These distinctions make the argument testable rather than weakening it.

## Corrections Implemented

| Finding | Correction | Evidence |
| --- | --- | --- |
| #4148: Inverse Dynamics | Standard inverse dynamics returns applied generalized load. Feeding it matched zero-input acceleration returns zero; subtracting a supposed drift output from it double-counts bias terms. Retain rigid-flexible off-diagonal inertia. | Coupled-mass and pendulum counterexamples; shared inverse-dynamics include; Newton–Euler identities. |
| #4148: Constraint Forces | Ideal reactions lie in the range of the constraint Jacobian transpose, not generally in the actuation nullspace. Reactions depend on applied input. | Fully actuated constrained example; workless reaction identity. |
| #4148: Wrenches and Power | Translate moments using the same force and reference point; power uses the matching point velocity. Net hand wrench does not identify bilateral hand forces or muscle forces. | Wrench translation and power-invariance tests. |
| #4148: Impedance and Flexibility | Stiffness does not add to physical inertia. Configuration, modal coupling, preload, activation history, and contact assumptions affect different parts of the model. | Scalar spring response; constrained inverse mass; corrected state ordering and spatial/modal Jacobians. |
| #4149: Optimal Control | Repair Hamiltonian/Lagrangian signs, matrix dimensions, costate gradients, iLQR/DDP distinction, Riccati cross terms, convergence assumptions, and finite-horizon controllability claims. | Analytic CARE residual, closed-loop eigenvalues, cross-cost identity, uncontrollable finite-horizon example. |
| #4149: Passive Stabilization | Separate restoring stability from attraction, finite stiffness from kinematic rank, intrinsic response from metabolically passive tissue, and UCM covariance from causal identification. | Compliance example, stiffness derivative with moment arms, variable-spring energy balance, normalized UCM projection. |
| #4150: Impact | Derive spin loft by a vector dot product; compute spin direction from contact geometry; distinguish speed from its projection, relative COR from energy fraction, and screw-axis distance from total-speed/angular-speed ratio. | Nonzero attack/loft counterexample; normal-impulse vector calculation; momentum and energy identities. |
| #4150: Measurement Interpretation | Observational regression and mediation support associations, not established causal efficiency mechanisms. Null associations do not prove equivalence or identify timing adaptation. | Primary study design and explicit dimensional distinction between impulse and work. |

The longest foundational monograph and its multipart/manifesto editions share five reviewed explanatory includes. The inverse-dynamics and intentional-constraint-collapse articles were revised substantially. Canonical LaTeX and Quarto editions of the optimal-control, passive-stabilization, and impact chapters were revised together; the Bosch integration copy follows its canonical chapter. The impact reference, tangent LQR chapter, proximal-distal article, and force-measurement article received targeted corrections.

Unsupported numerical result tables and physiological diagrams were removed where no reproducible result package or identified study supported them. They were replaced with checkable derivations, worked examples, and specified experiments. This is not evidence that the underlying research hypothesis is false.

## Primary Sources Checked

- [Modern Robotics: Constrained Dynamics](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-7-constrained-dynamics/) — constraint reactions and projection.
- [MIT Underactuated Robotics: LQR](https://underactuated.mit.edu/lqr.html) and [Trajectory Optimization](https://underactuated.mit.edu/trajopt.html) — value propagation and model/algorithm scope.
- [OpenSim Activation Dynamics](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090590) — activation as a dynamic state distinct from excitation.
- [Rack and Westbury, 1974](https://pubmed.ncbi.nlm.nih.gov/4424163/) — short-range response of activated muscle; not evidence of a universal golf stiffness schedule.
- [Scholz and Schöner, 1999](https://pubmed.ncbi.nlm.nih.gov/10382616/) — task-equivalent variability and the uncontrolled manifold.
- [USGA Collision Explanation](https://www.usga.org/content/usga/home-page/articles/2025/05/what-happens-collision-between-club-ball.html) — ordinary relative-speed COR definition.
- [Rachnavy et al., 2026](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2026.1790645/full) — observational design underlying the mediation discussion.

## Coverage and Remaining Work

`corpus-review-index.csv` inventories tracked article/book/content QMD and LaTeX sources by length and records the scope of this pass. An indexed or pattern-scanned source has not completed a line-by-line technical audit. Likewise, repairing a claim does not clear every other claim on its route.

The existing full-corpus tracker #4021 and route batches #4054–#4061 remain open. Continue with the long motion-control manuscript, remaining Geometry of Motion volumes, tangent/control monographs, the complete impact/aerodynamic evidence tables, remaining Physics of Golf chapters, and then all shorter articles and critiques. Check each source's references, equations, worked examples, figures, accessible summaries, and paired editions. Do not mark deferred routes reviewed merely because their sources were enumerated or searched.

The immutable `articles/proximal_distal_energy_transfer/` publication remains unchanged. Its upstream source and revision-gated refresh process govern corrections to that monograph.

## Validation

The first full Python run passed 3,707 tests with 92.62% coverage and exposed six failures. The 71-test focused rerun passed after updating shared-source assertions, removing obsolete figure counts, refreshing evidence digests, and completing coverage-file cleanup. The Python 3.12 content lane passed 128 tests with four skips. New tests independently check equations as well as preventing the identified wording regressions. Final build and browser results are recorded in the PR and handoff.
