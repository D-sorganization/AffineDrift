# Nonlinear Control Insights: Technical Review — #4431

## Scope and Argument

Read the entire article, its generated critique annotation and the complete
linked sequencing critique. The main argument contradicted its own more careful
lay summary: it inferred physiological uniqueness from an affine model, used an
indefinite inertia matrix, mixed degrees with radians, and conflated coupling,
energy amplification, accessibility and practical control authority.

The replacement follows five connected questions: instantaneous acceleration,
energy accounting, declared intervention, finite-time reachability and
measurement identifiability. Earlier inputs change the state at which later
drift and input effectiveness are evaluated. Contact affects both acceleration
and reaction forces. Neither a large contribution nor a good trajectory fit
establishes the cause or efficacy of a human intervention.

## Corrected Findings

- **P1 — Units and Complete State:** Derive load, acceleration and state-rate
  contributions separately. Include retained flexible coordinates and identify
  when physiological or controller memory requires extra state. Correct the
  zero-input flow derivative and distinguish instantaneous drift from history.
- **P1 — Intervention and Contact:** Replace unique anatomical input/zero
  activation claims with a declared model intervention, local well-posedness,
  retained loads and states, contact feasibility, and hybrid continuation rules.
  Explain that a velocity-reset calculation is not a load-cell measurement.
- **P1 — Coordinate and Input Transformations:** Preserve the physical input
  under a state diffeomorphism, include the acceleration Hessian term, and show
  why an input offset changes the zero-input field. Limit the geodesic statement
  to a free system with a purely kinetic Lagrangian.
- **P1 — Actuation and Task Authority:** Use input-map rank and admissible
  acceleration sets. An underactuated horizontal model at rest is a counterexample
  to necessary drift dominance. Include task Jacobians and velocity terms;
  distinguish direction, bounds and horizon from a scalar magnitude ratio.
- **P1 — Physical Coupling and Energy:** Replace the invalid inertia/degree
  arithmetic with the Chapter 6 Cartesian rod model. Solve the full matrix;
  distinguish acceleration increment, total acceleration, relative and absolute
  distal angle. Derive mechanical power balance and separate it from angular
  momentum and segment/interface energy accounting. Remove the unsupported
  five-to-ten amplification and universal braking benefit.
- **P1 — Control Geometry and Finite Time:** Distinguish accessibility, STLC,
  reversible driftless commutators, geometric phase and finite-time output
  effects. Supply counterexamples and a trajectory variational equation. High
  speed does not make geometry categorically irrelevant; bounds and event-time
  sensitivity must accompany any useful performance claim.
- **P1 — Tool and Identification Scope:** State feasibility, output-rank and
  internal-dynamics conditions for partial feedback linearization. Define
  optimal-control costs and constraints without predicting universally small
  inputs. Separate energy shaping, observability, unknown-input inference,
  sensitivity, robustness guarantees and learning identifiable dynamics.
- **P2 — Evidence and Resource Claims:** Replace unverified video timestamps
  and lecture attributions with inspected primary-source links. Part 5 is a
  numerical verification protocol without a revision-bound historical run
  package. Preserve the open governed critique and avoid claiming a human test.

## Independently Checked Mechanics

The old matrix [[3.5,0.8],[0.8,0.15]] has determinant -0.115 and one negative
eigenvalue (-0.031239478); it cannot represent positive kinetic energy on two
independent massive coordinates. Converting the old acceleration values to
radians would give coupling loads -0.698132 and +2.792527 N m, rather than -40
and +160, but would not repair that inertia defect.

The replacement reuses the Chapter 6 two uniform rods: masses (2,0.2) kg,
lengths (0.4,0.3) m, COMs L/2, COM inertias mL²/12, g=9.81 m/s², q1 CCW from
horizontal and q2 relative. At q=(45,70) degrees, v=(8,12) rad/s, the Cartesian
COM Jacobian construction gives inertia eigenvalues (0.005308140,0.153567010).
With u=(-2,0) N m, the input acceleration increment is
(-14.721123,+24.790964) rad/s² and the total is (-3.021639,-94.462667).
The absolute distal-angle increment is the sum, +10.069841 rad/s².

The new tests reuse the independently assembled Cartesian mass, potential and
bias functions in `tests/test_zero_torque_chapter_rigor.py`, without changing
that frozen file or introducing a production solver. A separate directional
finite difference of kinetic plus potential energy at step 1e-6 s gives
-16.00000000046 W, agreeing with actuator power v·u=-16 W. Positive, negative
and zero torque cases are checked. These are local teaching examples, not an
upstream qualified forward-run fixture or fitted golfer data.

Other numerical checks integrate the nonlinear coordinate change y=q², a
bounded scalar drift that cannot reverse, saturated/sinusoidal double-integrator
inputs and four reversible driftless flows with displacement epsilon². The
input-offset identity preserves the family of dynamics while changing its zero
slice. The initial red publication check failed on the old article's missing
checked acceleration; the rewritten source and all numerical checks then pass.

## Primary-Source Access and Limits

- MIT, [Underactuated Robotics introduction](https://underactuated.mit.edu/intro.html):
  read the definitions/input constraints. It supports model-specific actuation
  analysis, not a universal golf drift-dominance claim.
- MIT, [Acrobot/cart-pole chapter](https://underactuated.mit.edu/acrobot.html):
  read partial feedback linearization, output rank and internal dynamics.
- MIT, [LQR chapter](https://underactuated.mit.edu/lqr.html): read the local
  trajectory-linearization and input/state-constraint sections. No golf
  controller or optimal policy was reproduced.
- Modern Robotics publisher-hosted transcripts,
  [13.3.2 Part 2](https://modernrobotics.northwestern.edu/nu-gm-book-resource/13-3-2-controllability-of-wheeled-mobile-robots-part-2-of-4/)
  and [Part 4](https://modernrobotics.northwestern.edu/nu-gm-book-resource/13-3-2-controllability-of-wheeled-mobile-robots-part-4-of-4/):
  read reachable-set definitions and the displayed driftless rank theorem.
  No video playback or timestamps were verified.
- Kelly and Murray,
  [Geometric Phases and Robotic Locomotion](https://murray.cds.caltech.edu/Geometric_Phases_and_Robotic_Locomotion):
  author-hosted abstract only. The linked full preprint timed out. No detailed
  theorem or golf-specific result is attributed to an unread paper.
- The linked critique cites Putnam (1993). Search metadata was available but
  PubMed returned no readable body and the publisher returned 403. No full-paper
  read or empirical conclusion from it is claimed or added to the article.

## Adversarial Review and Acceptance Boundary

Positive local acceleration increments need not give positive total acceleration
or a later speed benefit. Braking can remove total energy. Coordinate covariance
does not select a physiological intervention. Full field span with bounded drift
does not ensure STLC. A fixed local gain does not specify endpoint correction.
Unknown inputs can confound learned drift, and a fixed-contact continuation can
be infeasible. Each counterexample limits a specific implication while leaving
the useful mechanical or control concept intact.

The sequencing critique itself makes unsupported categorical full-actuation,
three-joint reachability, momentum-conservation and necessary-efficiency claims.
Its source and governed open disposition are preserved. The replacement notes
those limits rather than adopting them as authority or silently adjudicating the
critique. No shared critique ledger, physiological model, solver or fixture is
changed.

The associated rendering record documents all22 displays and106 expressions,
four desktop/mobile and light/dark cases, six mobile wide-expression endpoints
in both themes, and keyboard-expanded reader summaries with four clean axe scans.
Initial mobile math was too small; page-local CSS restores reading size with
scrolling. A long inline sum was shortened after visual inspection. All27
new/shared checks, Black100, Ruff, title638 and final Quarto links pass. Source/render acceptance must be bound to a committed
checkpoint; CI, main merge and live publication are separate release gates.

The user requested a stopping checkpoint while this rewrite was in progress.
Finish #4431 and the already-open manifesto PR #4432, verify publication and
save turnover records, then pause the broader goal. Do not start new reviews.

## Release Link Correction

PR #4433 CI identified 17 internal links using source `.qmd` suffixes.
Changed only those suffixes to the required published `.html` routes; no
scientific statement, formula, CSS or numerical test changed. The initial
source/render checkpoint remains 3053bb71; final link validation and rendering
passed (site gate; warning-free Quarto render; production 4/4, zero serious or
critical axe violations) and are recorded before rebinding the final evidence. The full content
lint suite passed: 131 passed, four existing skips. The issue record now names
the new regression module as well as the reused mechanics helper module.
