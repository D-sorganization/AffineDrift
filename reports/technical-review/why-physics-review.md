# Why Physics Matters: Paired Technical Review — #4450

## Scope and Argument

Reviewed both complete opening-chapter sources, their force diagram, coaching and
skill claims, model descriptions, equations, road map and exercises. Compared the
corrected Chapter 2 state/coordinate treatment and Chapter 3/5 model and input
conventions. The revised argument connects motion, loads, energy, constraints and
chosen inputs to finite-time club delivery and impact. It does not infer a
physiological or coaching result from an exact toy-model calculation.

The two editions use the same argument and worked examples. The old print figure
is replaced by a computed paired vector figure. This review covers Chapter 1;
recompiling the complete book does not certify its remaining chapters or the
whole-book reconciliation. The broader corpus/epic remains open.

## Corrected Findings

1. **P1 — Acceleration, Momentum and Work:** Removed momentum as an applied force
   or new energy source, the radius-free 179g claim, and the unsupported passive-work
   percentage. Distinguish tangential and normal acceleration, force power and
   integrated work. A declared point-mass example has 1280 m/s² normal acceleration,
   257.962 N tension and zero instantaneous power at the bottom. Its 160 J kinetic
   energy already exists; a 1 m gravity drop supplies only 1.962 J in this model.
2. **P1 — Drift, Inputs and Skill:** Replace a unique passive/muscular force split
   with a chosen-input state-derivative decomposition. Include the input map and
   kinematic drift block, explain retained internal states and show a baseline
   shift preserving acceleration while changing attribution. Remove elite/novice
   DCR diagnoses and coaching promises; specify what further validation requires.
3. **P1 — Constraints and Intervention:** Separate drive-torque removal, attachment
   removal and physiological relaxation. Recompute reactions with actuation, state
   contact feasibility and the energy boundary, and avoid claiming reactions are
   independent of muscular action. A retained unforced pendulum and a released
   mass begin at the same state but follow different paths. For a rigid released
   club, ballistic COM motion is distinct from the clubhead's rotational motion.
4. **P1 — Model and Human Inference:** Use effective two-link bodies rather than a
   uniquely anatomical model. Retain limitations involving bilateral grasp, moving
   support, shaft flexibility, spatial face orientation and impact. Net torque does
   not uniquely identify muscle force or metabolic effort. Remove universal chaos,
   feedback-stability and continuous-nonzero-torque assertions. Separate measured
   evidence, model predictions and exact identities.
5. **P2 — Scientific Positioning and Outcome Chain:** Replace dismissals of prior
   work and unsupported named-player angles with scoped primary-source examples.
   Relate feasible state/input histories to delivery, collision and ball flight;
   distinguish same-clock-time comparison from each trajectory's impact event.
6. **P2 — Exercises and Presentation:** Supply six well-posed exercises and worked
   answers. Correct free-fall assumptions, point-contact spin versus slip/rolling,
   radial pulling power without pivot torque, cue-to-torque ambiguity, throwing
   energy versus peak muscle force and input-baseline dependence. Preserve chapter,
   equation and figure destinations and the three On This Site bridge links.

## Independent Mechanics Checks

`scripts/build_why_physics_figure.py` is the reproducible figure recipe. It solves
an unforced pendulum from theta = 0 and angular rate = 32 rad/s with L = 1.25 m,
g = 9.81 m/s² through 60 ms. The alternative removes the tether without an impulse.
Figure markers are 10 ms apart, with equal spatial axis scales. Parameters are
manufactured and are not fitted anthropometry or an observed golf trajectory.

`tests/test_why_physics_rigor.py` independently differentiates the Cartesian
trajectory to check its radius, mechanical-energy budget, initial velocity and
released acceleration. It verifies positive tether tension throughout the shown
interval, the bottom Newton balance and zero power, the gravity height budget,
baseline-shift invariance, radial-pull work and muscle-force nonuniqueness. It also
checks both source editions against the identified false statements and published
numerical results. Tests do not certify golfer behavior or metabolic predictions.

RED evidence: nine content failures and three setup errors for the absent figure
module, with eight independent checks passing. The subsequent sole failure was a
NumPy expected-array shape mismatch, corrected by checking each acceleration
component separately without changing the physical tolerance or expected result.

## Primary Sources and Interpretation

- [Tedrake, Multi-Body Dynamics](https://underactuated.mit.edu/multibody.html):
  inspected the manipulator, generalized-velocity and bilateral-constraint
  formulations. The chapter declares its own sign conventions and model boundary.
- [Nesbit and Serrano, Work and Power Analysis of the Golf Swing](https://www.jssm.org/jssm-04-520.xml-Fulltext):
  read methods, results and discussion. The study uses modeled work/power from
  one selected swing per each of four amateur subjects. This supports explicit
  energy accounting, not direct muscle-metabolism measurement or a population
  passivity rule. Existing bibliography key `Nesbit2005b` is retained.
- [MacKenzie and Sprigings, Three-Dimensional Forward Dynamics Model](https://people.stfx.ca/smackenz/Publications/MacKenzie%202009%20A%20three%20dimensional%20forward%20dynamics%20model%20of%20the%20golf%20swing.pdf):
  checked model construction, actuation, fitting/optimization and reported
  interpretation. A model with torque generators and a flexible shaft does not
  establish the opening chapter's universal passive-work percentage. Existing key
  `MacKenzie2009` is retained. We do not claim an exhaustive literature refutation.

## Verification and Release Boundary

Final machine-readable print/web verification and source hashes are recorded
in `why-physics-render-verification.json`: 529-page PDF, Chapter 1 physical pages
32–41 inspected, four production browser cases passed, 103/103 math expressions,
six mobile displays and the figure keyboard-scrollable at reading size. The
claim-audit route remains deferred during editing. Bind the completed six-finding
review only after that immutable evidence revision exists. Record merge and live
publication separately so frozen source/render reports are not rewritten later.
