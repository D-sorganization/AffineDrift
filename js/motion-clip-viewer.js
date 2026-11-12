/**
 * 3D golfer viewer draft (VIS-SITE-3, #5425): plays the synthetic clip in js/motion-clip-data.js
 * (scripts/generate_motion_clip_data.py) as perspective SVG. No WebGL, library or network, so it
 * works offline; nothing moves until the reader presses Play.
 */
(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) module.exports = factory();
  else root.AffineDriftMotionClipViewer = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const SVG_NS = 'http://www.w3.org/2000/svg';
  const LOOK_AT = [0, 1.15, 0.3];
  const CAMERA_DISTANCE_M = 4;
  const PITCH_RAD = (10 * Math.PI) / 180;
  const HALF_SPAN = 2.1;
  const SLOW_MOTION_CYCLE_S = 6;
  const JOINT_RADIUS = 0.022;
  const CLUBHEAD = 7;

  /**
   * Perspective projection of a model point (m) to view units (SVG y down).
   * The camera sits in front of the golfer on +z, turned by ``yawRad`` about
   * the vertical and tipped down by a fixed pitch; nearer points look larger.
   */
  function project(point, yawRad) {
    if (![...point, yawRad].every(Number.isFinite)) throw new TypeError('inputs must be finite');
    const [x, y, z] = point.map((v, i) => v - LOOK_AT[i]);
    const xr = x * Math.cos(yawRad) + z * Math.sin(yawRad);
    const zr = -x * Math.sin(yawRad) + z * Math.cos(yawRad);
    const yp = y * Math.cos(PITCH_RAD) - zr * Math.sin(PITCH_RAD);
    const zp = y * Math.sin(PITCH_RAD) + zr * Math.cos(PITCH_RAD);
    const scale = CAMERA_DISTANCE_M / (CAMERA_DISTANCE_M - zp);
    return [xr * scale, -yp * scale];
  }

  /** Plain-language summary of one frame for the live region. */
  function describeFrame(frame, count) {
    const index = Math.round(frame.s * (count - 1));
    return `Swing ${Math.round(frame.s * 100)}%, frame ${index + 1} of ${count} (synthetic clip).`;
  }

  function el(name, attrs) {
    const node = document.createElementNS(SVG_NS, name);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  }

  function buildScene(data) {
    const span = 2 * HALF_SPAN;
    const viewBox = [-HALF_SPAN, -HALF_SPAN, span, span].join(' ');
    const svg = el('svg', { viewBox, class: 'sv-svg', 'aria-hidden': 'true', focusable: 'false' });
    const links = data.segments.map(() => svg.appendChild(el('line', { class: 'sv-link' })));
    const dots = data.markers.map((_, i) =>
      svg.appendChild(el('circle', { class: i === CLUBHEAD ? 'sv-tip' : 'sv-joint', r: JOINT_RADIUS })),
    );
    return { svg, links, dots };
  }

  function drawFrame(scene, data, index, yawRad) {
    const view = data.frames[index].points.map((p) => project(p, yawRad));
    data.segments.forEach(([a, b], i) => {
      const ends = { x1: view[a][0], y1: view[a][1], x2: view[b][0], y2: view[b][1] };
      Object.entries(ends).forEach(([key, value]) => scene.links[i].setAttribute(key, value));
    });
    scene.dots.forEach((dot, i) =>
      dot.setAttribute('transform', `translate(${view[i][0]} ${view[i][1]})`),
    );
  }

  /** Mount the viewer into ``container`` (the page's #motion-viewer element). */
  function mount(container, data) {
    const frames = data.frames;
    const scene = buildScene(data);
    const slider = container.querySelector('.sv-slider');
    const yaw = container.querySelector('.mv-yaw');
    const button = container.querySelector('.sv-play');
    const readout = container.querySelector('.sv-readout');
    const caveats = container.querySelector('.mv-caveats');
    container.querySelector('.sv-stage').appendChild(scene.svg);
    data.caveats.forEach((text) => {
      const item = document.createElement('li');
      item.textContent = text;
      caveats.appendChild(item);
    });
    slider.max = String(frames.length - 1);

    let timer = null;
    const show = (index) => {
      slider.value = String(index);
      drawFrame(scene, data, index, (Number(yaw.value) * Math.PI) / 180);
      readout.textContent = describeFrame(frames[index], frames.length);
    };
    const stop = () => {
      if (timer !== null) cancelAnimationFrame(timer);
      timer = null;
      button.textContent = 'Play';
      button.setAttribute('aria-pressed', 'false');
    };
    const play = () => {
      const start = Number(slider.value) >= frames.length - 1 ? 0 : Number(slider.value);
      let wall0 = null;
      button.textContent = 'Pause';
      button.setAttribute('aria-pressed', 'true');
      const tick = (now) => {
        if (wall0 === null) wall0 = now;
        const s = frames[start].s + (now - wall0) / 1000 / SLOW_MOTION_CYCLE_S;
        const index = Math.min(frames.length - 1, Math.round(s * (frames.length - 1)));
        show(index);
        if (index >= frames.length - 1) stop();
        else timer = requestAnimationFrame(tick);
      };
      timer = requestAnimationFrame(tick);
    };
    button.addEventListener('click', () => (timer === null ? play() : stop()));
    slider.addEventListener('input', () => {
      stop();
      show(Number(slider.value));
    });
    yaw.addEventListener('input', () => show(Number(slider.value)));
    show(0);
    container.classList.add('sv-ready');
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
      const container = document.getElementById('motion-viewer');
      const data = typeof window !== 'undefined' ? window.AffineDriftMotionClipData : null;
      if (container && data) mount(container, data);
    });
  }

  return { LOOK_AT, HALF_SPAN, project, describeFrame, mount };
});
