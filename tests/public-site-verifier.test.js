const {
  assertManifest,
  buildEvidencePlan,
  canonicalPathMatches,
  fixedElementCanObscureHeading,
  headingBeginsWithinViewport,
  isActionableConsoleError,
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
});
