/** Mirrors src/affine_control/reachability.py::LinearScalarSystem,
 * instantaneous_scalar_dcr, scalar_linear_reachable_interval, and
 * constant_additive_drift_interval. Pure functions only; no DOM dependency.
 */
'use strict';

function assert(condition, message) {
  if (!condition) throw new Error(`[dcr-visualizer] Contract violation: ${message}`);
}

function requireFinite(values, label) {
  assert(values.every(Number.isFinite), `${label} must be finite`);
}

/** Scalar system `x_dot = driftGradient*x + driftOffset + u` with bounded input. */
function linearScalarSystem(initialState, driftGradient, driftOffset, controlBound) {
  requireFinite([initialState, driftGradient, driftOffset, controlBound], 'linear-system values');
  assert(controlBound > 0, 'control_bound must be positive');
  return {initialState, driftGradient, driftOffset, controlBound};
}

/** The declared scalar absolute-value DCR at the system's current state. */
function instantaneousScalarDcr(system) {
  const drift = system.driftGradient * system.initialState + system.driftOffset;
  return Math.abs(drift) / system.controlBound;
}

/** Exact reachable interval for `x_dot = drift + control`, `|control| <= controlBound`. */
function constantAdditiveDriftInterval(initialState, drift, controlBound, horizon) {
  requireFinite([initialState, drift, controlBound, horizon], 'reachability inputs');
  assert(controlBound >= 0, 'control_bound must be nonnegative');
  assert(horizon >= 0, 'horizon must be nonnegative');
  const center = initialState + drift * horizon;
  const radius = controlBound * horizon;
  requireFinite([center, radius], 'derived reachability interval');
  const interval = [center - radius, center + radius];
  assert(interval[0] <= interval[1], 'reachability interval postcondition failed');
  return interval;
}

/** Exact reachable interval for a scalar affine-linear bounded-input system. */
function scalarLinearReachableInterval(system, horizon) {
  assert(Number.isFinite(horizon) && horizon >= 0, 'horizon must be finite and nonnegative');
  if (system.driftGradient === 0.0) {
    return constantAdditiveDriftInterval(
      system.initialState, system.driftOffset, system.controlBound, horizon);
  }
  const transition = Math.exp(system.driftGradient * horizon);
  assert(Number.isFinite(transition), 'state transition must remain finite');
  const inputFactor = (transition - 1.0) / system.driftGradient;
  const center = transition * system.initialState + inputFactor * system.driftOffset;
  const radius = inputFactor * system.controlBound;
  requireFinite([center, radius], 'reachable interval');
  return [center - radius, center + radius];
}

/** Zero-input drift trajectory of `x_dot = driftOffset` (constant/additive drift). */
function additiveDriftState(initialState, driftOffset, t) {
  requireFinite([initialState, driftOffset, t], 'additive drift state inputs');
  return initialState + driftOffset * t;
}

/** Zero-input drift trajectory of `x_dot = driftGradient*x` (state-dependent drift). */
function multiplicativeDriftState(initialState, driftGradient, t) {
  requireFinite([initialState, driftGradient, t], 'multiplicative drift state inputs');
  return initialState * Math.exp(driftGradient * t);
}

const DcrVisualizer = {
  linearScalarSystem, instantaneousScalarDcr, scalarLinearReachableInterval,
  constantAdditiveDriftInterval, additiveDriftState, multiplicativeDriftState,
};
if (typeof window !== 'undefined') window.DcrVisualizer = DcrVisualizer;
if (typeof module !== 'undefined') module.exports = DcrVisualizer;
