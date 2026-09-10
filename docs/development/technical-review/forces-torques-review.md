# Forces, Torques and Physical Attribution Review

Governing issue: #4355; epics #4009/#4021/#4054. Both original Chapter 4
sources were read completely before replacement, including the seven exercises.
The print source contained approximately 5,242 words and the web source 4,129.
This audit concerns this complete chapter, not certification of the remaining corpus.

## Problem and Editorial Argument

The old chapter treated five equation terms as five independent physical force
sources. It mixed inertial-frame acceleration with rotating-frame inertial forces,
read acceleration from a diagonal inertia despite coupling, and used incompatible
parameters and arithmetic across print and web. Its numerical phase tables did
not specify sufficient states to reproduce their values. Categorical statements
about elite golfers, passive assistance, grip squeeze and muscle control exceeded
both the mechanics and the cited evidence.

The replacement connects five questions in order: which physical body receives a
load; how coupled generalized equations represent that load; how joint motion maps
to an endpoint; which contact and actuator states make it feasible; and where
mechanical energy enters, transfers, stores or dissipates. This preserves the
investigation of coordinated golf motion while making its conclusions testable.

## Technical Corrections

- The terms M qddot and c arise from differentiating kinetic momentum. They are
  not extra external agents. The physical gravity moment is minus the potential
  gradient g when g is retained on the left. Eliminated ideal reactions remain
  physically present and must not be added again to a reduced equation.
- Sum of external forces equals m a_COM. Scalar I alpha is qualified as planar
  or fixed-axis; spatial body-axis rotation includes omega cross I omega. Moment
  balances about a moving point require the corresponding transport terms.
- Prescribing both accelerations and freeing one input are different experiments.
  The old M11 values 1.54 and 2.22 and inconsistent mass choices are removed.
  Full inverse dynamics includes M12 a2; free response uses inverse coupled
  inertia. Mass alone cannot establish golfer effort or equipment performance.
- Uniform circular acceleration is inward. An outward reaction on a string acts
  on the string; a centrifugal inertial force on a particle belongs to a rotating
  frame. Coriolis acceleration in the transport identity has positive 2 Omega
  cross v_relative; moving it to the rotating-frame force balance changes sign.
  Origin acceleration, Euler and centrifugal transport terms are retained.
- Quadratic bias scaling establishes neither beneficial acceleration nor energy
  supply. Joint bias, endpoint curvature and physical interface force are distinct.
  Endpoint curvature needs the actual path, not an assumed shoulder-to-head radius.
- Gravity work is minus the final-minus-initial potential change. A complete
  configuration cycle has zero net gravity work even if final speed differs.
  Setting the first angle to zero does not cancel distal gravity at arbitrary
  second angle. Early/late downswing work cannot be inferred without a trajectory.
- Net generalized moments do not identify muscle tensions or instantaneous neural
  commands. Signed moment arms, nonnegative tendon tension, activation and fiber
  states matter. Generic 50/30 N m budgets previously attributed to knee research
  are removed. Independent symmetric torque boxes are explicit approximations.
- Contact loads must satisfy an admissible contact model. Low input does not
  necessarily cause slip, and greater torque does not monotonically increase every
  reaction. A full-body floating base is not directly actuated by internal muscles.
- Clubhead mass times clubhead acceleration does not recover a whole-club grip
  wrench. Use whole-club COM force and moment balances, accounting for other
  external loads. The net wrench does not identify each hand's load or finger
  pressure; antagonist/contact forces can cancel while internal loading changes.
- Torque sign alone does not decide braking. Channel power uses its conjugate
  relative velocity; segment powers use absolute velocities. Zero summed internal
  force power can coexist with substantial power exchanged between bodies.
- Unspecified phase tables and underdetermined exercises are replaced with one
  declared state, a controlled rate-scaling comparison and seven worked answers.
  Smooth swing mechanics do not predict impact peak force or impulse without
  incident-state and contact information.

## Derivation and Reproducible Example

The reproducer `build_forces_torques_figures.py` reuses the audited two-link
operator for generalized dynamics but recovers applied moments independently
from Newton–Euler body balances. The complete inputs and outputs are stored in
`forces-torques-numerics.json`; the SVG and PDF show the same computed bars.

Parameters are m=(2.5,0.4) kg, L1=0.35 m, distal endpoint length 1 m,
COM distances (0.175,0.5) m, centroidal inertias (0.025,0.03) kg m²,
and gravity 9.81 m/s². They are manufactured, not measured golfer parameters.
Angles are q=(0,-5 degrees), relative rates (10,9) rad/s, and prescribed
accelerations (20,-30) rad/s².

| Generalized Quantity | First Component | Second Component |
|---|---:|---:|
| M qddot (N m) | 2.408586289 | 0.094672577 |
| c (N m) | 1.592335420 | -0.610090199 |
| g (N m) | -0.170999567 | -0.170999567 |
| Required Input (N m) | 3.829922141 | -0.686417189 |

For body 2, recover f_H=m2(a_C2-g0) and
tau2=I2(alpha1+alpha2)-(r_H-r_C2) cross f_H. For body 1, recover
f_base=m1(a_C1-g0)+f_H, then balance its COM moments including the
opposite hinge force and opposite distal actuator moment. These independent
balances return the same input as M qddot+c+g at four test configurations.

Here a_C2=(17.750638075,215.248921719) m/s²,
f_H=(7.100255230,90.023568688) N, and
f_base=(15.850255230,158.298568688) N.
At H, v_H=(3.5,0) m/s: force powers are plus/minus 24.850893306 W.
Actuator powers into the bodies are (45.163393306,-13.041926594) W;
gravity powers are (0,3.248991778) W. The body kinetic-energy derivatives
are (20.3125,15.057958489) W. Their sum is input power 32.121466711 W
plus gravity power. Finite differences of independent segment kinetic energies
check these derivatives. The distal generalized channel absorbs 6.177754703 W.

The endpoint acceleration is J qddot+Jdot qdot. At fixed state its four
algebraic contributions are J M^-1 tau, -J M^-1 c, -J M^-1 g and Jdot qdot:

| Endpoint Contribution (m/s²) | Horizontal | Vertical |
|---|---:|---:|
| Input | -13.218658154 | 2.478277871 |
| Velocity Bias | 8.796881238 | -1.454180019 |
| Gravity | 1.459829935 | -0.152540424 |
| Curvature | 31.463223132 | 394.626286011 |
| Total | 28.501276151 | 395.497843439 |

These are fixed-state contributions. Removing an input throughout a trajectory
changes the state and every subsequent term, requiring a new forward solution.
The large curvature contribution is not an independent energy source.

Holding q and qddot fixed while scaling rates by s=(0,1,2) gives input powers
(0,32.121466711,126.838187864) W. Bias scales by s²; this counterexample
refutes inevitable passive assistance without asserting a universal opposite.
Reversing all rates preserves quadratic bias and reverses its conjugate power.

The moving-frame identity is independently checked by finite differences of
a quadratic relative trajectory in a rotating, accelerating frame. Wrench
reference-shift tests use force-first ordering, n_K=n_H-d cross f and
v_K=v_H+omega cross d; f dot v+n dot omega remains invariant.

## Worked-Answer Checks

1. At q=(0,0), zero rates and qddot=(500 pi/180,0), required inputs are
   (3.670100168,1.745329252) N m. The distal input enforces zero relative acceleration.
2. A separate 1 kg particle at radius 1.35 m and angular rate 10.47 rad/s
   has inward acceleration 147.988215 m/s² and inward resultant 147.988215 N.
3. At q2=-5 degrees and rates (8,5), c=(0.640594708,-0.390457728) N m.
   Rates alone were insufficient in the original exercise.
4. At q=(150,-70 degrees), physical gravity moments are
   (-4.764830311,-1.932192811) N m; target-frame direction and acceleration
   require further conventions and the full dynamics.
5. Complete inverse dynamics gives the tabled input. Omitting M12 a2 adds
   5.992008866 N m to the first estimate and solves a different problem.
6. Whole distal-body COM and moment balances recover the tabled interface load;
   no finger-pressure estimate follows from that resultant alone.
7. Potential rises 12.192849345 J from (0,0) to (150,-70 degrees).
   Gravity does negative work on ascent, positive on return, and zero net work.

## Primary Evidence and Reading Limits

- [Tedrake, Multi-Body Dynamics](https://underactuated.mit.edu/multibody.html):
  read the relevant manipulator/energy derivation, nonunique C representation
  and generalized-velocity discussion; earlier constraint review supplies the
  compatible-motion context. It supports equation structure, not golfer parameters.
- [OpenSim, Joint Reactions Analysis](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53089600/Joint+Reactions+Analysis):
  read overview, inputs/outputs and joint-reaction versus inverse-dynamics
  discussion, including actuator-representation and receiving-body/frame conventions.
- [OpenSim, First-Order Activation Dynamics](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090590/First-Order+Activation+Dynamics):
  read the technical summary and implementation discussion. Reuse the existing
  bibliography key rather than introducing a duplicate citation to the same page.
  No universal human time constant is inferred from this model documentation.
- [OpenSim, Getting Started With Forward Dynamics](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53089648):
  read overview and inputs through states, controls and external forces;
  the complete best-practice/output ending was not read.
- [Lynch and Park, Wrenches](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-4-wrenches/):
  read the complete technical transcript. Its moment-first ordering differs from
  the chapter's explicitly matched force-first convention; power remains invariant.
- [Choi and Park (2020)](https://doi.org/10.3390/s20133672): reuse the prior
  constraint-chapter primary-PDF reading of abstract, methods, results and discussion
  through the start of the conclusion. The complete ending/references were not
  read. Nine professionals, a modified 551 g club and foam balls limit transfer
  to ordinary driver swings; the study does not prove a universal squeeze rule.

The Millard paper search returned an abstract but its full page was blocked;
it is not cited as a fully read source or relied on for a new chapter claim.
Historical removed citation destinations redirect to corrected explanatory
paragraphs rather than falsely preserving unsupported citations.

## Validation and Delivery

Local validation and complete paired reading are finished; protected delivery remains. Initial TDD produced two source failures and nine missing-module errors.
The implemented numerical suite exposed an incorrect test sign assertion, which
was corrected using the conjugate-power algebra. Eleven physical/source tests
then passed. A twelfth regression test was added after visual review exposed
unconverted inline math: it failed before the delimiter correction and passed
afterward. The paired-source/figure suite now has 35 passing tests.

Print reading exposed margin overruns in long inline vectors and one multi-vector
display; these were reformatted before final review. Bibliography reading exposed
a duplicate activation-document entry, replaced with the existing key. Full web
reading exposed inline TeX being parsed as ordinary Markdown despite passing
layout gates; the converter now uses dollar delimiters and the browser check
requires inline expressions as well as displays. These failures are retained
here so future reviewers do not confuse successful layout checks with complete
mathematical reading.

Preserve peer-owned #4253/#4255/Chapter 29, immutable proximal-distal publications,
authority pins and the original checkout. Scratch authoring scripts, screenshots
and render-generated trust-file churn are excluded from canonical delivery.

## Final Local Evidence

- Root `py -3.12 -X utf8 -m pytest --cov`: 5,254 passed, 29 skipped,
  132 deselected, 59 warnings, 79.29% configured coverage. This run preceded
  the additional inline-delimiter regression; final focused rerun has 35 passes.
- Content-lint 131 passed/four skipped; all 34 static CI contracts and title
  audit of 636 sources passed. Configured mypy passed over 91 files. Black100,
  Ruff and focused code-quality checks passed for the numerical helper/tests.
- Full PDF rebuilt, now 542 pages. All 12 chapter pages 68–79 and relevant
  bibliography pages 527/529/531 were visually read. The last wording clarification
  changed only page 79 by full-book text comparison; it was rerendered and read.
  Chapter 4 has no final overfull/underfull or undefined-reference warnings.
  Other chapters retain their pre-existing layout warnings.
- All 23 full web captures were read through the references. Unit expressions
  were then kept together to prevent separated exponents; changed paragraphs
  were reread. A last wording correction distinguishes a vanishing generalized
  gravity moment from vanishing gravity. Desktop and mobile/light/dark captures
  verify that correction, with the changed exercise fully reread.
- Exhaustive browser verification found 149 expressions, 26 displays, one
  loaded/labelled figure, no duplicate IDs or broken local fragments, and all
  33 historical destinations retained. Fourteen viewport/theme cases passed;
  162 detailed equation/figure regions and 86 keyboard-scroll checks passed.
  Both themes retain only the shared moderate landmark-unique axe finding.
  Console noise remains; no claim of zero console errors is made.
- Final canonical site verification: every one of the 14 actual-route records
  was individually inspected, HTTP 200/pass with no record or inspection
  failures. The configured route axe scan has no serious/critical violations.
- Figure parity keeps 38 print figures: eight TikZ and 30 includegraphics;
  31 web figures leave seven missing-parity figures elsewhere in the book.
- All local QA sessions were reaped before staging/replay. Development-log
  validation reports only pre-existing peer metadata gaps in DL-#3903/#3902;
  those entries are preserved. One issue-keyed SPEC row is reserved for the PR.

Exact reproduction commands include the focused test pair
`py -3.12 -X utf8 -m pytest tests/test_forces_torques_chapter_rigor.py tests/test_audit_quarto_figure_parity.py --no-cov`,
`py -3.12 -X utf8 docs/development/technical-review/build_forces_torques_figures.py`,
root-selected Quarto render through `render_selected.py`, and
`pdflatex -interaction=nonstopmode -halt-on-error main.tex` with BibTeX and two
resolution passes in the book directory. The normal production gate is
`node scripts/verify-public-site.js` with the actual Chapter 4 route manifest.
