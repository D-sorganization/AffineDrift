const {
  assertManifest,
  buildEvidencePlan,
  canonicalPathMatches,
  fixedElementCanObscureHeading,
  headingBeginsWithinViewport,
  isActionableConsoleError,
  isActionablePageError,
  navigateWithRetry,
  navigationRetryPolicyEvidence,
  parseArgs,
  RETRYABLE_STATUS_CODES,
  summarizeNavigationAttempts,
  screenshotOptions,
  screenshotName,
  waitForSettledPage,
  waitForVisibleMath,
} = require('../scripts/verify-public-site.js');
const fs = require('fs');
const path = require('path');

function fixtureManifest() {
  return {
    schema_version: 'affinedrift/public-site-manifest/v1',
    page_count: 2,
    pages: [
      { route: '/', page_kind: 'home' },
      { route: '/articles/example.html', page_kind: 'article' },
    ],
    verification: {
      themes: ['light', 'dark'],
      viewports: [
        { id: 'mobile', width: 390, height: 844 },
        { id: 'desktop', width: 1440, height: 900 },
        { id: 'tablet', width: 768, height: 1024 },
      ],
      every_page: {
        viewports: ['mobile', 'desktop'],
        themes: ['light', 'dark'],
      },
    },
  };
}

describe('public-site verifier contracts (WEB-D)', () => {
  test('accepts a complete manifest and rejects duplicate or stale counts', () => {
    expect(() => assertManifest(fixtureManifest())).not.toThrow();

    const stale = fixtureManifest();
    stale.page_count = 3;
    expect(() => assertManifest(stale)).toThrow(/page_count/);

    const duplicate = fixtureManifest();
    duplicate.pages[1].route = '/';
    expect(() => assertManifest(duplicate)).toThrow(/duplicate route/);
  });

  test('builds exactly one evidence item per route, viewport, and theme', () => {
    const plan = buildEvidencePlan(fixtureManifest());

    expect(plan).toHaveLength(8);
    expect(plan[0]).toEqual({
      route: '/',
      pageKind: 'home',
      viewport: { id: 'mobile', width: 390, height: 844 },
      theme: 'light',
    });
  });

  test('supports bounded viewport/theme subsets without duplicating inventories', () => {
    const plan = buildEvidencePlan(fixtureManifest(), {
      viewportIds: ['desktop'],
      themes: ['dark'],
    });

    expect(plan).toHaveLength(2);
    expect(new Set(plan.map((item) => item.route))).toEqual(
      new Set(['/', '/articles/example.html']),
    );
  });

  test('supports representative viewports outside the every-page default', () => {
    const plan = buildEvidencePlan(fixtureManifest(), {
      viewportIds: ['tablet'],
      themes: ['light'],
    });

    expect(plan).toHaveLength(2);
    expect(plan.every((item) => item.viewport.id === 'tablet')).toBe(true);
  });

  test('supports an explicit representative route subset', () => {
    const plan = buildEvidencePlan(fixtureManifest(), {
      routes: ['/articles/example.html'],
    });

    expect(plan).toHaveLength(4);
    expect(new Set(plan.map((item) => item.route))).toEqual(
      new Set(['/articles/example.html']),
    );
    expect(() => buildEvidencePlan(fixtureManifest(), { routes: ['/missing.html'] }))
      .toThrow(/route/);
  });

  test('creates stable filesystem-safe screenshot names', () => {
    expect(screenshotName('/articles/The Physics.html', 'desktop', 'dark')).toBe(
      'articles__the-physics__desktop__dark.png',
    );
    expect(screenshotName('/', 'mobile', 'light')).toBe('home__mobile__light.png');
  });

  test('captures a deterministic visible fold instead of unbounded textbook pages', () => {
    expect(screenshotOptions()).toEqual({ animations: 'disabled', fullPage: false });
  });

  test('keeps document retries disabled unless the live gate opts in', () => {
    const defaults = parseArgs([]);
    expect(defaults.documentRetries).toBe(0);
    expect(defaults.documentRetryDelayMs).toBe(500);

    const live = parseArgs([
      '--document-retries',
      '2',
      '--document-retry-delay-ms',
      '500',
    ]);
    expect(live.documentRetries).toBe(2);
    expect(live.documentRetryDelayMs).toBe(500);
    expect(() => parseArgs(['--document-retries', '-1'])).toThrow(/non-negative integer/);
  });

  test('requires the primary heading to begin inside the visible fold', () => {
    const viewport = { width: 768, height: 1024 };
    expect(headingBeginsWithinViewport(
      { left: 50, right: 700, top: 150, bottom: 220, width: 650, height: 70 },
      viewport,
    )).toBe(true);
    expect(headingBeginsWithinViewport(
      { left: 50, right: 700, top: 1025, bottom: 1095, width: 650, height: 70 },
      viewport,
    )).toBe(false);
  });

  test('accepts canonical directory URLs for index documents only', () => {
    expect(canonicalPathMatches('/books/', '/books/index.html')).toBe(true);
    expect(canonicalPathMatches('/books/index.html', '/books/index.html')).toBe(true);
    expect(canonicalPathMatches('/books/', '/books/roadmap.html')).toBe(false);
  });

  test('ignores fixed glass layers behind the page while retaining active overlays', () => {
    expect(fixedElementCanObscureHeading({ zIndex: '-1', pointerEvents: 'auto' })).toBe(false);
    expect(fixedElementCanObscureHeading({ zIndex: '1000', pointerEvents: 'none' })).toBe(false);
    expect(fixedElementCanObscureHeading({ zIndex: '1000', pointerEvents: 'auto' })).toBe(true);
  });

  test('filters browser compute-pressure and net::ERR_ noise but keeps real console errors', () => {
    expect(isActionableConsoleError(
      'Permissions policy violation: compute-pressure is not allowed in this document.',
    )).toBe(false);
    expect(isActionableConsoleError(
      'Failed to load resource: net::ERR_CONNECTION_REFUSED',
    )).toBe(false);
    expect(isActionableConsoleError(
      'Failed to load resource: net::ERR_NAME_NOT_RESOLVED',
    )).toBe(false);
    expect(isActionableConsoleError('ReferenceError: broken is not defined')).toBe(true);
    expect(isActionableConsoleError(
      'Failed to load resource: the server responded with a status of 404 (File not found)',
    )).toBe(true);
  });

  test('filters third-party embed localStorage SecurityError but keeps real page errors', () => {
    expect(isActionablePageError(
      "Failed to read the 'localStorage' property from 'Window': Access is denied for this document.",
    )).toBe(false);
    expect(isActionablePageError('ReferenceError: broken is not defined')).toBe(true);
  });

  describe('navigateWithRetry bounded transient 5xx policy (ISSUE-4104)', () => {
    test('declares standard retryable 5xx status codes', () => {
      expect(RETRYABLE_STATUS_CODES).toBeInstanceOf(Set);
      expect(RETRYABLE_STATUS_CODES.has(502)).toBe(true);
      expect(RETRYABLE_STATUS_CODES.has(503)).toBe(true);
      expect(RETRYABLE_STATUS_CODES.has(504)).toBe(true);
      expect(RETRYABLE_STATUS_CODES.has(500)).toBe(false);
      expect(RETRYABLE_STATUS_CODES.has(404)).toBe(false);
    });

    test('validates contracts and throws on invalid arguments', async () => {
      const page = { goto: jest.fn() };
      await expect(navigateWithRetry(page, '')).rejects.toThrow(TypeError);
      await expect(navigateWithRetry(page, 'http://test', { maxRetries: -1 })).rejects.toThrow(TypeError);
      await expect(navigateWithRetry(page, 'http://test', { baseDelayMs: -10 })).rejects.toThrow(TypeError);
    });

    test('succeeds immediately on HTTP 200 without retrying', async () => {
      const mockResponse = { status: () => 200, ok: () => true };
      const page = { goto: jest.fn().mockResolvedValue(mockResponse) };
      const sleeps = [];
      const sleepFn = (ms) => { sleeps.push(ms); return Promise.resolve(); };

      const result = await navigateWithRetry(page, 'http://test/page.html', {
        maxRetries: 3,
        baseDelayMs: 100,
        sleepFn,
      });

      expect(page.goto).toHaveBeenCalledTimes(1);
      expect(result.response).toBe(mockResponse);
      expect(result.error).toBeNull();
      expect(result.retried).toBe(false);
      expect(result.attempts).toHaveLength(1);
      expect(result.attempts[0]).toEqual({ attempt: 1, status: 200, error: null });
      expect(sleeps).toEqual([]);
    });

    test('recovers from transient HTTP 503 on retry and records observable backoff', async () => {
      const res503 = { status: () => 503, ok: () => false };
      const res200 = { status: () => 200, ok: () => true };
      const page = {
        goto: jest.fn()
          .mockResolvedValueOnce(res503)
          .mockResolvedValueOnce(res200),
      };
      const sleeps = [];
      const logs = [];
      const sleepFn = (ms) => { sleeps.push(ms); return Promise.resolve(); };
      const logger = (msg) => logs.push(msg);
      const resetAttemptEvidence = jest.fn();

      const result = await navigateWithRetry(page, 'http://test/articles/page.html', {
        maxRetries: 3,
        baseDelayMs: 250,
        sleepFn,
        logger,
        verbose: true,
        resetAttemptEvidence,
      });

      expect(page.goto).toHaveBeenCalledTimes(2);
      expect(result.response).toBe(res200);
      expect(result.error).toBeNull();
      expect(result.retried).toBe(true);
      expect(result.attempts).toHaveLength(2);
      expect(result.attempts[0]).toEqual({ attempt: 1, status: 503, error: null });
      expect(result.attempts[1]).toEqual({ attempt: 2, status: 200, error: null });
      expect(sleeps).toEqual([250]); // 250 * 2^0
      expect(resetAttemptEvidence).toHaveBeenCalledTimes(2);
      expect(logs[0]).toContain('Transient HTTP 503 on http://test/articles/page.html (attempt 1/4); retrying in 250ms...');
    });

    test('recovers on 3rd attempt with exponential backoff progression', async () => {
      const res503 = { status: () => 503, ok: () => false };
      const res502 = { status: () => 502, ok: () => false };
      const res200 = { status: () => 200, ok: () => true };
      const page = {
        goto: jest.fn()
          .mockResolvedValueOnce(res503)
          .mockResolvedValueOnce(res502)
          .mockResolvedValueOnce(res200),
      };
      const sleeps = [];
      const sleepFn = (ms) => { sleeps.push(ms); return Promise.resolve(); };

      const result = await navigateWithRetry(page, 'http://test/page.html', {
        maxRetries: 3,
        baseDelayMs: 200,
        sleepFn,
      });

      expect(page.goto).toHaveBeenCalledTimes(3);
      expect(result.response).toBe(res200);
      expect(result.retried).toBe(true);
      expect(result.attempts).toHaveLength(3);
      expect(sleeps).toEqual([200, 400]); // 200 * 2^0, 200 * 2^1
    });

    test('exhausts retries on persistent HTTP 503 and preserves failed response', async () => {
      const res503 = { status: () => 503, ok: () => false };
      const page = { goto: jest.fn().mockResolvedValue(res503) };
      const sleeps = [];
      const sleepFn = (ms) => { sleeps.push(ms); return Promise.resolve(); };

      const result = await navigateWithRetry(page, 'http://test/failed.html', {
        maxRetries: 3,
        baseDelayMs: 100,
        sleepFn,
      });

      expect(page.goto).toHaveBeenCalledTimes(4); // initial + 3 retries
      expect(result.response).toBe(res503);
      expect(result.retried).toBe(true);
      expect(result.attempts).toHaveLength(4);
      expect(sleeps).toEqual([100, 200, 400]);
    });

    test('does not retry non-retriable HTTP 404 or HTTP 500 status codes', async () => {
      const res404 = { status: () => 404, ok: () => false };
      const page = { goto: jest.fn().mockResolvedValue(res404) };
      const sleeps = [];
      const sleepFn = (ms) => { sleeps.push(ms); return Promise.resolve(); };

      const result = await navigateWithRetry(page, 'http://test/missing.html', {
        maxRetries: 3,
        baseDelayMs: 100,
        sleepFn,
      });

      expect(page.goto).toHaveBeenCalledTimes(1);
      expect(result.response).toBe(res404);
      expect(result.retried).toBe(false);
      expect(result.attempts).toHaveLength(1);
      expect(sleeps).toEqual([]);
    });

    test('does not retry navigation exceptions outside the response policy', async () => {
      const res200 = { status: () => 200, ok: () => true };
      const page = {
        goto: jest.fn()
          .mockRejectedValueOnce(new Error('net::ERR_CONNECTION_RESET'))
          .mockResolvedValueOnce(res200),
      };
      const sleeps = [];
      const sleepFn = (ms) => { sleeps.push(ms); return Promise.resolve(); };

      const result = await navigateWithRetry(page, 'http://test/reset.html', {
        maxRetries: 2,
        baseDelayMs: 150,
        sleepFn,
      });

      expect(page.goto).toHaveBeenCalledTimes(1);
      expect(result.response).toBeNull();
      expect(result.error).toBe('net::ERR_CONNECTION_RESET');
      expect(result.retried).toBe(false);
      expect(result.attempts).toHaveLength(1);
      expect(result.attempts[0].error).toBe('net::ERR_CONNECTION_RESET');
      expect(sleeps).toEqual([]);
    });
  });

  test('summarizes transient attempts without hiding exhausted evidence cells', () => {
    expect(summarizeNavigationAttempts([
      {
        navigation_attempts: [
          { attempt: 1, status: 503, error: null },
          { attempt: 2, status: 200, error: null },
        ],
      },
      {
        navigation_attempts: [
          { attempt: 1, status: 502, error: null },
          { attempt: 2, status: 502, error: null },
          { attempt: 3, status: 502, error: null },
        ],
      },
      { navigation_attempts: [{ attempt: 1, status: 404, error: null }] },
    ])).toEqual({
      navigation_attempt_count: 6,
      retried_evidence_count: 2,
      transient_response_count: 4,
      exhausted_retry_count: 1,
    });
  });

  test('emits self-describing bounded retry policy evidence', () => {
    expect(navigationRetryPolicyEvidence({
      documentRetries: 2,
      documentRetryDelayMs: 500,
    })).toEqual({
      max_retries: 2,
      maximum_attempts: 3,
      base_delay_ms: 500,
      backoff: 'exponential',
      retryable_status_codes: [502, 503, 504],
    });
  });
});

describe('axe-core policy (ISSUE-4126)', () => {
  const {
    AXE_FAILING_IMPACTS,
    axePolicyEvidence,
    markAxeCells,
    summarizeAxeViolations,
  } = require('../scripts/verify-public-site.js');

  test('defaults to fail and rejects unknown modes', () => {
    expect(parseArgs([]).axe).toBe('fail');
    expect(parseArgs(['--axe', 'warn']).axe).toBe('warn');
    expect(parseArgs(['--axe', 'off']).axe).toBe('off');
    expect(() => parseArgs(['--axe', 'loud'])).toThrow(/--axe must be one of/);
  });

  test('keeps only serious and critical violations, sorted by rule id', () => {
    expect(AXE_FAILING_IMPACTS).toEqual(['serious', 'critical']);
    const summary = summarizeAxeViolations([
      { id: 'region', impact: 'moderate', help: 'x', helpUrl: 'u', nodes: [{ target: ['main'] }] },
      { id: 'link-name', impact: 'serious', help: 'Links must have discernible text', helpUrl: 'u1', nodes: [{ target: ['a.x'] }, { target: ['a.y'] }] },
      { id: 'color-contrast', impact: 'serious', help: 'c', helpUrl: 'u2', nodes: [] },
      { id: 'image-alt', impact: 'critical', help: 'i', helpUrl: 'u3', nodes: [{ target: ['img'] }] },
      { id: 'label', impact: 'minor', help: 'l', helpUrl: 'u4', nodes: [] },
    ]);
    expect(summary.map((v) => v.id)).toEqual(['color-contrast', 'image-alt', 'link-name']);
    expect(summary[2]).toEqual({
      id: 'link-name',
      impact: 'serious',
      help: 'Links must have discernible text',
      help_url: 'u1',
      node_count: 2,
      first_target: 'a.x',
    });
    expect(() => summarizeAxeViolations(null)).toThrow(TypeError);
  });

  test('scans each evidence cell in the plan unless axe is off (#4562)', () => {
    const plan = buildEvidencePlan(fixtureManifest());
    const marked = markAxeCells(plan, 'warn');
    expect(marked.filter((item) => item.axe)).toHaveLength(plan.length);
    expect(markAxeCells(plan, 'off').some((item) => item.axe)).toBe(false);
    expect(marked).toHaveLength(plan.length);
  });

  test('summarizes scanned routes and violations without hiding warn-mode findings', () => {
    const results = [
      { route: '/', axe_violations: [] },
      { route: '/a.html', axe_violations: [{ id: 'link-name' }, { id: 'image-alt' }] },
      { route: '/a.html' },
      { route: '/b.html', axe_violations: [{ id: 'link-name' }] },
    ];
    expect(axePolicyEvidence({ axe: 'warn' }, results)).toEqual({
      mode: 'warn',
      impacts: ['serious', 'critical'],
      scanned_route_count: 3,
      scanned_cell_count: 3,
      routes_with_violations: ['/a.html', '/b.html'],
      violation_count: 3,
    });
  });

  test('summarizes scanned routes and zero violations in fail mode (#4561)', () => {
    const results = [
      { route: '/', axe_violations: [] },
      { route: '/articles/theory-part1.html', axe_violations: [] },
    ];
    expect(axePolicyEvidence({ axe: 'fail' }, results)).toEqual({
      mode: 'fail',
      impacts: ['serious', 'critical'],
      scanned_route_count: 2,
      scanned_cell_count: 2,
      routes_with_violations: [],
      violation_count: 0,
    });
  });

  test('summarizes multi-viewport and multi-theme cells for the same route (#4562)', () => {
    const results = [
      { route: '/', viewport: { id: 'desktop-small' }, theme: 'light', axe_violations: [] },
      { route: '/', viewport: { id: 'desktop-small' }, theme: 'dark', axe_violations: [] },
      { route: '/', viewport: { id: 'mobile' }, theme: 'light', axe_violations: [] },
      { route: '/', viewport: { id: 'mobile' }, theme: 'dark', axe_violations: [{ id: 'color-contrast' }] },
      { route: '/b.html', viewport: { id: 'desktop-small' }, theme: 'light', axe_violations: [{ id: 'color-contrast' }] },
      { route: '/b.html', viewport: { id: 'desktop-small' }, theme: 'dark', axe_violations: [{ id: 'color-contrast' }] },
    ];
    expect(axePolicyEvidence({ axe: 'fail' }, results)).toEqual({
      mode: 'fail',
      impacts: ['serious', 'critical'],
      scanned_route_count: 2,
      scanned_cell_count: 6,
      routes_with_violations: ['/', '/b.html'],
      violation_count: 3,
    });
  });
});

describe('waitForFunction timeouts', () => {
  // Playwright: page.waitForFunction(pageFunction, arg, options). A `{ timeout }`
  // passed as the second argument is treated as `arg` and silently ignored.
  function mockPage() {
    return {
      waitForFunction: jest.fn().mockResolvedValue(true),
      evaluate: jest.fn().mockResolvedValue(undefined),
    };
  }

  test('waitForVisibleMath passes its timeout as the options argument', async () => {
    const page = mockPage();
    await waitForVisibleMath(page);
    expect(page.waitForFunction).toHaveBeenCalledTimes(1);
    const [fn, arg, options] = page.waitForFunction.mock.calls[0];
    expect(typeof fn).toBe('function');
    expect(arg).toBeUndefined();
    expect(options).toEqual({ timeout: 15000 });
  });

  test('waitForSettledPage passes every timeout as the options argument', async () => {
    const page = mockPage();
    await waitForSettledPage(page);
    const calls = page.waitForFunction.mock.calls;
    // MathJax gate, visible math (x2), fixed-header padding, deferred wrappers.
    expect(calls.map(([, , options]) => options)).toEqual([
      { timeout: 20000 },
      { timeout: 15000 },
      { timeout: 15000 },
      { timeout: 15000 },
      { timeout: 15000 },
    ]);
    for (const [fn, arg] of calls) {
      expect(typeof fn).toBe('function');
      expect(arg).toBeUndefined();
    }
  });

  test('no waitForFunction call in the verifier passes options as the arg', () => {
    const source = fs.readFileSync(
      path.join(__dirname, '..', 'scripts', 'verify-public-site.js'),
      'utf8',
    );
    expect(source).toContain('waitForFunction(');
    expect(source).not.toMatch(/\},\s*\{\s*timeout\s*:/);
  });
});
