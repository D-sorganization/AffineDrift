/** The ztcf-explorer controller and live readout on the real article markup (#5254). */
const fs = require('fs');
const path = require('path');

const STEPS = 200;

function controller() {
  return window.AffineDriftWidgets['ztcf-explorer'];
}

function text(id) {
  return document.getElementById(id).textContent;
}

beforeEach(() => {
  jest.resetModules();
  delete window.AffineDriftWidgets;
  const source = fs.readFileSync(
    path.join(__dirname, '../articles/zero-torque-counterfactual.qmd'), 'utf8');
  const block = [...source.matchAll(/```\{=html\}\s*([\s\S]*?)```/g)]
    .map(match => match[1]).find(html => html.includes('ztx-app'));
  document.body.innerHTML = block;
  // jsdom has no 2D canvas; the drawing calls are irrelevant to the contract.
  const noop = () => {};
  HTMLCanvasElement.prototype.getContext = () => new Proxy({}, {get: () => noop});
  performance.mark = performance.mark || noop;
  window.ZTCFExplorer = require('../js/ztcf-explorer');
  require('../js/ztcf-explorer-ui');
  document.dispatchEvent(new Event('DOMContentLoaded'));
});

test('registers a getState/setParam/step controller on window.AffineDriftWidgets', () => {
  const widget = controller();
  expect(typeof widget.getState).toBe('function');
  expect(typeof widget.setParam).toBe('function');
  expect(typeof widget.step).toBe('function');
  expect(widget.getState().interventionStep).toBe(50);
});

test('setParam drives the same state the slider shows', () => {
  const before = text('ztx-speed-branch');
  const state = controller().setParam('interventionStep', 150);
  expect(document.getElementById('ztx-step').value).toBe('150');
  expect(state.interventionStep).toBe(150);
  expect(text('ztx-speed-branch')).not.toBe(before);
  expect(String(state.speedDifference)).toBe(text('ztx-speed-difference'));
  expect(document.getElementById('ztx-status').dataset.valid).toBe('true');
});

test('step moves one sample at a time and stops at the ends of the range', () => {
  expect(controller().step(1).interventionStep).toBe(51);
  expect(controller().step(-2).interventionStep).toBe(49);
  controller().setParam('interventionStep', STEPS - 1);
  expect(controller().step(1).interventionStep).toBe(STEPS - 1);
  controller().setParam('interventionStep', 0);
  expect(controller().step(-1).interventionStep).toBe(0);
});

test('setParam rejects unknown names and out-of-range values without changing state', () => {
  expect(() => controller().setParam('torque', 1)).toThrow(/unknown parameter/);
  expect(() => controller().setParam('interventionStep', STEPS)).toThrow(/integer in \[0, 199\]/);
  expect(() => controller().setParam('interventionStep', 1.5)).toThrow(/integer/);
  expect(controller().getState().interventionStep).toBe(50);
});

test('getState returns a snapshot the caller cannot use to mutate the widget', () => {
  const state = controller().getState();
  expect(Object.isFrozen(state)).toBe(true);
  expect(Object.isFrozen(state.dq)).toBe(true);
});

test('a polite, atomic live readout announces the intervention time and difference', () => {
  const readout = document.getElementById('ztx-readout');
  expect(readout.getAttribute('aria-live')).toBe('polite');
  expect(readout.getAttribute('aria-atomic')).toBe('true');
  controller().setParam('interventionStep', 150);
  expect(readout.textContent).toContain(`t = ${text('ztx-step-value')} s`);
  expect(readout.textContent).toContain(`${text('ztx-speed-difference')} m/s`);
});

test('the widget creates its own live readout right after the status line', () => {
  const readout = document.getElementById('ztx-readout');
  expect(readout.previousElementSibling.id).toBe('ztx-status');
  expect(document.querySelectorAll('#ztx-readout')).toHaveLength(1);
});

test('setParam fails closed when the engine throws, keeping the last valid state', () => {
  window.ZTCFExplorer.explore = () => { throw new Error('engine failed'); };
  expect(() => controller().setParam('interventionStep', 100)).toThrow(/engine failed/);
  expect(() => controller().step(1)).toThrow(/engine failed/);
  expect(controller().getState().interventionStep).toBe(50);
  expect(document.getElementById('ztx-step').value).toBe('50');
  expect(document.getElementById('ztx-status').dataset.valid).toBe('false');
});
