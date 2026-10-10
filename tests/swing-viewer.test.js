/** Pure helpers of the planar swing viewer (#4540); physics parity is in test_swing_viewer_data.py. */
const SV = require('../js/swing-viewer');
const DATA = require('../js/swing-viewer-data');

describe('strokeFor mixes drift and input colours by share', () => {
  test.each([
    [0, '0%'],
    [0.5, '50%'],
    [1, '100%'],
    [1.7, '100%'],
    [-0.2, '0%'],
  ])('%p -> %p input', (share, percent) => {
    expect(SV.strokeFor(share)).toBe(
      `color-mix(in srgb, var(--sv-input) ${percent}, var(--sv-drift))`,
    );
  });

  test('rejects a non-finite share', () => {
    expect(() => SV.strokeFor(NaN)).toThrow(TypeError);
  });
});

test('toView flips the vertical axis only', () => {
  expect(SV.toView([1.5, -0.25])).toEqual([1.5, 0.25]);
});

test('describeFrame names time, speed and every link share', () => {
  const text = SV.describeFrame(DATA.frames[DATA.frames.length - 1]);
  expect(text).toMatch(/^t = 0\.\d{3} s, club-head speed \d+\.\d m\/s; /);
  for (const name of ['hub link', 'arm link', 'club link']) expect(text).toContain(name);
});

test('data module carries the model label and ordered frames', () => {
  expect(DATA.label).toContain('Planar (2D)');
  expect(DATA.frames.length).toBeGreaterThan(10);
  DATA.frames.slice(1).forEach((frame, i) => expect(frame.t).toBeGreaterThan(DATA.frames[i].t));
});
