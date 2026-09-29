/**
 * Tests for js/page-feedback.js — issue #4605.
 * Per-page "Was this helpful? / Report a problem" footer control.
 */

import { initPageFeedback } from '../js/page-feedback.js';

function flushMicrotasks() {
  return Promise.resolve().then(() => Promise.resolve());
}

function githubIssueParams(href) {
  const url = new URL(href);
  return url.searchParams;
}

describe('page-feedback.js', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="quarto-document-content"></div>';
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ source_revision: 'abc1234' }),
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('is a no-op when the page has no content container', () => {
    document.body.innerHTML = '';
    expect(() => initPageFeedback()).not.toThrow();
    expect(document.querySelector('.page-feedback')).toBeNull();
  });

  test('appends exactly one widget to #quarto-document-content', async () => {
    initPageFeedback();
    await flushMicrotasks();
    const widgets = document.querySelectorAll('.page-feedback');
    expect(widgets.length).toBe(1);
    expect(document.getElementById('quarto-document-content').contains(widgets[0])).toBe(true);
  });

  test('is idempotent — a second call does not duplicate the widget', async () => {
    initPageFeedback();
    await flushMicrotasks();
    initPageFeedback();
    await flushMicrotasks();
    expect(document.querySelectorAll('.page-feedback').length).toBe(1);
  });

  test('renders keyboard-accessible native controls', async () => {
    initPageFeedback();
    await flushMicrotasks();
    const yes = document.querySelector('[data-vote="yes"]');
    const no = document.querySelector('[data-vote="no"]');
    const report = document.querySelector('.page-feedback__report-link');
    const email = document.querySelector('.page-feedback__email-link');

    expect(yes.tagName).toBe('BUTTON');
    expect(yes.getAttribute('type')).toBe('button');
    expect(no.tagName).toBe('BUTTON');
    expect(no.getAttribute('type')).toBe('button');
    expect(report.tagName).toBe('A');
    expect(report.hasAttribute('href')).toBe(true);
    expect(email.tagName).toBe('A');
    expect(email.getAttribute('href')).toMatch(/^mailto:/);

    for (const el of [yes, no, report, email]) {
      expect(el.getAttribute('tabindex')).not.toBe('-1');
    }
  });

  test('report link opens the content-correction template with the page URL and commit', async () => {
    initPageFeedback();
    await flushMicrotasks();
    const report = document.querySelector('.page-feedback__report-link');
    const params = githubIssueParams(report.getAttribute('href'));

    expect(report.getAttribute('href')).toMatch(
      /^https:\/\/github\.com\/D-sorganization\/AffineDrift\/issues\/new\?/
    );
    expect(params.get('template')).toBe('content-correction.md');
    expect(params.get('body')).toContain(window.location.href);
    expect(params.get('body')).toContain('abc1234');
  });

  test('falls back to an "unknown" revision when the manifest fetch fails', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('network error'));
    initPageFeedback();
    await flushMicrotasks();
    const report = document.querySelector('.page-feedback__report-link');
    const params = githubIssueParams(report.getAttribute('href'));
    expect(params.get('body')).toContain('unknown');
  });

  test('email fallback link carries the page URL and commit for readers without a GitHub account', async () => {
    initPageFeedback();
    await flushMicrotasks();
    const email = document.querySelector('.page-feedback__email-link');
    const decoded = decodeURIComponent(email.getAttribute('href'));

    expect(decoded).toContain(window.location.href);
    expect(decoded).toContain('abc1234');
    expect(email.getAttribute('href')).not.toContain('+');
  });

  test('clicking "Yes" announces thanks and disables both vote buttons', async () => {
    initPageFeedback();
    await flushMicrotasks();
    const yes = document.querySelector('[data-vote="yes"]');
    const no = document.querySelector('[data-vote="no"]');

    yes.click();

    expect(yes.disabled).toBe(true);
    expect(no.disabled).toBe(true);
    const liveRegion = document.querySelector('[aria-live="polite"]');
    expect(liveRegion).not.toBeNull();
    expect(liveRegion.textContent).toMatch(/thanks/i);
  });

  test('clicking "No" announces thanks and disables both vote buttons', async () => {
    initPageFeedback();
    await flushMicrotasks();
    const yes = document.querySelector('[data-vote="yes"]');
    const no = document.querySelector('[data-vote="no"]');

    no.click();

    expect(no.disabled).toBe(true);
    expect(yes.disabled).toBe(true);
    const liveRegion = document.querySelector('[aria-live="polite"]');
    expect(liveRegion.textContent).toMatch(/thanks/i);
  });

  test('never calls a third-party endpoint — only same-origin fetch', async () => {
    initPageFeedback();
    await flushMicrotasks();
    for (const call of global.fetch.mock.calls) {
      expect(String(call[0])).toMatch(/^\//);
    }
  });
});
