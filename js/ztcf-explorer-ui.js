/** Binds the checked ZTCFExplorer engine to the WEB-06.4 widget (#4534).
 * The reader picks an intervention time; the widget overlays the declared
 * torque-driven run and the zero-torque branch started from the actual state
 * at that time, and reports their simulated difference at the horizon.
 * Exploratory model output; not a golfer measurement or a contribution share.
 */
(function () {
  'use strict';
  const ZE = window.ZTCFExplorer;
  const byId = id => document.getElementById(id);
  const format = value => Number(value.toPrecision(4)).toString();
  const TABLE_EVERY = 10;
  const {q0, qd0, torque, horizon, steps} = ZE.DEFAULTS;
  const model = ZE.makeModel(ZE.DEFAULTS.params);
  let run = null;

  function status(message, valid) {
    const element = byId('ztx-status');
    element.textContent = message;
    element.dataset.valid = String(valid);
  }

  function color(name) {
    return getComputedStyle(byId('ztx-app')).getPropertyValue(name).trim() || '#888';
  }

  function drawPath(ctx, toPx, points, stroke, width, dash) {
    ctx.save();
    ctx.strokeStyle = stroke;
    ctx.lineWidth = width;
    ctx.setLineDash(dash);
    ctx.beginPath();
    points.forEach((point, i) => (i ? ctx.lineTo : ctx.moveTo).call(ctx, ...toPx(point)));
    ctx.stroke();
    ctx.restore();
  }

  /** Uniform scale and offset that fit every drawn point inside the canvas margin. */
  function fitToCanvas(points, canvas) {
    const xs = points.map(p => p[0]);
    const ys = points.map(p => p[1]);
    const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
    const margin = 0.08 * canvas.width;
    const scale = (canvas.width - 2 * margin) / Math.max(x1 - x0, y1 - y0, 1e-9);
    const [cx, cy] = [(x0 + x1) / 2, (y0 + y1) / 2];
    return ([x, y]) => [canvas.width / 2 + (x - cx) * scale, canvas.height / 2 - (y - cy) * scale];
  }

  function drawScene(step) {
    const canvas = byId('ztx-canvas');
    const ctx = canvas.getContext('2d');
    const tip = sample => ZE.chainPoints(model, sample.q)[3];
    const paths = [
      [ZE.chainPoints(model, run.actual[step].q), color('--ztx-past'), 2, []],
      [run.actual.map(tip), color('--ztx-actual'), 1.5, []],
      [run.branch.map(tip), color('--ztx-branch'), 1.5, [6, 4]],
      [ZE.chainPoints(model, run.actual[steps].q), color('--ztx-actual'), 4, []],
      [ZE.chainPoints(model, run.branch[run.branch.length - 1].q), color('--ztx-branch'), 3, [6, 4]],
    ];
    const toPx = fitToCanvas(paths.flatMap(path => path[0]), canvas);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    paths.forEach(([points, stroke, width, dash]) => drawPath(ctx, toPx, points, stroke, width, dash));
    canvas.setAttribute('aria-label', `Three-link model at the ${format(horizon)} s horizon. `
      + `Declared-torque run and zero-torque branch from t = ${format(run.actual[step].t)} s. `
      + 'Numbers are in the tables below.');
  }

  function polyline(times, values, lo, hi, width, height) {
    const span = hi - lo || 1;
    return values.map((value, i) => `${((times[i] / horizon) * width).toFixed(1)},`
      + `${(height - ((value - lo) / span) * height).toFixed(1)}`).join(' ');
  }

  function drawChart(step) {
    const svg = byId('ztx-chart');
    const [, , width, height] = svg.getAttribute('viewBox').split(' ').map(Number);
    const speeds = run.actual.map(s => s.speed).concat(run.branch.map(s => s.speed));
    const [lo, hi] = [Math.min(...speeds), Math.max(...speeds)];
    const line = samples => polyline(samples.map(s => s.t), samples.map(s => s.speed), lo, hi, width, height);
    svg.querySelector('.ztx-line-actual').setAttribute('points', line(run.actual));
    svg.querySelector('.ztx-line-branch').setAttribute('points', line(run.branch));
    const x = ((run.actual[step].t / horizon) * width).toFixed(1);
    svg.querySelector('.ztx-cursor').setAttribute('points', `${x},0 ${x},${height}`);
    byId('ztx-range').textContent = `[${format(lo)}, ${format(hi)}]`;
  }

  function renderResults() {
    const a = run.actual[steps];
    const b = run.branch[run.branch.length - 1];
    byId('ztx-speed-actual').textContent = format(a.speed);
    byId('ztx-speed-branch').textContent = format(b.speed);
    byId('ztx-speed-difference').textContent = format(run.difference.clubheadSpeed);
    run.difference.q.forEach((value, i) => { byId(`ztx-dq${i + 1}`).textContent = format(value); });
    const branchAt = new Map(run.branch.map(s => [Math.round(s.t / (horizon / steps)), s]));
    byId('ztx-data').innerHTML = run.actual.filter((_, i) => i % TABLE_EVERY === 0).map((s, row) => {
      const ztcf = branchAt.get(row * TABLE_EVERY);
      return `<tr><td>${format(s.t)}</td><td>${format(s.speed)}</td>`
        + `<td>${ztcf ? format(ztcf.speed) : '—'}</td></tr>`;
    }).join('');
  }

  function update() {
    try {
      const step = Number(byId('ztx-step').value);
      run = ZE.explore(model, q0, qd0, torque, horizon, steps, step);
      byId('ztx-step-value').textContent = format(run.actual[step].t);
      drawScene(step);
      drawChart(step);
      renderResults();
      status('Computed in your browser by the checked mirror of '
        + 'src/affine_control/ztcf_explorer.py.', true);
    } catch (error) {
      status(`${error.message}. Showing the last valid result.`, false);
    }
  }

  function boot() {
    const app = byId('ztx-app');
    if (!app || app.dataset.bound) return;
    app.dataset.bound = 'true';
    performance.mark('ztx-boot');
    byId('ztx-step').addEventListener('input', update);
    update();
    app.dataset.widgetReady = 'true';
    performance.mark('ztx-ready');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
