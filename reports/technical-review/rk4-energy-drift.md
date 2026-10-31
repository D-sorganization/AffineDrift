# RK4 Energy Drift in the ZTCF Explorer and Drift-Control Sandbox Widgets

Issue #5256 (parent epic #5122; F-AD-007 lists the five fixed-step RK4 copies).

## Question

Do the fixed-step RK4 integrators in `js/ztcf-explorer.js` (`rk4`) and
`js/drift-control-sandbox.js` (`planarTrajectory`) conserve energy well enough
on the passive case to keep, or should either widget switch integrator?

## Method

- Passive case: zero torque and no damping term. Both models are conservative,
  so the total energy E = ½ q̇ᵀ M(q) q̇ + V(q) must stay constant. Any change is
  integrator error plus the finite-difference Coriolis error (step 1e-6).
- The energy comes from each widget's own exported `rigidMassMatrix` /
  `massMatrix` and `potentialEnergy` / `potential`.
- Each trajectory is a widget's declared `DEFAULTS` (initial state, horizon,
  steps). The metric is max over samples of |E(t) − E(0)| / |E(0)|.
- Reproduce with `npx jest tests/rk4-energy-drift.test.js`.

## Results

| Widget | Horizon | dt | Steps | Max Relative Drift |
| --- | --- | --- | --- | --- |
| ztcf-explorer (default) | 0.2 s | 1 ms | 200 | 2.9e-12 |
| ztcf-explorer | 0.2 s | 2 ms | 100 | 1.2e-10 |
| ztcf-explorer | 0.2 s | 4 ms | 50 | 2.0e-9 |
| ztcf-explorer (10× horizon) | 2.0 s | 1 ms | 2000 | 1.1e-8 |
| drift-control-sandbox (default) | 0.5 s | 1 ms | 500 | 7.6e-11 |
| drift-control-sandbox | 0.5 s | 2 ms | 250 | 1.3e-9 |
| drift-control-sandbox | 0.5 s | 4 ms | 125 | 2.0e-8 |
| drift-control-sandbox (10× horizon) | 5.0 s | 1 ms | 5000 | 4.6e-9 |

Initial energies are 13.13 J (ztcf-explorer) and 27.44 J (sandbox). Halving dt
cuts the drift about 16×, which is RK4's fourth order. So the drift is
integrator truncation error, not a model inconsistency between M, V and the
gravity torque.

## Recommendation

- **ztcf-explorer: keep RK4.** At the default horizon and dt the drift is
  2.9e-12 relative (about 4e-11 J). That is far below anything visible in the
  clubhead-speed readout, and the widget only integrates 0.2 s.
- **drift-control-sandbox: keep RK4.** The default drift is 7.6e-11 relative.
  Even at ten times the horizon it stays under 1e-8.
- A symplectic or variational integrator would buy nothing at these horizons.
  It would also break parity with the Python references
  (`GolfModel.ztcf_trajectory`, `planar_double_pendulum_trajectory`), which
  are fixed-step RK4 too.

## Documented Thresholds (Enforced by the Test)

- Default horizon and dt: max relative drift < 1e-9 (about 300× headroom over
  the worse widget).
- Ten times the default horizon, same dt: < 1e-7.
- Halving dt must shrink the drift by more than 8× (order at least 3).
- Negative control: a 2-step integration must exceed 1e-9, so the measurement
  can fail.

## Limitations

- Only the passive case is measured. Forced cases are not conservative, so
  energy drift is not defined for them.
- One initial state per widget (the declared defaults). Stiffer states, such
  as larger initial velocities, would drift more at the same dt.
- The other three RK4 copies listed in F-AD-007 are out of scope here.
