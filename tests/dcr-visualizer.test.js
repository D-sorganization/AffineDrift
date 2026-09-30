/** Parity checks against src/affine_control/reachability.py's closed-form formulas. */
const DV = require('../js/dcr-visualizer');
const FIXTURE = require('./fixtures/dcr_visualizer_parity.json');

describe('instantaneousScalarDcr matches the declared scalar formula', () => {
  test.each([
    [{initialState: 0, driftGradient: 0, driftOffset: 0, controlBound: 1}, 0],
    [{initialState: 1, driftGradient: 0, driftOffset: 1, controlBound: 1}, 1],
    [{initialState: 1, driftGradient: 1, driftOffset: 0, controlBound: 1}, 1],
    [{initialState: 2, driftGradient: -3, driftOffset: 4, controlBound: 2}, 1],
  ])('%p -> %p', (system, expected) => {
    expect(DV.instantaneousScalarDcr(system)).toBeCloseTo(expected, 12);
  });
});

describe('linearScalarSystem enforces the same contract as LinearScalarSystem.__post_init__', () => {
  test.each([
    [0, 0, 0, 0],
    [0, 0, 0, -1],
  ])('rejects nonpositive control_bound %p,%p,%p,%p', (x0, gradient, offset, bound) => {
    expect(() => DV.linearScalarSystem(x0, gradient, offset, bound)).toThrow();
  });

  test.each([
    [NaN, 0, 0, 1],
    [0, Infinity, 0, 1],
    [0, 0, NaN, 1],
  ])('rejects nonfinite inputs %p,%p,%p,%p', (x0, gradient, offset, bound) => {
    expect(() => DV.linearScalarSystem(x0, gradient, offset, bound)).toThrow();
  });
});

describe('constantAdditiveDriftInterval matches the checked reachability contract', () => {
  test('zero drift gives a symmetric interval', () => {
    expect(DV.constantAdditiveDriftInterval(0, 0, 1, 1)).toEqual([-1, 1]);
  });

  test('arbitrarily large constant drift translates without widening', () => {
    const [lo, hi] = DV.constantAdditiveDriftInterval(0, 100, 1, 1);
    expect(lo).toBeCloseTo(99, 12);
    expect(hi).toBeCloseTo(101, 12);
    expect(hi - lo).toBeCloseTo(2, 12);
  });

  test('rejects a negative horizon', () => {
    expect(() => DV.constantAdditiveDriftInterval(0, 0, 1, -1)).toThrow();
  });
});

describe('scalarLinearReachableInterval reproduces the governed equal-DCR counterexample', () => {
  const {initial_state: x0, control_bound: ubar, horizon} = FIXTURE;
  const expected = FIXTURE.expected;
  const additive = DV.linearScalarSystem(
    x0, FIXTURE.additive_system.drift_gradient, FIXTURE.additive_system.drift_offset, ubar);
  const stateDependent = DV.linearScalarSystem(
    x0, FIXTURE.state_dependent_system.drift_gradient,
    FIXTURE.state_dependent_system.drift_offset, ubar);

  test('both systems share the same instantaneous DCR at the initial state', () => {
    expect(DV.instantaneousScalarDcr(additive)).toBeCloseTo(expected.instantaneous_dcr, 12);
    expect(DV.instantaneousScalarDcr(stateDependent)).toBeCloseTo(expected.instantaneous_dcr, 12);
  });

  test('their reachable-interval widths differ, so DCR does not fix reachability', () => {
    const [loA, hiA] = DV.scalarLinearReachableInterval(additive, horizon);
    const [loB, hiB] = DV.scalarLinearReachableInterval(stateDependent, horizon);
    const [expLoA, expHiA] = expected.additive_reachable_interval;
    const [expLoB, expHiB] = expected.state_dependent_reachable_interval;
    expect(loA).toBeCloseTo(expLoA, 9);
    expect(hiA).toBeCloseTo(expHiA, 9);
    expect(loB).toBeCloseTo(expLoB, 9);
    expect(hiB).toBeCloseTo(expHiB, 9);
    expect(hiA - loA).toBeCloseTo(expected.additive_reachable_width, 9);
    expect(hiB - loB).toBeCloseTo(expected.state_dependent_reachable_width, 9);
  });

  test('rejects a nonfinite or negative horizon', () => {
    expect(() => DV.scalarLinearReachableInterval(additive, -1)).toThrow();
    expect(() => DV.scalarLinearReachableInterval(additive, NaN)).toThrow();
  });
});

describe('swing-phase state trajectories', () => {
  test('additive drift is linear in time', () => {
    expect(DV.additiveDriftState(1, 1, 1)).toBeCloseTo(2, 12);
  });

  test('multiplicative drift is exponential in time', () => {
    expect(DV.multiplicativeDriftState(1, 1, 1)).toBeCloseTo(Math.E, 12);
  });

  test('the additive system’s instantaneous ratio stays flat through the phase', () => {
    const evolved = DV.additiveDriftState(1, 1, 1);
    const system = DV.linearScalarSystem(evolved, 0, 1, 1);
    expect(DV.instantaneousScalarDcr(system)).toBeCloseTo(1, 12);
  });

  test('the state-dependent system’s instantaneous ratio grows through the phase', () => {
    const evolved = DV.multiplicativeDriftState(1, 1, 1);
    const system = DV.linearScalarSystem(evolved, 1, 0, 1);
    expect(DV.instantaneousScalarDcr(system)).toBeCloseTo(Math.E, 12);
  });
});
