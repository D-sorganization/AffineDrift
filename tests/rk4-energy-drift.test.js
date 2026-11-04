/**
 * Passive (zero-torque, zero-damping) energy drift of the fixed-step RK4 in
 * js/ztcf-explorer.js and js/drift-control-sandbox.js (#5256). The measured
 * values and the keep-RK4 recommendation are in
 * reports/technical-review/rk4-energy-drift.md; the thresholds below are the
 * documented ones there.
 */
const ZE = require('../js/ztcf-explorer.js');
const DCS = require('../js/drift-control-sandbox.js');

/** Documented threshold: max |E(t) - E(0)| / |E(0)| over the widget's default horizon and dt. */
const DEFAULT_REL_DRIFT_MAX = 1e-9;
/** Documented threshold at ten times the default horizon, same dt. */
const LONG_REL_DRIFT_MAX = 1e-7;

function kinetic(mass, qd) {
  return 0.5 * qd.reduce((acc, v, i) => acc + v * mass[i].reduce((s, m, j) => s + m * qd[j], 0), 0);
}

/** Largest relative departure of E = T + V from E(0) along the samples. */
function relativeDrift(samples, energy) {
  const e0 = energy(samples[0]);
  return Math.max(...samples.map(s => Math.abs(energy(s) - e0))) / Math.abs(e0);
}

function ztcfDrift(horizon, steps) {
  const d = ZE.DEFAULTS;
  const model = ZE.makeModel(d.params);
  const energy = s => kinetic(ZE.rigidMassMatrix(model, s.q), s.qd) + ZE.potentialEnergy(model, s.q);
  return relativeDrift(ZE.ztcfTrajectory(model, d.q0, d.qd0, horizon, steps), energy);
}

function sandboxDrift(horizon, steps) {
  const d = DCS.DEFAULTS;
  const p = DCS.makeParams(d.params);
  const energy = s => kinetic(DCS.massMatrix(s.q, p), s.qd) + DCS.potential(s.q, p);
  return relativeDrift(DCS.simulate(p, d.q0, d.qd0, [0.0, 0.0], horizon, steps), energy);
}

const WIDGETS = [
  ['ztcf-explorer', ztcfDrift, ZE.DEFAULTS],
  ['drift-control-sandbox', sandboxDrift, DCS.DEFAULTS],
];

describe.each(WIDGETS)('%s passive RK4 energy drift', (name, drift, d) => {
  test('stays under the documented threshold over the default horizon and dt', () => {
    expect(drift(d.horizon, d.steps)).toBeLessThan(DEFAULT_REL_DRIFT_MAX);
  });

  test('stays under the long-horizon threshold at ten times the horizon, same dt', () => {
    expect(drift(10 * d.horizon, 10 * d.steps)).toBeLessThan(LONG_REL_DRIFT_MAX);
  });

  test('shrinks at roughly fourth order when dt halves (integrator error, not model error)', () => {
    const coarse = drift(d.horizon, d.steps / 4);
    const fine = drift(d.horizon, d.steps / 2);
    expect(coarse / fine).toBeGreaterThan(8);
  });

  test('negative control: a coarse step exceeds the threshold, so the measurement can fail', () => {
    expect(drift(d.horizon, 2)).toBeGreaterThan(DEFAULT_REL_DRIFT_MAX);
  });
});
