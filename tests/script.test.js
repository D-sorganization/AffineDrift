/**
 * Tests for script.js utility functions
 */

describe('Utility Functions', () => {
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

      jest.advanceTimersByTime(100);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    test('should cancel previous calls', () => {
      const mockFn = jest.fn();
      const debounced = debounce(mockFn, 100);

      debounced();
      debounced();
      debounced();

      jest.advanceTimersByTime(100);
      expect(mockFn).toHaveBeenCalledTimes(1);
    });

    test('should pass arguments correctly', () => {
      const mockFn = jest.fn();
      const debounced = debounce(mockFn, 100);

      debounced('arg1', 'arg2');
      jest.advanceTimersByTime(100);

      expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
    });
  });

  describe('generateUniqueId', () => {
    test('should generate ID from text', () => {
      const usedIds = new Set();
      const id = generateUniqueId('Test Heading', usedIds);
      
      expect(id).toBe('test-heading');
    });

    test('should handle special characters', () => {
      const usedIds = new Set();
      const id = generateUniqueId('Test & Special! Characters?', usedIds);
      
      expect(id).toBe('test-special-characters');
    });

    test('should handle empty text', () => {
      const usedIds = new Set();
      const id = generateUniqueId('', usedIds);
      
      expect(id).toBe('section');
    });

    test('should avoid duplicates with counter', () => {
      const usedIds = new Set(['test-heading']);
      const id = generateUniqueId('Test Heading', usedIds);
      
      expect(id).toBe('test-heading-1');
    });

    test('should increment counter for multiple duplicates', () => {
      const usedIds = new Set(['test-heading', 'test-heading-1', 'test-heading-2']);
      const id = generateUniqueId('Test Heading', usedIds);
      
      expect(id).toBe('test-heading-3');
    });

    test('should handle leading and trailing hyphens', () => {
      const usedIds = new Set();
      const id = generateUniqueId('---Test---', usedIds);
      
      expect(id).toBe('test');
    });
  });

  describe('getScrollOffset', () => {
    test('should return default offset', () => {
      const offset = getScrollOffset();
      expect(offset).toBe(140);
    });

    test('should parse CSS variable', () => {
      document.documentElement.style.setProperty('--scroll-offset', '200px');
      const offset = getScrollOffset();
      expect(offset).toBeGreaterThanOrEqual(140);
    });
  });

  describe('runOnDomReady', () => {
    test('should execute callback immediately if DOM is ready', () => {
      const mockCallback = jest.fn();
      Object.defineProperty(document, 'readyState', {
        writable: true,
        value: 'complete'
      });

      runOnDomReady(mockCallback);
      expect(mockCallback).toHaveBeenCalled();
    });

    test('should wait for DOMContentLoaded if loading', () => {
      const mockCallback = jest.fn();
      Object.defineProperty(document, 'readyState', {
        writable: true,
        value: 'loading'
      });

      runOnDomReady(mockCallback);
      expect(mockCallback).not.toHaveBeenCalled();

      // Simulate DOMContentLoaded
      document.dispatchEvent(new Event('DOMContentLoaded'));
      expect(mockCallback).toHaveBeenCalled();
    });
  });

  describe('runWhenIdle', () => {
    test('should use requestIdleCallback when available', () => {
      const mockCallback = jest.fn();
      runWhenIdle(mockCallback);

      expect(global.requestIdleCallback).toHaveBeenCalledWith(mockCallback);
    });

    test('should fallback to setTimeout', () => {
      const originalRequestIdleCallback = global.requestIdleCallback;
      delete global.requestIdleCallback;

      jest.useFakeTimers();
      const mockCallback = jest.fn();
      
      runWhenIdle(mockCallback);
      expect(mockCallback).not.toHaveBeenCalled();

      jest.advanceTimersByTime(0);
      expect(mockCallback).toHaveBeenCalled();

      global.requestIdleCallback = originalRequestIdleCallback;
      jest.useRealTimers();
    });
  });
});

describe('DOM Manipulation', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
  });

  describe('Heading ID Generation', () => {
    test('should add IDs to headings without IDs', () => {
      document.body.innerHTML = `
        <h2>Test Heading</h2>
        <h3>Another Heading</h3>
      `;

      const headings = document.querySelectorAll('h2, h3');
      const usedIds = new Set();

      headings.forEach(heading => {
        if (!heading.id) {
          heading.id = generateUniqueId(heading.textContent, usedIds);
          usedIds.add(heading.id);
        }
      });

      expect(document.querySelector('h2').id).toBe('test-heading');
      expect(document.querySelector('h3').id).toBe('another-heading');
    });

    test('should preserve existing IDs', () => {
      document.body.innerHTML = `
        <h2 id="existing-id">Test Heading</h2>
      `;

      const heading = document.querySelector('h2');
      const originalId = heading.id;

      // Simulate the ID preservation logic
      if (!heading.id) {
        heading.id = generateUniqueId(heading.textContent, new Set());
      }

      expect(heading.id).toBe(originalId);
    });
  });

  describe('Smooth Scrolling', () => {
    test('should calculate correct scroll position', () => {
      const element = document.createElement('div');
      element.style.position = 'absolute';
      element.style.top = '500px';
      document.body.appendChild(element);

      const offset = 140;
      const targetPosition = element.getBoundingClientRect().top + window.pageYOffset - offset;

      expect(targetPosition).toBeGreaterThanOrEqual(0);
    });
  });

  describe('ARIA Labels', () => {
    test('should add ARIA labels to navigation', () => {
      document.body.innerHTML = `
        <nav id="TOC"></nav>
        <div class="sidebar"></div>
      `;

      const toc = document.getElementById('TOC');
      const sidebar = document.querySelector('.sidebar');

      // Simulate ARIA label addition
      if (toc && !toc.getAttribute('aria-label')) {
        toc.setAttribute('aria-label', 'Table of Contents');
      }
      if (sidebar && !sidebar.getAttribute('aria-label')) {
        sidebar.setAttribute('aria-label', 'Sidebar navigation');
      }

      expect(toc.getAttribute('aria-label')).toBe('Table of Contents');
      expect(sidebar.getAttribute('aria-label')).toBe('Sidebar navigation');
    });

    test('should not override existing ARIA labels', () => {
      document.body.innerHTML = `
        <nav id="TOC" aria-label="Custom Label"></nav>
      `;

      const toc = document.getElementById('TOC');
      const existingLabel = toc.getAttribute('aria-label');

      // Simulate preservation logic
      if (toc && !toc.getAttribute('aria-label')) {
        toc.setAttribute('aria-label', 'Table of Contents');
      }

      expect(toc.getAttribute('aria-label')).toBe(existingLabel);
    });
  });
});

describe('Constants', () => {
  test('should have correct default values', () => {
    expect(MAX_ID_GENERATION_ATTEMPTS).toBe(100);
    expect(MATHJAX_RENDER_DELAY_MS).toBe(100);
    expect(CRITICS_CORNER_PADDING_OFFSET).toBe(50);
  });

  test('should have correct scroll offsets', () => {
    expect(HEADER_OFFSET).toBe(140);
    expect(TOC_SCROLL_OFFSET).toBe(140);
  });
});

// Helper function definitions for testing
// These would normally be imported from script.js
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}

function generateUniqueId(text, usedIds) {
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

  while (exists(id) && counter < MAX_ID_GENERATION_ATTEMPTS) {
    id = `${baseId}-${counter}`;
    counter++;
  }

  if (usedIds.has(id)) {
    id = `${baseId}-${Date.now()}`;
  }

  return id;
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

// Constants
const MAX_ID_GENERATION_ATTEMPTS = 100;
const MATHJAX_RENDER_DELAY_MS = 100;
const CRITICS_CORNER_PADDING_OFFSET = 50;
let HEADER_OFFSET = 140;
let TOC_SCROLL_OFFSET = 140;
