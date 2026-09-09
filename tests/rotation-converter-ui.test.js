/** Exercise actual article inputs and UI state, with the optional renderer stubbed. */
const fs = require('fs');
const path = require('path');

function input(selector, value) {
  const cell = document.querySelector(selector);
  cell.value = value;
  cell.dispatchEvent(new Event('input', {bubbles:true}));
}

beforeEach(() => {
  jest.resetModules();
  const source = fs.readFileSync(path.join(__dirname,'../articles/rotation-converter.qmd'),'utf8');
  document.body.innerHTML = [...source.matchAll(/```\{=html\}\s*([\s\S]*?)```/g)]
    .map(match => match[1]).join('\n');
  window.RotationConverter = require('../js/rotation-converter');
  window.RotationConverterViz = {init: jest.fn(),update: jest.fn()};
  require('../js/rotation-converter-ui');
  document.dispatchEvent(new Event('DOMContentLoaded'));
});

test.each(['90garbage','Infinity','','-','0x10'])(
  'rejects incomplete or nondecimal input %p and marks results stale', value => {
    input('.rc-euler-cell[data-comp="psi"]',value);
    expect(document.querySelector('#rc-app').dataset.valid).toBe('false');
    expect(document.querySelector('#rc-status').textContent).toMatch(/previous|last valid/i);
  });

test('zero axis with nonzero angle is rejected instead of inventing a direction', () => {
  input('.rc-aa-cell[data-comp="angle"]','45');
  input('.rc-aa-cell[data-comp="nz"]','0');
  expect(document.querySelector('#rc-app').dataset.valid).toBe('false');
  expect(document.querySelector('#rc-status').textContent).toMatch(/zero/i);
});

test('invalid matrix is not reported as loaded successfully', () => {
  input('.rc-matrix-cell[data-row="2"][data-col="2"]','-1');
  document.querySelector('.rc-load-btn[data-rep="R"]').click();
  expect(document.querySelector('#rc-status').textContent).not.toMatch(/Loaded from/);
  expect(document.querySelector('#rc-app').dataset.valid).toBe('false');
});

test('half-turn and identity formulas explicitly handle singular branches', () => {
  document.querySelector('[data-preset="rz180"]').click();
  expect(document.querySelector('#rc-formula-text').textContent).toMatch(/largest/i);
  expect(document.querySelector('#rc-formula-text').textContent).toMatch(/sign/i);
  document.querySelector('[data-preset="identity"]').click();
  expect(document.querySelector('#rc-formula-text').textContent).toMatch(/axis.*undefined/i);
});

test('unit toggle refreshes visualization and leaves rotation-vector components in radians', () => {
  document.querySelector('[data-preset="rz90"]').click();
  const vector = document.querySelector('.rc-exp-cell[data-comp="2"]').value;
  const radio = document.querySelector('#rc-rad');
  radio.checked = true;
  radio.dispatchEvent(new Event('change'));
  expect(document.querySelector('.rc-exp-cell[data-comp="2"]').value).toBe(vector);
  expect(window.RotationConverterViz.update.mock.calls.at(-1)[1]).toBe(false);
});

test('editing an Euler field does not replace its in-progress spelling', () => {
  input('.rc-euler-cell[data-comp="psi"]','1.');
  expect(document.querySelector('.rc-euler-cell[data-comp="psi"]').value).toBe('1.');
});

test.each([false,true])('numeric controls survive unavailable WebGL (throws=%p)', throws => {
  if (throws) window.THREE = {WebGLRenderer: class {constructor() {throw new Error('No GPU');}}};
  else delete window.THREE;
  require('../js/rotation-converter-viz');
  expect(() => window.RotationConverterViz.init()).not.toThrow();
  expect(document.querySelector('#rc-webgl-fallback').style.display).toBe('block');
  input('.rc-euler-cell[data-comp="psi"]','90');
  expect(document.querySelector('#rc-app').dataset.valid).toBe('true');
  delete window.THREE;
});
