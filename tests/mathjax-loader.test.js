/**
 * Behavioral tests for the gated MathJax loader in
 * _includes/mathjax-loader.html (issue #3332-A).
 *
 * MathJax is the single largest third-party asset on the site (~1MB+). The
 * loader must only inject it when the rendered page actually contains math,
 * so math-free pages (contact, about, resource lists) never pay for it.
 *
 * The loader ships as an inline <script> inside a Quarto include rather than a
 * standalone module, so we extract the script body and evaluate it against a
 * jsdom document with controlled content. This exercises the real shipped
 * source (no duplicated logic) and exposes the gating API on window.
 */

const fs = require('fs');
const path = require('path');

const INCLUDE_PATH = path.join(__dirname, '..', '_includes', 'mathjax-loader.html');

/** Extract the JavaScript body from the single <script> in the include. */
function readLoaderSource() {
  const html = fs.readFileSync(INCLUDE_PATH, 'utf8');
  const match = html.match(/<script>([\s\S]*?)<\/script>/);
  if (!match) {
    throw new Error('mathjax-loader.html: no <script> block found');
  }
  return match[1];
}

/**
 * Evaluate the loader source against the current jsdom document. The loader
 * registers a DOMContentLoaded listener when document.readyState === 'loading';
 * jsdom reports 'complete' after setup, so adLoadMathJax runs synchronously.
 */
function runLoader() {
  // eslint-disable-next-line no-new-func
  new Function(readLoaderSource())();
}

function mathjaxScriptCount() {
  return document.querySelectorAll('script[src*="mathjax"]').length;
}

describe('gated MathJax loader (#3332-A)', () => {
  beforeEach(() => {
    document.documentElement.innerHTML = '<head></head><body></body>';
    delete window.MathJax;
    delete window.AffineDriftMathJax;
  });

  test('does NOT inject MathJax on a math-free page', () => {
    document.body.innerHTML =
      '<main><h1>Contact</h1><p>Email us. Price is 5 dollars.</p></main>';
    runLoader();
    expect(mathjaxScriptCount()).toBe(0);
    expect(window.AffineDriftMathJax.hasMath()).toBe(false);
  });

  test('injects MathJax when a .math span is present', () => {
    document.body.innerHTML =
      '<main><p>Energy <span class="math inline">E=mc^2</span>.</p></main>';
    runLoader();
    expect(mathjaxScriptCount()).toBe(1);
  });

  test('injects MathJax when raw display-math delimiters are present', () => {
    document.body.innerHTML = '<main><p>$$\\int_0^1 x\\,dx$$</p></main>';
    runLoader();
    expect(mathjaxScriptCount()).toBe(1);
  });

  test('injects MathJax when raw inline \\( delimiters are present', () => {
    document.body.innerHTML = '<main><p>The value \\(x\\) is bounded.</p></main>';
    runLoader();
    expect(mathjaxScriptCount()).toBe(1);
  });

  test('pins the exact MathJax version with an SRI integrity hash', () => {
    document.body.innerHTML = '<main><span class="math">x</span></main>';
    runLoader();
    const script = document.querySelector('script[src*="mathjax"]');
    expect(script.src).toContain('mathjax@3.2.2');
    expect(script.integrity).toMatch(/^sha384-/);
    expect(script.crossOrigin).toBe('anonymous');
  });

  test('is idempotent: a second run does not inject a duplicate script', () => {
    document.body.innerHTML = '<main><span class="math">x</span></main>';
    runLoader();
    runLoader();
    expect(mathjaxScriptCount()).toBe(1);
  });

  test('exposes the gating API on window for downstream callers', () => {
    document.body.innerHTML = '<main><p>no math here</p></main>';
    runLoader();
    expect(typeof window.AffineDriftMathJax.hasMath).toBe('function');
    expect(typeof window.AffineDriftMathJax.load).toBe('function');
  });
});
