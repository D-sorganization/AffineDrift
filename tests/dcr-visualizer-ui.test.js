/** Exercises the actual article widget markup and its live DOM state. */
const fs = require('fs');
const path = require('path');

function setValue(id, value) {
  const element = document.getElementById(id);
  element.value = value;
  element.dispatchEvent(new Event('input', {bubbles: true}));
}

beforeEach(() => {
  jest.resetModules();
  const source = fs.readFileSync(
    path.join(__dirname, '../articles/drift-control-ratio.qmd'), 'utf8');
  const block = [...source.matchAll(/```\{=html\}\s*([\s\S]*?)```/g)]
    .map(match => match[1]).find(html => html.includes('dcrviz-app'));
  document.body.innerHTML = block;
  window.DcrVisualizer = require('../js/dcr-visualizer');
  require('../js/dcr-visualizer-ui');
  document.dispatchEvent(new Event('DOMContentLoaded'));
});

test('defaults reproduce the governed equal-DCR, different-width counterexample', () => {
  expect(document.getElementById('dcrviz-dcr-a-now').textContent).toBe('1');
  expect(document.getElementById('dcrviz-dcr-b-now').textContent).toBe('1');
  expect(document.getElementById('dcrviz-width-a').textContent).toBe('2');
  expect(Number(document.getElementById('dcrviz-width-b').textContent))
    .toBeCloseTo(2 * (Math.E - 1), 4);
  expect(document.getElementById('dcrviz-app').dataset.valid).toBe('true');
});

test('dragging the phase slider grows the state-dependent DCR but not the additive one', () => {
  setValue('dcrviz-phase', '1');
  expect(document.getElementById('dcrviz-dcr-a-now').textContent).toBe('1');
  expect(Number(document.getElementById('dcrviz-dcr-b-now').textContent))
    .toBeCloseTo(Math.E, 4);
});

test('a zero initial state is rejected with an explicit message, keeping the last valid result', () => {
  setValue('dcrviz-x0', '0');
  expect(document.getElementById('dcrviz-app').dataset.valid).toBe('false');
  expect(document.getElementById('dcrviz-status').textContent).toMatch(/nonzero/i);
  expect(document.getElementById('dcrviz-width-a').textContent).toBe('2');
});

test('a nonpositive control bound is rejected', () => {
  setValue('dcrviz-ubar', '0');
  expect(document.getElementById('dcrviz-app').dataset.valid).toBe('false');
  expect(document.getElementById('dcrviz-status').textContent).toMatch(/positive/i);
});

test('the sampled data table is populated as an accessible text alternative', () => {
  const rows = document.querySelectorAll('#dcrviz-table-body tr');
  expect(rows.length).toBe(21);
  expect(rows[0].children[0].textContent).toBe('0');
});
