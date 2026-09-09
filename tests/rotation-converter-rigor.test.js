/** Reconstruction tests use independent quaternion and elementary-rotation formulas. */
const RC = require('../js/rotation-converter');

function quaternionMatrix([w, x, y, z]) {
  return [w*w+x*x-y*y-z*z, 2*(x*y-w*z), 2*(x*z+w*y),
    2*(x*y+w*z), w*w-x*x+y*y-z*z, 2*(y*z-w*x),
    2*(x*z-w*y), 2*(y*z+w*x), w*w-x*x-y*y+z*z];
}

function closeMatrix(actual, expected, tolerance = 2e-12) {
  expect(actual.every(Number.isFinite)).toBe(true);
  expect(Math.max(...actual.map((x, i) => Math.abs(x-expected[i])))).toBeLessThan(tolerance);
}

const axis = [-1/Math.sqrt(14), 2/Math.sqrt(14), -3/Math.sqrt(14)];
test.each([1e-12, 1e-8, 0.7, Math.PI-1e-4, Math.PI-1e-7,
  Math.PI-1e-8, Math.PI, Math.PI+1e-8, 2*Math.PI-1e-8])(
  'all representations reconstruct independently built angle %p', angle => {
    const quaternion = [Math.cos(angle/2), ...axis.map(x => x*Math.sin(angle/2))];
    const matrix = quaternionMatrix(quaternion);
    const out = RC.convert(matrix, 'R');
    expect(Math.hypot(...out.quaternion)).toBeCloseTo(1, 13);
    closeMatrix(quaternionMatrix(out.quaternion), matrix);
    closeMatrix(RC.axisAngleToR(out.axisAngle.axis, out.axisAngle.angle), matrix);
    closeMatrix(RC.expCoordToR(out.expCoord), matrix);
    expect(out.axisAngle.angle).toBeGreaterThanOrEqual(0);
    expect(out.axisAngle.angle).toBeLessThanOrEqual(Math.PI);
  });

test.each([Math.PI/2, -Math.PI/2, Math.PI/2-1e-4, -Math.PI/2+1e-4,
  Math.PI/2-1e-8, -Math.PI/2+1e-8])('ZYX preserves nonzero roll near %p', pitch => {
  const matrix = RC.eulerZYXToR(0.7, pitch, -0.9);
  const out = RC.rToEulerZYX(matrix);
  closeMatrix(RC.eulerZYXToR(out.psi, out.theta, out.phi), matrix);
});

test.each([[1,0,0,0,1,0,0,0,-1], [0,0,0,0,0,0,0,0,0],
  [1,0.01,0,0,1,0,0,0,1], [NaN,0,0,0,1,0,0,0,1]].map(matrix => [matrix]))(
  'rejects nonrotations before conversion %p', matrix => {
    expect(() => RC.convert(matrix, 'R')).toThrow();
    expect(() => RC.rToQuaternion(matrix)).toThrow();
    expect(() => RC.rToAxisAngle(matrix)).toThrow();
    expect(() => RC.rToEulerZYX(matrix)).toThrow();
  });

test.each([[Infinity,1,0], ['1',0,0], [NaN,0,0], [0,0,0]].map(vector => [vector]))(
  'axis normalization rejects invalid vector %p', vector => {
    expect(() => RC.normalizeAxis(vector)).toThrow();
  });

test.each([[Infinity,0,0,0], ['1',0,0,0], [NaN,0,0,0], [0,0,0,0]].map(vector => [vector]))(
  'quaternion normalization rejects invalid vector %p', vector => {
    expect(() => RC.normalizeQuaternion(vector)).toThrow();
  });

test('normalizes large finite magnitudes without overflow', () => {
  const out = RC.convert([1e308,-1e308,1e308,-1e308], 'quaternion');
  closeMatrix(out.R, quaternionMatrix([0.5,-0.5,0.5,-0.5]));
});

test('maximum entry residual differs from induced infinity norm', () => {
  const matrix = [1,1e-6,1e-6,0,1,0,0,0,1];
  expect(RC.validateR(matrix).orthogError).toBeCloseTo(1e-6, 14);
});
