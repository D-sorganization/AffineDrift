/**
 * Behavioral tests for js/dark-mode-toggle.js (issue #3233).
 *
 * The module is a browser IIFE with no exports that self-executes on import and
 * mutates document/localStorage. We require() the real file (so Istanbul
 * instruments it for coverage) once per test via jest.resetModules(), after
 * wiring localStorage + matchMedia mocks. This exercises the actual shipped
 * code and contributes real coverage.
 */

const MODULE_PATH = '../js/dark-mode-toggle.js';

function loadModule({ prefersDark = false } = {}) {
  const changeHandlers = [];
  window.matchMedia = jest.fn().mockImplementation((query) => ({
    matches: query.includes('dark') ? prefersDark : false,
    media: query,
    addEventListener: (_evt, cb) => changeHandlers.push(cb),
    removeEventListener: jest.fn(),
    addListener: jest.fn(),
    removeListener: jest.fn(),
    dispatchEvent: jest.fn(),
  }));
  jest.resetModules();
  jest.isolateModules(() => {
    require(MODULE_PATH);
  });
  return { changeHandlers };
}

describe('dark-mode-toggle', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.removeAttribute('data-bs-theme');
    document.body.innerHTML = '<nav class="navbar"></nav>';
  });

  test('applies stored theme preference on load', () => {
    localStorage.setItem('affinedrift-theme', 'dark');
    loadModule();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(document.documentElement.getAttribute('data-bs-theme')).toBe('dark');
  });

  test('falls back to prefers-color-scheme when no stored preference', () => {
    loadModule({ prefersDark: true });
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  test('defaults to light when neither stored nor system prefers dark', () => {
    loadModule({ prefersDark: false });
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  test('clicking the toggle flips the theme and persists it', () => {
    loadModule({ prefersDark: false }); // starts light
    document.dispatchEvent(new Event('DOMContentLoaded'));
    const btn = document.getElementById('theme-toggle');
    expect(btn).not.toBeNull();

    btn.click();
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(localStorage.getItem('affinedrift-theme')).toBe('dark');

    btn.click();
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(localStorage.getItem('affinedrift-theme')).toBe('light');
  });

  test('applying the system theme on load does NOT persist it (issue #3333)', () => {
    // A fresh visitor whose OS prefers dark should get dark applied, but with an
    // empty localStorage so the prefers-color-scheme listener keeps working.
    loadModule({ prefersDark: true });
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(localStorage.getItem('affinedrift-theme')).toBeNull();
  });

  test('system preference change is respected after a no-persist load (issue #3333)', () => {
    const { changeHandlers } = loadModule({ prefersDark: false }); // light, unpersisted
    expect(localStorage.getItem('affinedrift-theme')).toBeNull();
    // OS flips to dark at sunset -> theme should follow, no manual clear needed.
    changeHandlers[0]({ matches: true });
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  test('system preference change updates theme only when storage is unset', () => {
    const { changeHandlers } = loadModule({ prefersDark: false });
    expect(changeHandlers.length).toBeGreaterThan(0);

    // Simulate a user who has not chosen a theme: clear the on-load persistence.
    localStorage.clear();
    changeHandlers[0]({ matches: true });
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');

    // With a stored preference present, a subsequent system change is ignored.
    localStorage.setItem('affinedrift-theme', 'dark');
    changeHandlers[0]({ matches: false });
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
  });

  test('does not throw when the navbar is absent (no-DOM path)', () => {
    document.body.innerHTML = '';
    expect(() => {
      loadModule();
      document.dispatchEvent(new Event('DOMContentLoaded'));
    }).not.toThrow();
    // Button falls back to document.body.
    expect(document.getElementById('theme-toggle')).not.toBeNull();
  });

  describe('header placement and accessibility (#5167)', () => {
    function mount(html, options) {
      document.body.innerHTML = html;
      const result = loadModule(options || { prefersDark: false });
      document.dispatchEvent(new Event('DOMContentLoaded'));
      return { btn: document.getElementById('theme-toggle'), ...result };
    }

    test('is a real button with a stable name and aria-pressed state', () => {
      const { btn } = mount('<nav class="navbar"></nav>');
      expect(btn.tagName).toBe('BUTTON');
      expect(btn.getAttribute('type')).toBe('button');
      expect(btn.getAttribute('aria-label')).toBe('Dark mode');
      expect(btn.getAttribute('aria-pressed')).toBe('false');
      expect(btn.querySelector('svg')).not.toBeNull();

      btn.click();
      expect(btn.getAttribute('aria-pressed')).toBe('true');
      expect(btn.getAttribute('aria-label')).toBe('Dark mode');
    });

    test('reflects a stored dark preference in aria-pressed on load', () => {
      localStorage.setItem('affinedrift-theme', 'dark');
      const { btn } = mount('<nav class="navbar"></nav>');
      expect(btn.getAttribute('aria-pressed')).toBe('true');
    });

    test('sits in the navbar row next to the menu toggler', () => {
      mount(
        '<nav class="navbar"><div class="navbar-container">' +
          '<button class="navbar-toggler"></button></div></nav>'
      );
      // Earlier tests leave DOMContentLoaded listeners behind, so assert on the
      // element adjacent to the toggler rather than the first #theme-toggle.
      const toggler = document.querySelector('.navbar-toggler');
      expect(toggler.previousElementSibling.id).toBe('theme-toggle');
    });

    test('OS preference change refreshes aria-pressed', () => {
      const { btn, changeHandlers } = mount('<nav class="navbar"></nav>');
      localStorage.clear();
      changeHandlers[0]({ matches: true });
      expect(btn.getAttribute('aria-pressed')).toBe('true');
    });
  });
});
