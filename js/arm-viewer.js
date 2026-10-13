/**
 * Spatial arm viewer (swing viewer Phase 2, #4973).
 *
 * Draws the precomputed frames in js/arm-viewer-data.js, generated from the
 * cited 3D arm chain JOHNSON_2015_ARM (src/affine_control/golf_model_3d.py) by
 * scripts/generate_arm_viewer_data.py. There is no kinematics here: the page
 * only projects the stored 3D points, orthographically, at a view angle the
 * reader chooses. The caveats and the joint table come from the same payload
 * and are always shown beside the figure.
 */
(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) module.exports = factory();
  else root.AffineDriftArmViewer = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const SVG_NS = 'http://www.w3.org/2000/svg';
  const HALF_SPAN_M = 0.95;
  const PITCH_RAD = (20 * Math.PI) / 180;
  const SLOW_MOTION_CYCLE_S = 8;
  const DEG_PER_RAD = 180 / Math.PI;
  const TRIAD_ORIGIN = [-HALF_SPAN_M + 0.35, HALF_SPAN_M - 0.35];
  const AXES = [
    ['x', [0.3, 0, 0]],
    ['y', [0, 0.3, 0]],
    ['z', [0, 0, 0.3]],
  ];

  /**
   * Orthographic projection of a model point (m) to view units (SVG y down).
   * Yaw turns the scene about the model's vertical (+y) axis; a fixed pitch
   * tips it toward the viewer so out-of-plane motion (+z) is visible.
   */
  function project(point, yawRad) {
    if (![...point, yawRad].every(Number.isFinite)) throw new TypeError('inputs must be finite');
    const [x, y, z] = point;
    const xr = x * Math.cos(yawRad) + z * Math.sin(yawRad);
    const zr = -x * Math.sin(yawRad) + z * Math.cos(yawRad);
    const yr = y * Math.cos(PITCH_RAD) - zr * Math.sin(PITCH_RAD);
    return [xr, -yr];
  }

  /** Degrees, one decimal, for an angle in radians. */
  function degrees(rad) {
    return (rad * DEG_PER_RAD).toFixed(1);
  }

  /** Plain-language summary of one frame for the live region. */
  function describeFrame(frame, joints) {
    const parts = joints.map(
      (joint, i) => `${joint.name} ${degrees(frame.q[i])} degrees`,
    );
    return `Cycle ${Math.round(frame.s * 100)}%: ${parts.join(', ')}.`;
  }

  /** One table row per joint: name, axis, limits in degrees (a plain-text summary). */
  function jointRows(joints) {
    return joints.map((joint) => ({
      name: joint.name,
      axisLabel: ['x', 'y', 'z'][joint.axis.findIndex((v) => v !== 0)],
      limits: `${degrees(joint.limitsRad[0])} to ${degrees(joint.limitsRad[1])}`,
    }));
  }

  function el(name, attrs) {
    const node = document.createElementNS(SVG_NS, name);
    Object.entries(attrs || {}).forEach(([key, value]) => node.setAttribute(key, value));
    return node;
  }

  function textEl(tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function buildScene(frames) {
    const span = 2 * HALF_SPAN_M;
    const svg = el('svg', {
      viewBox: [-HALF_SPAN_M, -HALF_SPAN_M, span, span].join(' '),
      class: 'sv-svg',
      'aria-hidden': 'true',
      focusable: 'false',
    });
    const triad = AXES.map(([name]) => {
      const line = el('line', { class: 'sv-axis' });
      const label = el('text', { class: 'sv-axis-label', 'font-size': '0.07' });
      label.textContent = `+${name} (assumed)`;
      svg.append(line, label);
      return { line, label };
    });
    const trace = el('polyline', { class: 'sv-trace', points: '' });
    svg.appendChild(trace);
    const links = [0, 1, 2].map(() => svg.appendChild(el('line', { class: 'sv-link' })));
    const dots = frames[0].points.map((_, i) =>
      svg.appendChild(el('circle', { class: i === 3 ? 'sv-tip' : 'sv-joint', r: 0.025 })),
    );
    return { svg, triad, trace, links, dots };
  }

  function drawFrame(scene, frames, index, yawRad) {
    const view = frames[index].points.map((p) => project(p, yawRad));
    scene.links.forEach((line, i) => {
      line.setAttribute('x1', view[i][0]);
      line.setAttribute('y1', view[i][1]);
      line.setAttribute('x2', view[i + 1][0]);
      line.setAttribute('y2', view[i + 1][1]);
    });
    scene.dots.forEach((dot, i) => {
      dot.setAttribute('cx', view[i][0]);
      dot.setAttribute('cy', view[i][1]);
    });
    scene.triad.forEach((axis, i) => {
      const [dx, dy] = project(AXES[i][1], yawRad);
      axis.line.setAttribute('x1', TRIAD_ORIGIN[0]);
      axis.line.setAttribute('y1', TRIAD_ORIGIN[1]);
      axis.line.setAttribute('x2', TRIAD_ORIGIN[0] + dx);
      axis.line.setAttribute('y2', TRIAD_ORIGIN[1] + dy);
      axis.label.setAttribute('x', TRIAD_ORIGIN[0] + dx);
      axis.label.setAttribute('y', TRIAD_ORIGIN[1] + dy);
    });
    const tip = frames.slice(0, index + 1).map((f) => project(f.points[3], yawRad).join(','));
    scene.trace.setAttribute('points', tip.join(' '));
  }

  /** Render the always-visible caveat list and joint table into ``container``. */
  function renderNotes(container, data) {
    const caveats = container.querySelector('.av-caveats');
    data.caveats.forEach((text) => caveats.appendChild(textEl('li', text)));
    const body = container.querySelector('.av-joints tbody');
    jointRows(data.joints).forEach((row) => {
      const tr = document.createElement('tr');
      [row.name, `+${row.axisLabel} (assumed)`, row.limits].forEach((cell) =>
        tr.appendChild(textEl('td', cell)),
      );
      body.appendChild(tr);
    });
  }

  /** Mount the viewer into ``container`` (the page's #arm-viewer element). */
  function mount(container, data) {
    const frames = data.frames;
    const scene = buildScene(frames);
    const slider = container.querySelector('.sv-slider');
    const yaw = container.querySelector('.av-yaw');
    const button = container.querySelector('.sv-play');
    const readout = container.querySelector('.sv-readout');
    container.querySelector('.sv-stage').appendChild(scene.svg);
    slider.max = String(frames.length - 1);
    renderNotes(container, data);

    let timer = null;
    const yawRad = () => (Number(yaw.value) * Math.PI) / 180;
    const show = (index) => {
      slider.value = String(index);
      drawFrame(scene, frames, index, yawRad());
      readout.textContent = describeFrame(frames[index], data.joints);
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
        let index = start;
        while (index < frames.length - 1 && frames[index + 1].s <= s) index += 1;
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
      const container = document.getElementById('arm-viewer');
      const data = typeof window !== 'undefined' ? window.AffineDriftArmViewerData : null;
      if (container && data) mount(container, data);
    });
  }

  return { project, degrees, describeFrame, jointRows, mount };
});
