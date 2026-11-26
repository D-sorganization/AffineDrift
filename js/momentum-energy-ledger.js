/** Mirrors src/affine_control/momentum_energy_ledger.py. DOM-free. */
'use strict';

const STATE_FIELDS = [
  'mass', 'inertia_about_com', 'com_x', 'com_y', 'com_vx', 'com_vy', 'angular_velocity',
];
const WRENCH_FIELDS = ['force_x', 'force_y', 'torque_about_com'];
const HALF = 0.5;

function finiteNumber(value, name) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`${name} must be a finite number`);
  }
  return value;
}

function numbers(payload, fields, label) {
  if (payload === null || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error(`${label} must be an object`);
  }
  const record = {};
  for (const field of fields) {
    if (!Object.prototype.hasOwnProperty.call(payload, field)) {
      throw new Error(`${label} missing ${field}`);
    }
    record[field] = finiteNumber(payload[field], `${label}.${field}`);
  }
  return record;
}

function requireSegment(payload) {
  const state = numbers(payload, STATE_FIELDS, 'state');
  if (state.mass <= 0) throw new Error('mass must be positive');
  if (state.inertia_about_com < 0) throw new Error('inertia_about_com must be non-negative');
  return state;
}

function requireGravity(gravity) {
  const value = finiteNumber(gravity, 'gravity');
  if (value < 0) throw new Error('gravity must be non-negative');
  return value;
}

function angularAcceleration(inertia, torque) {
  if (inertia === 0) {
    if (torque !== 0) throw new Error('torque_about_com requires positive inertia');
    return 0;
  }
  return torque / inertia;
}

/** Mirrors momentum_energy_ledger.py::segment_ledger. */
function segmentLedger(state, gravity) {
  const segment = requireSegment(state);
  const weight = requireGravity(gravity);
  const momentumX = segment.mass * segment.com_vx;
  const momentumY = segment.mass * segment.com_vy;
  const spin = segment.inertia_about_com * segment.angular_velocity;
  const orbit = segment.com_x * momentumY - segment.com_y * momentumX;
  const speedSq = segment.com_vx ** 2 + segment.com_vy ** 2;
  const kinetic = HALF * (segment.mass * speedSq + segment.inertia_about_com * segment.angular_velocity ** 2);
  const potential = segment.mass * weight * segment.com_y;
  return {
    linear_momentum_x: momentumX,
    linear_momentum_y: momentumY,
    angular_momentum_about_com: spin,
    angular_momentum_about_origin: orbit + spin,
    kinetic_energy: kinetic,
    potential_energy: potential,
    mechanical_energy: kinetic + potential,
  };
}

function positionIntegral(origin, rate, acceleration, duration) {
  const halfDt2 = HALF * duration * duration;
  return origin * duration + rate * halfDt2 + (acceleration * duration * halfDt2) / 3;
}

function intervalBalance(segment, loads, weight, step) {
  const totalForceX = loads.force_x;
  const totalForceY = loads.force_y - segment.mass * weight;
  const integralX = positionIntegral(segment.com_x, segment.com_vx, step.accelerationX, step.elapsed);
  const integralY = positionIntegral(segment.com_y, segment.com_vy, step.accelerationY, step.elapsed);
  const work = loads.force_x * (step.comX - segment.com_x)
    + loads.force_y * (step.comY - segment.com_y)
    + loads.torque_about_com * step.deltaTheta;
  return {
    linear_impulse_x: totalForceX * step.elapsed,
    linear_impulse_y: totalForceY * step.elapsed,
    angular_impulse_about_origin: totalForceY * integralX - totalForceX * integralY
      + loads.torque_about_com * step.elapsed,
    work_at_com: work,
  };
}

/** Mirrors momentum_energy_ledger.py::advance_constant_wrench. */
function advanceConstantWrench(state, wrench, gravity, duration) {
  const segment = requireSegment(state);
  const loads = numbers(wrench, WRENCH_FIELDS, 'wrench');
  const weight = requireGravity(gravity);
  const elapsed = finiteNumber(duration, 'duration');
  if (elapsed <= 0) throw new Error('duration must be positive');
  const accelerationX = loads.force_x / segment.mass;
  const accelerationY = loads.force_y / segment.mass - weight;
  const alpha = angularAcceleration(segment.inertia_about_com, loads.torque_about_com);
  const halfDt2 = HALF * elapsed * elapsed;
  const finalState = {
    mass: segment.mass,
    inertia_about_com: segment.inertia_about_com,
    com_x: segment.com_x + segment.com_vx * elapsed + accelerationX * halfDt2,
    com_y: segment.com_y + segment.com_vy * elapsed + accelerationY * halfDt2,
    com_vx: segment.com_vx + accelerationX * elapsed,
    com_vy: segment.com_vy + accelerationY * elapsed,
    angular_velocity: segment.angular_velocity + alpha * elapsed,
  };
  const balance = intervalBalance(segment, loads, weight, {
    elapsed,
    accelerationX,
    accelerationY,
    comX: finalState.com_x,
    comY: finalState.com_y,
    deltaTheta: segment.angular_velocity * elapsed + alpha * halfDt2,
  });
  return {final_state: finalState, balance};
}

const MomentumEnergyLedger = {segmentLedger, advanceConstantWrench};
if (typeof module !== 'undefined') module.exports = MomentumEnergyLedger;
