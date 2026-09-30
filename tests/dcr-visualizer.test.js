/** Parity checks against src/affine_control/reachability.py's closed-form formulas. */
const DV = require('../js/dcr-visualizer');

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
  const additive = DV.linearScalarSystem(1, 0, 1, 1);
  const stateDependent = DV.linearScalarSystem(1, 1, 0, 1);

  test('both systems share the same instantaneous DCR at the initial state', () => {
    expect(DV.instantaneousScalarDcr(additive)).toBeCloseTo(1, 12);
    expect(DV.instantaneousScalarDcr(stateDependent)).toBeCloseTo(1, 12);
  });

  test('their reachable-interval widths differ, so DCR does not fix reachability', () => {
    const [loA, hiA] = DV.scalarLinearReachableInterval(additive, 1);
    const [loB, hiB] = DV.scalarLinearReachableInterval(stateDependent, 1);
    expect(loA).toBeCloseTo(1, 12);
    expect(hiA).toBeCloseTo(3, 12);
    expect(loB).toBeCloseTo(1, 12);
    expect(hiB).toBeCloseTo(2 * Math.E - 1, 12);
    expect(hiA - loA).toBeCloseTo(2, 12);
    expect(hiB - loB).toBeCloseTo(2 * (Math.E - 1), 12);
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
