# Verification and Validation of the Wrist Companion

Technical revision: 8 September 2026 (#4299).

Use separate evidence levels. Passing a software check verifies the specified
calculation; it does not validate a biological mechanism or a coaching recommendation.
The earlier document's checked “validation complete” claims are superseded.

## 1. Independent Cardan Verification

The phase convention is chi = atan2(cos(delta) sin(phi), cos(phi)), continued
through revolutions. Use radians in functions. For fixed |delta| < pi/2:

1. Differentiate that angle numerically away from branch discontinuities and
   compare with the helper's speed ratio. A centered step of 1e-6 radians is
   suitable for the tested moderate bends; check step-size sensitivity.
2. Integrate the speed ratio over 0 to 2 pi. It must produce one full output
   revolution. This catches the older square-root denominator independently
   of its reciprocal torque formula.
3. At zero bend check unit speed ratio for all phases. At a 30-degree bend
   check 0.866025 at phase 0 and 1.154701 at phase 90 degrees. Delivered torque
   ratios are reciprocal under the declared ideal quasistatic assumptions.
4. Check periodicity, even symmetry about phase 0, nonfinite-input rejection
   and the explicitly disclosed legacy 89-degree clipping behavior.
5. Verify phase/bend argument order in the current-value graph, phase sweep,
   Qt helpers and standalone JavaScript calculation.

The full reference table is in [MATHEMATICAL_DERIVATION.md](MATHEMATICAL_DERIVATION.md).
The old table's exact unit ratio at 45 degrees and its reversed extrema did not
match a consistent Cardan convention. Do not retain those values as expected tests.

Run focused Python tests from the repository root using its Python 3.12 environment:

```bash
python -m pytest tests/test_wrist_constraint_mechanics.py tests/test_wrist_simulator.py tests/test_wrist_universal_joint.py --no-cov
```

The new angle-derivative, full-turn, finite-input and sweep-parity cases fail
against the old implementation and pass after correction. The repository's
full tests, lint, type checks and visual publication gates remain separate
requirements; consult the development log for their actual recorded outcomes.

## 2. Wrist Mechanics Verification

Verify the relative-rotation Jacobian by finite differences of the rotation
matrix. Check orthogonality of the reaction direction to both permitted
instantaneous axes. Change configuration and verify its coordinates in both
forearm and hand frames rather than assuming a fixed longitudinal axis.

Solve the full constrained acceleration/multiplier system and verify both
force balance and acceleration-level constraints. Perturb an actuator input
at fixed state: reactions can change. Reconstruct the same motion from
reduced coordinates, then recover reactions for comparison.

Check individual segment power as well as combined constraint power, using
the same frame and reference point for each wrench–velocity pair. Verify
inertia transport and the accelerating-reference-point term. For a compliant
extension, account for stored energy and dissipation instead of asserting
zero constraint power for a deforming connection.

For uncertainty, reproduce the frozen scalar torque example including the
one-half integration factor. Change the temporal covariance deliberately and
verify the different terminal variance. Compare the face-normal Jacobian with
finite orientation perturbations; do not equate scalar shaft rotation with
face yaw at arbitrary loft and lie.

## 3. Inspect Every Interface

Check meaningful labels, units, keyboard operation and readable layouts in
the browser and Qt application. A diagram of a hand must not imply that
Cardan shaft phase is anatomical wrist deviation. Verify that each graph and
information panel describes the same selected synthetic angles.

The time traces evaluate a fixed-phase gain on an arbitrary input signal.
They are not integrated shaft or swing trajectories. Component amplitude
percentages are not shares of energy; their sum need not be 100 percent. The
default inertia ratio is illustrative, and acceleration traces are isolated
scalar responses. Inspect zero, moderate and near-limit angles, positive and
negative phases, and all plot modes for numerical and explanatory consistency.

## 4. Mechanical and Human Qualification

For a physical Cardan rig, characterize geometry, supports, compliance,
friction, sensors and component inertia. Compare both motion and port power,
with uncertainty and independent trials. Do not invent an expected 1–2 percent
accuracy target without an instrument/model error budget.

For the wrist hypothesis, measure hand–club attachment, carpal/forearm motion,
club delivery and repeat-trial variability. Add force sensing or explicitly
justify contact-load allocation when both hands form a closed chain. Validate
on participants and perturbations not used to tune the model. Include adaptation,
measurement covariance, actuator feasibility and model sensitivity.

The preferred grip is an outcome to investigate, not an acceptance criterion.
A model that predicts 20–40 degrees is not validated merely because familiar
instruction recommends something that sounds similar. The prediction must
use measured coordinates and survive the relevant comparisons. Empirical
golf qualification remains outstanding.
