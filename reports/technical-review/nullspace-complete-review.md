# Constraint Null Spaces, Dynamics and Finite-Time Golf Control

## Scope and Scientific Message

Issue #4371 belongs to epic #4009, corpus #4021 and core review #4058.
The complete original and revised article and bibliography companion were read,
including explanatory panels, critics' responses, appendices and references.
All 44 original heading destinations remain. This review covers these two web
sources; it does not certify other textbooks, an empirical golfer model or
production publication.

Constraint geometry specifies compatible motion. Inertia, velocity and applied
loads determine acceleration and reactions. Actuator limits and available time
determine reachable changes. An objective selects among feasible trajectories.
These layers explain why a useful geometric identity is insufficient to infer
muscle recruitment, an optimal grip or an effortless swing.

## Corrected Findings

| Original Problem                                                        | Correction and Check                                                                                                               |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Kernel dimension treated as physical mobility at a singular description | State regularity; the level set x^2+y^2=0 is a point despite its zero Jacobian there.                                              |
| Moving constraints treated as a homogeneous velocity space              | Derive J qdot + Phi_t=0 and J qddot + gamma=0, including mixed and explicit time derivatives.                                      |
| Arbitrary basis speeds called coordinate derivatives                    | Supply reconstruction and moving-frame terms; a rotating plane frame has nonzero Lie bracket despite spanning an integrable plane. |
| Position DAE and acceleration saddle system assigned the same index     | Distinguish the original index 3 formulation from differentiated index 1 equations and require consistent initialization.          |
| Euclidean force projection used with general inertia                    | Derive dual mass-metric velocity/force projectors and verify against a direct saddle solve.                                        |
| Constraint curvature omitted from drift                                 | Include the normal-acceleration term and verify a circular trajectory.                                                             |
| Instantaneous input rank treated as necessary for controllability       | Give a controllable two-mass system with rank 1 acceleration input and construct its finite-time control.                          |
| Controllability used without force or deadline limits                   | Compare minimum squared-force cost with a hard force-cap bound, proving a target unreachable in two seconds.                       |
| Golf coordinates and grip Jacobian incomplete                           | Declare all seven planar coordinates and both rotating grip offsets; finite-difference every Jacobian column.                      |
| Null-space basis and PCA promoted to neural synergies                   | Demonstrate basis invariance and degenerate projector eigenvalues; require separate measurements and physiological hypotheses.     |
| Clubhead acceleration lacks changing-Jacobian terms                     | Derive the full task acceleration and check centripetal acceleration independently.                                                |
| Normal reaction declared wasted energy                                  | Separate net ideal reaction power, interbody transfer, tissue load and metabolic cost; check nonzero moving-support power.         |
| Bibliography contains unsupported citation edges                        | Replace the graph with a bounded primary-source reading map; remove impossible chronological edges.                                |

## Independent Derivations and Numerical Evidence

Use M a=f+J^T lambda and J a=-gamma. With W=J M^-1 J^T,
lambda=-W^-1(J M^-1 f+gamma) and
A_c=M^-1-M^-1 J^T W^-1 J M^-1. Thus
a=A_c f-M^-1 J^T W^-1 gamma. Full row rank and positive-definite
inertia justify these inverses; redundant or singular descriptions need separate
treatment. The velocity projector is P_v=I-M^-1 J^T W^-1 J and its
force dual is P_tau=P_v^T. A_c=P_v M^-1=M^-1 P_tau.
For any full-column-rank tangent basis N,
A_c=N(N^T M N)^-1 N^T. Reduced dynamics retain Ndot nu:
(N^T M N) nudot=N^T f-N^T M Ndot nu.

For M=[[2,1],[1,3]] kg, J=[1,1], f=[1,0] N and zero curvature,
the exact saddle solution is a=[1/3,-1/3] m/s^2 and lambda=-2/3 N.
The incorrect Euclidean-force shortcut yields [.4,-.3], violating J a=0.
Tests also check idempotence, work duality, mass orthogonality and an
unnormalized basis; they do not merely duplicate one projection implementation.

On the unit circle, M=2I kg, q=[1,0] m and v=[0,3] m/s give
gamma=9 m/s^2. Gravity yields a=[-9,-9.81] m/s^2, lambda=-18 N,
and zero reaction power. N=[0,1], Ndot=[-3,0] /s and nu=3 m/s
independently reconstruct this acceleration. For a prescribed moving guide
x=t^2 in SI units, a 2 kg mass at t=1 s has v=2 m/s and a=2 m/s^2.
An applied 3 N force and 1 N reaction supply 6 W and 2 W, respectively, matching
8 W kinetic-energy growth. Rescaling the constraint by -1000 changes the
multiplier but preserves acceleration and physical reaction.

The two-unit-mass spring system has K=[[2,-1],[-1,2]] and a force on the
first mass. Its four-state controllability matrix has rank 4 and determinant
magnitude 1, despite acceleration input rank 1. From zero state to
[0,1,0,0] at 2 s, the Gramian control has minimum squared-force integral
59.63940852941051 N^2 s. Independent forward integration recovers the target
and cost. A 5 N magnitude cap permits at most 50 N^2 s over 2 s, so this
particular target and deadline are impossible under that cap. Squared force
is not mechanical work or metabolic energy.

The planar mechanism has two fixed shoulders, two two-link arms and a free
planar club: four arm angles, two club translations and one club angle.
Both grips impose point coincidence only. At the declared consistent pose,
rank(J)=4, dim ker(J)=3 and dim ker([J;J_H])=1. The latter permits club
rotation while the selected point is instantaneously stationary. Neither a
welded grasp nor finite-interval point stationarity follows. All seven columns
are finite-differenced. A separate rotating-point example at radius .5m and
angular speed 2 rad/s has 2 m/s^2 centripetal acceleration with zero angular
acceleration, checking the changing-Jacobian term.

Sixteen tests cover these results, rotating-frame brackets, basis rotations,
invalid mass metrics and stored-example reproduction. The builder and tests
are independently inspectable; all examples are constructed, with no fitted
human inertias, muscle forces, measured swing or claimed coaching validation.

## Primary Sources and Reading Boundaries

- Tedrake, multibody notes: generalized-speed and bilateral-position passages
  read; signs and dual transposes were independently derived rather than copied.
- Tedrake, acrobot notes: modal/general controllability and related control
  discussion read. The spring Gramian and cap certificate are independent work.
- Hairer, _Solving Differential Equations on Manifolds_, June 2011: cover and
  complete section IV.4, printed 34-36 / physical 38-40, read. Opposite multiplier
  convention is translated. The entire 55-page document is not certified.
- Nesbit 2005, JSSM 4:499-519: abstract, introduction and initial methods through
  physical page 3 read, including printed 501's omitted hands and flexible wrists.
  The remaining results and figures are not certified; this source does not
  validate a perfectly rigid golfer grasp or an optimal grip.
- SciPy null_space documentation: function, parameters, returns and examples
  read. Its relative cutoff is an arithmetic default, not measurement uncertainty.

The bibliography companion links these exact sources and states their limits.
The Caltech MLS book was unavailable from its former public PDF location and
was not read or used to substantiate a specific derivation. No unsupported
source-to-source citation graph remains.

## Rendered Review and Remaining Presentation Issues

All 29 latest article reading captures and all six bibliography captures in each
theme were visually read. Mobile equation details, expanded explanations,
the equation table across scroll positions and the bibliography boundary
column were separately inspected. There are 209 typeset expressions and 46
displays, zero MathJax errors, all 44 old destinations, no duplicate IDs or
broken fragments. Fourteen article width/theme cases and eight bibliography
cases show no page overflow. The article pass records 184 regions and 46
successful keyboard scroll checks; supplemental checks cover eight visible
callouts and four article plus four bibliography table configurations.

The existing readable-math stylesheet prevents compounded mobile scaling.
The two short explanatory panels remain expanded after a real Enter test
exposed the shared collapsible-header keyboard defect, tracked in #4374.
The shared TOC active-heading defect remains #4370. Custom axe checks in both
themes report only the existing moderate landmark-unique issue. Instrumented
axe font fetches emitted CSP messages; these are retained in scratch logs.

The actual production verifier passes all 28 article/bibliography route cases:
HTTP 200, no record/inspection/console failures, overflow or retries. It performs
axe on one configuration per route, with zero serious/critical violations;
it is not 28 independent axe scans. Only the selected generated article's
legacy polyfill was normalized through the production helper. No deployment
pruning function was run on the local docs tree.

Machine-readable evidence and exact source hashes are in
reports/technical-review/nullspace-render-verification.json. The reviewed
implementation is 1cfa47d45ebd14c719c0ec981e83eb53a231fb4d; all seven source,
stylesheet, test and numerical-example paths were compared byte-for-byte
against that commit. Route-inventory binding must name a subsequent actual
commit containing these durable reports. Hosted checks, protected merge and
live publication are separate gates. The wider corpus remains unfinished.
