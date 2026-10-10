/** Mirrors src/affine_control/golf_model.py::GolfModel (rigid_mass_matrix,
 * gravity_torque, drift_acceleration, clubhead_speed, ztcf_trajectory),
 * dynamics.py::christoffel_coriolis and
 * src/affine_control/ztcf_explorer.py::actual_trajectory and explore
 * (WEB-06.4, #4534). Pure functions only; no DOM dependency. Parity with
 * Python is checked against tests/fixtures/widgets/ztcf-explorer.parity.json.
 */
'use strict';

function assert(condition, message) {
  if (!condition) throw new Error(`[ztcf-explorer] Contract violation: ${message}`);
}

/** Mirrors ztcf_contract.py::GRAVITY_M_S2 (golf_model.py uses the same value). */
const GRAVITY_M_S2 = 9.81;

/** Mirrors ztcf_contract.py::_build_supported_model; parameters from the fixture record. */
function makeModel({masses, lengths, inertias, com_fractions: comFractions}) {
  for (const [name, values] of Object.entries({masses, lengths, inertias, comFractions})) {
    assert(Array.isArray(values) && values.length === 3, `${name} must have three entries`);
    assert(values.every(v => Number.isFinite(v) && v > 0), `${name} must be finite and positive`);
  }
  return Object.freeze({masses, lengths, inertias, comFractions});
}

/** Mirrors GolfModel.com_offsets. */
function comOffsets(model) {
  return model.lengths.map((length, i) => length * model.comFractions[i]);
}

/** Mirrors GolfModel.link_angles (cumulative sum of relative joint angles). */
function linkAngles(q) {
  const out = [];
  let total = 0;
  for (const angle of q) {
    total += angle;
    out.push(total);
  }
  return out;
}

/** Mirrors GolfModel.com_jacobian; returns rows [dx/dq, dy/dq]. */
function comJacobian(model, q, index) {
  const angles = linkAngles(q);
  const offsets = comOffsets(model);
  const jac = [[0, 0, 0], [0, 0, 0]];
  for (let joint = 0; joint <= index; joint += 1) {
    let dx = 0;
    let dy = 0;
    for (let link = joint; link <= index; link += 1) {
      const reach = link === index ? offsets[link] : model.lengths[link];
      dx -= reach * Math.sin(angles[link]);
      dy += reach * Math.cos(angles[link]);
    }
    jac[0][joint] = dx;
    jac[1][joint] = dy;
  }
  return jac;
}

/** Mirrors GolfModel.rigid_mass_matrix. */
function rigidMassMatrix(model, q) {
  const total = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  for (let index = 0; index < 3; index += 1) {
    const jv = comJacobian(model, q, index);
    for (let r = 0; r < 3; r += 1) {
      for (let c = 0; c < 3; c += 1) {
        const linear = jv[0][r] * jv[0][c] + jv[1][r] * jv[1][c];
        const angular = r <= index && c <= index ? 1.0 : 0.0;
        total[r][c] += model.masses[index] * linear + model.inertias[index] * angular;
      }
    }
  }
  return total.map((row, r) => row.map((value, c) => 0.5 * (value + total[c][r])));
}

/** Mirrors GolfModel.potential_energy. */
function potentialEnergy(model, q, gravity = GRAVITY_M_S2) {
  const angles = linkAngles(q);
  const offsets = comOffsets(model);
  let height = 0;
  let total = 0;
  for (let index = 0; index < 3; index += 1) {
    total += model.masses[index] * gravity * (height + offsets[index] * Math.sin(angles[index]));
    height += model.lengths[index] * Math.sin(angles[index]);
  }
  return total;
}

/** Mirrors GolfModel.gravity_torque (central differences, step 1e-6). */
function gravityTorque(model, q, gravity = GRAVITY_M_S2, step = 1e-6) {
  return q.map((_, index) => {
    const forward = q.slice();
    const backward = q.slice();
    forward[index] += step;
    backward[index] -= step;
    return (potentialEnergy(model, forward, gravity) - potentialEnergy(model, backward, gravity))
      / (2.0 * step);
  });
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
  return grad.map((_, k) => grad.map((__, j) => {
    let total = 0;
    for (let i = 0; i < n; i += 1) total += (grad[i][k][j] + grad[j][k][i] - grad[k][i][j]) * qd[i];
    return 0.5 * total;
  }));
}

function matVec(a, v) {
  return a.map(row => row.reduce((sum, value, i) => sum + value * v[i], 0));
}

/** Gaussian elimination with partial pivoting, as numpy.linalg.solve (LAPACK getrf/getrs). */
function solve(a, b) {
  const n = b.length;
  const m = a.map(row => row.slice());
  const x = b.slice();
  for (let col = 0; col < n; col += 1) {
    let pivot = col;
    for (let r = col + 1; r < n; r += 1) if (Math.abs(m[r][col]) > Math.abs(m[pivot][col])) pivot = r;
    assert(m[pivot][col] !== 0, 'mass matrix must be nonsingular');
    [m[col], m[pivot]] = [m[pivot], m[col]];
    [x[col], x[pivot]] = [x[pivot], x[col]];
    const inverse = 1.0 / m[col][col];
    for (let r = col + 1; r < n; r += 1) {
      const factor = m[r][col] * inverse;
      for (let c = col; c < n; c += 1) m[r][c] -= factor * m[col][c];
      x[r] -= factor * x[col];
    }
  }
  for (let r = n - 1; r >= 0; r -= 1) {
    let total = x[r];
    for (let c = r + 1; c < n; c += 1) total -= m[r][c] * x[c];
    x[r] = total / m[r][r];
  }
  return x;
}

/** Mirrors GolfModel.drift_acceleration: qdd with zero applied torque. */
function driftAcceleration(model, q, qd) {
  const coriolis = matVec(christoffelCoriolis(p => rigidMassMatrix(model, p), q, qd), qd);
  const gravity = gravityTorque(model, q);
  const bias = coriolis.map((value, i) => value + gravity[i]);
  return solve(rigidMassMatrix(model, q), bias).map(value => -value);
}

/** Mirrors ztcf_explorer.py::_forced_acceleration: drift plus M^-1 tau. */
function forcedAcceleration(model, q, qd, torque) {
  const input = solve(rigidMassMatrix(model, q), torque);
  return driftAcceleration(model, q, qd).map((value, i) => value + input[i]);
}

/** Mirrors GolfModel.clubhead_speed: speed of the distal end of link three. */
function clubheadSpeed(model, q, qd) {
  const angles = linkAngles(q);
  let vx = 0;
  let vy = 0;
  let rate = 0;
  for (let link = 0; link < 3; link += 1) {
    rate += qd[link];
    vx += rate * model.lengths[link] * -Math.sin(angles[link]);
    vy += rate * model.lengths[link] * Math.cos(angles[link]);
  }
  return Math.hypot(vx, vy);
}

/** Club-tip and joint positions for drawing; base at the origin. */
function chainPoints(model, q) {
  const angles = linkAngles(q);
  const points = [[0, 0]];
  for (let link = 0; link < 3; link += 1) {
    const [x, y] = points[link];
    points.push([x + model.lengths[link] * Math.cos(angles[link]),
      y + model.lengths[link] * Math.sin(angles[link])]);
  }
  return points;
}

/** Fixed-step RK4 shared by GolfModel.ztcf_trajectory and actual_trajectory. */
function rk4(model, acceleration, q0, qd0, duration, steps) {
  assert(Number.isFinite(duration) && duration > 0, 'duration must be finite and positive');
  assert(Number.isInteger(steps) && steps >= 1, 'steps must be at least 1');
  const dt = duration / steps;
  const derivative = state => {
    const pos = state.slice(0, 3);
    const vel = state.slice(3);
    return vel.concat(acceleration(pos, vel));
  };
  const axpy = (state, scale, k) => state.map((value, i) => value + scale * k[i]);
  let state = q0.concat(qd0);
  const sample = t => ({t, q: state.slice(0, 3), qd: state.slice(3),
    speed: clubheadSpeed(model, state.slice(0, 3), state.slice(3))});
  const out = [sample(0.0)];
  for (let index = 0; index < steps; index += 1) {
    const k1 = derivative(state);
    const k2 = derivative(axpy(state, 0.5 * dt, k1));
    const k3 = derivative(axpy(state, 0.5 * dt, k2));
    const k4 = derivative(axpy(state, dt, k3));
    const sum = k1.map((value, i) => value + 2 * k2[i] + 2 * k3[i] + k4[i]);
    state = axpy(state, dt / 6.0, sum);
    out.push(sample((index + 1) * dt));
  }
  return out;
}

/** Mirrors GolfModel.ztcf_trajectory. */
function ztcfTrajectory(model, q0, qd0, duration, steps) {
  return rk4(model, (q, qd) => driftAcceleration(model, q, qd), q0, qd0, duration, steps);
}

/** Mirrors ztcf_explorer.py::actual_trajectory. */
function actualTrajectory(model, q0, qd0, torque, duration, steps) {
  assert(torque.length === 3 && torque.every(Number.isFinite), 'torque must be three finite values');
  return rk4(model, (q, qd) => forcedAcceleration(model, q, qd, torque), q0, qd0, duration, steps);
}

/** Mirrors ztcf_explorer.py::explore (without the Python-side contract replay record). */
function explore(model, q0, qd0, torque, horizon, steps, interventionStep) {
  assert(Number.isInteger(interventionStep) && interventionStep >= 0 && interventionStep < steps,
    `intervention_step must be an integer in [0, ${steps})`);
  const actual = actualTrajectory(model, q0, qd0, torque, horizon, steps);
  const start = actual[interventionStep];
  const branch = ztcfTrajectory(model, start.q, start.qd, horizon - start.t, steps - interventionStep)
    .map(s => ({...s, t: start.t + s.t}));
  const [a, b] = [actual[actual.length - 1], branch[branch.length - 1]];
  const difference = {
    q: a.q.map((v, i) => v - b.q[i]),
    qd: a.qd.map((v, i) => v - b.qd[i]),
    clubheadSpeed: a.speed - b.speed,
  };
  return {actual, branch, difference};
}

/** Declared scenario; ztcf_explorer.py and the parity fixture pin the same values. */
const DEFAULTS = Object.freeze({
  params: {masses: [10.0, 5.0, 0.81], lengths: [0.3, 0.35, 1.15], inertias: [0.25, 0.08, 0.089],
    shaft_mass: 0.3, modal_frequencies: [40.0, 120.0], com_fractions: [0.5, 0.5, 0.5]},
  q0: [0.2, -0.4, 0.6],
  qd0: [2.0, -1.0, 3.0],
  torque: [40.0, 15.0, 3.0],
  horizon: 0.2,
  steps: 200,
});

const ZTCFExplorer = {
  GRAVITY_M_S2, makeModel, comJacobian, rigidMassMatrix, potentialEnergy, gravityTorque,
  christoffelCoriolis, solve, driftAcceleration, forcedAcceleration, clubheadSpeed, chainPoints,
  ztcfTrajectory, actualTrajectory, explore, DEFAULTS,
};
if (typeof window !== 'undefined') window.ZTCFExplorer = ZTCFExplorer;
if (typeof module !== 'undefined') module.exports = ZTCFExplorer;
