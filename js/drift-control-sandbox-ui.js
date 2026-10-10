/** Binds the checked DriftControlSandbox engine to the WEB-06.3 widget (#4533).
 * Shows the same-state split qdd = f(x) + G(x)u along a driven double-pendulum
 * run, and the separately integrated zero-torque counterfactual from the same
 * initial state. Exploratory model output; not a golfer measurement.
 */
(function () {
  'use strict';
  const DCS = window.DriftControlSandbox;
  const byId = id => document.getElementById(id);
  const format = value => Number(value.toPrecision(4)).toString();
  const TABLE_EVERY = 25;
  const PLAYBACK_SLOWDOWN = 4;
  const SLIDERS = ['shoulder', 'wrist', 'l1', 'l2', 'm1', 'm2'];
  let run = null;
  let playing = false;

  function status(message, valid) {
    const element = byId('dcsb-status');
    element.textContent = message;
    element.dataset.valid = String(valid);
  }

  function readSlider(name) {
    const value = Number(byId(`dcsb-${name}`).value);
    if (!Number.isFinite(value)) throw new Error(`${name} must be a finite number`);
    byId(`dcsb-${name}-value`).textContent = format(value);
    return value;
  }

  function compute() {
    const values = Object.fromEntries(SLIDERS.map(name => [name, readSlider(name)]));
    const params = DCS.makeParams({...DCS.DEFAULTS.params,
      l1: values.l1, l2: values.l2, m1: values.m1, m2: values.m2});
    const {q0, qd0, horizon, steps} = DCS.DEFAULTS;
    const torque = DCS.generalizedTorque(values.shoulder, values.wrist);
    const driven = DCS.simulate(params, q0, qd0, torque, horizon, steps);
    const counterfactual = DCS.simulate(params, q0, qd0, [0, 0], horizon, steps);
    const tips = driven.map(s => DCS.tipAccelerationSplit(s.q, s.qd, s.driftQdd, s.inputQdd, params));
    const peak = Math.max(1e-9, ...tips.flat().map(a => Math.hypot(a[0], a[1])));
    return {params, driven, counterfactual, tips, peak};
  }

  function color(name) {
    return getComputedStyle(byId('dcsb-app')).getPropertyValue(name).trim() || '#888';
  }

  function linkagePoints(q, params) {
    const elbow = [params.l1 * Math.sin(q[0]), -params.l1 * Math.cos(q[0])];
    return [[0, 0], elbow, DCS.tipPosition(q, params)];
  }

  function drawLinkage(ctx, toPx, points, stroke, dashed) {
    ctx.save();
    ctx.strokeStyle = stroke;
    ctx.lineWidth = dashed ? 2 : 4;
    ctx.setLineDash(dashed ? [6, 5] : []);
    ctx.beginPath();
    points.forEach((point, i) => (i ? ctx.lineTo : ctx.moveTo).call(ctx, ...toPx(point)));
    ctx.stroke();
    ctx.restore();
  }

  function drawArrow(ctx, from, to, stroke) {
    const angle = Math.atan2(to[1] - from[1], to[0] - from[0]);
    ctx.save();
    ctx.strokeStyle = stroke;
    ctx.fillStyle = stroke;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(...from);
    ctx.lineTo(...to);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(...to);
    ctx.lineTo(to[0] - 10 * Math.cos(angle - 0.4), to[1] - 10 * Math.sin(angle - 0.4));
    ctx.lineTo(to[0] - 10 * Math.cos(angle + 0.4), to[1] - 10 * Math.sin(angle + 0.4));
    ctx.fill();
    ctx.restore();
  }

  function drawScene(index) {
    const canvas = byId('dcsb-canvas');
    const ctx = canvas.getContext('2d');
    const {params, driven, counterfactual, tips, peak} = run;
    const reach = params.l1 + params.l2;
    const pxPerMetre = (0.45 * canvas.width) / reach;
    const toPx = ([x, y]) => [canvas.width / 2 + x * pxPerMetre, canvas.height / 2 - y * pxPerMetre];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (byId('dcsb-ghost').checked) {
      drawLinkage(ctx, toPx, linkagePoints(counterfactual[index].q, params), color('--dcsb-ghost'), true);
    }
    const points = linkagePoints(driven[index].q, params);
    drawLinkage(ctx, toPx, points, color('--dcsb-linkage'), false);
    const tip = toPx(points[2]);
    const arrowMetres = 0.5 * reach / peak;
    const [tipDrift, tipInput] = tips[index];
    const end = a => [tip[0] + a[0] * arrowMetres * pxPerMetre, tip[1] - a[1] * arrowMetres * pxPerMetre];
    drawArrow(ctx, tip, end(tipDrift), color('--dcsb-drift'));
    drawArrow(ctx, tip, end(tipInput), color('--dcsb-input'));
    byId('dcsb-arrow-scale').textContent = format(1 / arrowMetres);
    canvas.setAttribute('aria-label', `Double pendulum at t = ${format(driven[index].t)} s. Tip `
      + `acceleration from drift ${format(Math.hypot(...tipDrift))} m/s², from input `
      + `${format(Math.hypot(...tipInput))} m/s². Numbers are in the table below.`);
  }

  function polyline(values, minValue, maxValue, width, height) {
    const span = maxValue - minValue || 1;
    return values.map((value, i) => {
      const x = (i / (values.length - 1)) * width;
      return `${x.toFixed(1)},${(height - ((value - minValue) / span) * height).toFixed(1)}`;
    }).join(' ');
  }

  function drawCharts() {
    for (const joint of [0, 1]) {
      const svg = byId(`dcsb-chart-q${joint + 1}`);
      const [, , width, height] = svg.getAttribute('viewBox').split(' ').map(Number);
      const drift = run.driven.map(s => s.driftQdd[joint]);
      const input = run.driven.map(s => s.inputQdd[joint]);
      const lo = Math.min(0, ...drift, ...input);
      const hi = Math.max(0, ...drift, ...input);
      svg.querySelector('.dcsb-line-drift').setAttribute('points', polyline(drift, lo, hi, width, height));
      svg.querySelector('.dcsb-line-input').setAttribute('points', polyline(input, lo, hi, width, height));
      svg.querySelector('.dcsb-zero').setAttribute('points', polyline([0, 0], lo, hi, width, height));
      byId(`dcsb-range-q${joint + 1}`).textContent = `[${format(lo)}, ${format(hi)}]`;
    }
  }

  function drawCursor(index) {
    for (const joint of [1, 2]) {
      const svg = byId(`dcsb-chart-q${joint}`);
      const [, , width, height] = svg.getAttribute('viewBox').split(' ').map(Number);
      const x = ((index / (run.driven.length - 1)) * width).toFixed(1);
      svg.querySelector('.dcsb-cursor').setAttribute('points', `${x},0 ${x},${height}`);
    }
  }

  function renderTable() {
    const rows = run.driven.filter((_, i) => i % TABLE_EVERY === 0).map(s => `<tr><td>${format(s.t)}</td>`
      + [s.q[0], s.q[1], s.driftQdd[0], s.inputQdd[0], s.driftQdd[1], s.inputQdd[1]]
        .map(v => `<td>${format(v)}</td>`).join('') + '</tr>');
    byId('dcsb-data').innerHTML = rows.join('');
  }

  function showFrame() {
    const index = Number(byId('dcsb-time').value);
    const sample = run.driven[index];
    const [tipDrift, tipInput] = run.tips[index];
    byId('dcsb-time-value').textContent = format(sample.t);
    byId('dcsb-now-drift-1').textContent = format(sample.driftQdd[0]);
    byId('dcsb-now-input-1').textContent = format(sample.inputQdd[0]);
    byId('dcsb-now-drift-2').textContent = format(sample.driftQdd[1]);
    byId('dcsb-now-input-2').textContent = format(sample.inputQdd[1]);
    byId('dcsb-now-tip-drift').textContent = format(Math.hypot(...tipDrift));
    byId('dcsb-now-tip-input').textContent = format(Math.hypot(...tipInput));
    drawScene(index);
    drawCursor(index);
  }

  function update() {
    try {
      run = compute();
      const slider = byId('dcsb-time');
      slider.max = String(run.driven.length - 1);
      drawCharts();
      renderTable();
      showFrame();
      status('Computed in your browser by the checked mirror of '
        + 'src/affine_control/double_pendulum_affine.py.', true);
    } catch (error) {
      status(`${error.message}. Showing the last valid result.`, false);
    }
  }

  function applyPreset() {
    const preset = DCS.PRESETS[byId('dcsb-preset').value];
    byId('dcsb-shoulder').value = String(preset.shoulder);
    byId('dcsb-wrist').value = String(preset.wrist);
    byId('dcsb-time').value = '0';
    update();
  }

  function togglePlay() {
    playing = !playing;
    byId('dcsb-play').textContent = playing ? 'Pause' : 'Play';
    byId('dcsb-play').setAttribute('aria-pressed', String(playing));
    if (!playing) return;
    const slider = byId('dcsb-time');
    if (Number(slider.value) >= Number(slider.max)) slider.value = '0';
    let last = null;
    const msPerSample = (1000 * DCS.DEFAULTS.horizon * PLAYBACK_SLOWDOWN) / DCS.DEFAULTS.steps;
    const tick = now => {
      if (!playing) return;
      if (last !== null) {
        const advance = Math.floor((now - last) / msPerSample);
        if (advance > 0) {
          slider.value = String(Math.min(Number(slider.max), Number(slider.value) + advance));
          last += advance * msPerSample;
          showFrame();
        }
      } else {
        last = now;
      }
      if (Number(slider.value) >= Number(slider.max)) togglePlay();
      else window.requestAnimationFrame(tick);
    };
    window.requestAnimationFrame(tick);
  }

  function boot() {
    const app = byId('dcsb-app');
    if (!app || app.dataset.bound) return;
    app.dataset.bound = 'true';
    performance.mark('dcsb-boot');
    SLIDERS.forEach(name => byId(`dcsb-${name}`).addEventListener('input', update));
    byId('dcsb-preset').addEventListener('change', applyPreset);
    byId('dcsb-ghost').addEventListener('change', showFrame);
    byId('dcsb-time').addEventListener('input', showFrame);
    byId('dcsb-play').addEventListener('click', togglePlay);
    applyPreset();
    app.dataset.widgetReady = 'true';
    performance.mark('dcsb-ready');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
