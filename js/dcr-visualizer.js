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

const WIDGET_ID = 'dcr-visualizer';
const STATE_SCHEMA_VERSION = 1;
const MAX_STATE_HASH_LENGTH = 512;
const DCR_STATE_DEFAULTS = Object.freeze({x0: 1, ubar: 1, horizon: 1, phase: 0.5});
const DCR_PARAM_KEYS = Object.freeze(['x0', 'ubar', 'horizon', 'phase']);

function validateDcrStateParams(params) {
  if (!params || typeof params !== 'object' || Array.isArray(params)) {
    return 'params must be a plain object';
  }
  const keys = Object.keys(params);
  if (keys.length !== DCR_PARAM_KEYS.length || !DCR_PARAM_KEYS.every(k => Object.prototype.hasOwnProperty.call(params, k))) {
    return 'params must contain exactly x0, ubar, horizon, phase';
  }
  const {x0, ubar, horizon, phase} = params;
  if (![x0, ubar, horizon, phase].every(v => typeof v === 'number' && Number.isFinite(v))) {
    return 'all state parameters must be finite numbers';
  }
  if (x0 === 0 || x0 < -100 || x0 > 100) return 'x0 must be nonzero within [-100, 100]';
  if (ubar <= 0 || ubar > 100) return 'ubar must be within (0, 100]';
  if (horizon < 0 || horizon > 20) return 'horizon must be within [0, 20]';
  if (phase < 0 || phase > 1) return 'phase must be within [0, 1]';
  return null;
}

/** Encode validated DCR widget state into a bounded `#state=` URL hash. */
function encodeWidgetStateHash(params) {
  const err = validateDcrStateParams(params);
  assert(err === null, err || 'invalid state params');
  const envelope = {
    v: STATE_SCHEMA_VERSION,
    w: WIDGET_ID,
    p: {x0: params.x0, ubar: params.ubar, horizon: params.horizon, phase: params.phase},
  };
  const hash = `#state=${encodeURIComponent(JSON.stringify(envelope))}`;
  assert(hash.length <= MAX_STATE_HASH_LENGTH, 'encoded hash exceeds maximum length');
  return hash;
}

/** Safely decode a `#state=` URL hash, falling back to defaults without throwing. */
function decodeWidgetStateHash(rawHash, defaults = DCR_STATE_DEFAULTS) {
  const fallback = {
    x0: defaults.x0,
    ubar: defaults.ubar,
    horizon: defaults.horizon,
    phase: defaults.phase,
  };
  if (typeof rawHash !== 'string' || rawHash.length === 0) {
    return {valid: false, state: fallback, reason: 'empty hash'};
  }
  if (rawHash.length > MAX_STATE_HASH_LENGTH) {
    return {valid: false, state: fallback, reason: 'hash exceeds maximum length'};
  }
  const normalized = rawHash.startsWith('#') ? rawHash.slice(1) : rawHash;
  if (!normalized.startsWith('state=')) {
    return {valid: false, state: fallback, reason: 'missing state= prefix'};
  }
  const encodedPayload = normalized.slice('state='.length);
  if (!encodedPayload) {
    return {valid: false, state: fallback, reason: 'empty state payload'};
  }
  let parsed;
  try {
    parsed = JSON.parse(decodeURIComponent(encodedPayload));
  } catch (_err) {
    return {valid: false, state: fallback, reason: 'malformed URI or JSON payload'};
  }
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    return {valid: false, state: fallback, reason: 'envelope must be an object'};
  }
  const envKeys = Object.keys(parsed);
  if (envKeys.length !== 3 || parsed.v !== STATE_SCHEMA_VERSION || parsed.w !== WIDGET_ID) {
    return {valid: false, state: fallback, reason: 'unsupported schema version or widget id'};
  }
  const paramErr = validateDcrStateParams(parsed.p);
  if (paramErr !== null) {
    return {valid: false, state: fallback, reason: paramErr};
  }
  return {
    valid: true,
    state: {
      x0: parsed.p.x0,
      ubar: parsed.p.ubar,
      horizon: parsed.p.horizon,
      phase: parsed.p.phase,
    },
    reason: null,
  };
}

const DcrVisualizer = {
  linearScalarSystem, instantaneousScalarDcr, scalarLinearReachableInterval,
  constantAdditiveDriftInterval, additiveDriftState, multiplicativeDriftState,
  WIDGET_ID, STATE_SCHEMA_VERSION, MAX_STATE_HASH_LENGTH, DCR_STATE_DEFAULTS,
  encodeWidgetStateHash, decodeWidgetStateHash,
};
if (typeof window !== 'undefined') window.DcrVisualizer = DcrVisualizer;
if (typeof module !== 'undefined') module.exports = DcrVisualizer;
