/** Pure helpers of the spatial arm viewer (#4973); kinematics parity is in test_arm_viewer_data.py. */
const AV = require('../js/arm-viewer');
const DATA = require('../js/arm-viewer-data');

const PITCH = (20 * Math.PI) / 180;

describe('project', () => {
  test('at zero yaw the in-plane x axis maps to screen x and +y points up', () => {
    const [x, y] = AV.project([1, 0, 0], 0);
    expect(x).toBeCloseTo(1);
    expect(y).toBeCloseTo(0);
    expect(AV.project([0, 1, 0], 0)[1]).toBeCloseTo(-Math.cos(PITCH));
  });

  test('out-of-plane +z shows only through pitch at zero yaw and through x at 90 degrees', () => {
    expect(AV.project([0, 0, 1], 0)[0]).toBeCloseTo(0);
    expect(AV.project([0, 0, 1], Math.PI / 2)[0]).toBeCloseTo(1);
  });

  test('yaw preserves the horizontal length of a point in the x-z plane', () => {
    const [x0] = AV.project([0.6, 0, 0], 0);
    const [x1] = AV.project([0.6, 0, 0], Math.PI / 2);
    expect(x0).toBeCloseTo(0.6);
    expect(x1).toBeCloseTo(0);
  });

  test('rejects non-finite input', () => {
    expect(() => AV.project([NaN, 0, 0], 0)).toThrow(TypeError);
    expect(() => AV.project([0, 0, 0], Infinity)).toThrow(TypeError);
  });
});

test('describeFrame names every joint in degrees', () => {
  const text = AV.describeFrame(DATA.frames[10], DATA.joints);
  for (const joint of DATA.joints) expect(text).toContain(joint.name);
  expect(text).toMatch(/^Cycle \d+%: /);
});

test('jointRows reports the assumed axis and the Table 3.4 limits in degrees', () => {
  const rows = AV.jointRows(DATA.joints);
  expect(rows.map((r) => r.axisLabel)).toEqual(['z', 'x', 'z']);
  expect(rows[0].limits).toBe('-73.9 to 69.3');
});

test('data module carries the label, every caveat and ordered frames', () => {
  expect(DATA.label).toContain('Spatial (3D)');
  expect(DATA.label).toContain('not a measured or simulated swing');
  const caveats = DATA.caveats.join(' ');
  for (const phrase of ['passive-moment breakpoints', 'are assumed', 'unverified', 'viewer placement']) {
    expect(caveats).toContain(phrase);
  }
  expect(DATA.frames.length).toBeGreaterThan(10);
  DATA.frames.slice(1).forEach((frame, i) => expect(frame.s).toBeGreaterThan(DATA.frames[i].s));
});
