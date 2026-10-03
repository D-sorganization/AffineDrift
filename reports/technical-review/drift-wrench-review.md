# Drift, Wrench and Double-Pendulum Power — Article Review

Issue #4855, epic #4009/corpus #4021. Baseline remote main is `c1d33e780b9a920cf500da2b3adbf2d250441a4b`, the verified delivery of DCR PR #4856. The complete original article and generated critique include were read. This checkpoint contains corrections and focused validation; broad regression and source binding remain pending. It does not advance whole-corpus completion or close the empirical energy-blindness critique.

## Argument and Corrections

The article's useful question is how current input changes a transmitted force and the power entering a connected body. The original mass matrix, velocity bias, gravity and corrected inverse-dynamics/power identities are valid. The opening nevertheless equated active force with conscious pushing, drift with passive momentum, and late-downswing pulling power with natural dominance. Those interpretations do not follow from the model and conflict with its later qualifications.

- Define the input zero and retained loads before interpreting drift. Re-centering the input shifts the drift term; net torque is not a measurement of individual muscle action, intent or metabolic effort. Constraint reactions generally depend on input and must be solved with acceleration.
- Declare the inertial axes, positive angles and torque signs, force direction, application point, COM distances and centroidal inertias. Define the actuation-map dimensions and distinguish generalized coordinate rates from other speeds. Remove the nonexistent equation (2.6) reference and distinguish the scalar velocity-bias coefficient from the earlier vector bias, and the identity input map from distal inertia.
- Derive distal power from COM translation, gravitational potential and the COM moment balance. Pair force with the velocity at its application point. A translated wrench preserves power only when its moment and point velocity are transformed together; an observer change is a different operation.
- Show that inter-link force powers cancel between bodies sharing a joint-point velocity, while equal-and-opposite motor couples supply power at the relative rate. A zero relative rate at an instant does not lock the joint. Positive torque can do negative work.
- Give manufactured same-state examples in which proximal torque changes distal force power despite zero distal torque. Force-versus-couple and drift-versus-input are different decompositions. A later zero-input trajectory has changed state and is a separate comparison.
- Replace unsupported flexible-shaft capacity and three-dimensional face-closure claims with their actual model limits. Label the critique boxes as questions rather than invented attributed consensus. Replace the Streamlit promise and two-import stub with links to existing mechanics and executable power checks. Restore real cross-reference targets.

These corrections retain the earlier valid inverse-dynamics, torque-pair, impedance and spatial-fidelity qualifications. Algebraic equations are preserved or typeset equivalently; they are not recast as discoveries of previously incorrect mechanics.

## Independent Mechanical Evidence

The preparatory SymPy derivation starts with COM positions and kinetic/gravitational energies for arbitrary positive parameters. Five exact assertions verify the mass matrix; combined velocity bias and gravity; the distal COM moment balance; distal energy rate versus interface power; and whole-system energy rate versus relative-coordinate motor power. This is mathematical evidence for the declared ideal model, not golfer data or a reproduction of an experiment.

The new numerical tests reuse the previously reviewed two-link operators without modifying them. They independently differentiate distal COM energy, check moments using the COM-to-joint lever, test a Cartesian set of three states and three inputs, and verify the affine force gain and motor-pair power. They also bind the article's displayed force-power values to the calculation. Relative tolerances are explicitly zero for the finite-difference and moment checks; the directional energy derivative has an absolute tolerance of 2e-8 W. The existing chapter tests retain independent kinetic-energy, potential-gradient and whole-system power checks.

At the declared example state, zero input gives 0.341483 W of distal force power. A 2 N m proximal input with zero distal input gives 1.130753 W, including 0.789270 W of same-state input-induced force power; whole-system motor power is 3.4 W. A 2 N m distal input instead gives -1.2 W of distal moment power and -4.6 W of motor-pair power. These are arbitrary mechanical cases, not calibrated swing phases or recommended strategies.

## Primary Reading and Limits

- [MIT Underactuated Robotics, Multibody Dynamics](https://underactuated.mit.edu/multibody.html): Lagrange/manipulator formulation, relative-coordinate double pendulum, generalized speeds and bilateral constraints. Supports the mechanics framework, not empirical golf claims.
- [Robertson and Winter (1980)](<https://doi.org/10.1016/0021-9290(80)90172-4>): publisher abstract and PubMed metadata, concerning a sagittal walking model. Full-paper retrieval failed; no full-text review or golf-specific inference is claimed.
- [MacKenzie, McCourt and Champoux (2020)](https://www.golfsciencejournal.org/article/12640-how-amateur-golfers-deliver-energy-to-the-driver): publisher abstract, introduction, methods, results/tables and opening discussion. The study concerns 76 right-handed golfers and grip force/couple work, with between-person associations. It does not identify the article's drift/input split or establish a coaching intervention. The COM moment sign here is independently derived from the COM-to-application-point lever; the paper's printed lever notation is not copied uncritically.

## Validation and Preservation

Against the original article, eight publication-contract cases failed while twelve new mechanical cases passed (3.25 s). Seven failures identify the unsupported wording; the eighth requires the new worked example. After correction, the combined new/retained mechanics and scope suite passed 48 cases in 2.94 s. Black and Ruff passed. The final line-wrap correction rerun also passed all 48 cases (4.18 s). The full regression remains required.

The first corrected render passed four browser/axe cells but manual inspection found a clipped COM Jacobian on desktop and long acceleration pairs on mobile. The formulas and numerical prose were reflowed without changing their values. Original screenshots and the first verifier result remain in QA; twelve revised/detail captures were inspected, and all four browser/axe cells pass again. The existing mobile floating-control overlap and small responsive display-math type remain explicit layout limitations. Exact scoped evidence is in `drift-wrench-render-verification.json`. This demonstrates why automated page-overflow checks alone are not visual acceptance.

`drift-wrench-prior-review.json` preserves the historical route record, the original article digest, 46 protected files and a reproducible fingerprint of the other 250 route identities/dispositions. Shared evidence-digest refreshes do not renew their scientific acceptance. Eighteen original rendered section anchors are retained. No new physical measurements, three-dimensional fidelity result, live deployment or whole-book certification is claimed.

## Delegation and Lead Adjudication

Eight successful text-only agy CLI Gemini 3.8 Flash helpers supplied equation/claim inventories, a summary, a test plan, link inventory, numerical draft, copy review and handoff draft. They had no tool/edit/merge or acceptance authority. Lead review rejected a wrong potential-energy sign in a checklist, confusion of an instantaneous zero rate with a locked joint, identification of a force contribution as total force, and an invented placeholder-organization complaint. It accepted missing Jacobian/angular-velocity definitions and unresolved links. The numerical draft was expanded to all nine state/input combinations with explicit absolute tolerances and an independent affine force-gain check. Handoff drafts' invented file-URI links and ambiguous file-digest/Git-revision wording were rejected.
