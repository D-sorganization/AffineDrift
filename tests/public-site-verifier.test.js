const {
  assertManifest,
  buildEvidencePlan,
  canonicalPathMatches,
  fixedElementCanObscureHeading,
  headingBeginsWithinViewport,
  isActionableConsoleError,
  isRetriableDocumentStatus,
  navigateDocumentWithRetries,
  parseArgs,
  summarizeNavigationAttempts,
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

  test('keeps retries opt-in and validates the bounded live policy arguments', () => {
    const defaults = parseArgs([]);
    expect(defaults.documentAttempts).toBe(1);
    expect(defaults.documentRetryDelayMs).toBe(500);

    const live = parseArgs([
      '--document-attempts',
      '3',
      '--document-retry-delay-ms',
      '500',
    ]);
    expect(live.documentAttempts).toBe(3);
    expect(live.documentRetryDelayMs).toBe(500);
    expect(() => parseArgs(['--document-attempts', '0'])).toThrow(/positive integer/);
    expect(() => parseArgs(['--document-retry-delay-ms', '-1'])).toThrow(/non-negative integer/);
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

  test('retries an observable transient document response until success', async () => {
    const statuses = [503, 200];
    const page = {
      goto: jest.fn(async () => {
        const status = statuses.shift();
        return {
          ok: () => status >= 200 && status < 400,
          status: () => status,
        };
      }),
    };
    const wait = jest.fn(async () => undefined);
    const resetAttemptEvidence = jest.fn();
    const reportRetry = jest.fn();

    const result = await navigateDocumentWithRetries({
      page,
      targetUrl: 'https://affinedrift.org/example.html',
      maxAttempts: 3,
      retryDelayMs: 25,
      wait,
      resetAttemptEvidence,
      reportRetry,
    });

    expect(result.navigationError).toBeNull();
    expect(result.response.status()).toBe(200);
    expect(result.attempts).toEqual([
      { attempt: 1, status: 503, outcome: 'retry' },
      { attempt: 2, status: 200, outcome: 'success' },
    ]);
    expect(wait).toHaveBeenCalledWith(25);
    expect(resetAttemptEvidence).toHaveBeenCalledTimes(2);
    expect(reportRetry).toHaveBeenCalledWith(
      'Transient document response 503 for https://affinedrift.org/example.html; retrying 2/3.',
    );
  });

  test('fails closed after exhausting the bounded transient response policy', async () => {
    const page = {
      goto: jest.fn(async () => ({ ok: () => false, status: () => 503 })),
    };
    const reportRetry = jest.fn();

    const result = await navigateDocumentWithRetries({
      page,
      targetUrl: 'https://affinedrift.org/example.html',
      maxAttempts: 3,
      retryDelayMs: 0,
      wait: async () => undefined,
      reportRetry,
    });

    expect(page.goto).toHaveBeenCalledTimes(3);
    expect(result.response.status()).toBe(503);
    expect(result.attempts).toEqual([
      { attempt: 1, status: 503, outcome: 'retry' },
      { attempt: 2, status: 503, outcome: 'retry' },
      { attempt: 3, status: 503, outcome: 'exhausted' },
    ]);
    expect(reportRetry).toHaveBeenCalledTimes(2);
  });

  test('does not retry non-retriable responses or navigation exceptions', async () => {
    expect(isRetriableDocumentStatus(500)).toBe(true);
    expect(isRetriableDocumentStatus(502)).toBe(true);
    expect(isRetriableDocumentStatus(503)).toBe(true);
    expect(isRetriableDocumentStatus(504)).toBe(true);
    expect(isRetriableDocumentStatus(404)).toBe(false);
    expect(isRetriableDocumentStatus(501)).toBe(false);

    const notFoundPage = {
      goto: jest.fn(async () => ({ ok: () => false, status: () => 404 })),
    };
    const notFound = await navigateDocumentWithRetries({
      page: notFoundPage,
      targetUrl: 'https://affinedrift.org/missing.html',
      wait: async () => undefined,
    });
    expect(notFoundPage.goto).toHaveBeenCalledTimes(1);
    expect(notFound.attempts).toEqual([{ attempt: 1, status: 404, outcome: 'non-retriable' }]);

    const failedPage = {
      goto: jest.fn(async () => {
        throw new Error('connection reset');
      }),
    };
    const failed = await navigateDocumentWithRetries({
      page: failedPage,
      targetUrl: 'https://affinedrift.org/example.html',
      wait: async () => undefined,
    });
    expect(failedPage.goto).toHaveBeenCalledTimes(1);
    expect(failed.navigationError).toBe('connection reset');
    expect(failed.attempts).toEqual([
      {
        attempt: 1,
        status: null,
        outcome: 'navigation-error',
        error: 'connection reset',
      },
    ]);
  });

  test('summarizes retry evidence without hiding transient or exhausted responses', () => {
    const summary = summarizeNavigationAttempts([
      {
        navigation_attempts: [
          { attempt: 1, status: 503, outcome: 'retry' },
          { attempt: 2, status: 200, outcome: 'success' },
        ],
      },
      {
        navigation_attempts: [
          { attempt: 1, status: 502, outcome: 'retry' },
          { attempt: 2, status: 502, outcome: 'retry' },
          { attempt: 3, status: 502, outcome: 'exhausted' },
        ],
      },
      {
        navigation_attempts: [{ attempt: 1, status: 404, outcome: 'non-retriable' }],
      },
    ]);

    expect(summary).toEqual({
      navigation_attempt_count: 6,
      retried_evidence_count: 2,
      transient_response_count: 4,
      exhausted_retry_count: 1,
    });
  });
});
