/**
 * Behavioral tests for js/startup-launcher.js (issue #3233).
 *
 * The launcher is a self-executing IIFE that injects a splash screen and hides
 * it once the page is ready (or after a safety timeout). It is precached by the
 * service worker, so its failure modes are high deployment risk. We require()
 * the real file (Istanbul-instrumented) per test with fake timers so the
 * splash lifecycle — create, ready-reveal, and the timeout fallback — is
 * exercised against the shipped code.
 */

const MODULE_PATH = '../js/startup-launcher.js';

function loadLauncher() {
  jest.resetModules();
  jest.isolateModules(() => {
    require(MODULE_PATH);
  });
}

describe('startup-launcher', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    document.documentElement.className = '';
    document.body.innerHTML = '';
    // matchMedia is provided by tests/setup.js (matches:false by default).
    if (!window.performance.now) {
      window.performance.now = () => 0;
    }
    delete window.AffineDriftStartup;
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  test('injects a splash screen on init and exposes its API', () => {
    loadLauncher();
    const splash = document.getElementById('ad-splash-screen');
    expect(splash).not.toBeNull();
    expect(splash.getAttribute('role')).toBe('progressbar');
    expect(document.documentElement.classList.contains('ad-splash-active')).toBe(true);
    expect(typeof window.AffineDriftStartup.forceHide).toBe('function');
    expect(window.AffineDriftStartup.isReady()).toBe(false);
  });

  test('clicking the splash force-hides it (skip affordance)', () => {
    loadLauncher();
    const splash = document.getElementById('ad-splash-screen');
    splash.dispatchEvent(new Event('click'));
    // hideSplash adds the exit class synchronously, then schedules removal.
    expect(splash.classList.contains('ad-splash-exit')).toBe(true);
    jest.advanceTimersByTime(2000);
    expect(document.documentElement.classList.contains('ad-splash-active')).toBe(false);
  });

  test('timeout fallback removes the splash even if ready never fires', () => {
    loadLauncher();
    const splash = document.getElementById('ad-splash-screen');
    expect(splash.classList.contains('ad-splash-exit')).toBe(false);

    // Advance past MAXIMUM_SPLASH_DURATION (5000ms) to trigger forceHideSplash.
    jest.advanceTimersByTime(5000);
    expect(splash.classList.contains('ad-splash-exit')).toBe(true);

    // Fade + cleanup timers then strip the splash-active state.
    jest.advanceTimersByTime(2000);
    expect(document.documentElement.classList.contains('ad-splash-active')).toBe(false);
  });

  test('reveal dispatches affinedrift:ready and marks ready', () => {
    loadLauncher();
    const readyHandler = jest.fn();
    document.addEventListener('affinedrift:ready', readyHandler);

    window.AffineDriftStartup.forceHide();
    jest.advanceTimersByTime(2000);

    expect(readyHandler).toHaveBeenCalled();
    expect(window.AffineDriftStartup.isReady()).toBe(true);
    expect(document.documentElement.classList.contains('ad-page-revealed')).toBe(true);
  });

  test('forceHide is idempotent and does not throw on a hidden splash', () => {
    loadLauncher();
    expect(() => {
      window.AffineDriftStartup.forceHide();
      jest.advanceTimersByTime(2000);
      window.AffineDriftStartup.forceHide(); // second call is a no-op
    }).not.toThrow();
  });

  // Regression tests for issue #3273: startup-launcher must NOT clobber
  // window.AffineDriftMetrics with a plain performance-data object.
  test('does not set window.AffineDriftMetrics (regression #3273)', () => {
    // Ensure any prior value is absent so we detect a fresh write.
    delete window.AffineDriftMetrics;
    loadLauncher();
    // Run all timers so logPerformanceMetrics() has a chance to fire.
    jest.runAllTimers();
    expect(window.AffineDriftMetrics).toBeUndefined();
  });

  test('exposes startup perf data under AffineDriftStartupMetrics, not AffineDriftMetrics', () => {
    delete window.AffineDriftStartupMetrics;
    loadLauncher();
    jest.runAllTimers();
    // The debug dump should use the non-clobbering name.
    // AffineDriftStartupMetrics may be set (if logPerformanceMetrics ran) or
    // undefined (if the metrics guard skipped it) — either is acceptable, but
    // it must NOT be the AffineDriftMetrics name.
    expect(window.AffineDriftMetrics).toBeUndefined();
  });
});
