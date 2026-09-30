/** Binds the checked DcrVisualizer engine to the article widget. Compares an
 * additive-drift system against a state-dependent-drift system that share the
 * same instantaneous DCR at the start of the phase, to show that DCR does not
 * determine the reachable-interval width (claim ad-dcr-001).
 */
(function () {
  'use strict';
  const DV = window.DcrVisualizer;
  const byId = id => document.getElementById(id);
  const format = value => Number(value.toPrecision(6)).toString();
  const SAMPLE_COUNT = 21;

  function readNumber(id, label) {
    const element = byId(id);
    const text = element.value.trim();
    const value = Number(text);
    if (text === '' || !Number.isFinite(value)) {
      throw new Error(`${label} must be a finite number`);
    }
    return value;
  }

  function status(message, valid) {
    const element = byId('dcrviz-status');
    element.textContent = message;
    element.dataset.valid = String(valid);
    byId('dcrviz-app').dataset.valid = String(valid);
  }

  function polylinePoints(values, maxValue, width, height) {
    return values.map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - (maxValue > 0 ? (value / maxValue) * height : 0);
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    }).join(' ');
  }

  function renderChart(samplesA, samplesB) {
    const svg = byId('dcrviz-chart');
    const width = Number(svg.getAttribute('viewBox').split(' ')[2]);
    const height = Number(svg.getAttribute('viewBox').split(' ')[3]);
    const maxValue = Math.max(...samplesA, ...samplesB, 1e-12);
    byId('dcrviz-line-a').setAttribute('points', polylinePoints(samplesA, maxValue, width, height));
    byId('dcrviz-line-b').setAttribute('points', polylinePoints(samplesB, maxValue, width, height));
    byId('dcrviz-chart-max').textContent = format(maxValue);
    svg.setAttribute('aria-label',
      `Instantaneous DCR across the phase; vertical axis maximum ${format(maxValue)}. `
      + 'A full accessible table of sampled values follows.');
  }

  function renderTable(times, samplesA, samplesB) {
    byId('dcrviz-table-body').innerHTML = times.map((t, index) =>
      `<tr><td>${format(t)}</td><td>${format(samplesA[index])}</td>`
      + `<td>${format(samplesB[index])}</td></tr>`).join('');
  }

  function dcrAtEvolvedState(driveState, gradient, controlBound) {
    return DV.instantaneousScalarDcr(DV.linearScalarSystem(driveState, gradient, 0, controlBound));
  }

  function update() {
    try {
      const x0 = readNumber('dcrviz-x0', 'Initial state');
      const ubar = readNumber('dcrviz-ubar', 'Control bound');
      const horizon = readNumber('dcrviz-horizon', 'Horizon');
      const phaseFraction = Number(byId('dcrviz-phase').value);
      if (x0 === 0) {
        throw new Error('Initial state must be nonzero: the state-dependent system is undefined at x0 = 0');
      }
      if (!(ubar > 0)) throw new Error('Control bound must be positive');
      if (!(horizon >= 0)) throw new Error('Horizon must be nonnegative');

      const gradientB = ubar / x0;
      const additive = DV.linearScalarSystem(x0, 0, ubar, ubar);
      const stateDependent = DV.linearScalarSystem(x0, gradientB, 0, ubar);
      const [loA, hiA] = DV.scalarLinearReachableInterval(additive, horizon);
      const [loB, hiB] = DV.scalarLinearReachableInterval(stateDependent, horizon);

      const times = Array.from({length: SAMPLE_COUNT}, (_, i) => (i / (SAMPLE_COUNT - 1)) * horizon);
      const dcrA = DV.instantaneousScalarDcr(additive);
      const samplesA = times.map(() => dcrA);
      const samplesB = times.map(t => dcrAtEvolvedState(
        DV.multiplicativeDriftState(x0, gradientB, t), gradientB, ubar));

      renderChart(samplesA, samplesB);
      renderTable(times, samplesA, samplesB);

      const t = phaseFraction * horizon;
      const dcrBNow = dcrAtEvolvedState(DV.multiplicativeDriftState(x0, gradientB, t), gradientB, ubar);
      byId('dcrviz-phase-time').textContent = format(t);
      byId('dcrviz-dcr-a-now').textContent = format(dcrA);
      byId('dcrviz-dcr-b-now').textContent = format(dcrBNow);
      byId('dcrviz-width-a').textContent = format(hiA - loA);
      byId('dcrviz-width-b').textContent = format(hiB - loB);
      byId('dcrviz-interval-a').textContent = `[${format(loA)}, ${format(hiA)}]`;
      byId('dcrviz-interval-b').textContent = `[${format(loB)}, ${format(hiB)}]`;
      status('Computed from the declared LinearScalarSystem, instantaneous_scalar_dcr, and '
        + 'scalar_linear_reachable_interval formulas.', true);
    } catch (error) {
      status(`${error.message}. Showing the last valid result.`, false);
    }
  }

  function boot() {
    if (!byId('dcrviz-app') || byId('dcrviz-app').dataset.ready) return;
    byId('dcrviz-app').dataset.ready = 'true';
    ['dcrviz-x0', 'dcrviz-ubar', 'dcrviz-horizon', 'dcrviz-phase'].forEach(id => {
      byId(id).addEventListener('input', update);
    });
    update();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
