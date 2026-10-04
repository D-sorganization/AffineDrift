# Shared Nomenclature Review

Epic #4009 / corpus #4021, issue #4865. This review concerns the common
`articles/The_Geometry_of_Motion/nomenclature.tex` included by Geometry Volumes
0–V. It does not re-review their complete chapters or establish empirical
golf-swing validity. The source starts from PR #4869's reviewed head
`53e4676ee1e2ffa32a05257cca64913fcbc25769`; that parent must be verified on
remote main before publishing this child.

## Coordinates, Velocities, and Mechanical Power

The previous list assigned both configuration and generalized velocity to
`R^n` without stating its coordinate convention. That is valid for independent
regular local coordinates with `v = qdot`, and remains the convention for the
short mechanical entries. It is not a general statement about configuration
storage. A scalar-first unit quaternion stores four numbers subject to a norm
constraint, whereas body angular velocity has three components. The general
representation uses `qdot = N(q) v` on its admissible domain.

This distinction agrees with the already reviewed Volume 0 state-space and
rotation chapters, Volume I superposition and induced-acceleration chapters,
Volume II configuration-manifold chapter, and Volume III mechanical/actuator
state discussion. The common list now states that agreement instead of
overriding valid chapter equations. State size is defined as `n_x`, replacing
the literal `nx`; additional actuator/internal states and representation
constraints remain explicit.

The same representation choice changes the task-velocity Jacobian and the
components conjugate to velocity: `J_v = J_q N` and `tau_v = N^T tau_q`.
Consequently `tau_v^T v = tau_q^T qdot`. For a time-independent club-point map,
both representations must predict the same point velocity and mechanical
power. Cartesian point acceleration is not just the vector of coordinate
second derivatives. The list identifies those second derivatives without
adding a new chapter-level acceleration derivation.

[Tedrake's multibody notes](https://underactuated.mit.edu/multibody.html),
Manipulator Equations, supply the primary reference for the quaternion
position/velocity distinction and velocity map. Exact independent checks in
`shared-nomenclature-independent-checks.json` verify a Hamilton quaternion
map, its tangent identities, a rigid point's velocity, and a rational force–
power example. These are manufactured mechanical checks, not golfer data.

## Mass Matrix and Velocity-Product Force

Positive definiteness is qualified by independent regular velocities and
strictly positive modeled kinetic energy in every nonzero such direction.
This preserves the assumptions already stated in Volume I Chapter 3.
Redundant coordinates, constraints, massless idealizations, and singular
charts require representation-specific treatment; the revision does not
assert that all such mass matrices are singular.

An independently checked quaternion example shows why that restraint matters.
For unit `q`, `N^T N = I/4`. With positive-definite body inertia `J`, the ambient
form `M_q = 16 N J N^T` is singular in the radial direction. Adding `q q^T`
makes it positive definite while preserving its restriction to every
admissible rate `qdot = N v`. Both restrictions give `v^T J v`. Ambient
definiteness alone therefore does not identify the physical degrees of
freedom or remove representation constraints.

The Coriolis/centrifugal matrix is distinguished from its generalized-force
product `C qdot`, and its nonunique factorization is stated. The prior name
“force matrix” was ambiguous rather than evidence that the chapters used an
incorrect force vector. Existing chapter mechanics and counterfactual/DCR
definitions remain unchanged. Gravity follows each chapter's declared sign
and equation-side convention.

## Full Dynamics, Discrete Updates, and Curves

The old indexed Jacobians differentiated `f` with respect to both state and
input, while the same list later defined `f(x)` as zero-input drift. The
revision declares a discrete update `x_(k+1) = F_k(x_k,u_k)` and evaluates
`D_x F_k` and `D_u F_k` at the same nominal pair. Chapter-specific full
continuous fields `f(x,u,t)` remain valid notation and are distinguished from
the autonomous drift convention. A numerical update must be differentiated
as that update; it does not inherit an exact-flow Jacobian by notation alone.

For the integrator `xdot = u`, the exact held-input update is `x + h u`:
its input Jacobian is `h`, the continuous input derivative is `1`, and the
derivative of zero drift with respect to input is `0`. For `xdot = x^2 + x u`,
the full state derivative is `2x + u`; differentiating drift alone loses the
nominal-input contribution. These counterexamples agree with Volume I's
variational chapter and Volume II's trajectory-optimization discussion.

The curve entry now permits a declared parameter, preserving Volume II's
general curves. A timed trajectory with fixed initial data and input law is
distinguished from an evolution map retaining initial-time/state dependence.
No global existence, autonomous-flow group, or uniqueness claim is inferred
from the notation. The model and its domain of existence must be declared.

## Delegation and Publication Scope

Two successful supplied-text agy CLI Gemini 3.8 Flash helpers supplied a
notation inventory and copy review. The lead checked all scientific claims
and chapter contexts. The copy review's new-symbol typography suggestions
were applied. Its request to remove the golf connection was rejected because
that connection serves the user's stated purpose. Its proposals to expand
previously reviewed DCR definitions were not treated as new proven defects.

Visual inspection also found inherited ``Contents'' running headings on the
nomenclature pages and confirmed the previously indexed DCR line overflow in
the narrower editions. The shared heading mark is corrected and the same
DCR formula is displayed on its own line. Its mathematical definition is
unchanged.

All six enclosing PDFs require intentional regeneration because they include
the shared file. Their frontmatter and adjacent pages need visual inspection;
unchanged chapter source and any page-number shifts must be distinguished
from newly reviewed content. Publication acceptance, dependent hashes, and
actual test/render outcomes are recorded separately. This document alone
does not clear the six complete books, title-card issue #4868, the remaining
corpus, or live deployment.
