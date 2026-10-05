/** Mirrors src/affine_control/dynamics.py::double_pendulum_mass_matrix,
 * christoffel_coriolis, double_pendulum_coriolis and
 * planar_double_pendulum_trajectory, and
 * src/affine_control/double_pendulum_affine.py (WEB-06.3, #4533).
 * Pure functions only; no DOM dependency. Parity with Python is checked
 * against tests/fixtures/widgets/drift-control-sandbox.parity.json.
 */
'use strict';

function assert(condition, message) {
  if (!condition) throw new Error(`[drift-control-sandbox] Contract violation: ${message}`);
}

/** Mirrors double_pendulum_affine.py::DoublePendulumParams. */
function makeParams({m1, m2, l1, l2, gravity = 9.81}) {
  const params = {m1, m2, l1, l2, gravity};
  for (const [name, value] of Object.entries(params)) {
    assert(Number.isFinite(value) && value > 0, `${name} must be finite and positive`);
  }
  return Object.freeze(params);
}

/** Mirrors dynamics.py::double_pendulum_mass_matrix. */
function massMatrix(q, p) {
  const off = 0.5 * p.m2 * p.l1 * p.l2 * Math.cos(q[0] - q[1]);
  return [[(p.m1 / 4.0 + p.m2) * (p.l1 * p.l1), off], [off, p.m2 * (p.l2 * p.l2) / 4.0]];
}

/** Mirrors dynamics.py::christoffel_coriolis (central differences, step 1e-6). */
function christoffelCoriolis(massMatrixFn, q, qd, step = 1e-6) {
  const n = q.length;
  const grad = [];
  for (let k = 0; k < n; k += 1) {
    const forward = q.slice();
    const backward = q.slice();
    forward[k] += step;
    backward[k] -= step;
    const mf = massMatrixFn(forward);
    const mb = massMatrixFn(backward);
    grad.push(mf.map((row, r) => row.map((value, c) => (value - mb[r][c]) / (2.0 * step))));
  }
  const coriolis = [];
  for (let k = 0; k < n; k += 1) {
    const row = [];
    for (let j = 0; j < n; j += 1) {
      let total = 0;
      for (let i = 0; i < n; i += 1) {
        total += (grad[i][k][j] + grad[j][k][i] - grad[k][i][j]) * qd[i];
      }
      row.push(0.5 * total);
    }
    coriolis.push(row);
  }
  return coriolis;
}

/** Mirrors dynamics.py::double_pendulum_coriolis. */
function coriolis(q, qd, p) {
  const k = 0.5 * p.m2 * p.l1 * p.l2 * Math.sin(q[0] - q[1]);
  return [[0.0, k * qd[1]], [-k * qd[0], 0.0]];
}

function matVec(a, v) {
  return [a[0][0] * v[0] + a[0][1] * v[1], a[1][0] * v[0] + a[1][1] * v[1]];
}

/** 2x2 solve with partial pivoting, as numpy.linalg.solve (LAPACK getrf/getrs). */
function solve2(a, b) {
  let [r0, r1] = [0, 1];
  if (Math.abs(a[1][0]) > Math.abs(a[0][0])) [r0, r1] = [1, 0];
  const a00 = a[r0][0];
  assert(a00 !== 0, 'mass matrix must be nonsingular');
  const l = a[r1][0] * (1.0 / a00);
  const u11 = a[r1][1] - l * a[r0][1];
  assert(u11 !== 0, 'mass matrix must be nonsingular');
  const y1 = b[r1] - l * b[r0];
  const x1 = y1 / u11;
  const x0 = (b[r0] - x1 * a[r0][1]) / a00;
  return [x0, x1];
}

/** Mirrors double_pendulum_affine.py::potential. */
function potential(q, p) {
  return -p.gravity * ((0.5 * p.m1 + p.m2) * p.l1 * Math.cos(q[0]) + 0.5 * p.m2 * p.l2 * Math.cos(q[1]));
}

/** Mirrors double_pendulum_affine.py::grad_potential. */
function gradPotential(q, p) {
  return [
    p.gravity * (0.5 * p.m1 + p.m2) * p.l1 * Math.sin(q[0]),
    p.gravity * 0.5 * p.m2 * p.l2 * Math.sin(q[1]),
  ];
}

/** Mirrors double_pendulum_affine.py::generalized_torque. */
function generalizedTorque(shoulder, wrist) {
  assert(Number.isFinite(shoulder) && Number.isFinite(wrist), 'torques must be finite');
  return [shoulder - wrist, wrist];
}

/** Mirrors double_pendulum_affine.py::affine_split; returns [driftQdd, inputQdd]. */
function affineSplit(q, qd, torque, p) {
  const mass = massMatrix(q, p);
  const cqd = matVec(coriolis(q, qd, p), qd);
  const grad = gradPotential(q, p);
  const bias = [cqd[0] + grad[0], cqd[1] + grad[1]];
  return [solve2(mass, [-bias[0], -bias[1]]), solve2(mass, torque)];
}

/** Mirrors double_pendulum_affine.py::tip_position. */
function tipPosition(q, p) {
  return [
    p.l1 * Math.sin(q[0]) + p.l2 * Math.sin(q[1]),
    -p.l1 * Math.cos(q[0]) - p.l2 * Math.cos(q[1]),
  ];
}

/** Mirrors double_pendulum_affine.py::tip_acceleration_split. */
function tipAccelerationSplit(q, qd, driftQdd, inputQdd, p) {
  const [c1, s1, c2, s2] = [Math.cos(q[0]), Math.sin(q[0]), Math.cos(q[1]), Math.sin(q[1])];
  const jacobian = [[p.l1 * c1, p.l2 * c2], [p.l1 * s1, p.l2 * s2]];
  const jdotQd = [
    -p.l1 * s1 * qd[0] ** 2 - p.l2 * s2 * qd[1] ** 2,
    p.l1 * c1 * qd[0] ** 2 + p.l2 * c2 * qd[1] ** 2,
  ];
  const jd = matVec(jacobian, driftQdd);
  return [[jd[0] + jdotQd[0], jd[1] + jdotQd[1]], matVec(jacobian, inputQdd)];
}

/** Mirrors dynamics.py::planar_double_pendulum_trajectory (fixed-step RK4). */
function planarTrajectory(massMatrixFn, gradPotentialFn, q0, qd0, torque, horizon, steps) {
  const dt = horizon / steps;
  const derivative = state => {
    const pos = state.slice(0, 2);
    const vel = state.slice(2);
    const cv = matVec(christoffelCoriolis(massMatrixFn, pos, vel), vel);
    const gp = gradPotentialFn(pos);
    const acc = solve2(massMatrixFn(pos), [torque[0] - (cv[0] + gp[0]), torque[1] - (cv[1] + gp[1])]);
    return [vel[0], vel[1], acc[0], acc[1]];
  };
  const axpy = (state, scale, k) => state.map((value, i) => value + scale * k[i]);
  let state = [q0[0], q0[1], qd0[0], qd0[1]];
  const out = [[0.0, q0.slice(), qd0.slice()]];
  for (let index = 0; index < steps; index += 1) {
    const k1 = derivative(state);
    const k2 = derivative(axpy(state, 0.5 * dt, k1));
    const k3 = derivative(axpy(state, 0.5 * dt, k2));
    const k4 = derivative(axpy(state, dt, k3));
    const sum = k1.map((value, i) => value + 2 * k2[i] + 2 * k3[i] + k4[i]);
    state = axpy(state, dt / 6.0, sum);
    out.push([(index + 1) * dt, state.slice(0, 2), state.slice(2)]);
  }
  return out;
}

/** Mirrors double_pendulum_affine.py::simulate; each sample carries its split. */
function simulate(p, q0, qd0, torque, horizon, steps) {
  assert(Number.isFinite(horizon) && horizon > 0, 'horizon must be finite and positive');
  assert(Number.isInteger(steps) && steps >= 1, 'steps must be at least 1');
  const trajectory = planarTrajectory(
    q => massMatrix(q, p), q => gradPotential(q, p), q0, qd0, torque, horizon, steps);
  return trajectory.map(([t, q, qd]) => {
    const [driftQdd, inputQdd] = affineSplit(q, qd, torque, p);
    return {t, q, qd, driftQdd, inputQdd};
  });
}

/** Declared illustrative scenario; scripts/generate_widget_parity.py pins the same values. */
const DEFAULTS = Object.freeze({
  params: {m1: 7.0, m2: 0.6, l1: 0.75, l2: 1.1, gravity: 9.81},
  q0: [2.6, 4.2],
  qd0: [0.0, 0.0],
  horizon: 0.5,
  steps: 500,
});
const PRESETS = Object.freeze({
  'zero-torque': {shoulder: 0.0, wrist: 0.0},
  'shoulder-drive': {shoulder: -20.0, wrist: 0.0},
  'shoulder-and-wrist': {shoulder: -20.0, wrist: -3.0},
});

const DriftControlSandbox = {
  makeParams, massMatrix, christoffelCoriolis, coriolis, solve2, potential, gradPotential,
  generalizedTorque, affineSplit, tipPosition, tipAccelerationSplit, planarTrajectory, simulate,
  DEFAULTS, PRESETS,
};
if (typeof window !== 'undefined') window.DriftControlSandbox = DriftControlSandbox;
if (typeof module !== 'undefined') module.exports = DriftControlSandbox;
