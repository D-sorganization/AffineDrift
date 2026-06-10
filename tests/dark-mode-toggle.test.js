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
});
