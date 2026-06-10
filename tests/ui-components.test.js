/**
 * Tests for js/ui-components.js — issue #3233.
 * ESM module transformed for Jest via babel-jest (babel.config.js).
 */

// Re-require a fresh module instance per test so document-level click
// listeners registered by initAccordions do not accumulate across tests.
let registerScrollCallback;
let unregisterScrollCallback;
let initAccordions;
let initBackToTop;
let initFadeAnimations;

describe('ui-components.js', () => {
  beforeEach(() => {
    jest.resetModules();
    document.body.innerHTML = '';
    // Replace document so previously-attached listeners are gone.
    document.head.innerHTML = '';
    const mod = require('../js/ui-components.js');
    registerScrollCallback = mod.registerScrollCallback;
    unregisterScrollCallback = mod.unregisterScrollCallback;
    initAccordions = mod.initAccordions;
    initBackToTop = mod.initBackToTop;
    initFadeAnimations = mod.initFadeAnimations;
  });

  describe('scroll callbacks', () => {
    test('registering then unregistering toggles the scroll listener', () => {
      const addSpy = jest.spyOn(window, 'addEventListener');
      const removeSpy = jest.spyOn(window, 'removeEventListener');
      const cb = jest.fn();

      registerScrollCallback(cb);
      expect(addSpy).toHaveBeenCalledWith('scroll', expect.any(Function), {
        passive: true,
      });

      unregisterScrollCallback(cb);
      expect(removeSpy).toHaveBeenCalledWith('scroll', expect.any(Function));

      addSpy.mockRestore();
      removeSpy.mockRestore();
    });
  });

  describe('initAccordions', () => {
    function buildAccordion() {
      document.body.innerHTML = `
        <div class="accordion-header" aria-expanded="false">
          <span>Section</span>
        </div>
        <div class="accordion-content">body</div>
      `;
    }

    test('wires aria on init and toggles expanded/hidden on click', () => {
      buildAccordion();
      initAccordions();
      const header = document.querySelector('.accordion-header');
      const content = document.querySelector('.accordion-content');

      // init-time aria wiring
      expect(content.id).toBeTruthy();
      expect(header.getAttribute('aria-controls')).toBe(content.id);
      expect(content.getAttribute('aria-hidden')).toBe('true');

      // click toggles state (single init -> single document listener)
      header.querySelector('span').click();
      expect(header.getAttribute('aria-expanded')).toBe('true');
      expect(content.getAttribute('aria-hidden')).toBe('false');
    });

    test('no-DOM: no accordions is a no-op, not a throw', () => {
      expect(() => initAccordions()).not.toThrow();
    });
  });

  describe('initBackToTop', () => {
    test('appends an accessible back-to-top button', () => {
      initBackToTop();
      const btn = document.querySelector('.back-to-top');
      expect(btn).not.toBeNull();
      expect(btn.getAttribute('aria-label')).toBe('Scroll to top');
    });

    test('uses instant scroll when reduced motion is requested', () => {
      window.matchMedia = jest.fn().mockImplementation((query) => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));
      const scrollTo = jest.fn();
      window.scrollTo = scrollTo;

      initBackToTop();
      document.querySelector('.back-to-top').click();

      expect(scrollTo).toHaveBeenCalledWith({
        top: 0,
        behavior: 'auto',
      });
    });
  });

  describe('initFadeAnimations', () => {
    test('no-DOM safe even without IntersectionObserver targets', () => {
      // jsdom lacks IntersectionObserver; provide a minimal stub.
      window.IntersectionObserver = class {
        observe() {}
        unobserve() {}
        disconnect() {}
      };
      expect(() => initFadeAnimations()).not.toThrow();
    });
  });
});
