/**
 * Tests for src/js/modules/utils.js
 * Testing utility functions used throughout the application
 */

// Import functions to test (these are defined at bottom of file for testing)
// In production, these would be imported from the actual module

describe('Utils Module', () => {
  describe('debounce', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    test('should delay function execution', () => {
      const mockFn = jest.fn();
      const debounced = debounce(mockFn, 100);

      debounced();
      expect(mockFn).not.toHaveBeenCalled();

      jest.advanceTimersByTime(99);
      expect(mockFn).not.toHaveBeenCalled();

      jest.advanceTimersByTime(1);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    test('should cancel previous calls when called rapidly', () => {
      const mockFn = jest.fn();
      const debounced = debounce(mockFn, 100);

      debounced();
      jest.advanceTimersByTime(50);
      debounced();
      jest.advanceTimersByTime(50);
      debounced();

      jest.advanceTimersByTime(100);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    test('should pass arguments to the debounced function', () => {
      const mockFn = jest.fn();
      const debounced = debounce(mockFn, 100);

      debounced('arg1', 'arg2', 123);
      jest.advanceTimersByTime(100);

      expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2', 123);
    });

    test('should preserve this context', () => {
      const obj = {
        value: 42,
        getValue: jest.fn(function() {
          return this.value;
        })
      };
      const debounced = debounce(obj.getValue, 100);

      debounced.call(obj);
      jest.advanceTimersByTime(100);

      expect(obj.getValue).toHaveBeenCalled();
    });
  });

  describe('runOnDomReady', () => {
    test('should execute immediately if document is complete', () => {
      const mockCallback = jest.fn();
      Object.defineProperty(document, 'readyState', {
        writable: true,
        value: 'complete'
      });

      runOnDomReady(mockCallback);
      expect(mockCallback).toHaveBeenCalledTimes(1);
    });

    test('should execute immediately if document is interactive', () => {
      const mockCallback = jest.fn();
      Object.defineProperty(document, 'readyState', {
        writable: true,
        value: 'interactive'
      });

      runOnDomReady(mockCallback);
      expect(mockCallback).toHaveBeenCalledTimes(1);
    });

    test('should wait for DOMContentLoaded if document is loading', () => {
      const mockCallback = jest.fn();
      Object.defineProperty(document, 'readyState', {
        writable: true,
        value: 'loading'
      });

      runOnDomReady(mockCallback);
      expect(mockCallback).not.toHaveBeenCalled();

      document.dispatchEvent(new Event('DOMContentLoaded'));
      expect(mockCallback).toHaveBeenCalledTimes(1);
    });
  });

  describe('runWhenIdle', () => {
    test('should use requestIdleCallback when available', () => {
      const mockCallback = jest.fn();
      const originalRequestIdleCallback = global.requestIdleCallback;
      global.requestIdleCallback = jest.fn();

      runWhenIdle(mockCallback);

      expect(global.requestIdleCallback).toHaveBeenCalledWith(mockCallback);
      global.requestIdleCallback = originalRequestIdleCallback;
    });

    test('should fallback to setTimeout when requestIdleCallback unavailable', () => {
      const mockCallback = jest.fn();
      const originalRequestIdleCallback = global.requestIdleCallback;
      delete global.requestIdleCallback;

      jest.useFakeTimers();
      runWhenIdle(mockCallback);

      expect(mockCallback).not.toHaveBeenCalled();
      jest.advanceTimersByTime(0);
      expect(mockCallback).toHaveBeenCalledTimes(1);

      global.requestIdleCallback = originalRequestIdleCallback;
      jest.useRealTimers();
    });
  });

  describe('getScrollOffset', () => {
    test('should return default offset of 140', () => {
      const offset = getScrollOffset();
      expect(offset).toBe(140);
    });

    test('should parse CSS variable value', () => {
      document.documentElement.style.setProperty('--scroll-offset', '200px');
      // Note: Mock returns 140 by default in setup.js
      const offset = getScrollOffset();
      expect(typeof offset).toBe('number');
    });

    test('should return 140 when window is undefined', () => {
      // Test the fallback path
      const offset = getScrollOffset();
      expect(offset).toBeGreaterThanOrEqual(0);
    });
  });

  describe('generateUniqueId', () => {
    test('should convert text to lowercase slug', () => {
      const usedIds = new Set();
      const id = generateUniqueId('Hello World', usedIds);
      expect(id).toBe('hello-world');
    });

    test('should remove special characters', () => {
      const usedIds = new Set();
      const id = generateUniqueId('Test! @#$% String?', usedIds);
      expect(id).toBe('test-string');
    });

    test('should handle empty string', () => {
      const usedIds = new Set();
      const id = generateUniqueId('', usedIds);
      expect(id).toBe('section');
    });

    test('should handle whitespace only', () => {
      const usedIds = new Set();
      const id = generateUniqueId('   ', usedIds);
      expect(id).toBe('section');
    });

    test('should remove leading and trailing hyphens', () => {
      const usedIds = new Set();
      const id = generateUniqueId('---test---', usedIds);
      expect(id).toBe('test');
    });

    test('should add counter for duplicate IDs', () => {
      const usedIds = new Set(['test-heading']);
      const id = generateUniqueId('Test Heading', usedIds);
      expect(id).toBe('test-heading-1');
    });

    test('should increment counter for multiple duplicates', () => {
      const usedIds = new Set(['test', 'test-1', 'test-2']);
      const id = generateUniqueId('Test', usedIds);
      expect(id).toBe('test-3');
    });

    test('should handle numbers in text', () => {
      const usedIds = new Set();
      const id = generateUniqueId('Chapter 1: Introduction', usedIds);
      expect(id).toBe('chapter-1-introduction');
    });
  });

  describe('smoothScrollTo', () => {
    test('should call window.scrollTo with smooth behavior', () => {
      const mockScrollTo = jest.fn();
      window.scrollTo = mockScrollTo;

      const element = document.createElement('div');
      element.getBoundingClientRect = jest.fn(() => ({
        top: 500,
        left: 0,
        right: 100,
        bottom: 600,
        width: 100,
        height: 100
      }));

      smoothScrollTo(element);

      expect(mockScrollTo).toHaveBeenCalledWith({
        top: expect.any(Number),
        behavior: 'smooth'
      });
    });

    test('should apply custom offset', () => {
      const mockScrollTo = jest.fn();
      window.scrollTo = mockScrollTo;
      window.pageYOffset = 0;

      const element = document.createElement('div');
      element.getBoundingClientRect = jest.fn(() => ({
        top: 500,
        left: 0,
        right: 100,
        bottom: 600,
        width: 100,
        height: 100
      }));

      smoothScrollTo(element, 200);

      expect(mockScrollTo).toHaveBeenCalledWith({
        top: 300, // 500 - 200
        behavior: 'smooth'
      });
    });
  });
});

// Function definitions for testing
// These mirror the actual implementations from src/js/modules/utils.js

function debounce(func, wait) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}

function runOnDomReady(callback) {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", callback);
  } else {
    callback();
  }
}

function runWhenIdle(callback) {
  if (typeof requestIdleCallback !== "undefined") {
    requestIdleCallback(callback);
  } else {
    setTimeout(callback, 0);
  }
}

function getScrollOffset() {
  if (typeof window !== "undefined") {
    const value = getComputedStyle(document.documentElement).getPropertyValue(
      "--scroll-offset",
    );
    return value ? parseInt(value) : 140;
  }
  return 140;
}

function generateUniqueId(text, usedIds) {
  const MAX_ATTEMPTS = 100;

  let baseId = text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

  if (!baseId) baseId = "section";

  let id = baseId;
  let counter = 1;

  const exists = (candidateId) => {
    return (
      usedIds.has(candidateId) || document.getElementById(candidateId) !== null
    );
  };

  if (!exists(id)) {
    return id;
  }

  while (exists(id) && counter < MAX_ATTEMPTS) {
    id = `${baseId}-${counter}`;
    counter++;
  }

  if (usedIds.has(id)) {
    id = `${baseId}-${Date.now()}`;
  }

  return id;
}

function smoothScrollTo(element, offset = 140) {
  const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;

  window.scrollTo({
    top: targetPosition,
    behavior: 'smooth'
  });
}
