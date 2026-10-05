/**
 * Planar swing viewer (WEB-06.10 Phase 1, #4540).
 *
 * Draws the precomputed frames in js/swing-viewer-data.js, generated from
 * src/affine_control/golf_model.py by scripts/generate_swing_viewer_data.py.
 * There is no physics here: each link is coloured by the input share of its
 * angular acceleration, which the generator computed. Plain SVG, so no WebGL
 * is needed; nothing animates until the reader presses Play.
 */
(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) module.exports = factory();
  else root.AffineDriftSwingViewer = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var SVG_NS = 'http://www.w3.org/2000/svg';
  var HALF_SPAN_M = 2.1;
  var SLOW_MOTION = 8;
  var LINK_NAMES = ['hub link', 'arm link', 'club link'];

  /** Stroke colour between drift (share 0) and input (share 1), theme-aware via CSS variables. */
  function strokeFor(share) {
    if (!Number.isFinite(share)) throw new TypeError('share must be finite');
    var percent = Math.round(Math.min(1, Math.max(0, share)) * 100);
    return 'color-mix(in srgb, var(--sv-input) ' + percent + '%, var(--sv-drift))';
  }

  /** Model metres to SVG user units (y up in the model, down in SVG). */
  function toView(point) {
    return [point[0], -point[1]];
  }

  /** Plain-language summary of one frame for the live region. */
  function describeFrame(frame) {
    var shares = frame.inputShare
      .map(function (share, i) {
        return LINK_NAMES[i] + ' ' + Math.round(share * 100) + '% input';
      })
      .join(', ');
    return (
      't = ' + frame.t.toFixed(3) + ' s, club-head speed ' +
      frame.clubheadSpeed.toFixed(1) + ' m/s; ' + shares + '.'
    );
  }

  function el(name, attrs) {
    var node = document.createElementNS(SVG_NS, name);
    Object.keys(attrs || {}).forEach(function (key) {
      node.setAttribute(key, attrs[key]);
    });
    return node;
  }

  function buildSvg(frames) {
    var span = 2 * HALF_SPAN_M;
    var svg = el('svg', {
      viewBox: [-HALF_SPAN_M, -HALF_SPAN_M, span, span].join(' '),
      class: 'sv-svg',
      'aria-hidden': 'true',
      focusable: 'false',
    });
    var trace = el('polyline', {class: 'sv-trace', points: ''});
    svg.appendChild(trace);
    var links = [0, 1, 2].map(function () {
      var line = el('line', {class: 'sv-link'});
      svg.appendChild(line);
      return line;
    });
    var joints = frames[0].points.map(function (_, i) {
      var dot = el('circle', {class: i === 3 ? 'sv-tip' : 'sv-joint', r: i === 3 ? 0.05 : 0.04});
      svg.appendChild(dot);
      return dot;
    });
    return {svg: svg, trace: trace, links: links, joints: joints};
  }

  function drawFrame(scene, frames, index) {
    var frame = frames[index];
    var view = frame.points.map(toView);
    scene.links.forEach(function (line, i) {
      line.setAttribute('x1', view[i][0]);
      line.setAttribute('y1', view[i][1]);
      line.setAttribute('x2', view[i + 1][0]);
      line.setAttribute('y2', view[i + 1][1]);
      line.style.stroke = strokeFor(frame.inputShare[i]);
    });
    scene.joints.forEach(function (dot, i) {
      dot.setAttribute('cx', view[i][0]);
      dot.setAttribute('cy', view[i][1]);
    });
    scene.trace.setAttribute(
      'points',
      frames.slice(0, index + 1).map(function (f) { return toView(f.points[3]).join(','); }).join(' ')
    );
  }

  /** Mount the viewer into ``container`` (the page's #swing-viewer element). */
  function mount(container, data) {
    var frames = data.frames;
    var scene = buildSvg(frames);
    var stage = container.querySelector('.sv-stage');
    var slider = container.querySelector('.sv-slider');
    var button = container.querySelector('.sv-play');
    var readout = container.querySelector('.sv-readout');
    stage.appendChild(scene.svg);
    slider.max = String(frames.length - 1);

    var timer = null;
    function show(index) {
      slider.value = String(index);
      drawFrame(scene, frames, index);
      readout.textContent = describeFrame(frames[index]);
    }
    function stop() {
      if (timer !== null) cancelAnimationFrame(timer);
      timer = null;
      button.textContent = 'Play';
      button.setAttribute('aria-pressed', 'false');
    }
    function play() {
      var startIndex = Number(slider.value) >= frames.length - 1 ? 0 : Number(slider.value);
      var t0 = frames[startIndex].t;
      var wall0 = null;
      button.textContent = 'Pause';
      button.setAttribute('aria-pressed', 'true');
      function tick(now) {
        if (wall0 === null) wall0 = now;
        var t = t0 + (now - wall0) / 1000 / SLOW_MOTION;
        var index = startIndex;
        while (index < frames.length - 1 && frames[index + 1].t <= t) index += 1;
        show(index);
        if (index >= frames.length - 1) { stop(); return; }
        timer = requestAnimationFrame(tick);
      }
      timer = requestAnimationFrame(tick);
    }
    button.addEventListener('click', function () {
      if (timer === null) play();
      else stop();
    });
    slider.addEventListener('input', function () {
      stop();
      show(Number(slider.value));
    });
    show(0);
    container.classList.add('sv-ready');
  }

  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function () {
      var container = document.getElementById('swing-viewer');
      var data = typeof window !== 'undefined' ? window.AffineDriftSwingViewerData : null;
      if (container && data) mount(container, data);
    });
  }

  return {strokeFor: strokeFor, toView: toView, describeFrame: describeFrame, mount: mount};
});
