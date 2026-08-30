const {
  assertManifest,
  buildEvidencePlan,
  canonicalPathMatches,
  fixedElementCanObscureHeading,
  headingBeginsWithinViewport,
  isActionableConsoleError,
  navigateWithRetry,
  RETRYABLE_STATUS_CODES,
  screenshotOptions,
  screenshotName,
} = require('../scripts/verify-public-site.js');

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

  test('filters the browser compute-pressure warning but keeps real console errors', () => {
    expect(isActionableConsoleError(
      'Permissions policy violation: compute-pressure is not allowed in this document.',
    )).toBe(false);
    expect(isActionableConsoleError('ReferenceError: broken is not defined')).toBe(true);
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

      const result = await navigateWithRetry(page, 'http://test/articles/page.html', {
        maxRetries: 3,
        baseDelayMs: 250,
        sleepFn,
        logger,
        verbose: true,
      });

      expect(page.goto).toHaveBeenCalledTimes(2);
      expect(result.response).toBe(res200);
      expect(result.error).toBeNull();
      expect(result.retried).toBe(true);
      expect(result.attempts).toHaveLength(2);
      expect(result.attempts[0]).toEqual({ attempt: 1, status: 503, error: null });
      expect(result.attempts[1]).toEqual({ attempt: 2, status: 200, error: null });
      expect(sleeps).toEqual([250]); // 250 * 2^0
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

    test('recovers from transient network/navigation errors', async () => {
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

      expect(page.goto).toHaveBeenCalledTimes(2);
      expect(result.response).toBe(res200);
      expect(result.error).toBeNull();
      expect(result.retried).toBe(true);
      expect(result.attempts).toHaveLength(2);
      expect(result.attempts[0].error).toBe('net::ERR_CONNECTION_RESET');
      expect(result.attempts[1].status).toBe(200);
      expect(sleeps).toEqual([150]);
    });
  });
});
