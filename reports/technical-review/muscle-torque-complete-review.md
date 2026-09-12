# Muscle Geometry, Torque Feasibility and Golf Inference

## Scope and Scientific Message

Issue #4369 belongs to technical-review epic #4009 and corpus audit #4021.
The complete original and revised Chapter 16 sources were read in both LaTeX
and Quarto. The original print chapter contained about 5,283 words. All eleven
exercises now have worked answers. Original heading destinations, print labels
and the figure destination are retained. This is a local scientific and rendered
review, not a claim of production publication or completion of the whole book.

The chapter connects anatomical geometry, transmitted tension, generalized
force, feasible motion and hand-club contact through virtual work and state
constraints. Geometry alone cannot determine recruitment or performance.
An estimated net joint moment does not identify muscle forces. Signed joint
powers can describe transfer between coordinates without establishing tendon
work, metabolic cost or a validated coaching intervention.

## Findings and Corrections

| Finding                                                                        | Correction                                                                                                                                   |
| ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Unsigned perpendicular distance presented as a general moment arm              | Define signed axial moment and distinguish it from the full moment vector and line-to-axis distance.                                         |
| Length derivative, transpose and torque-map conventions conflict               | Declare positive tension and lengthening; derive the negative transpose from virtual work.                                                   |
| Redundancy treated as unconstrained freedom                                    | Intersect a null-space family with nonnegative force and capacity bounds; distinguish static feasibility from dynamic reachability.          |
| Separate joint maxima treated as jointly attainable                            | Construct a coupled torque polytope and explicitly show the incompatible maxima.                                                             |
| Co-contraction and positive material stiffness treated as stability guarantees | Separate antagonistic action from null-space redistribution and include geometric stiffness; provide an unstable taut-spring counterexample. |
| Joint torque presented as complete physiological control                       | Explain activation, tendon, contact, floating-base and inverse-estimation limits.                                                            |
| Biarticular energy transfer asserted from geometry alone                       | Calculate signed coordinate powers for two velocities; distinguish transfer, absorption and tissue energetics.                               |
| Anatomical and grip prescriptions unsupported                                  | Correct triceps-head and wrist/finger distinctions; withdraw universal percentages, leverage claims and instructions to grip harder.         |
| Unique optimization solution confused with identified neural strategy          | State strict convexity and feasibility assumptions; separate mathematical uniqueness from physiological evidence.                            |

## Derivations and Independent Checks

For a massless, frictionless, configuration-only path with uniform positive
tension, L = d ell/dq has muscle rows and coordinate columns. Tensile virtual
work is -F^T L delta q, so tau_M = -L^T F = rF and skeletal power is
tau_M^T qdot = -F^T ell_dot. Moving guides, friction, path inertia or independent
attachment motion require additional terms. For qdot = Nv, force conjugate to
v is -N^T L^T F. For q = phi(s), reduced force is T^T tau, T = d phi/ds.
Contact maps must use the same representation: J_v = J_c N, so
J_v^T lambda = N^T J_c^T lambda. Point forces and free couples have distinct
translational and angular Jacobian contributions.

The nonsymmetric example L = [[-.05,0],[-.02,-.04]] and F = [500,300] N yields
tau = [31,12] Nm. At qdot = [2,-3] rad/s the path rates are [-.10,.08] m/s and
power is 26 W. A second transpose instead yields [25,22] and changes the model.

For r = [[.04,.02,-.03],[0,.03,.02]], F0 = [100,200,50] N and capacities
[400,300,250] N, the null direction [13,-8,12] gives
F = F0 + t[13,-8,12], with -25/6 <= t <= 50/3 N. The target is [6.5,7] Nm.
Independent torque maxima [22,14] Nm cannot coexist: torque2 = 14 Nm forces
torque1 <= 14.5 Nm. The shared figure displays this feasible set and the
separate biarticular power cases.

The restoring stiffness is Kq = L^T K_ell L + sum_j F_j Hessian(ell_j).
For attachment radii .1 and .2 m, spring stiffness 1000 N/m, slack length .2 m
and q = pi, ell = .3 m, tension = 100 N and ell' = 0. The geometric contribution
is -20/3 Nm/rad: the equilibrium is an energy maximum despite positive material
stiffness. Positive restoring stiffness alone also does not prove asymptotic
stability without the remaining dynamics.

At 300 N and moment arms [.02,.04] m, speeds [2,-1] rad/s produce powers
[12,-12] W, transferring power from coordinate 2 to coordinate 1. Speeds
[2,-3] instead produce [12,-36] W and net absorption of 24 W. Coordinate power
partitions depend on representation; total power retains virtual-work meaning.

The synergist exercise gives F2 = 2500 N - 2F1 for a 50 Nm target, with
750 <= F1 <= 1000 N and 500 <= F2 <= 1000 N. At 60 Nm both reach capacity;
61 Nm is infeasible under these bounds. This is synergist sharing, not an
antagonist example. A positive-capacity normalized quadratic objective is
strictly convex on a convex force set, giving a unique minimizer when feasible.
That property does not identify a nervous-system objective or impose temporal
activation and tendon constraints.

Nine independent checks in `tests/test_muscle_torque_rigor.py` use cross-product
geometry, finite differences, linear programming, coordinate reduction, power
identities and stiffness calculations. These verify constructed examples;
they do not validate an empirical golfer model.

## Primary Evidence and Limits

- Sherman, Seth and Delp (2013), DOI 10.1115/DETC2013-13633: complete extracted
  paper read. Its path-length sign convention must be reconciled with ours;
  it is not cited as an unexplained endorsement of a minus sign.
- Murray, Delp and Buchanan (1995), DOI 10.1016/0021-9290(94)00114-j: all thirteen
  scanned pages inspected. Two elderly cadavers plus modeling do not establish
  a golfer-population optimum. Excursion and torque conventions are explicit.
- Holzbaur, Murray and Delp (2005), DOI 10.1007/s10439-005-3320-7: methods,
  results, model table and conclusion read. The generic 15-coordinate,
  50-compartment model omits intrinsic hand muscles and prescribes scapular
  motion; calibrated joint moments are not independent golf validation.
- OpenSim FunctionBasedPath 4.5 API: detailed description and force-parameter
  sections read, not the entire API. Length, speed and moment-arm consistency
  is an implementation requirement, not anatomical validation.
- Rice NMSM surrogate-model guide: complete guide body read, cited as undated.
  A consistent surrogate still needs independent validation and domain limits.

Exact reading boundaries, source URLs, earlier failed checks and build recovery
are retained in `docs/development/technical-review/muscle-torque-review.md`.

## Rendered Review and Remaining Presentation Defect

All 29 final web reading captures were inspected. Automated checks cover 170
expressions, 16 displays, 14 width/theme cases, 68 display/figure regions and
24 keyboard-scroll cases. The production route verifier checks all fourteen
navigation records individually: HTTP 200, no record or inspection failures,
no retries and no page overflow. Its axe scan covers one route/configuration;
the separate browser review scans both themes and records the existing
moderate `landmark-unique` finding. No serious or critical violations were found.

The corrected full-book PDF has 536 pages. The chapter occupies physical pages
179-193 (printed 149-163), all visually inspected; the four new references on
physical pages 530-533 were also inspected. A final explicit exercise-box break
keeps question 4 together; affected pages 191-193 were reread. No undefined
citations or chapter overfull boxes remain. Other chapters' warnings and pages
are outside this rendered review. The figure labels were enlarged and inspected
in print, desktop and horizontally scrolled mobile views.

**Open presentation issue #4370:** settled table-of-contents selection can name
a late grip subsection while the reader is at an earlier heading. A fresh
browser reproduced the defect; relative `offsetTop` values are compared with
document scroll positions in the generated Quarto tracker. Anchor navigation
itself reaches the requested section. This record does not certify correct
active-section highlighting. The independent scientific corrections can be
reviewed while the shared navigation defect remains explicitly tracked.

Machine-readable local evidence and source hashes are in
`reports/technical-review/muscle-torque-render-verification.json`. Route-ledger
binding must use an actual commit containing these reviewed files. Hosted
checks, protected merge and live publication remain separate delivery gates.
