/**
 * Browser parity for the planar momentum and energy ledger (#5886).
 * Golden values: tests/fixtures/momentum_energy_ledger_analytic.json.
 * Python reference: src/affine_control/momentum_energy_ledger.py.
 */
const fs = require('fs');
const path = require('path');
const ledger = require('../js/momentum-energy-ledger.js');

const fixture = JSON.parse(fs.readFileSync(
  path.join(__dirname, 'fixtures/momentum_energy_ledger_analytic.json'), 'utf8'));

function expectClose(actual, expected, tolerance, label) {
  const bound = tolerance.abs + tolerance.rel * Math.abs(expected);
  const gap = Math.abs(actual - expected);
  if (!(gap <= bound)) {
    throw new Error(`${label}: |${actual} - ${expected}| = ${gap} > ${bound}`);
  }
}

function expectRecord(actual, expected, tolerance, label) {
  expect(Object.keys(actual).sort()).toEqual(Object.keys(expected).sort());
  for (const key of Object.keys(expected)) {
    expectClose(actual[key], expected[key], tolerance, `${label}.${key}`);
  }
}

describe('momentum and energy ledger parity fixture', () => {
  test('declares the analytic schema and closed-form tolerance', () => {
    expect(fixture.schema).toBe('affinedrift/momentum-energy-ledger-analytic/v1');
    expect(fixture.tolerance).toEqual({abs: 1e-12, rel: 1e-12});
  });

  test('replays every analytic ledger', () => {
    for (const item of fixture.ledgers) {
      expectRecord(
        ledger.segmentLedger(item.state, fixture.gravity),
        item.expected,
        fixture.tolerance,
        item.id,
      );
    }
  });

  test('replays every analytic interval', () => {
    for (const item of fixture.intervals) {
      const advanced = ledger.advanceConstantWrench(
        item.state, item.wrench, fixture.gravity, item.duration);
      expectRecord(advanced.final_state, item.expected_state, fixture.tolerance, item.id);
      expectRecord(
        ledger.segmentLedger(advanced.final_state, fixture.gravity),
        item.expected_ledger,
        fixture.tolerance,
        `${item.id}.ledger`,
      );
      expectRecord(advanced.balance, item.expected_balance, fixture.tolerance, `${item.id}.balance`);
    }
  });

  test('rejects a non-positive mass and a couple on a point mass', () => {
    const spinning = fixture.ledgers[0].state;
    const point = fixture.ledgers[1].state;
    const wrench = {force_x: 0, force_y: 0, torque_about_com: 1};
    expect(() => ledger.segmentLedger({...spinning, mass: 0}, fixture.gravity))
      .toThrow('mass must be positive');
    expect(() => ledger.advanceConstantWrench(point, wrench, fixture.gravity, 0.2))
      .toThrow('torque_about_com requires positive inertia');
  });
});
