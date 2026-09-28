# Volume I Mathematical Reference Review — #4469

## Scope and Argument

Read the complete `Volume_I/main.tex`: front matter, notation reference,
differential geometry primer, linear algebra appendix and both printed Python
examples. The substantive chapter inputs are unchanged and are not newly
certified by this review. Regenerating the complete PDF verifies compilation;
it does not complete the remaining whole-book or corpus audits under #4021/#4009.

The corrected reference distinguishes three questions that recur in the golf
investigation: how coordinates represent a motion, how nearby solutions respond
to perturbations, and what conditions certify decay or optimality. Geometry
supplies objects and comparison rules; the specified dynamics determine flow
sensitivity; stability and optimization require additional hypotheses. None of
these calculations alone identifies muscle activity or validates a club design.

## Corrected Findings

1. **P1 — Controlled Jacobian.** The state derivative includes the nominal-input
   terms and, for feedback, the policy derivative. The scalar model `-x + xu`
   at input 2 reverses the drift-only stability conclusion. Zero input refers to
   the declared actuator/state model and retains assigned passive loads/history.
2. **P1 — Transport and Sensitivity.** Levi-Civita parallel transport preserves
   metric inner products; a flow variation obeys the differentiated dynamics.
   A flat Euclidean example expands along one axis. Geodesic deviation depends
   on initial separation and derivative, and curvature sign does not establish
   contraction of a forced swing. State the contraction inequality, domain,
   invariance, input, metric bounds and hybrid conditions separately.
3. **P1 — Rotation Maps.** Rodrigues' formula requires a unit axis or properly
   scaled rotation vector. Give removable zero-angle limits, the half-turn
   exception, branch ambiguity and ordered integration for changing generators.
   Replace `logm(R).real` with a rotation-vector round trip. A group exponential
   is not a geodesic of every chosen metric.
4. **P1 — Dual Frame Maps and State Spaces.** Declare frame direction and
   angular-first ordering; wrenches use the inverse-transpose twist map to
   preserve power. Specify the finite adjoint versus infinitesimal Lie bracket.
   Mechanical momentum in `T*Q` differs from a first-order control costate in
   `T*X`, particularly when the state manifold is `X = TQ`.
5. **P2 — Geometric Hypotheses.** Supply chart, topology and completeness
   conditions; distinguish unrestricted revolute angles from joint/contact
   constraints. Explain the tangent bundle, coordinate-rate maps and augmented
   states. Metric congruence preserves inner products; positivity alone is not
   a stability certificate. Smooth fields can escape in finite time.
6. **P1 — Linear Algebra and Identification.** State Schur-complement symmetry
   and definiteness assumptions. A rectangular map can have only positive
   listed singular values yet retain an input nullspace. Metric-weighted gains
   separate physical norms from coordinate units; singular values alone do not
   establish a unique force history or performance sensitivity.
7. **P1 — Time Ordering and Matrix Equations.** Pairwise commutation is sufficient
   for the ordinary exponential of the time integral; accidental endpoint
   equality does not imply commutation. Specify column-major vectorization,
   Lyapunov uniqueness and the Hurwitz/positive-definite case. Riccati's quadratic
   term does not become linear merely by vectorization. Ordinary coordinate
   Hessians need not transform tensorially away from stationary points.
8. **P1 — Spectral Claims.** Distinguish regular and singular descriptor pencils,
   finite and infinite eigenvalues, and the symmetric definite special case.
   The closed pseudospectrum includes eigenvalues and requires a stated norm
   and perturbation class. A checked nonnormal example separates eigenvalue
   sensitivity from a complete transient or biological-uncertainty model.
9. **P1 — Solvers and Certificates.** PSD cone convexity does not make every
   joint controller/metric search convex. State affine LMI structure, numerical
   margins and the need for between-sample certification. Separate a sparse
   linear solve from an SDP. CG requires an SPD operator; indefinite KKT systems
   need a suitable method. Replace the truncated `import nu` example with a
   complete residual-checked manufactured solve.
10. **P2 — Printed Reference Integrity.** Restore appendix letters and section
    numbering after back matter, and use valid theorem titles and actual labels
    for the two examples. Previously the label strings appeared in printed text.
    Keep each code listing together and reserve contents-number width for
    multi-digit sections so section numbers do not run into their titles.

## Independent Checks and Delegation

`tests/test_volume_one_reference_rigor.py` supplies 13 numerical cases, two
executed examples extracted directly from the manuscript, and six targeted
source regressions. The initial baseline had 13 passing numerical cases and
eight failing source/example checks. All 21 pass after correction. Checks cover
zero/near-zero/general/half-turn rotations, input-dependent Jacobians, dual
frame power, flat-space expansion, noncommuting transitions, coordinate-scaled
norms, the Lyapunov operator, Schur quadratic forms, a regular descriptor pencil,
nonnormal eigenvalue sensitivity, and both complete printed programs.

Four supplied-text-only agy Gemini 3.8 Flash calls ran in two parallel pairs:
initial claim inventories and final notation/example checks. They used plan/print
mode without tools, file access, network, edits, publishing or permission bypass.
The lead verified all accepted findings. Rejected suggestions include universal
necessity of a commutation condition, loss of feasible-set convexity merely from
scalarizing a PSD condition, and a supposed change in wrench ordering caused by
the order of two prose equations. Locally defined symbol reuse is not itself a
mathematical inconsistency. Flash's arithmetic review was static; actual example
execution is recorded by the tests.

## Primary Sources Read

- [Lynch and Park, Rodrigues' Formula](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-3-exponential-coordinates-of-rotation-part-2-of-2/):
  unit-axis and constant-generator conventions.
- [Lynch and Park, Wrenches](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/):
  force/moment transformation and power pairing.
- [Figalli and Villani, Optimal Transport and Curvature](https://people.math.ethz.ch/~afigalli/lecture-notes-pdf/Optimal-Transport-and-Curvature.pdf),
  Sections 1.11–1.12: geodesic variations, parallel frames and the Jacobi equation.
- [Boyd et al., Linear Matrix Inequalities in System and Control Theory](https://web.stanford.edu/~boyd/lmibook/lmibook.pdf),
  Chapter 2: affine symmetric coefficients, convexity, Schur complements and
  decision-variable distinctions.
- [Embree–Trefethen Pseudospectra Gateway Theorem](https://www.cs.ox.ac.uk/pseudospectra/thms/thm1.pdf):
  the closed-set singular-value, resolvent and perturbation equivalences.
- [SciPy Rotation Vectors](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.as_rotvec.html)
  and [Conjugate Gradients](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.cg.html):
  API conventions, SPD assumption, tolerance and return status.
- [CVXPY Semidefinite Constraints](https://www.cvxpy.org/tutorial/constraints/index.html#semidefinite-matrices):
  square affine cone expressions and symmetric-variable declarations.

These are mathematical and software sources, not empirical golfer validation.
Numerical fixtures are manufactured and do not establish neural control,
coaching efficacy, tissue properties or equipment benefits.

## Print Validation

The 149-page volume compiles with pdflatex, BibTeX, makeindex and two final
pdflatex passes. All changed reference pages (physical 139–146), bibliography
(147–149), front matter (1, 3–4) and contents (5–11) were visually inspected.
No overfull boxes or undefined references remain in the final log. Existing
header-height warnings in Chapter 4 and a list-width warning elsewhere remain
outside this bounded scientific review. The linked chapters retain their
independent review histories; a successful build is not whole-book acceptance.
