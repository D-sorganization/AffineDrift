/**
 * Tests for js/forms.js — issue #3233.
 * ESM module transformed for Jest via babel-jest (babel.config.js).
 */

import {
  initEmailCopy,
  initCodeCopy,
  initFormAccessibility,
  initAutoGrowTextareas,
} from '../js/forms.js';

describe('forms.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '';
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.restoreAllMocks();
  });

  describe('initEmailCopy', () => {
    test('adds a copy button after a mailto link', () => {
      document.body.innerHTML = '<a href="mailto:hi@example.com">Email</a>';
      initEmailCopy();
      const btn = document.querySelector('.copy-email-btn');
      expect(btn).not.toBeNull();
      expect(btn.getAttribute('aria-label')).toBe('Copy email address');
    });

    test('is idempotent — does not add a second button on re-init', () => {
      document.body.innerHTML = '<a href="mailto:hi@example.com">Email</a>';
      initEmailCopy();
      initEmailCopy();
      expect(document.querySelectorAll('.copy-email-btn').length).toBe(1);
    });

    test('ignores non-mailto links', () => {
      document.body.innerHTML = '<a href="https://example.com">Site</a>';
      initEmailCopy();
      expect(document.querySelector('.copy-email-btn')).toBeNull();
    });

    test('copies the email to the clipboard on click', async () => {
      const writeText = jest.fn().mockResolvedValue(undefined);
      Object.assign(navigator, { clipboard: { writeText } });
      document.body.innerHTML = '<a href="mailto:hi@example.com?subject=x">Email</a>';
      initEmailCopy();
      document.querySelector('.copy-email-btn').click();
      expect(writeText).toHaveBeenCalledWith('hi@example.com');
    });

    test('no-DOM: empty document is a no-op, not a throw', () => {
      expect(() => initEmailCopy()).not.toThrow();
    });
  });

  describe('initCodeCopy', () => {
    test('wraps a code block and adds a copy button', () => {
      document.body.innerHTML = '<pre>const x = 1;</pre>';
      initCodeCopy();
      const wrapper = document.querySelector('.code-wrapper');
      expect(wrapper).not.toBeNull();
      expect(wrapper.querySelector('button[data-action="copy-code"]')).not.toBeNull();
    });

    test('skips empty pre blocks', () => {
      document.body.innerHTML = '<pre>   </pre>';
      initCodeCopy();
      expect(document.querySelector('.code-wrapper')).toBeNull();
    });
  });

  describe('initFormAccessibility', () => {
    test('marks a required input label with a required indicator', () => {
      document.body.innerHTML =
        '<label for="n">Name</label><input id="n" required />';
      initFormAccessibility();
      const indicator = document.querySelector('.required-indicator');
      expect(indicator).not.toBeNull();
      expect(indicator.getAttribute('aria-hidden')).toBe('true');
    });

    test('does not mark optional inputs', () => {
      document.body.innerHTML =
        '<label for="n">Name</label><input id="n" />';
      initFormAccessibility();
      expect(document.querySelector('.required-indicator')).toBeNull();
    });
  });

  describe('initAutoGrowTextareas', () => {
    test('no-DOM: no textareas is a no-op, not a throw', () => {
      expect(() => initAutoGrowTextareas()).not.toThrow();
    });
  });
});
