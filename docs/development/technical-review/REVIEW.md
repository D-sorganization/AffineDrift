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
| #4151: Underactuation and Release | Define absolute and relative coordinates through virtual work; distinguish full column rank from full row rank; include input bounds in feasibility; distinguish forward reachability from an orbit; replace unsupported phase-stability assertions with a variational calculation. | Power-invariant coordinate transformation, positive-definite mass matrices with opposite coupling signs, bounded-input counterexample, and a drifting system that cannot move backward. |
| #4154: Tangent-Space Reference | Use the evolved baseline in a four-trajectory interaction; derive mixed second variations with state-transition transport; separate intrinsic curvature, nonlinear interaction, and integration error; correct repeated DDP/iLQR, energy-bookkeeping, and constrained-control claims. | Linear-system false-interaction counterexample, nonlinear input on a flat line, exponentially amplified Hessian source, and a finite-difference endpoint-map bound. |

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

The existing full-corpus tracker #4021 and route batches #4054–#4061 remain open. Continue with the remaining chapters of the long motion-control manuscript and Geometry of Motion volumes, tangent/control monographs, the complete impact/aerodynamic evidence tables, remaining Physics of Golf chapters, and then all shorter articles and critiques. Check each source's references, equations, worked examples, figures, accessible summaries, and paired editions. Do not mark deferred routes reviewed merely because their sources were enumerated or searched.

The immutable `articles/proximal_distal_energy_transfer/` publication remains unchanged. Its upstream source and revision-gated refresh process govern corrections to that monograph.

## Validation

The final first-wave Python run passed 3,715 tests with 92.62% coverage, with 26 skips. The Python 3.12 content lane passed 128 tests with four skips. Ruff and Black passed repository-wide; the CI mypy command passed 74 source files. Four additional underactuation tests passed after the new wording guard failed on the old editions. New tests independently check equations as well as preventing the identified wording regressions.

The revised Physics of Golf and Geometry of Motion Volume I PDFs compiled. All revised optimal-control, passive-stabilization, and impact chapter pages were visually inspected. The changed QMD editions rendered. The foundation article rendered 651 math expressions and the impact reference 270, with no MathJax error nodes. Local site preview blocked a legacy Quarto polyfill under the existing CSP; full site deployment and live-route checks remain separate.

The revised Geometry Volume II and complete motion-control PDFs also compiled, with no undefined references in their final logs; their underactuation chapter pages were visually inspected. The complete motion manuscript was missing 25 chapter macro definitions, which were restored from the standalone chapter preambles. Its legacy `compile_book.py` still contains machine-specific paths and is not the build command used here; reproducible PDF builds used `latexmk` on the tracked complete LaTeX source.

After the tangent corrections and CI-format fixes, the Python 3.12 full suite passed 3,712 tests, with 29 skips and 92.32% coverage. The separate 3.13 run above had different optional dependencies; its coverage is not directly interchangeable. CI found three malformed LaTeX commands and a disallowed textbook callout format; the corrected sources pass `scan_quarto_syntax.py` and the textbook-quality tests. The inspected tangent HTML rendered without MathJax error nodes. Its paired PDF is regenerated from the QMD with Quarto/XeLaTeX, with equation labels, contents, lists, and revised derivation pages checked visually.
