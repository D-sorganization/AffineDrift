/**
 * Jest setup file for DOM testing
 */

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock requestIdleCallback
global.requestIdleCallback = jest.fn((callback) => {
  return setTimeout(callback, 0);
});

global.cancelIdleCallback = jest.fn((id) => {
  clearTimeout(id);
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};

// Mock getComputedStyle
const originalGetComputedStyle = window.getComputedStyle;
window.getComputedStyle = jest.fn((element) => {
  const style = originalGetComputedStyle(element);
  return {
    ...style,
    getPropertyValue: jest.fn((prop) => {
      if (prop === '--scroll-offset') return '140';
      if (prop === '--header-offset') return '120';
      return style.getPropertyValue(prop);
    }),
  };
});

// Clean up timers after each test to prevent worker process hang
afterEach(() => {
  jest.clearAllTimers();
});
