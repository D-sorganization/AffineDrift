/**
 * Parity of js/ztcf-explorer.js with its Python reference (#4534).
 * Golden vectors: tests/fixtures/widgets/ztcf-explorer.parity.json, generated
 * by `python -m scripts.generate_widget_parity` (ADR 0002 section 6).
 */
const fs = require('fs');
const path = require('path');
const ZE = require('../js/ztcf-explorer.js');

const fixture = JSON.parse(fs.readFileSync(
  path.join(__dirname, 'fixtures/widgets/ztcf-explorer.parity.json'), 'utf8'));

/** ADR 0002 rule: |actual - expected| <= abs + rel * |expected|, element by element. */
function expectClose(actual, expected, tolerance, label) {
  if (Array.isArray(expected)) {
    expect(actual).toHaveLength(expected.length);
    expected.forEach((value, i) => expectClose(actual[i], value, tolerance, `${label}[${i}]`));
    return;
  }
  const bound = tolerance.abs + tolerance.rel * Math.abs(expected);
  const error = Math.abs(actual - expected);
  if (!(error <= bound)) throw new Error(`${label}: |${actual} - ${expected}| = ${error} > ${bound}`);
}

/** The fixture keeps every sample_every-th sample plus the terminal one. */
function kept(samples, every) {
  const out = samples.filter((_, i) => i % every === 0);
  if ((samples.length - 1) % every) out.push(samples[samples.length - 1]);
  return out;
}

function expectSamples(samples, expected, every, tolerance, label) {
  const picked = kept(samples, every);
  expectClose(picked.map(s => s.t), expected.t, tolerance, `${label}.t`);
  expectClose(picked.map(s => s.q), expected.q, tolerance, `${label}.q`);
  expectClose(picked.map(s => s.qd), expected.qd, tolerance, `${label}.qd`);
  expectClose(picked.map(s => s.speed), expected.clubhead_speed, tolerance, `${label}.speed`);
}

describe('ZTCF explorer parity fixture', () => {
  test('declares the v1 schema and cites the Python source', () => {
    expect(fixture.schema).toBe('affinedrift/widget-parity/v1');
    expect(fixture.widget).toBe('ztcf-explorer');
    expect(fixture.source).toBe('src/affine_control/ztcf_explorer.py::explore');
    expect(Object.keys(fixture.dependency_sha256)).toContain(
      'data/ztcf/planar_golf_forward_fixture_v2.json');
  });

  test('replays the registered fixture to its terminal state', () => {
    const c = fixture.cases.find(item => item.id === 'fixture-replay');
    const model = ZE.makeModel(c.inputs.params);
    const samples = ZE.ztcfTrajectory(model, c.inputs.q0, c.inputs.qd0, c.inputs.duration, c.inputs.steps);
    const last = samples[samples.length - 1];
    expectClose(last.q, c.expected.q, c.tolerance, 'q');
    expectClose(last.qd, c.expected.qd, c.tolerance, 'qd');
    expectClose(last.speed, c.expected.clubhead_speed, c.tolerance, 'speed');
  });

  const exploreCases = fixture.cases.filter(c => c.id.startsWith('explore-step-'));

  test.each(exploreCases.map(c => [c.id, c]))('explorer branch %s', (_id, c) => {
    const i = c.inputs;
    const run = ZE.explore(ZE.makeModel(i.params), i.q0, i.qd0, i.torque, i.horizon, i.steps,
      i.intervention_step);
    expectSamples(run.actual, c.expected.actual, i.sample_every, c.tolerance, 'actual');
    expectSamples(run.branch, c.expected.branch, i.sample_every, c.tolerance, 'branch');
    expectClose(run.difference.q, c.expected.difference.q, c.tolerance, 'difference.q');
    expectClose(run.difference.qd, c.expected.difference.qd, c.tolerance, 'difference.qd');
    expectClose(run.difference.clubheadSpeed, c.expected.difference.clubhead_speed, c.tolerance,
      'difference.speed');
  });

  test('widget defaults are the fixture scenario', () => {
    for (const c of exploreCases) {
      expect(ZE.DEFAULTS.params).toEqual(c.inputs.params);
      expect(ZE.DEFAULTS.q0).toEqual(c.inputs.q0);
      expect(ZE.DEFAULTS.qd0).toEqual(c.inputs.qd0);
      expect(ZE.DEFAULTS.torque).toEqual(c.inputs.torque);
      expect(ZE.DEFAULTS.horizon).toBe(c.inputs.horizon);
      expect(ZE.DEFAULTS.steps).toBe(c.inputs.steps);
    }
  });
});

describe('ZTCF explorer contracts', () => {
  const model = ZE.makeModel(ZE.DEFAULTS.params);

  test('rejects nonphysical parameters', () => {
    expect(() => ZE.makeModel({...ZE.DEFAULTS.params, masses: [1, 0, 1]})).toThrow(/masses/);
    expect(() => ZE.makeModel({...ZE.DEFAULTS.params, lengths: [1, 1]})).toThrow(/lengths/);
  });

  test('rejects an intervention step outside the run and a bad torque', () => {
    const {q0, qd0, torque, horizon, steps} = ZE.DEFAULTS;
    expect(() => ZE.explore(model, q0, qd0, torque, horizon, steps, steps)).toThrow(/intervention_step/);
    expect(() => ZE.explore(model, q0, qd0, torque, horizon, steps, -1)).toThrow(/intervention_step/);
    expect(() => ZE.explore(model, q0, qd0, [NaN, 0, 0], horizon, steps, 0)).toThrow(/torque/);
  });

  test('zero declared torque leaves no difference', () => {
    const {q0, qd0, horizon, steps} = ZE.DEFAULTS;
    const run = ZE.explore(model, q0, qd0, [0, 0, 0], horizon, steps, 0);
    expect(run.difference.q).toEqual([0, 0, 0]);
    expect(run.difference.clubheadSpeed).toBe(0);
  });

  test('the branch starts from the actual state at the intervention', () => {
    const {q0, qd0, torque, horizon, steps} = ZE.DEFAULTS;
    const run = ZE.explore(model, q0, qd0, torque, horizon, steps, 80);
    expect(run.branch[0].q).toEqual(run.actual[80].q);
    expect(run.branch[0].t).toBe(run.actual[80].t);
    expect(run.branch).toHaveLength(steps - 80 + 1);
  });

  test('the mass matrix is symmetric and positive definite', () => {
    const m = ZE.rigidMassMatrix(model, [0.3, -1.1, 0.7]);
    expect(m[0][1]).toBe(m[1][0]);
    const x = ZE.solve(m, [1, 2, 3]);
    expect(x.reduce((sum, v, i) => sum + v * [1, 2, 3][i], 0)).toBeGreaterThan(0);
  });

  test('chain points end at the club tip', () => {
    const points = ZE.chainPoints(model, [0, 0, 0]);
    expectClose(points[3], [1.8, 0], {abs: 1e-12, rel: 0}, 'tip');
  });
});
