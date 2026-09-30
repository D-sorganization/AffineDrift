/**
 * Tests for js/pdf.js — WEB-07.9 (#4550).
 * ESM module transformed for Jest via babel-jest (babel.config.js).
 */

let initPrintMathTypesetting;

describe('pdf.js', () => {
  beforeEach(() => {
    jest.resetModules();
    // Replace window so previously-attached listeners are gone.
    const mod = require('../js/pdf.js');
    initPrintMathTypesetting = mod.initPrintMathTypesetting;
  });

  describe('initPrintMathTypesetting', () => {
    // WEB-07.9 (#4550) / WEB-11.3: lazy-loaded, off-screen math is not
    // typeset until scrolled into view. A native print (Ctrl+P) must not
    // ship raw TeX, so `beforeprint` forces a full typeset.
    test('forces MathJax.typesetPromise on beforeprint when MathJax is present', () => {
      const typesetPromise = jest.fn().mockResolvedValue(undefined);
      window.MathJax = { typesetPromise };

      initPrintMathTypesetting();
      window.dispatchEvent(new Event('beforeprint'));

      expect(typesetPromise).toHaveBeenCalledTimes(1);

      delete window.MathJax;
    });

    test('does not throw when MathJax is unavailable', () => {
      delete window.MathJax;

      initPrintMathTypesetting();
      expect(() => window.dispatchEvent(new Event('beforeprint'))).not.toThrow();
    });
  });
});
