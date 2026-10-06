/**
 * Tests for the WEB-11.6 symbol hover references (#4584).
 *
 * scripts/filters/symbol-hover.lua wraps opted-in symbols in MathJax
 * `\class{symref symref--KEY}` and writes a native <details> symbol list after
 * the equation. js/symbol-hover.js adds a pointer tooltip on the typeset
 * symbol, reading the definition from that list, so keyboard and screen-reader
 * users get the same text from the <details> without any script.
 */

const MATH = `
  <p><mjx-container><mjx-math aria-hidden="true">
    <mjx-mrow class="symref symref--f"><mjx-mi id="sym-f">f</mjx-mi></mjx-mrow>
    <mjx-mrow class="symref symref--Q"><mjx-mi id="sym-q">Q</mjx-mi></mjx-mrow>
  </mjx-math></mjx-container></p>
  <details class="symbol-refs"><summary>Symbols in this equation</summary>
    <dl class="symbol-refs__list">
      <div class="symbol-refs__item" data-symref="f">
        <dt>Drift f(x)</dt><dd>Complete autonomous drift.</dd>
      </div>
    </dl>
  </details>`;

function hover(element, related = null) {
  element.dispatchEvent(new MouseEvent('mouseover', {bubbles: true, relatedTarget: related}));
}

function leave(element, related = null) {
  element.dispatchEvent(new MouseEvent('mouseout', {bubbles: true, relatedTarget: related}));
}

describe('symbol hover references', () => {
  let SymbolHover;

  beforeEach(() => {
    jest.resetModules();
    document.body.innerHTML = MATH;
    SymbolHover = require('../js/symbol-hover.js');
    SymbolHover.bind(document);
  });

  test('reads the symbol key from the MathJax class hook', () => {
    expect(SymbolHover.keyFrom(document.getElementById('sym-f'))).toBe('f');
    expect(SymbolHover.keyFrom(document.body)).toBeNull();
  });

  test('looks the definition up in the accessible symbol list', () => {
    expect(SymbolHover.definitionFor(document, 'f')).toEqual({
      name: 'Drift f(x)',
      definition: 'Complete autonomous drift.',
    });
    expect(SymbolHover.definitionFor(document, 'Q')).toBeNull();
    expect(SymbolHover.definitionFor(document, 'f"] , x[y="')).toBeNull();
  });

  test('hovering a symbol shows its definition and leaving hides it', () => {
    hover(document.getElementById('sym-f'));
    const tip = document.querySelector('.symbol-hover-tip');
    expect(tip.hidden).toBe(false);
    expect(tip.textContent).toBe('Drift f(x): Complete autonomous drift.');
    expect(tip.getAttribute('aria-hidden')).toBe('true');
    leave(document.getElementById('sym-f'), document.body);
    expect(tip.hidden).toBe(true);
  });

  test('the tooltip stays while the pointer moves onto it', () => {
    hover(document.getElementById('sym-f'));
    const tip = document.querySelector('.symbol-hover-tip');
    leave(document.getElementById('sym-f'), tip);
    expect(tip.hidden).toBe(false);
  });

  test('Escape dismisses the tooltip', () => {
    hover(document.getElementById('sym-f'));
    document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
    expect(document.querySelector('.symbol-hover-tip').hidden).toBe(true);
  });

  test('a symbol without a listed definition shows nothing', () => {
    hover(document.getElementById('sym-q'));
    const tip = document.querySelector('.symbol-hover-tip');
    expect(tip === null || tip.hidden).toBe(true);
  });

  test('binding twice does not duplicate listeners', () => {
    SymbolHover.bind(document);
    hover(document.getElementById('sym-f'));
    expect(document.querySelectorAll('.symbol-hover-tip')).toHaveLength(1);
  });
});
