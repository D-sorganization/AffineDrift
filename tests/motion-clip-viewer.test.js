/** 3D golfer viewer (#5425): perspective helpers and mounting; clip checks are in test_motion_clip_data.py. */
const MV = require('../js/motion-clip-viewer');
const DATA = require('../js/motion-clip-data');

describe('project', () => {
  test('the look-at point maps to the view centre', () => {
    const [x, y] = MV.project(MV.LOOK_AT, 0);
    expect(x).toBeCloseTo(0);
    expect(y).toBeCloseTo(0);
  });

  test('+x is screen right, +y is screen up, and nearer points look larger', () => {
    const [x] = MV.project([1, MV.LOOK_AT[1], 0], 0);
    expect(x).toBeGreaterThan(0);
    expect(MV.project([0, MV.LOOK_AT[1] + 1, 0], 0)[1]).toBeLessThan(0);
    const [near] = MV.project([0.5, MV.LOOK_AT[1], 1], 0);
    const [far] = MV.project([0.5, MV.LOOK_AT[1], -1], 0);
    expect(near).toBeGreaterThan(far);
  });

  test('a quarter-turn yaw brings depth (+z) onto the screen x axis', () => {
    const deep = [0, MV.LOOK_AT[1], MV.LOOK_AT[2] + 0.5];
    expect(Math.abs(MV.project(deep, 0)[0])).toBeCloseTo(0);
    expect(Math.abs(MV.project(deep, Math.PI / 2)[0])).toBeGreaterThan(0.4);
  });

  test('rejects non-finite input', () => {
    expect(() => MV.project([NaN, 0, 0], 0)).toThrow(TypeError);
    expect(() => MV.project([0, 0, 0], Infinity)).toThrow(TypeError);
  });
});

test('every frame stays inside the view box at every view angle', () => {
  for (let deg = -180; deg <= 180; deg += 15) {
    for (const frame of DATA.frames) {
      for (const point of frame.points) {
        const view = MV.project(point, (deg * Math.PI) / 180);
        expect(Math.max(...view.map(Math.abs))).toBeLessThan(MV.HALF_SPAN);
      }
    }
  }
});

test('describeFrame states the swing progress and that the clip is synthetic', () => {
  expect(MV.describeFrame(DATA.frames[12], DATA.frames.length)).toMatch(/^Swing \d+%, frame 13 of \d+ \(synthetic clip\)\.$/);
});

test('mount draws every segment and follows the frame slider', () => {
  document.body.innerHTML = `<figure id="motion-viewer"><div class="sv-stage"></div>
    <button type="button" class="sv-play" aria-pressed="false">Play</button>
    <input type="range" class="sv-slider"><input type="range" class="mv-yaw" value="30">
    <p class="sv-readout"></p><ul class="mv-caveats"></ul></figure>`;
  const container = document.getElementById('motion-viewer');
  MV.mount(container, DATA);
  expect(container.querySelectorAll('line.sv-link')).toHaveLength(DATA.segments.length);
  expect(container.querySelectorAll('.mv-caveats li')).toHaveLength(DATA.caveats.length);
  const slider = container.querySelector('.sv-slider');
  expect(slider.max).toBe(String(DATA.frames.length - 1));
  slider.value = '5';
  slider.dispatchEvent(new Event('input'));
  expect(container.querySelector('.sv-readout').textContent).toContain('frame 6 of');
  expect(container.classList.contains('sv-ready')).toBe(true);
});
